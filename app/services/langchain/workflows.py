import os
import asyncio
import random
import json
import re
import csv
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



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_SASB_PATH = os.path.join(BASE_DIR, "data", "lista_sasb.csv")

def load_sasb_rows_by_industry(industria_sasb: str):
    rows = []
    with open(CSV_SASB_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["INDUSTRIA"].strip() == industria_sasb.strip():
                rows.append({
                    "industria": row["INDUSTRIA"],
                    "tema": row["TEMA"],
                    "parametro_contabilidad": row["PARÁMETRO DE CONTABILIDAD"],
                    "categoria": row["CATEGORÍA"],
                    "unidad_medida": row["UNIDAD DE MEDIDA"],
                    "codigo": row["CÓDIGO"],
                })
    return rows



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

    # ====================================================
    # PROMPT 2 — Code Interpreter
    # ====================================================
    print("\n🧪 Ejecutando Prompt 2...")
    raw, thread_id = await execute(
        "Prompt 2",
        prompt_2.format(
            organization_name=organization_name,
            country=country,
            website=website,
            industry=industry,
        ),
        thread_id,
        use_tool=True
    )

    def extract_table(raw_text: str):
        try:
            match = re.search(r'"materiality_table"\s*:\s*\[(.*?)\]', raw_text, re.DOTALL)
            if not match:
                return None
            arr = "[" + match.group(1) + "]"
            return json.loads(arr)
        except:
            return None

    rows = extract_table(raw or "")
    count = len(rows) if rows else 0

    print(f"📊 Prompt 2 devolvió {count} filas")

    # ─────────────────────────────────────────────
    # SI TRAE MENOS DEL MÍNIMO → UN SOLO REINTENTO
    # ─────────────────────────────────────────────
    if count < MIN_ROWS_PROMPT_2:
        print(f"⚠️ Prompt 2 devolvió menos filas del mínimo ({MIN_ROWS_PROMPT_2}). Reintentando 1 vez más…")

        raw, thread_id = await execute(
            "Prompt 2",
            prompt_2.format(
                organization_name=organization_name,
                country=country,
                website=website,
                industry=industry,
            ),
            thread_id,
            use_tool=True
        )
        

        rows = extract_table(raw or "")
        count = len(rows) if rows else 0

        print(f"📊 Segundo intento de Prompt 2 devolvió {count} filas")

        if count < MIN_ROWS_PROMPT_2:
            print("❌ Prompt 2 falló definitivamente — muy pocas filas.")
            return {"status": "failed", "error": f"Prompt 2 devolvió solo {count} filas"}

    rows = rows[:MAX_ROWS_PROMPT_2]

    responses.append({
        "name": prompt_2.name,
        "response_content": {"materiality_table": rows}
    })

    # ==================================================
    # PROMPTS 3 → 6  (ANTES iban después, ahora están donde corresponde)
    # ==================================================
    for p in [prompt_3, prompt_4, prompt_5, prompt_6]:
        parsed = await run_prompt(
            p,
            p.template,
            name=p.name,
            retries=3,
        )

        if parsed:
            responses.append(
                {"name": p.name, "response_content": parsed, "thread_id": thread_id}
            )
        else:
            failed_prompts.append(p)

    # ==================================================
    # PROMPT 8 (LLM) → mapeo sector S&P → industria SASB
    # ==================================================
    print("\n📌 Ejecutando Prompt 8 (mapeo SASB)…")

    p8_raw = await safe_invoke({
        "content": prompt_8.format(industry=industry)
    })

    try:
        p8_text = p8_raw[0].content[0].text.value
    except Exception:
        raise RuntimeError("❌ No se pudo leer la salida del Prompt 8")

    p8_json = try_fix_json(p8_text)

    if not p8_json or "mapeo_sasb" not in p8_json:
        raise RuntimeError(f"❌ Prompt 8 devolvió JSON inválido:\n{p8_text}")

    industria_sasb = p8_json["mapeo_sasb"][0]["industria_sasb"]
    print(f"✅ Industria SASB detectada por Prompt 8: {industria_sasb}")

    responses.append({
        "name": prompt_8.name,
        "response_content": p8_json
    })

    # ==================================================
    # PROMPT 9 (CSV local)
    # ==================================================
    print("\n📌 Ejecutando Prompt 9 local (desde CSV)…")

    tabla_sasb = load_sasb_rows_by_industry(industria_sasb)

    print(f"✅ CSV devolvió {len(tabla_sasb)} filas SASB para '{industria_sasb}'")

    if len(tabla_sasb) == 0:
        raise RuntimeError(
            f"❌ No se encontraron filas SASB para '{industria_sasb}'. "
            "Revisá si existe en lista_sasb.csv."
        )

    responses.append({
        "name": "Prompt 9 (CSV)",
        "response_content": {
            "tabla_sasb": tabla_sasb
        }
    })

    # ==================================================
    # PROMPTS 10 → 11
    # ==================================================
    for p in [prompt_10, prompt_11]:

        parsed = await run_prompt(
            p,
            p.template,
            name=p.name,
            retries=3,
        )

        raw = getattr(run_prompt, "last_raw", "")

        # Rescate especial SOLO para Prompt 10
        if not parsed and p is prompt_10:
            print(f"\n⚠️ JSON inválido en {p.name}, RAW:")
            print(raw[:2000])

            arr = extract_array_from_key(raw, "regulaciones")
            if arr:
                parsed = {"regulaciones": arr}

        if parsed:
            responses.append(
                {"name": p.name, "response_content": parsed, "thread_id": thread_id}
            )
        else:
            failed_prompts.append(p)

    # ==================================================
    # RESULTADO FINAL
    # ==================================================
    status = "complete" if not failed_prompts else "incomplete"

    return {
        "status": status,
        "responses": responses,
        "failed_prompts": [p.name for p in failed_prompts],
    }