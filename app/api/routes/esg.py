from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response, JSONResponse
from app.schemas.analysis_request import AnalysisRequest
from app.services.langchain.workflows import run_esg_analysis, run_prompts_1_to_11
from app.services.pdf_generation.pdf import PDFGenerator
from app.db.session import get_db
from sqlalchemy.orm import Session
import base64
import os
import json 

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
        website=data.website,
        industry=data.industry,
        document=data.document or ""
        )

    return result

# ==========================================================
# 🧾 Análisis ESG completo con PDF (JSON + base64 + link)
# ==========================================================

@router.post("/esg-analysis-with-pdf-api")
async def esg_analysis_with_pdf_api(data: AnalysisRequest, db: Session = Depends(get_db)):
    """
    Igual que /esg-analysis-test, pero para el flujo completo.
    Devuelve JSON + PDF base64 para integrarse con NestJS.
    """
    try:
        print(f"🚀 Iniciando análisis ESG para {data.organization_name}")

        # 1️⃣ Ejecutar (por ahora) solo Prompt 1 — igual que el test
        #    ⚙️ Más adelante podés volver a run_esg_analysis(...)
        pipeline_data = await run_esg_analysis(
            organization_name=data.organization_name,
            country=data.country,
            website=data.website,
            industry=data.industry,
            document=data.document or ""
        )

        # 2️⃣ Generar PDF en memoria
        print("📄 Generando PDF del reporte...")
        generator = PDFGenerator()
        pdf_bytes = generator.generate_esg_report(pipeline_data=pipeline_data, output_path=None)

        # 3️⃣ Codificar PDF
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        # 4️⃣ Preparar nombre
        safe_name = "".join(c for c in data.organization_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_').lower()
        filename = f"esg_report_{safe_name}.pdf"

        print(f"✅ PDF generado exitosamente ({len(pdf_bytes)} bytes)")

        # 5️⃣ Devolver igual que el test
        return JSONResponse(
            content={
                "filename": filename,
                "pdf_base64": pdf_base64,
                "analysis_json": pipeline_data
            }
        )

    except Exception as e:
        print(f"❌ Error en análisis ESG con PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generando análisis ESG: {str(e)}")



@router.post("/esg-prompt-2")
async def run_prompts_1_to_5_endpoint(data: AnalysisRequest, db: Session = Depends(get_db)):
    """
    Ejecuta exclusivamente los Prompt 1 al 5 del análisis ESG.
    """
    try:
        print(f"🚀 Ejecutando Prompts 1 al 5 para {data.organization_name}", flush=True)

        # 👇 Esto ahora llama al verdadero `run_prompts_1_to_5` del módulo workflows
        responses = await run_prompts_1_to_11(
            organization_name=data.organization_name,
            country=data.country,
            website=data.website,
            industry=data.industry,
            document=data.document or ""
        )

        if not responses or not isinstance(responses, list):
            raise ValueError("⚠️ No se recibieron respuestas válidas del modelo")

        # Buscar los prompts 1 a 5
        prompt1_response = next((r for r in responses if r["name"].startswith("🔹 Prompt 1")), None)
        prompt2_response = next((r for r in responses if r["name"].startswith("🔹 Prompt 2")), None)
        prompt3_response = next((r for r in responses if r["name"].startswith("🔹 Prompt 3")), None)
        prompt4_response = next((r for r in responses if r["name"].startswith("🔹 Prompt 4")), None)
        prompt5_response = next((r for r in responses if r["name"].startswith("🔹 Prompt 5")), None)

        print(f"✅ Prompts 1–5 completados exitosamente para {data.organization_name}", flush=True)

        return JSONResponse(
            content={
                "organization_name": data.organization_name,
                "country": data.country,
                "website": data.website,
                "prompt_1": prompt1_response["response_content"] if prompt1_response else None,
                "prompt_2": prompt2_response["response_content"] if prompt2_response else None,
                "prompt_3": prompt3_response["response_content"] if prompt3_response else None,
                "prompt_4": prompt4_response["response_content"] if prompt4_response else None,
                "prompt_5": prompt5_response["response_content"] if prompt5_response else None,
            }
        )

    except Exception as e:
        print(f"❌ Error ejecutando Prompts 1–5: {str(e)}", flush=True)
        raise HTTPException(status_code=500, detail=f"Error ejecutando Prompts 1–5: {str(e)}")
