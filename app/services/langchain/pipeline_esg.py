import os
import asyncio
import random
import base64
from typing import Optional, List, Dict, Any

from app.services.langchain.prompts import (
    prompt_1, prompt_2, prompt_2_1,
    prompt_3, prompt_4, prompt_5,
    prompt_6, prompt_7, prompt_8,
    prompt_9, prompt_10, prompt_11,
)
from app.utils.json_formatter import clean_and_parse_json, try_fix_json
from app.core.config import settings
from langchain_community.agents.openai_assistant import OpenAIAssistantV2Runnable
from app.services.langchain.workflows import validate_min_lengths
from app.services.pdf_generator import PDFGenerator

# ======================================================
# ⚙️ Configurar el asistente una sola vez
# ======================================================
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

assistant = OpenAIAssistantV2Runnable(
    assistant_id='asst_uN6jjvZ9s4Yv2PFmV1J4iRJB',
    tools=[
        {
            "type": "code_interpreter",
            "file_ids": [
                "file-LzzGj4YJdW1T4bsNp9EcCD",
                "file-96uwnReXqbEbh97miBRJd5",
                "file-6UCacZ7WF2eGxcuZuqPnuD",
                "file-4dixqFDgMjDU39mAEewmRw",
                "file-Sy8QSZkhRsZdkG7oMU3xNZ",
                "file-WucnFWVfve87jhWqW9DH4",
            ]
        }
    ],
)

# ======================================================
# 🧱 1️⃣ Funciones por Prompt (sin reintentos globales)
# ======================================================

async def run_prompt_1(data, thread_id=None):
    print("🧭 Ejecutando Prompt 1")
    try:
        response = await assistant.ainvoke({
            "content": prompt_1.format(
                organization_name=data["organization_name"],
                country=data["country"],
                website=data["website"],
                industry=data["industry"],
                document=data.get("document", "")
            )
        })
        raw_output = response.output[0].content[0].text.value.strip()
        parsed = clean_and_parse_json(raw_output)
        errors = validate_min_lengths(parsed)
        if errors:
            raise ValueError(f"Prompt 1 no cumplió: {errors}")

        print("✅ Prompt 1 completado")
        return {
            "name": prompt_1.name,
            "response_content": parsed,
            "thread_id": response.thread_id
        }
    except Exception as e:
        print(f"❌ Error en Prompt 1: {e}")
        return {"name": prompt_1.name, "error": str(e)}


async def run_prompt_2(data, thread_id=None):
    print("🧭 Ejecutando Prompt 2 (con 2.1 si hace falta)")
    try:
        response = await assistant.ainvoke({
            "content": prompt_2.format(
                organization_name=data["organization_name"],
                country=data["country"],
                website=data["website"],
                industry=data["industry"]
            ),
            **({"thread_id": thread_id} if thread_id else {})
        })

        raw_output = response.output[0].content[0].text.value.strip()
        parsed = clean_and_parse_json(raw_output)

        rows = parsed.get("materiality_table", [])
        exhausted = parsed.get("exhausted", False)
        print(f"📊 Prompt 2 devolvió {len(rows)} filas")

        # 🔁 Sub-retry interno
        if len(rows) < 15 and not exhausted:
            print("⚠️ Ejecutando Prompt 2.1 para completar filas")
            response_2 = await assistant.ainvoke({
                "content": prompt_2_1.format(
                    organization_name=data["organization_name"],
                    country=data["country"],
                    website=data["website"],
                    industry=data["industry"]
                ),
                **({"thread_id": thread_id} if thread_id else {})
            })
            raw_output_2 = response_2.output[0].content[0].text.value.strip()
            parsed_2 = clean_and_parse_json(raw_output_2)

            temas_existentes = {r["tema"] for r in rows if "tema" in r}
            nuevos = [r for r in parsed_2.get("materiality_table", [])
                      if "tema" in r and r["tema"] not in temas_existentes]
            parsed["materiality_table"] = rows + nuevos

        return {
            "name": prompt_2.name,
            "response_content": parsed,
            "thread_id": response.thread_id
        }
    except Exception as e:
        print(f"❌ Error en Prompt 2: {e}")
        return {"name": prompt_2.name, "error": str(e)}


async def run_prompt_generic(prompt, data, thread_id=None):
    print(f"🧭 Ejecutando {prompt.name}")
    try:
        response = await assistant.ainvoke({
            "content": prompt.template,
            **({"thread_id": thread_id} if thread_id else {})
        })
        raw_output = response.output[0].content[0].text.value.strip()
        parsed = try_fix_json(raw_output)
        return {
            "name": prompt.name,
            "response_content": parsed,
            "thread_id": response.thread_id
        }
    except Exception as e:
        print(f"❌ Error en {prompt.name}: {e}")
        return {"name": prompt.name, "error": str(e)}


# ======================================================
# 🧩 2️⃣ Diccionario de funciones
# ======================================================

PROMPT_FUNCTIONS = {
    "prompt_1": run_prompt_1,
    "prompt_2": run_prompt_2,
    "prompt_3": lambda data, t=None: run_prompt_generic(prompt_3, data, t),
    "prompt_4": lambda data, t=None: run_prompt_generic(prompt_4, data, t),
    "prompt_5": lambda data, t=None: run_prompt_generic(prompt_5, data, t),
    "prompt_6": lambda data, t=None: run_prompt_generic(prompt_6, data, t),
    "prompt_7": lambda data, t=None: run_prompt_generic(prompt_7, data, t),
    "prompt_8": lambda data, t=None: run_prompt_generic(prompt_8, data, t),
    "prompt_9": lambda data, t=None: run_prompt_generic(prompt_9, data, t),
    "prompt_10": lambda data, t=None: run_prompt_generic(prompt_10, data, t),
    "prompt_11": lambda data, t=None: run_prompt_generic(prompt_11, data, t),
}


# ======================================================
# 🧠 3️⃣ Función principal incremental
# ======================================================

async def run_esg_analysis_incremental(data: dict) -> dict:
    """
    Ejecuta solo los prompts faltantes o fallidos.
    data: {
      organization_name, country, website, industry, document?,
      previous_responses?: list
    }
    """
    previous_responses = data.get("previous_responses", [])
    completed = {r["name"] for r in previous_responses if "response_content" in r and not r.get("error")}
    failed = data.get("failed_prompts", [])
    thread_id = None

    if previous_responses:
        thread_id = previous_responses[-1].get("thread_id")

    print(f"🚀 Iniciando análisis incremental. Completados: {len(completed)} | Fallidos previos: {failed}")

    results = list(previous_responses)
    failed_prompts = []

    for name, func in PROMPT_FUNCTIONS.items():
        if name in completed:
            print(f"⏩ Saltando {name} (ya completado)")
            continue

        print(f"▶️ Ejecutando {name}")
        result = await func(data, thread_id)
        results.append(result)

        # actualizar thread_id si existe
        thread_id = result.get("thread_id", thread_id)

        if "error" in result:
            failed_prompts.append(name)

        await asyncio.sleep(random.randint(5, 10))

    status = "complete" if not failed_prompts else "incomplete"

    return {
        "status": status,
        "responses": results,
        "failed_prompts": failed_prompts
    }
