import os
import asyncio
import time
from app.services.langchain.prompts import *
from app.utils.json_formatter import clean_and_parse_json
from app.core.config import settings
from langchain_community.agents.openai_assistant import OpenAIAssistantV2Runnable
import re 
import json 
from typing import Optional
import random

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

assistant = OpenAIAssistantV2Runnable(
    assistant_id='asst_uN6jjvZ9s4Yv2PFmV1J4iRJB',
    tools=[{"type": "code_interpreter", "file_ids": ["file-LzzGj4YJdW1T4bsNp9EcCD","file-96uwnReXqbEbh97miBRJd5","file-6UCacZ7WF2eGxcuZuqPnuD","file-4dixqFDgMjDU39mAEewmRw","file-Sy8QSZkhRsZdkG7oMU3xNZ","file-WucnFWVfve87jhWqjW9DH4"]}],
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
MIN_ROWS_PROMPT_2 = 15
MAX_ROWS_PROMPT_2 = 30




def validate_min_lengths(data: dict):
    errors = []
    for key, min_len in MIN_LENGTHS.items():
        if len(data.get(key, "")) < min_len:
            errors.append(f"{key} (len {len(data.get(key,''))} < {min_len})")
    return errors


def try_fix_json(raw_text: str):
    import re, json
    raw_text = raw_text.strip()

    # 🧩 Extrae solo el bloque JSON si hay texto adicional
    json_candidate = re.search(r'\{.*\}', raw_text, re.DOTALL)
    if json_candidate:
        raw_text = json_candidate.group(0)

    # ✨ Limpiezas básicas
    fixed = raw_text
    fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)  # quita coma final
    fixed = fixed.replace('“', '"').replace('”', '"').replace("’", "'")
    fixed = fixed.replace('\n', ' ').replace('\t', ' ')

    # 💡 Arreglar números con coma decimal (12,5 → 12.5)
    fixed = re.sub(r'(\d+),(\d+)', r'\1.\2', fixed)

    # 🚑 Escapa comillas internas dentro de strings
    # Ejemplo: "descripcion": "Resolución ... el "costo de cumplimiento" ..."
    # se convierte en "descripcion": "Resolución ... el \"costo de cumplimiento\" ..."
    def escape_inner_quotes(match):
        inner = match.group(1)
        inner = re.sub(r'(?<!\\)"', r'\\"', inner)
        return f'"{inner}"'

    fixed = re.sub(r'"([^"]*?)"', escape_inner_quotes, fixed)

    try:
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        print(f"⚠️ Error de parseo persistente: {e}")
        snippet = fixed[max(0, e.pos - 200): e.pos + 200]
        print("📄 Fragmento problemático:\n", snippet)
        # 🔁 Último intento: reemplazar comillas internas rotas por comillas simples
        fallback = re.sub(r'(?<=: )"([^"]*?)"(?=[^:,]*:)', lambda m: m.group(0).replace('"', "'"), fixed)
        try:
            return json.loads(fallback)
        except:
            raise



# ===============================
# ⚙️ Helper: llamada segura con backoff
# ===============================
async def safe_invoke(call_params, retries=5, base_wait=15):
    """
    Envuelve assistant.invoke() con tolerancia a rate limits y desconexiones.
    Hace backoff progresivo y espera larga si se agotan los tokens.
    """
    for attempt in range(1, retries + 1):
        try:
            return assistant.invoke(call_params)
        except Exception as e:
            err = str(e).lower()

            # 🧩 Manejo de rate limit o tokens agotados
            if any(x in err for x in [
                "rate_limit", "quota", "tokens per", "insufficient_quota"
            ]):
                wait_time = base_wait * attempt + random.randint(5, 20)
                print(f"⚠️ Límite de tokens o cuota alcanzada (intento {attempt}/{retries}). "
                      f"Esperando {wait_time}s...", flush=True)
                await asyncio.sleep(wait_time)
                continue

            # 🧩 Errores temporales del modelo o red
            if "timeout" in err or "connection" in err:
                wait_time = base_wait * attempt
                print(f"🌐 Error temporal ({err}), reintentando en {wait_time}s...", flush=True)
                await asyncio.sleep(wait_time)
                continue

            # 🚫 Si no es error recuperable, lanza directo
            raise

    print("🚨 Se agotaron los reintentos individuales de safe_invoke()", flush=True)
    raise RuntimeError("No se pudo completar la llamada a OpenAI tras múltiples intentos.")


