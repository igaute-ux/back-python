import os
import asyncio
from app.services.langchain.prompts import *
from app.utils.json_formatter import clean_and_parse_json
from app.core.config import settings
from langchain_community.agents.openai_assistant import OpenAIAssistantV2Runnable
import re 
import json 

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

assistant = OpenAIAssistantV2Runnable(
    assistant_id='asst_uN6jjvZ9s4Yv2PFmV1J4iRJB',
    tools=[{"type": "code_interpreter", "file_ids": ["file-4utrNkHFDne6Egt6VZYrJK","file-NsDHe3whUTGZcEUt6k9Z5y","file-7YCPdsm2cPpGy6XLGtqbXe","file-4v5rfFJJowrhB1iTAziqRv","file-8JBPLJoGWWNTo6PAJfr22J","file-N4f3A6PBVuv8VZnGRYWaje"]}],
)

MIN_LENGTHS = {
    "nombre_empresa": 24,
    "pais_operacion": 40,
    "industria": 60,
    "tamano_empresa": 40,
    "ubicacion_geografica": 100,
    "modelo_negocio": 150,
    "cadena_valor": 200,
    "actividades_principales": 200,
    "madurez_esg": 100,
    "stakeholders_relevantes": 200,
}

MAX_RETRIES_PROMPT_2 = 10
MIN_ROWS_PROMPT_2 = 14

def validate_min_lengths(data: dict):
    errors = []
    for key, min_len in MIN_LENGTHS.items():
        if len(data.get(key, "")) < min_len:
            errors.append(f"{key} (len {len(data.get(key,''))} < {min_len})")
    return errors


    
def try_fix_json(raw_text: str):
    """
    Intenta reparar y parsear JSON con errores comunes generados por el modelo.
    """
    import re, json

    raw_text = raw_text.strip()

    # Si hay texto antes/después del JSON
    json_candidate = re.search(r'\{.*\}', raw_text, re.DOTALL)
    if json_candidate:
        raw_text = json_candidate.group(0)

    # Eliminar comas antes de cierre } o ]
    fixed = re.sub(r',(\s*[}\]])', r'\1', raw_text)

    # Corregir comillas mal balanceadas
    fixed = fixed.replace('“', '"').replace('”', '"').replace("’", "'")

    # Intentar parsear
    try:
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        print(f"⚠️ Error de parseo persistente: {e}")
        # Intentar cerrar el JSON si está incompleto
        if not fixed.strip().endswith('}'):
            fixed += '}'
        try:
            return json.loads(fixed)
        except Exception as e2:
            print(f"❌ No se pudo corregir JSON: {e2}")
            print("📄 Fragmento problemático:\n", fixed[-200:])
            raise



async def run_esg_analysis(organization_name: str, country: str, website: str) -> str:
    """
    Ejecuta el análisis ESG completo solo una vez.
    ✅ Prompt 2 mantiene reintentos internos para alcanzar las filas mínimas.
    ❌ No hay reintentos globales.
    """
    responses = []
    thread_id = None

    # ============================
    # 🧭 1. Prompt 1
    # ============================
    print(f"\n🔹 Ejecutando Prompt 1")
    call_params = {
        "content": prompt_1.format(
            organization_name=organization_name,
            country=country,
            website=website
        )
    }

    response = assistant.invoke(call_params)
    raw_output = response[0].content[0].text.value.strip()
    parsed_json = clean_and_parse_json(raw_output)
    errors = validate_min_lengths(parsed_json)
    if errors:
        raise ValueError(f"❌ Prompt 1 no cumplió: {errors}")

    print(f"✅ Prompt 1 completado")
    thread_id = response[0].thread_id
    responses.append({
        "name": prompt_1.name,
        "response_content": parsed_json,
        "thread_id": thread_id
    })

    # ============================
    # 🧭 2. Prompt 2 (con reintentos internos)
    # ============================
    print(f"\n🔹 Ejecutando Prompt 2 con validación de filas mínimas (>= {MIN_ROWS_PROMPT_2})...")
    for attempt in range(1, MAX_RETRIES_PROMPT_2 + 1):
        print(f"🧪 Prompt 2 - intento {attempt}/{MAX_RETRIES_PROMPT_2}")
        call_params = {"content": prompt_2.template}
        if thread_id:
            call_params["thread_id"] = thread_id

        response = assistant.invoke(call_params)
        raw_output = response[0].content[0].text.value.strip()

        try:
            parsed_json = clean_and_parse_json(raw_output)
        except Exception as e:
            print(f"❌ Error parseando JSON Prompt 2: {e}")
            if attempt == MAX_RETRIES_PROMPT_2:
                raise
            continue

        rows_count = len(parsed_json.get("materiality_table", []))
        if rows_count >= MIN_ROWS_PROMPT_2:
            print(f"✅ Prompt 2 pasó validación ({rows_count} filas)")
            thread_id = response[0].thread_id
            responses.append({
                "name": prompt_2.name,
                "response_content": parsed_json,
                "thread_id": thread_id
            })
            break
        else:
            print(f"⚠️ Prompt 2 devolvió solo {rows_count} filas")
            if attempt < MAX_RETRIES_PROMPT_2:
                feedback = (
                    f"La respuesta anterior devolvió solo {rows_count} filas. "
                    f"Necesito al menos {MIN_ROWS_PROMPT_2} filas."
                )
                retry_prompt = prompt_2.template + "\n\n" + feedback
                call_params["content"] = retry_prompt
                continue
            else:
                raise ValueError(
                    f"❌ Prompt 2 no alcanzó el mínimo de {MIN_ROWS_PROMPT_2} filas tras {MAX_RETRIES_PROMPT_2} intentos."
                )

    # ============================
    # 🧭 3. Resto de los prompts
    # ============================
    remaining_prompts = [
        prompt_3, prompt_4, prompt_5, prompt_6,
        prompt_7, prompt_8, prompt_9, prompt_10, prompt_11
    ]

    print(f"🚀 Ejecutando prompts restantes...")
    for i, prompt in enumerate(remaining_prompts, 1):
        print(f"🧪 Ejecutando {prompt.name}")
        call_params = {"content": prompt.template}
        if thread_id:
            call_params["thread_id"] = thread_id

        response = assistant.invoke(call_params)

        if not hasattr(response[0].content[0], "text"):
            raise ValueError(f"Tipo inesperado en content: {type(response[0].content[0])}")

        raw_output = response[0].content[0].text.value.strip()
        response_content = try_fix_json(raw_output)


        thread_id = response[0].thread_id
        responses.append({
            "name": prompt.name,
            "response_content": response_content,
            "thread_id": thread_id
        })

        print(f"✅ {prompt.name} completado exitosamente")

        # ⏳ delay opcional
        if i % 2 == 0 and i < len(remaining_prompts):
            delay = 30
            print(f"⏳ Esperando {delay} segundos antes del siguiente prompt...")
            await asyncio.sleep(delay)

    print(f"\n🎉 Análisis ESG completado exitosamente")
    print(f"📈 Total de respuestas generadas: {len(responses)}")
    return responses
