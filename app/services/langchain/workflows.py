import os
import asyncio
import random
import json
import re
from typing import Optional
from app.services.langchain.prompts import *
from app.utils.json_formatter import clean_and_parse_json
from app.core.config import settings
from langchain_community.agents.openai_assistant import OpenAIAssistantV2Runnable

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

assistant = OpenAIAssistantV2Runnable(
    assistant_id="asst_uN6jjvZ9s4Yv2PFmV1J4iRJB",
    tools=[{
        "type": "code_interpreter",
        "file_ids": [
            "file-LzzGj4YJdW1T4bsNp9EcCD",
            "file-96uwnReXqbEbh97miBRJd5",
            "file-6UCacZ7WF2eGxcuZuqPnuD",
            "file-4dixqFDgMjDU39mAEewmRw",
            "file-Sy8QSZkhRsZdkG7oMU3xNZ",
            "file-WucnFWVfve87jhWqW9DH4"
        ]
    }],
)

MIN_ROWS_PROMPT_2 = 15
MAX_ROWS_PROMPT_2 = 30


def try_fix_json(raw_text: str):
    raw_text = raw_text.strip()
    json_candidate = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if json_candidate:
        raw_text = json_candidate.group(0)
    fixed = re.sub(r",(\s*[}\]])", r"\1", raw_text)
    fixed = fixed.replace("“", '"').replace("”", '"').replace("’", "'")
    fixed = fixed.replace("\n", " ").replace("\t", " ")
    fixed = re.sub(r"(\d+),(\d+)", r"\1.\2", fixed)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError:
        return clean_and_parse_json(fixed)


