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
    tools=[
        {
            "type": "file_search",
            "vector_store_ids": ["vs_68c18287fbbc81919a024e80eb9d58b6"]
        },
        {"type": "code_interpreter"}
    ]
)

MIN_ROWS_PROMPT_2 = 10
MAX_ROWS_PROMPT_2 = 30


# ==================================================
# 🧽 FIX JSON — devuelve None si no se puede parsear
# ==================================================
def try_fix_json(raw_text: str):
    raw_text = raw_text.replace("“", '"').replace("”", '"').replace("’", "'")

    # Buscar bloque JSON
    json_candidate = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if json_candidate:
        raw_text = json_candidate.group(0)

    raw_text = raw_text.replace("\n", " ").replace("\t", " ")
    raw_text = re.sub(r",(\s*[}\]])", r"\1", raw_text)

    try:
        return json.loads(raw_text)
    except:
        try:
            return clean_and_parse_json(raw_text)
        except:
            return None   # ← importante: None, no {}


# ==================================================
# 🛟 Rescate manual de arrays en prompts con JSON roto
# ==================================================
def extract_array_from_key(raw_text: str, key: str):
    try:
        match = re.search(rf'"{key}"\s*:\s*\[(.*?)\]', raw_text, re.DOTALL)
        if not match:
            return None
        arr = "[" + match.group(1) + "]"
        return json.loads(arr)
    except:
        return None


# ==================================================
# 🔒 INVOCACIÓN SEGURA
# ==================================================
async def safe_invoke(params):
    for _ in range(5):
        try:
            return assistant.invoke(params)
        except Exception as e:
            err = str(e).lower()

            if "insufficient_quota" in err:
                raise RuntimeError("❌ Créditos agotados.")

            if "rate_limit" in err or "tokens per minute" in err:
                print("⏳ Rate limit. Esperando 3 minutos…")
                await asyncio.sleep(180)
                params.pop("thread_id", None)
                continue

            if "timeout" in err:
                await asyncio.sleep(10)
                continue

            raise

    raise RuntimeError("❌ Falló la llamada después de múltiples intentos.")