# ===============================
# ⚙️ Reintentos globales inteligentes
# ===============================
async def retry_failed_prompts(failed_prompts, thread_id, responses, max_global_retries=5):
    """
    Reintenta prompts fallidos con tiempos de enfriamiento y control global.
    """
    for retry_num in range(1, max_global_retries + 1):
        if not failed_prompts:
            break

        print(f"\n🔁 Reintento global #{retry_num} - {len(failed_prompts)} prompts fallidos", flush=True)

        # Si venís de un corte de tokens: esperá más largo
        global_cooldown = 60 * retry_num
        print(f"⏳ Esperando {global_cooldown}s antes de reintentar globalmente...", flush=True)
        await asyncio.sleep(global_cooldown)

        still_failed = []

        for prompt in failed_prompts:
            try:
                print(f"🔄 Reintentando {prompt.name}", flush=True)
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
                    "thread_id": thread_id
                })
                print(f"✅ {prompt.name} completado tras reintento global", flush=True)

                # Pausa corta entre prompts
                await asyncio.sleep(10 + random.randint(0, 5))

            except Exception as e:
                print(f"⚠️ {prompt.name} volvió a fallar: {e}", flush=True)
                still_failed.append(prompt)

        failed_prompts = still_failed

    # 🔚 Corte seguro si aún quedan fallidos
    if failed_prompts:
        print("\n🚨 Reintentos globales agotados. Abortando proceso.")
        for p in failed_prompts:
            print(f"   ❌ {p.name}", flush=True)
        raise RuntimeError("Se alcanzó el límite de reintentos globales o tokens agotados.")
    else:
        print("\n🎯 Todos los prompts completados exitosamente tras reintentos.")



async def run_esg_analysis(
    organization_name: str,
    country: str,
    website: str,
    industry: str,
    document: Optional[str] = None
) -> str:
    """
    Ejecuta el análisis ESG completo con control estricto:
    - Prompt 2 y Prompt 2.1 se ejecutan una sola vez.
    - Si no se alcanza el mínimo de 15 filas en materiality_table → aborta.
    """
    responses = []
    failed_prompts = []
    thread_id = None

    # ============================
    # 🧭 Prompt 1
    # ============================
    print(f"\n🔹 Ejecutando Prompt 1", flush=True)
    try:
        call_params = {
            "content": prompt_1.format(
                organization_name=organization_name,
                country=country,
                website=website,
                industry=industry,
                document=document or ""
            )
        }
        response = await safe_invoke(call_params)
        raw_output = response[0].content[0].text.value.strip()
        parsed_json = clean_and_parse_json(raw_output)
        errors = validate_min_lengths(parsed_json)
        if errors:
            raise ValueError(f"❌ Prompt 1 no cumplió: {errors}")

        print("✅ Prompt 1 completado", flush=True)
        thread_id = response[0].thread_id
        responses.append({
            "name": prompt_1.name,
            "response_content": parsed_json,
            "thread_id": thread_id
        })
    except Exception as e:
        print(f"❌ Error en Prompt 1: {e}", flush=True)
        failed_prompts.append(prompt_1)

    # ============================
    # 🧭 Prompt 2 con Prompt 2.1 opcional
    # ============================
    print(f"\n🔹 Ejecutando Prompt 2 (Identificación de Impactos)...", flush=True)
    try:
        call_params = {
            "content": prompt_2.format(
                organization_name=organization_name,
                country=country,
                website=website,
                industry=industry
            ),
            **({"thread_id": thread_id} if thread_id else {})
        }

        response = await safe_invoke(call_params)
        raw_output = response[0].content[0].text.value.strip()
        parsed_json = clean_and_parse_json(raw_output)
        rows = parsed_json.get("materiality_table", [])
        exhausted = parsed_json.get("exhausted", False)

        print(f"📊 Prompt 2 devolvió {len(rows)} filas", flush=True)

        # Si tiene menos de 15 filas y no está agotado, ejecutar Prompt 2.1
        if len(rows) < 15 and not exhausted:
            print(f"⚠️ Menos de 15 filas ({len(rows)}) → ejecutando Prompt 2.1 para completar...", flush=True)

            call_params_2 = {
                "content": prompt_2_1.format(
                    organization_name=organization_name,
                    country=country,
                    website=website,
                    industry=industry
                ),
                **({"thread_id": thread_id} if thread_id else {})
            }

            response_2 = await safe_invoke(call_params_2)
            raw_output_2 = response_2[0].content[0].text.value.strip()
            parsed_json_2 = clean_and_parse_json(raw_output_2)
            rows_2 = parsed_json_2.get("materiality_table", [])

            # Combinar sin duplicar por "tema"
            temas_existentes = {r["tema"] for r in rows if "tema" in r}
            nuevos = [r for r in rows_2 if "tema" in r and r["tema"] not in temas_existentes]
            merged_rows = rows + nuevos

            print(f"🧩 Prompt 2.1 añadió {len(nuevos)} filas nuevas → total {len(merged_rows)}", flush=True)

            if len(merged_rows) < 15:
                raise ValueError(f"❌ Ni Prompt 2 ni 2.1 alcanzaron el mínimo de 15 filas (solo {len(merged_rows)}).")

            parsed_json["materiality_table"] = merged_rows[:30]

        elif len(rows) < 15 and exhausted:
            raise ValueError(f"❌ Prompt 2 reportó 'exhausted' con solo {len(rows)} filas. Abortando proceso.")
        else:
            print("✅ Prompt 2 completado con cantidad suficiente de filas.", flush=True)

        # Guardar resultado válido
        responses.append({
            "name": prompt_2.name,
            "response_content": parsed_json,
            "thread_id": thread_id
        })
        thread_id = response[0].thread_id

    except Exception as e:
        print(f"❌ Error en Prompt 2: {e}", flush=True)
        print("⛔ Abortando ejecución de análisis completo por fallo crítico en Prompt 2.", flush=True)
        return {"error": str(e), "failed_prompt": "Prompt 2"}

    # ============================
    # 🧭 Prompts restantes
    # ============================
    remaining_prompts = [
        prompt_3, prompt_4, prompt_5, prompt_6,
        prompt_7, prompt_8, prompt_9, prompt_10, prompt_11
    ]

    print(f"\n🚀 Ejecutando prompts restantes...", flush=True)
    for i, prompt in enumerate(remaining_prompts, 1):
        try:
            print(f"🧪 Ejecutando {prompt.name}", flush=True)
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
                "thread_id": thread_id
            })

            print(f"✅ {prompt.name} completado exitosamente", flush=True)

            # Cooldown suave cada 2 prompts
            if i % 2 == 0 and i < len(remaining_prompts):
                delay = random.randint(25, 40)
                print(f"⏳ Esperando {delay}s para evitar rate limits...", flush=True)
                await asyncio.sleep(delay)

        except Exception as e:
            print(f"❌ Error en {prompt.name}: {e}", flush=True)
            failed_prompts.append(prompt)

    # ============================
    # 🔁 Reintentos globales
    # ============================
    await retry_failed_prompts(failed_prompts, thread_id, responses)

    print(f"\n🎯 Todos los prompts completados exitosamente 🎉", flush=True)
    print(f"📈 Total de respuestas: {len(responses)}", flush=True)
    return responses