async def safe_invoke(call_params, retries=5, base_wait=15):
    """
    Llama al assistant con tolerancia a rate limits y fallos de red.
    - Si es un rate limit de tokens/minuto → espera 3 min y reintenta.
    - Si es un error de cuota agotada → aborta inmediatamente.
    - Otros errores → reintentos progresivos normales.
    """
    for attempt in range(1, retries + 1):
        try:
            return assistant.invoke(call_params)

        except Exception as e:
            err = str(e).lower()

            # 🚫 Si no hay más crédito (no sirve esperar)
            if "insufficient_quota" in err or "exceeded your current quota" in err:
                raise RuntimeError(
                    "❌ Créditos de OpenAI agotados o sin plan activo. "
                    "No se puede continuar hasta recargar o cambiar API key."
                )

            # ⚠️ Si es un rate limit por tokens/minuto (TPM)
            if any(x in err for x in ["rate_limit", "tokens per minute", "too many requests"]):
                wait_time = 180  # 3 minutos fijos
                print(f"⚠️ Rate limit por tokens/minuto detectado — esperando {wait_time//60} minutos antes de reintentar...")
                await asyncio.sleep(wait_time)
                continue  # vuelve a intentar el mismo prompt después del cooldown

            # 🌐 Errores de red o conexión temporal
            if "timeout" in err or "connection" in err:
                wait_time = base_wait * attempt
                print(f"🌐 Error de conexión ({err}) — reintentando en {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue

            # 🚫 Otros errores no recuperables
            raise

    # Si después de todos los intentos sigue fallando, abortar con mensaje claro
    raise RuntimeError("No se pudo completar la llamada a OpenAI tras múltiples intentos.")



# ==================================================
# 🚀 Proceso principal con Prompt 2 iterativo
# ==================================================
async def run_esg_analysis(
    organization_name: str,
    country: str,
    website: str,
    industry: str,
    document: Optional[str] = None
) -> str:
    responses = []
    failed_prompts = []
    thread_id = None

    # ============================
    # 🧭 Prompt 1
    # ============================
    print(f"\n🔹 Ejecutando Prompt 1")
    try:
        call_params = {
            "content": prompt_1.format(
                organization_name=organization_name,
                country=country,
                website=website,
                industry=industry,
                document=document or "",
            )
        }
        response = await safe_invoke(call_params)
        raw_output = response[0].content[0].text.value.strip()
        parsed_json = clean_and_parse_json(raw_output)
        print("✅ Prompt 1 completado")
        thread_id = response[0].thread_id
        responses.append({
            "name": prompt_1.name,
            "response_content": parsed_json,
            "thread_id": thread_id,
        })
    except Exception as e:
        print(f"❌ Error en Prompt 1: {e}")
        failed_prompts.append(prompt_1)

    # ============================
    # 🧭 Prompt 2 (hasta 5 intentos)
    # ============================
    print(f"\n🔹 Ejecutando Prompt 2 (Identificación de Impactos)")
    rows = []
    parsed_json = {}
    for attempt in range(1, 6):
        try:
            print(f"🧪 Intento {attempt}/5 de Prompt 2…", flush=True)
            call_params = {
                "content": prompt_2.format(
                    organization_name=organization_name,
                    country=country,
                    website=website,
                    industry=industry,
                ),
                **({"thread_id": thread_id} if thread_id else {}),
            }
            response = await safe_invoke(call_params)
            raw_output = response[0].content[0].text.value.strip()
            parsed_json = clean_and_parse_json(raw_output)
            rows = parsed_json.get("materiality_table", [])
            print(f"📊 Prompt 2 devolvió {len(rows)} filas")

            if len(rows) >= MIN_ROWS_PROMPT_2:
                print("✅ Prompt 2 alcanzó el mínimo de filas requerido.")
                break
            else:
                wait_time = 10 + random.randint(0, 10)
                print(f"⚠️ Menos de {MIN_ROWS_PROMPT_2} filas → reintentando en {wait_time}s…")
                await asyncio.sleep(wait_time)

        except Exception as e:
            print(f"❌ Error en intento {attempt} de Prompt 2: {e}")
            await asyncio.sleep(15)

    # Después de 5 intentos, si sigue corto → ejecutar Prompt 2.1
    if len(rows) < MIN_ROWS_PROMPT_2:
        print("⚠️ Prompt 2 no alcanzó 15 filas tras 5 intentos → ejecutando Prompt 2.1…")
        try:
            call_params_2 = {
                "content": prompt_2_1.format(
                    organization_name=organization_name,
                    country=country,
                    website=website,
                    industry=industry,
                ),
                **({"thread_id": thread_id} if thread_id else {}),
            }
            response_2 = await safe_invoke(call_params_2)
            raw_output_2 = response_2[0].content[0].text.value.strip()
            parsed_json_2 = clean_and_parse_json(raw_output_2)
            rows_2 = parsed_json_2.get("materiality_table", [])
            temas_existentes = {r["tema"] for r in rows if "tema" in r}
            nuevos = [r for r in rows_2 if "tema" in r and r["tema"] not in temas_existentes]
            merged_rows = rows + nuevos
            print(f"🧩 Prompt 2.1 añadió {len(nuevos)} filas nuevas → total {len(merged_rows)}")

            if len(merged_rows) < MIN_ROWS_PROMPT_2:
                raise ValueError(f"❌ Ni Prompt 2 ni 2.1 alcanzaron {MIN_ROWS_PROMPT_2} filas.")
            parsed_json["materiality_table"] = merged_rows[:MAX_ROWS_PROMPT_2]
        except Exception as e:
            print(f"❌ Error en Prompt 2.1: {e}")
            print("⛔ Abortando proceso por falla crítica en Prompt 2.")
            return {"error": str(e), "failed_prompt": "Prompt 2"}

    responses.append({
        "name": prompt_2.name,
        "response_content": parsed_json,
        "thread_id": thread_id,
    })

    # ============================
    # 🧭 Prompts 3 → 11
    # ============================
    remaining_prompts = [
        prompt_3, prompt_4, prompt_5, prompt_6,
        prompt_7, prompt_8, prompt_9, prompt_10, prompt_11,
    ]

    print(f"\n🚀 Ejecutando prompts restantes…")
    for i, prompt in enumerate(remaining_prompts, 1):
        try:
            print(f"🧪 Ejecutando {prompt.name}")
            call_params = {"content": prompt.template}
            if thread_id:
                call_params["thread_id"] = thread_id
            response = await safe_invoke(call_params)
            raw_output = response[0].content[0].text.value.strip()
            response_content = try_fix_json(raw_output)
            thread_id = response[0].thread_id
            responses.append({
                "name": prompt.name,
                "response_content": response_content,
                "thread_id": thread_id,
            })
            print(f"✅ {prompt.name} completado")

            if i % 2 == 0 and i < len(remaining_prompts):
                delay = random.randint(25, 40)
                print(f"⏳ Esperando {delay}s…")
                await asyncio.sleep(delay)

        except Exception as e:
            print(f"❌ Error en {prompt.name}: {e}")
            failed_prompts.append(prompt)

    print(f"\n🎯 Proceso completado con {len(responses)} respuestas totales")

    status = "complete" if len(failed_prompts) == 0 else "incomplete"

    return {
        "status": status,
        "responses": responses,
        "failed_prompts": [p.name for p in failed_prompts],
    }

