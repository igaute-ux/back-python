import os
import pandas as pd
import re
import asyncio
from io import StringIO
from app.services.langchain.prompts import *
from app.utils.json_formatter import clean_and_parse_json
from app.core.config import settings
from langchain_community.agents.openai_assistant import OpenAIAssistantV2Runnable

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

assistant = OpenAIAssistantV2Runnable(
    assistant_id='asst_uN6jjvZ9s4Yv2PFmV1J4iRJB',
    tools=[{"type": "code_interpreter", "file_ids": ["file-4utrNkHFDne6Egt6VZYrJK","file-NsDHe3whUTGZcEUt6k9Z5y","file-7YCPdsm2cPpGy6XLGtqbXe","file-4v5rfFJJowrhB1iTAziqRv","file-8JBPLJoGWWNTo6PAJfr22J","file-N4f3A6PBVuv8VZnGRYWaje"]}],
)

def markdown_to_df(response_text: str) -> pd.DataFrame:
    match = re.search(r"(\|.+\|)", response_text, re.DOTALL)
    if not match:
        return pd.DataFrame()
    
    table_text = match.group(0)
    table_io = StringIO(table_text)
    df = pd.read_csv(table_io, sep="|", engine="python").dropna(axis=1, how="all")
    
    df.columns = [c.strip() for c in df.columns]
    df = df.applymap(lambda x: str(x).strip() if pd.notnull(x) else x)
    
    return df


async def run_assistant_test(organization_name: str, country: str, website: str) -> str:
    pipeline_responses = []

    context_response = assistant.invoke({
        "content": prompt_1.format(organization_name=organization_name, country=country, website=website)
    })

    context_response_content = context_response[0].content[0].text.value
    context_response_content = clean_and_parse_json(context_response_content)
    thread_id = context_response[0].thread_id
    pipeline_responses.append({"context_response_content": context_response_content, "thread_id": thread_id})
    
    impact_response = assistant.invoke({
        "content": prompt_2.template,
        "thread_id": thread_id
    })

    impact_response_content = impact_response[0].content[0].text.value
    impact_response_content = clean_and_parse_json(impact_response_content)
    thread_id = impact_response[0].thread_id
    pipeline_responses.append({"impact_response_content": impact_response_content, "thread_id": thread_id})

    impact_response_1 = assistant.invoke({
        "content": prompt_2_1.template,
        "thread_id": thread_id
    })
    impact_response_1_content = impact_response_1[0].content[0].text.value
    impact_response_1_content = clean_and_parse_json(impact_response_1_content)
    thread_id = impact_response_1[0].thread_id
    pipeline_responses.append({"impact_response_1_content": impact_response_1_content, "thread_id": thread_id})

    # materiality_response = assistant.invoke({
    #     "content": prompt_3.template,
    #     "thread_id": thread_id
    # })

    # materiality_response_content = materiality_response[0].content[0].text.value
    # thread_id = materiality_response[0].thread_id
    # pipeline_responses.append({"materiality_response_content": materiality_response_content, "thread_id": thread_id})

    return {"response_content": pipeline_responses}

async def run_esg_analysis(organization_name: str, country: str, website: str) -> str:
    """
    Ejecuta el análisis ESG completo con delays simples cada dos prompts.
    """
    responses = []
    thread_id = None
    
    # Lista de prompts con sus configuraciones
    prompts_config = [
        {
            "prompt": prompt_1,
            "content": prompt_1.format(organization_name=organization_name, country=country, website=website),
        },
        {
            "prompt": prompt_2,
            "content": prompt_2.template,
        },
        {
            "prompt": prompt_3,
            "content": prompt_3.template,
        },
        {
            "prompt": prompt_4,
            "content": prompt_4.template,
        },
        {
            "prompt": prompt_5,
            "content": prompt_5.template,
        },
        {
            "prompt": prompt_6,
            "content": prompt_6.template,
        },
        {
            "prompt": prompt_7,
            "content": prompt_7.template,
        },
        {
            "prompt": prompt_8,
            "content": prompt_8.template,
        },
        {
            "prompt": prompt_9,
            "content": prompt_9.template,
        },
        {
            "prompt": prompt_10,
            "content": prompt_10.template,
        },
        {
            "prompt": prompt_11,
            "content": prompt_11.template,
        }
    ]
    
    print(f"🚀 Iniciando análisis ESG para {organization_name}")
    print(f"📊 Total de prompts a ejecutar: {len(prompts_config)}")
    
    for i, config in enumerate(prompts_config, 1):
        prompt = config["prompt"]
        content = config["content"]
        
        print(f"\n🔄 Ejecutando {prompt.name} ({i}/{len(prompts_config)})")
        
        try:
            # Ejecutar prompt
            call_params = {"content": content}
            if thread_id:
                call_params["thread_id"] = thread_id
            
            response = assistant.invoke(call_params)
            
            # Extraer información de la respuesta
            response_content = clean_and_parse_json(response[0].content[0].text.value)
            thread_id = response[0].thread_id
            
            # Preparar respuesta base
            response_data = {
                "name": prompt.name,
                "response_content": response_content,
                "thread_id": thread_id
            }
            
            responses.append(response_data)
            print(f"✅ {prompt.name} completado exitosamente")
            
            # Delay simple cada dos prompts (después del prompt 2, 4, 6, 8, 10)
            if i % 2 == 0 and i < len(prompts_config):
                delay = 30  # 30 segundos de delay
                print(f"⏳ Esperando {delay} segundos antes del siguiente prompt...")
                await asyncio.sleep(delay)
                
        except Exception as e:
            print(f"❌ Error ejecutando {prompt.name}: {str(e)}")
            print(f"🛑 Pipeline interrumpido en el prompt {i}/{len(prompts_config)}")
            raise e
    
    print(f"\n🎉 Análisis ESG completado exitosamente para {organization_name}")
    print(f"📈 Total de respuestas generadas: {len(responses)}")
    
    return responses

