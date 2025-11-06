from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response, JSONResponse
from app.schemas.analysis_request import AnalysisRequest
from app.services.langchain.workflows import run_esg_analysis, run_esg_analysis_test
from app.services.pdf_generation.pdf import PDFGenerator
from app.db.session import get_db
from sqlalchemy.orm import Session
import base64
import os

router = APIRouter()

# ==========================================================
# 🧪 TEST: solo Prompt 1
# ==========================================================
@router.post("/esg-analysis-test")
async def esg_analysis_test(data: AnalysisRequest, db: Session = Depends(get_db)):
    """
    Ejecuta SOLO Prompt 1 (versión de prueba rápida).
    Devuelve el PDF (base64) + JSON para ver cómo llega a NestJS.
    """
    try:
        print(f"🧪 Iniciando análisis ESG TEST para {data.organization_name}")

        # 1️⃣ Ejecutar solo el primer prompt
        pipeline_data = await run_esg_analysis_test(
            organization_name=data.organization_name,
            country=data.country,
            website=data.website
        )

        # 2️⃣ Generar PDF con el pipeline de prueba
        print("📄 Generando PDF de prueba...")
        generator = PDFGenerator()
        pdf_bytes = generator.generate_esg_report(pipeline_data=pipeline_data, output_path=None)

        # 3️⃣ Codificar el PDF a base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        # 4️⃣ Preparar filename
        safe_name = "".join(c for c in data.organization_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_').lower()
        filename = f"esg_report_test_{safe_name}.pdf"

        print(f"✅ PDF generado exitosamente ({len(pdf_bytes)} bytes)")

        # 5️⃣ Devolver JSON + PDF base64
        return JSONResponse(
            content={
                "filename": filename,
                "pdf_base64": pdf_base64,
                "analysis_json": pipeline_data
            }
        )

    except Exception as e:
        print(f"❌ Error en test ESG: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en test ESG: {str(e)}")

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
            website=data.website
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


# ==========================================================
# 📥 Análisis ESG con PDF (solo PDF binario descargable)
# ==========================================================
@router.post("/esg-analysis-with-pdf")
async def esg_analysis_with_pdf(data: AnalysisRequest, db: Session = Depends(get_db)):
    """
    Ejecuta el análisis ESG completo y genera un PDF del reporte
    """
    try:
        print(f"🚀 Iniciando análisis ESG para {data.organization_name}")
        pipeline_data = await run_esg_analysis(
            organization_name=data.organization_name,
            country=data.country,
            website=data.website
        )
        
        print("📄 Generando PDF del reporte...")
        generator = PDFGenerator()
        
        safe_name = "".join(c for c in data.organization_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_').lower()
        filename = f"esg_report_{safe_name}.pdf"
        
        pdf_bytes = generator.generate_esg_report(
            pipeline_data=pipeline_data,
            output_path=None
        )
        
        print(f"✅ PDF generado exitosamente en memoria: {len(pdf_bytes)} bytes")

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes))
            }
        )
        
    except Exception as e:
        print(f"❌ Error en análisis ESG con PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generando análisis ESG: {str(e)}")
