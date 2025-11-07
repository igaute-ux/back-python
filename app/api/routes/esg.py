from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response, JSONResponse
from app.schemas.analysis_request import AnalysisRequest
from app.services.langchain.workflows import run_esg_analysis
from app.services.pdf_generation.pdf import PDFGenerator
from app.db.session import get_db
from sqlalchemy.orm import Session
import base64
import os

router = APIRouter()


# ==========================================================
# 🚀 Análisis ESG completo (sin PDF)
# ==========================================================
@router.post("/esg-analysis")
async def esg_analysis(data: AnalysisRequest):
    print(data)
    result = await run_esg_analysis(
        organization_name=data.organization_name,
        country=data.country,
        website=data.website
    )
    return result

# ==========================================================
# 🧾 Análisis ESG completo con PDF (JSON + base64 + link)
# ==========================================================
@router.post("/esg-analysis-with-pdf-api")
async def run_esg_analysis(organization_name: str, country: str, website: str) -> str:
    """
    Ejecuta el análisis ESG completo con tolerancia total a fallos.
    ✅ Si un prompt falla, se salta y continúa.
    🔁 Al final reintenta SOLO los fallidos hasta que todos pasen correctamente.
    """
    responses = []
    failed_prompts = []
    thread_id = None
    MAX_GLOBAL_RETRIES = 10

    # ============================
    # 🧭 Prompt 1
    # ============================
    print(f"\n🔹 Ejecutando Prompt 1")
    try:
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
    except Exception as e:
        print(f"❌ Error en Prompt 1: {e}")
        failed_prompts.append(prompt_1)

    # ============================
    # 🧭 Prompt 2 (validación interna)
    # ============================
    print(f"\n🔹 Ejecutando Prompt 2 con validación de filas mínimas (>= {MIN_ROWS_PROMPT_2})...")
    try:
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
                    continue
                else:
                    raise ValueError("❌ Prompt 2 no alcanzó el mínimo de filas.")
    except Exception as e:
        print(f"❌ Error en Prompt 2: {e}")
        failed_prompts.append(prompt_2)

    # ============================
    # 🧭 Prompts restantes
    # ============================
    remaining_prompts = [
        prompt_3, prompt_4, prompt_5, prompt_6,
        prompt_7, prompt_8, prompt_9, prompt_10, prompt_11
    ]

    print(f"\n🚀 Ejecutando prompts restantes...")
    for i, prompt in enumerate(remaining_prompts, 1):
        try:
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

            if i % 2 == 0 and i < len(remaining_prompts):
                delay = 30
                print(f"⏳ Esperando {delay} segundos antes del siguiente prompt...")
                await asyncio.sleep(delay)

        except Exception as e:
            print(f"❌ Error en {prompt.name}: {e}")
            failed_prompts.append(prompt)

    # ============================
    # 🔁 Reintentar SOLO fallidos
    # ============================
    retries = 0
    while failed_prompts and retries < MAX_GLOBAL_RETRIES:
        retries += 1
        print(f"\n🔁 Reintento global #{retries} - quedan {len(failed_prompts)} prompts fallidos.")
        still_failed = []

        for prompt in failed_prompts:
            try:
                print(f"🔄 Reintentando {prompt.name}")
                call_params = {"content": prompt.template}
                if thread_id:
                    call_params["thread_id"] = thread_id

                response = assistant.invoke(call_params)
                raw_output = response[0].content[0].text.value.strip()
                response_content = try_fix_json(raw_output)

                thread_id = response[0].thread_id
                responses.append({
                    "name": prompt.name,
                    "response_content": response_content,
                    "thread_id": thread_id
                })
                print(f"✅ {prompt.name} reintentado con éxito")

            except Exception as e:
                print(f"⚠️ {prompt.name} volvió a fallar: {e}")
                still_failed.append(prompt)

        failed_prompts = still_failed

        if failed_prompts:
            print(f"⏳ Esperando 60 segundos antes del siguiente reintento...")
            await asyncio.sleep(60)

    # ============================
    # 🏁 Resultado final
    # ============================
    if failed_prompts:
        print(f"\n⚠️ Algunos prompts aún fallaron tras {MAX_GLOBAL_RETRIES} reintentos:")
        for p in failed_prompts:
            print(f"  - {p.name}")
    else:
        print("\n🎯 Todos los prompts completados exitosamente 🎉")

    print(f"📈 Total de respuestas: {len(responses)}")
    return responses
