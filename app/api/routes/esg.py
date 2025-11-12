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

@router.post("/esg-analysis-with-pdf-api")
async def esg_analysis_with_pdf_api(
    data: AnalysisRequest, 
    db: Session = Depends(get_db)
):
    """
    Ejecuta el flujo completo del análisis ESG.
    Devuelve:
    - JSON con el estado ("complete" | "incomplete" | "failed")
    - PDF base64 si se pudo generar
    - Errores y prompts fallidos
    """
    print(f"🚀 Iniciando análisis ESG para {data.organization_name}")
    
    pdf_base64 = None
    filename = None
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
        # 2️⃣ Intentar generar PDF (solo si hay respuestas)
        # ===========================
        if responses:
            try:
                print("📄 Generando PDF del reporte...")
                generator = PDFGenerator()
                pdf_bytes = generator.generate_esg_report(
                    pipeline_data=pipeline_result,
                    output_path=None
                )
                pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

                safe_name = "".join(
                    c for c in data.organization_name if c.isalnum() or c in (' ', '-', '_')
                ).rstrip().replace(' ', '_').lower()
                filename = f"esg_report_{safe_name}.pdf"
                print(f"✅ PDF generado exitosamente ({len(pdf_bytes)} bytes)")
            except Exception as pdf_err:
                print(f"⚠️ No se pudo generar PDF: {pdf_err}")
                pdf_base64 = None

        # ===========================
        # 3️⃣ Devolver respuesta a NestJS
        # ===========================
        return JSONResponse(
            status_code=200 if status == "complete" else 207,  # 207: multi-status/parcial
            content={
                "status": status,  # "complete" o "incomplete"
                "filename": filename,
                "pdf_base64": pdf_base64,
                "analysis_json": responses,
                "failed_prompts": failed_prompts,
            },
        )

    except Exception as e:
        # ===========================
        # 4️⃣ Error crítico → devolver parcial si existe
        # ===========================
        print(f"❌ Error en análisis ESG con PDF: {str(e)}")

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
