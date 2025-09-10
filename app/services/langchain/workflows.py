from app.services.langchain.prompts import prompt_1
from app.core.config import settings
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o", 
    temperature=0.2, 
    output_version='responses/v1',
    api_key=settings.OPENAI_API_KEY
)
tool = {"type": "web_search_preview"}
llm_with_tools = llm.bind_tools([tool])


async def run_prompt_1(organization_name: str, country: str, website: str) -> str:
    chain = prompt_1 | llm
    response = chain.invoke({
        "organization_name": organization_name,
        "country": country,
        "website": website,
    })
    return response.content