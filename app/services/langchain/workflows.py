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

# ==================================================
# 🧽 SANITIZADOR DE JSON — CRÍTICO PARA Prompt 2
# ==================================================

def sanitize_quotes(raw: str) -> str:
    """Repara comillas internas que rompen el JSON."""
    if not raw:
        return raw

    raw = raw.replace("“", '"').replace("”", '"').replace("’", "'")

    # Caso más crítico: "algo "texto" algo"
    raw = re.sub(
        r'"([^"]*?)"([^"]*?)"',
        r'"\1\"\2"',
        raw
    )

    # Caso específico del ESG: privacy by design
    raw = raw.replace('"privacy by design"', '\\"privacy by design\\"')

    return raw


# ==================================================
# 🧰 FIX JSON GENERAL
# ==================================================

def try_fix_json(raw_text: str):
    raw_text = sanitize_quotes(raw_text.strip())
    json_candidate = re.search(r"\{.*\}", raw_text, re.DOTALL)

    if json_candidate:
        raw_text = json_candidate.group(0)

    fixed = re.sub(r",(\s*[}\]])", r"\1", raw_text)
    fixed = fixed.replace("\n", " ").replace("\t", " ")
    fixed = re.sub(r"(\d+),(\d+)", r"\1.\2", fixed)

    # Intento directo
    try:
        return json.loads(fixed)
    except Exception:
        pass

    # Intento con tu reparador viejo
    try:
        return clean_and_parse_json(fixed)
    except Exception:
        return {}


# ==================================================
# 🔒 INVOCACIÓN CON RECUPERACIÓN DE THREAD LIMPIO
# ==================================================

async def safe_invoke(call_params, retries=5, base_wait=15):
    for attempt in range(1, retries + 1):
        try:
            result = assistant.invoke(call_params)
            run = result[0]

            if hasattr(run, "status") and run.status in ["expired", "failed"]:
                print(f"⚠️ Run inválido ({run.status}) → regenerando thread…")
                call_params.pop("thread_id", None)
                await asyncio.sleep(3)
                continue

            return result

        except Exception as e:
            err = str(e).lower()

            if "insufficient_quota" in err:
                raise RuntimeError("❌ Créditos agotados.")

            if any(x in err for x in ["rate_limit", "tokens per minute"]):
                print("⏳ Rate limit → esperando 3 minutos…")
                await asyncio.sleep(180)
                call_params.pop("thread_id", None)
                continue

            if "timeout" in err or "connection" in err:
                wait_time = base_wait * attempt
                print(f"🌐 Timeout → reintentando en {wait_time}s…")
                await asyncio.sleep(wait_time)
                continue

            raise

    raise RuntimeError("❌ No se pudo completar llamada tras múltiples intentos.")


# ==================================================
# 🚀 PIPELINE ESG
# ==================================================

async def run_esg_analysis(
    organization_name: str,
    country: str,
    website: str,
    industry: str,
    document: Optional[str] = None
):
    print("\n🚀 Iniciando análisis ESG para", organization_name)

    responses = []
    failed_prompts = []
    thread_id = None

    # -------------------------------------------------
    # Helper interno
    # -------------------------------------------------
    async def run_prompt(prompt, content, name=None, retries=4, use_thread=True):
        nonlocal thread_id

        for attempt in range(1, retries + 1):
            print(f"\n🧪 Ejecutando {name or prompt.name} (Intento {attempt}/{retries})")

            params = {"content": content}
            if use_thread and thread_id:
                params["thread_id"] = thread_id

            try:
                result = await safe_invoke(params)
                run = result[0]

                if hasattr(run, "thread_id"):
                    thread_id = run.thread_id

                raw = run.content[0].text.value.strip()
                parsed = try_fix_json(raw)

                print(f"✅ {name or prompt.name} completado")
                return parsed

            except Exception as e:
                print(f"⚠️ Error recuperable en {name}: {e}")
                thread_id = None
                await asyncio.sleep(5)
                continue

        print(f"⛔ {name or prompt.name} falló TODOS los intentos")
        failed_prompts.append(prompt)
        return None

    # ==================================================
    # 🧭 Prompt 1 — thread limpio
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
        responses.append({"name": prompt_1.name, "response_content": p1, "thread_id": thread_id})

      # ==================================================
    # 🧭 Prompt 2 (solo 2 intentos)
    # ==================================================
    print("\n🔹 Ejecutando Prompt 2 (máx 2 intentos)")
    rows = []
    p2 = None

    def extract_materiality_table(raw_text: str):
        """
        Permite rescatar la tabla incluso si el JSON está roto.
        """
        raw_text = sanitize_quotes(raw_text)

        # Buscar manualmente el array materiality_table
        match = re.search(
            r'"materiality_table"\s*:\s*\[(.*?)\]',
            raw_text,
            re.DOTALL
        )

        if not match:
            return None

        content = match.group(1)

        # Intentar envolver en JSON válido
        try:
            cleaned = "[" + content + "]"
            cleaned = cleaned.replace("\n", " ").replace("\t", " ")
            cleaned = sanitize_quotes(cleaned)
            arr = json.loads(cleaned)
            return arr
        except:
            return None

    for attempt in range(1, 3):
        print(f"\n🧪 Prompt 2 — Intento {attempt}/2")

        result = await run_prompt(
            prompt_2,
            prompt_2.format(
                organization_name=organization_name,
                country=country,
                website=website,
                industry=industry,
            ),
            name=f"Prompt 2 — Intento {attempt}/2"
        )

        if not result:
            print("❌ Prompt 2 devolvió None → reintentando…")
            await asyncio.sleep(10)
            continue

        # Si viene JSON válido → perfecto
        rows = result.get("materiality_table", [])

        # Si viene vacío → intentar extracción manual
        if not rows:
            print("⚠️ Intentando recuperación manual tabla...")
            rows = extract_materiality_table(
                raw_text=run_prompt.last_raw  # ← guardamos raw en run_prompt
            ) or []

        if len(rows) >= MIN_ROWS_PROMPT_2:
            print("✅ Prompt 2 alcanzó el mínimo de filas")
            break

        print("⚠️ Prompt 2 corto → esperando 10s…")
        await asyncio.sleep(10)

    # Si después de los 2 intentos sigue fallado → ABORTAR
    if len(rows) < MIN_ROWS_PROMPT_2:
        print("⛔ Prompt 2 falló definitivamente → abortando pipeline.")
        return {
            "status": "failed",
            "failed_prompts": ["Prompt 2"],
            "responses": responses
        }


    # ==================================================
    # 🧭 Prompts 3 → 11
    # ==================================================
    for i, p in enumerate(
        [prompt_3, prompt_4, prompt_5, prompt_6,
         prompt_7, prompt_8, prompt_9, prompt_10, prompt_11], 1
    ):

        parsed = await run_prompt(
            p,
            p.template,
            name=p.name,
            retries=3
        )

        if parsed:
            responses.append({"name": p.name, "response_content": parsed, "thread_id": thread_id})
        else:
            failed_prompts.append(p)

        if i % 2 == 0:
            await asyncio.sleep(random.randint(20, 40))

    # ==================================================
    # 🎯 RESULTADO FINAL
    # ==================================================
    return {
        "status": "complete" if not failed_prompts else "incomplete",
        "responses": responses,
        "failed_prompts": [p.name for p in failed_prompts]
    }
