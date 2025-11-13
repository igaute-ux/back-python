from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response, JSONResponse
from app.schemas.analysis_request import AnalysisRequest
from app.services.langchain.workflows import run_esg_analysis
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
@router.post("/esg-analysis-api")
async def esg_analysis_api(
    data: AnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Ejecuta el flujo completo del análisis ESG.
    Devuelve solo:
    - status: "complete" | "incomplete" | "failed"
    - analysis_json: respuestas de todos los prompts
    - failed_prompts: lista de prompts fallidos
    """
    print(f"🚀 Iniciando análisis ESG para {data.organization_name}")

    pipeline_result = None

    try:
        # ===========================
        # 1️⃣ Ejecutar análisis completo
        # ===========================
        pipeline_result = await run_esg_analysis(
            organization_name=data.organization_name,
            country=data.country,
            website=data.website,
            industry=data.industry,
            document=data.document or ""
        )

        status = pipeline_result.get("status", "failed")
        responses = pipeline_result.get("responses", [])
        failed_prompts = pipeline_result.get("failed_prompts", [])

        # ===========================
        # 2️⃣ Devolver SOLO JSON
        # ===========================
        return JSONResponse(
            status_code=200 if status == "complete" else 207,
            content={
                "status": status,
                "analysis_json": responses,
                "failed_prompts": failed_prompts,
            },
        )

    except Exception as e:
        # ===========================
        # 3️⃣ Error crítico → devolver parcial si existe
        # ===========================
        print(f"❌ Error en análisis ESG: {str(e)}")

        return JSONResponse(
            status_code=500,
            content={
                "status": "failed",
                "error": str(e),
                "partial_results": (
                    pipeline_result.get("responses") if pipeline_result else []
                ),
                "failed_prompts": (
                    pipeline_result.get("failed_prompts") if pipeline_result else []
                ),
            },
        )