# ==================================================
# 🧠 PIPELINE ESG
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

    # ==================================================
    # Helper interno — GUARDA RAW OUTPUT
    # ==================================================
    async def run_prompt(prompt, content, name=None, retries=4, use_thread=True):
        nonlocal thread_id
        last_raw = ""

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

                last_raw = run.content[0].text.value
                run_prompt.last_raw = last_raw

                parsed = try_fix_json(last_raw)

                print(f"✅ {name or prompt.name} completado")
                return parsed

            except Exception as e:
                print(f"⚠️ Error recuperable en {name}: {e}")
                thread_id = None
                await asyncio.sleep(5)

        print(f"⛔ {name or prompt.name} falló TODOS los intentos")
        failed_prompts.append(prompt)
        return None

    # ==================================================
    # PROMPT 1
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
        responses.append(
            {"name": prompt_1.name, "response_content": p1, "thread_id": thread_id}
        )

    # ==================================================
    # PROMPT 2 (con rescate de tabla + extensión con 2.1)
    # ==================================================
    def extract_table(raw_text: str):
        try:
            match = re.search(r'"materiality_table"\s*:\s*\[(.*?)\]', raw_text, re.DOTALL)
            if not match:
                return None
            arr = "[" + match.group(1) + "]"
            return json.loads(arr)
        except:
            return None

    print("\n🔹 Ejecutando Prompt 2 (máx 2 intentos)")

    rows = []
    exhausted = False
    raw_p2 = None

    # 👉 Primeras llamadas a Prompt 2
    for attempt in range(1, 3):
        p2 = await run_prompt(
            prompt_2,
            prompt_2.format(
                organization_name=organization_name,
                country=country,
                website=website,
                industry=industry,
            ),
            name="Prompt 2",
        )

        raw_p2 = run_prompt.last_raw

        if p2 and "materiality_table" in p2:
            rows = p2["materiality_table"]
            exhausted = p2.get("exhausted", False)
        else:
            extracted = extract_table(raw_p2)
            rows = extracted or []
            exhausted = False

        if exhausted:
            print("⚠️ Prompt 2 marcó exhausted → deteniendo reintentos.")
            break

        if len(rows) >= MIN_ROWS_PROMPT_2:
            print(f"✅ Prompt 2 OK con {len(rows)} filas (>= {MIN_ROWS_PROMPT_2}).")
            break

        print(
            f"⚠️ Prompt 2 devolvió solo {len(rows)} filas (< {MIN_ROWS_PROMPT_2}) → reintentando…"
        )
        await asyncio.sleep(8)

    # 👉 Si después de Prompt 2 aún no llegamos al mínimo y NO está exhausted,
    # usamos Prompt 2.1 para completar hasta MIN_ROWS_PROMPT_2 (o más).
    if len(rows) < MIN_ROWS_PROMPT_2 and not exhausted:
        print(
            f"⚠ Prompt 2 terminó con {len(rows)} filas (< {MIN_ROWS_PROMPT_2}) → ejecutando Prompt 2.1 para extender la tabla…"
        )

        p21 = await run_prompt(
            prompt_2_1,
            prompt_2_1.format(prev_rows=json.dumps(rows, ensure_ascii=False)),
            name="Prompt 2.1",
            retries=3,
        )

        if p21 and "materiality_table" in p21:
            extra_rows = p21["materiality_table"]
            print(f"✅ Prompt 2.1 devolvió {len(extra_rows)} filas adicionales.")
            rows.extend(extra_rows)
        else:
            print("⛔ Prompt 2.1 no pudo devolver filas adicionales.")

    # Log final de filas de Prompt 2 (+ 2.1)
    if len(rows) < MIN_ROWS_PROMPT_2:
        print(
            f"⚠️ Aún después de Prompt 2.1 hay solo {len(rows)} filas (< {MIN_ROWS_PROMPT_2})."
        )
    else:
        print(
            f"✅ Tabla final de Prompt 2 tiene {len(rows)} filas (antes de recortar a MAX_ROWS_PROMPT_2={MAX_ROWS_PROMPT_2})."
        )

    # Recortar al máximo permitido
    rows = rows[:MAX_ROWS_PROMPT_2]

    responses.append(
        {
            "name": prompt_2.name,
            "response_content": {
                "materiality_table": rows,
                "exhausted": exhausted,
            },
            "thread_id": thread_id,
        }
    )

    # ==================================================
    # PROMPTS 3 → 11 (con rescate especial 7 y 10)
    # ==================================================
    for i, p in enumerate(
        [prompt_3, prompt_4, prompt_5, prompt_6, prompt_7, prompt_8, prompt_9, prompt_10, prompt_11],
        1,
    ):
        parsed = await run_prompt(
            p,
            p.template,
            name=p.name,
            retries=3,
        )

        raw = getattr(run_prompt, "last_raw", "")

        # 🔍 si falla y es prompt 7 o 10 → intentar rescatar arrays
        if not parsed and (p is prompt_7 or p is prompt_10):
            print(f"\n⚠️ JSON inválido en {p.name}, RAW:")
            print(raw[:2000])

            if p is prompt_7:
                arr = extract_array_from_key(raw, "gri_mapping")
                if arr:
                    parsed = {"gri_mapping": arr}

            if p is prompt_10:
                arr = extract_array_from_key(raw, "regulaciones")
                if arr:
                    parsed = {"regulaciones": arr}

        if parsed:
            responses.append(
                {"name": p.name, "response_content": parsed, "thread_id": thread_id}
            )
        else:
            failed_prompts.append(p)

        if i % 2 == 0:
            await asyncio.sleep(random.randint(20, 40))

    # ==================================================
    # RESULTADO FINAL
    # ==================================================
    status = "complete" if not failed_prompts else "incomplete"

    return {
        "status": status,
        "responses": responses,
        "failed_prompts": [p.name for p in failed_prompts],
    }
