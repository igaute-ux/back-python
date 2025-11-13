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

MIN_ROWS_PROMPT_2 = 10
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
    Ejecuta una llamada al Assistant con:
    - Manejo real de rate limits
    - Regeneración automática de un thread limpio
    - Reintentos progresivos
    """

    for attempt in range(1, retries + 1):
        try:
            result = assistant.invoke(call_params)

            # El assistant devuelve un array con un "run"
            run = result[0]

            # ❌ Si el run está fallado o expirado → no sirve, regenerar thread
            if hasattr(run, "status") and run.status in ["expired", "failed"]:
                print(f"⚠️ Run inválido: {run.status} → regenerando thread…")
                if "thread_id" in call_params:
                    del call_params["thread_id"]
                continue

            return result

        except Exception as e:
            err = str(e).lower()

            # 🟥 Créditos agotados → abortar
            if "insufficient_quota" in err or "exceeded your current quota" in err:
                raise RuntimeError(
                    "❌ Créditos agotados. No se puede continuar hasta recargar."
                )

            # 🟡 Rate limit real → esperar y regenerar thread limpio
            if any(x in err for x in ["rate_limit", "tokens per minute", "too many requests"]):
                wait_time = 180  # 3 minutos
                print(f"⏳ Rate limit detectado — esperando {wait_time//60} minutos…")
                await asyncio.sleep(wait_time)

                print("🧼 Eliminando thread_id para crear un run completamente nuevo.")
                if "thread_id" in call_params:
                    del call_params["thread_id"]

                continue  # reintentar

            # 🔵 Timeout o errores de red
            if "timeout" in err or "connection" in err:
                wait_time = base_wait * attempt
                print(f"🌐 Error de red — reintentando en {wait_time}s…")
                await asyncio.sleep(wait_time)
                continue

            # 🔴 Otros errores → no reintentables
            raise

    raise RuntimeError("No se pudo completar la llamada a OpenAI tras múltiples intentos.")



# ==================================================
# 🚀 Proceso principal con Prompt 2 iterativo
# ==================================================
# ==================================================
# 🚀 PIPELINE ESG DEFINITIVO (con recuperación y thread limpio)
# ==================================================

async def run_esg_analysis(
    organization_name: str,
    country: str,
    website: str,
    industry: str,
    document: Optional[str] = None
) -> str:
    print("\n🚀 Iniciando análisis ESG para", organization_name)
    
    responses = []
    failed_prompts = []
    thread_id = None

    # -------------------------------------------------
    # 🧠 Helper: ejecutar un prompt con auto-recovery
    # -------------------------------------------------
    async def run_prompt(prompt, formatted_content, name=None, use_thread=True, retries=4):
        nonlocal thread_id
        
        for attempt in range(1, retries + 1):
            print(f"\n🧪 Ejecutando {name or prompt.name} (Intento {attempt}/{retries})")
            
            call_params = {"content": formatted_content}

            # Usar thread solo si está permitido
            if use_thread and thread_id:
                call_params["thread_id"] = thread_id

            try:
                result = await safe_invoke(call_params)
                run = result[0]

                # Guardar nuevo thread_id
                if hasattr(run, "thread_id"):
                    thread_id = run.thread_id

                raw_output = run.content[0].text.value.strip()
                parsed = try_fix_json(raw_output)

                print(f"✅ {name or prompt.name} completado")
                return parsed

            except Exception as e:
                err = str(e).lower()

                # ❌ Error recuperable → regenerar thread y reintentar
                if any(k in err for k in ["expired", "failed", "rate_limit"]):
                    print("⚠️ Error recuperable, limpiando thread…")
                    thread_id = None
                    await asyncio.sleep(5)
                    continue

                # ❌ Error no recuperable
                print(f"❌ Error en {name or prompt.name}: {e}")
                return None

        print(f"⛔ {name or prompt.name} falló todos los intentos")
        failed_prompts.append(prompt)
        return None

    # ==================================================
    # 🧭 Prompt 1 — SIEMPRE inicia con thread limpio
    # ==================================================
    p1 = await run_prompt(
        prompt_1,
        prompt_1.format(
            organization_name=organization_name,
            country=country,
            website=website,
            industry=industry,
            document=document or "",
        ),
        name="Prompt 1",
        use_thread=False
    )

    if p1:
        responses.append({
            "name": prompt_1.name,
            "response_content": p1,
            "thread_id": thread_id,
        })

    # ==================================================
    # 🧭 Prompt 2 — máx. 2 intentos
    # ==================================================
    print("\n🔹 Ejecutando Prompt 2 (máx 2 intentos)")
    rows = []
    p2 = None

    for attempt in range(1, 3):
        p2 = await run_prompt(
            prompt_2,
            prompt_2.format(
                organization_name=organization_name,
                country=country,
                website=website,
                industry=industry,
            ),
            name=f"Prompt 2 — Intento {attempt}/2",
            use_thread=True
        )

        if p2:
            rows = p2.get("materiality_table", [])
            if len(rows) >= MIN_ROWS_PROMPT_2:
                print("✅ Prompt 2 alcanzó el mínimo de filas")
                break

        print("⚠️ Prompt 2 corto → esperando 10s antes de reintentar…")
        await asyncio.sleep(10)

    # ==================================================
    # 🧭 Prompt 2.1 — SIEMPRE se ejecuta
    # ==================================================
    p21 = await run_prompt(
        prompt_2_1,
        prompt_2_1.format(
            organization_name=organization_name,
            country=country,
            website=website,
            industry=industry,
        ),
        name="Prompt 2.1",
        use_thread=True
    )

    if p21:
        extra_rows = p21.get("materiality_table", [])
        temas_existentes = {r["tema"] for r in rows if "tema" in r}
        nuevos = [r for r in extra_rows if r.get("tema") not in temas_existentes]
        rows.extend(nuevos)
        p2 = {"materiality_table": rows[:MAX_ROWS_PROMPT_2]}

    responses.append({
        "name": prompt_2.name,
        "response_content": p2,
        "thread_id": thread_id,
    })

    # ==================================================
    # 🧭 Prompts 3 → 11 con recuperación automática
    # ==================================================
    prompts = [
        prompt_3, prompt_4, prompt_5, prompt_6,
        prompt_7, prompt_8, prompt_9, prompt_10, prompt_11,
    ]

    for i, p in enumerate(prompts, 1):
        parsed = await run_prompt(
            p,
            p.template,
            name=p.name,
            use_thread=True,
            retries=3  # prompts pesados
        )

        if parsed:
            responses.append({
                "name": p.name,
                "response_content": parsed,
                "thread_id": thread_id,
            })
        else:
            failed_prompts.append(p)

        if i % 2 == 0:
            await asyncio.sleep(random.randint(20, 40))

    # ==================================================
    # ✔️ Resultado final
    # ==================================================

    print("\n🎯 ESG Analysis finalizado.")
    print("Prompts fallados:", [p.name for p in failed_prompts])

    return {
        "status": "complete" if not failed_prompts else "incomplete",
        "responses": responses,
        "failed_prompts": [p.name for p in failed_prompts],
    }