# ===============================
# 🚀 Ejecutar Prompts 1 al 11
# ===============================
async def run_prompts_1_to_11(
    organization_name: str,
    country: str,
    website: str,
    industry: str,
    document: Optional[str] = None
) -> str:
    """
    Ejecuta secuencialmente los Prompts 1 al 11 (con validación, reintentos y logs).
    Mantiene el contexto del thread_id entre cada prompt.
    """
    responses = []
    failed_prompts = []
    thread_id = None

    # ===============================
    # 🧭 Prompt 1
    # ===============================
    print(f"\n🔹 Ejecutando Prompt 1", flush=True)
    try:
        call_params = {
            "content": prompt_1.format(
                organization_name=organization_name,
                country=country,
                website=website,
                industry=industry,
                document=document or ""
            )
        }
        response = await safe_invoke(call_params)
        raw_output = response[0].content[0].text.value.strip()
        parsed_json = clean_and_parse_json(raw_output)
        errors = validate_min_lengths(parsed_json)
        if errors:
            raise ValueError(f"❌ Prompt 1 no cumplió: {errors}")

        print(f"✅ Prompt 1 completado", flush=True)
        thread_id = response[0].thread_id
        responses.append({
            "name": prompt_1.name,
            "response_content": parsed_json,
            "thread_id": thread_id
        })
    except Exception as e:
        print(f"❌ Error en Prompt 1: {e}", flush=True)
        failed_prompts.append(prompt_1)

    # ===============================
    # 🧭 Prompt 2
    # ===============================
    print(f"\n🔹 Ejecutando Prompt 2: Identificación de Impactos (basado en S&P)", flush=True)
    MAX_RETRIES_PROMPT_2 = 10
    MIN_ROWS_PROMPT_2 = 15
    MAX_ROWS_PROMPT_2 = 30
    attempt = 0
    while attempt < MAX_RETRIES_PROMPT_2:
        attempt += 1
        try:
            print(f"🧪 Intento {attempt}/{MAX_RETRIES_PROMPT_2}", flush=True)
            call_params = {"content": prompt_2.template}
            if thread_id:
                call_params["thread_id"] = thread_id
            response = await safe_invoke(call_params)
            raw_output = response[0].content[0].text.value.strip()
            try:
                parsed_json = clean_and_parse_json(raw_output)
            except Exception:
                parsed_json = try_fix_json(raw_output)
            materiality_table = parsed_json.get("materiality_table", [])
            if not isinstance(materiality_table, list) or len(materiality_table) == 0:
                raise ValueError("⚠️ No se encontraron registros en materiality_table")
            row_count = len(materiality_table)
            if row_count < MIN_ROWS_PROMPT_2 or row_count > MAX_ROWS_PROMPT_2:
                raise ValueError(f"⚠️ {row_count} filas fuera de rango válido.")
            print(f"✅ Prompt 2 completado exitosamente ({row_count} filas)", flush=True)
            responses.append({
                "name": prompt_2.name,
                "response_content": parsed_json,
                "thread_id": response[0].thread_id,
            })
            thread_id = response[0].thread_id
            break
        except Exception as e:
            print(f"❌ Error en Prompt 2 (intento {attempt}): {e}", flush=True)
            if attempt < MAX_RETRIES_PROMPT_2:
                wait_time = 15 * attempt
                print(f"⏳ Reintentando en {wait_time}s...", flush=True)
                await asyncio.sleep(wait_time)
            else:
                print(f"🚨 Prompt 2 falló tras {MAX_RETRIES_PROMPT_2} intentos.", flush=True)
                failed_prompts.append(prompt_2)
                raise

    # ===============================
    # 🧭 Prompts 3 al 11
    # ===============================
    prompts_rango = [
        (prompt_3, 8, 10, 25),
        (prompt_4, 8, 10, 25),
        (prompt_5, 8, 10, 25),
        (prompt_6, 8, 10, 25),
        (prompt_7, 8, 10, 25),
        (prompt_8, 8, 10, 25),
        (prompt_9, 8, 10, 25),
        (prompt_10, 8, 10, 25),
        (prompt_11, 8, 10, 25),
    ]

    print(f"\n🚀 Ejecutando Prompts 3–11...", flush=True)
    for prompt, MAX_RETRIES, MIN_ROWS, MAX_ROWS in prompts_rango:
        attempt = 0
        while attempt < MAX_RETRIES:
            attempt += 1
            try:
                print(f"\n🔹 Ejecutando {prompt.name} (intento {attempt}/{MAX_RETRIES})", flush=True)
                call_params = {"content": prompt.template}
                if thread_id:
                    call_params["thread_id"] = thread_id
                response = await safe_invoke(call_params)
                raw_output = response[0].content[0].text.value.strip()
                try:
                    parsed_json = clean_and_parse_json(raw_output)
                except Exception:
                    parsed_json = try_fix_json(raw_output)

                table_key = next((k for k in parsed_json.keys() if "table" in k.lower()), None)
                if not table_key:
                    raise ValueError("⚠️ No se encontró ninguna tabla en la respuesta.")
                table_data = parsed_json.get(table_key, [])
                if not isinstance(table_data, list) or len(table_data) == 0:
                    raise ValueError(f"⚠️ {prompt.name} devolvió una tabla vacía")
                row_count = len(table_data)
                if row_count < MIN_ROWS or row_count > MAX_ROWS:
                    raise ValueError(
                        f"⚠️ {prompt.name} devolvió {row_count} filas fuera del rango {MIN_ROWS}-{MAX_ROWS}"
                    )

                print(f"✅ {prompt.name} completado con {row_count} filas", flush=True)
                responses.append({
                    "name": prompt.name,
                    "response_content": parsed_json,
                    "thread_id": response[0].thread_id,
                })
                thread_id = response[0].thread_id
                break
            except Exception as e:
                print(f"❌ Error en {prompt.name} (intento {attempt}): {e}", flush=True)
                if attempt < MAX_RETRIES:
                    wait_time = 15 * attempt
                    print(f"⏳ Reintentando en {wait_time}s...", flush=True)
                    await asyncio.sleep(wait_time)
                else:
                    print(f"🚨 {prompt.name} falló tras {MAX_RETRIES} intentos.", flush=True)
                    failed_prompts.append(prompt)
                    break

    print(f"\n✅ Prompts 1–11 completados.\n", flush=True)
    return responses
