from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.models.analysis import AnalysisRequest
from app.services.langchain.workflows import run_assistant_test, run_esg_analysis
from app.services.pdf_generation.pdf import PDFGenerator
from pathlib import Path

router = APIRouter()

@router.post("/analyze-context")
async def analyze_context(data: AnalysisRequest):
    result = await run_assistant_test(
        organization_name=data.organization_name,
        country=data.country,
        website=data.website
    )
    return {"analysis": result}

@router.post("/esg-analysis")
async def esg_analysis(data: AnalysisRequest):
    result = await run_esg_analysis(
        organization_name=data.organization_name,
        country=data.country,
        website=data.website
    )
    return result

@router.post("/esg-analysis-with-pdf")
async def esg_analysis_with_pdf(data: AnalysisRequest):
    """
    Ejecuta el análisis ESG completo y genera un PDF del reporte
    """
    try:
        # Ejecutar el análisis ESG
        print(f"🚀 Iniciando análisis ESG para {data.organization_name}")
        pipeline_data = await run_esg_analysis(
            organization_name=data.organization_name,
            country=data.country,
            website=data.website
        )
        
        # Generar PDF en memoria
        print("📄 Generando PDF del reporte...")
        generator = PDFGenerator()
        
        # Nombre del archivo basado en la organización
        safe_name = "".join(c for c in data.organization_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_').lower()
        filename = f"esg_report_{safe_name}.pdf"
        
        # Generar PDF en memoria (sin guardar archivo)
        pdf_bytes = generator.generate_esg_report(
            pipeline_data=pipeline_data,
            output_path=None  # Genera en memoria
        )
        
        print(f"✅ PDF generado exitosamente en memoria: {len(pdf_bytes)} bytes")
        
        # Retornar PDF directamente en la respuesta
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

@router.get("/test-pdf-from-example")
async def test_pdf_from_example():
    """
    Genera un PDF de prueba usando el example_data.json
    """
    try:
        # Ruta al archivo de ejemplo
        current_dir = Path(__file__).parent.parent.parent
        example_data_path = current_dir / "services" / "pdf_generation" / "example_data.json"
        
        if not example_data_path.exists():
            raise HTTPException(status_code=404, detail="Archivo example_data.json no encontrado")
        
        # Generar PDF en memoria
        generator = PDFGenerator()
        
        # Generar PDF desde archivo en memoria
        pdf_bytes = generator.generate_esg_report_from_file(
            json_file_path=str(example_data_path),
            output_path=None  # Genera en memoria
        )
        
        filename = "esg_report_test_example.pdf"
        print(f"✅ PDF de prueba generado exitosamente en memoria: {len(pdf_bytes)} bytes")
        
        # Retornar PDF directamente en la respuesta
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes))
            }
        )
        
    except Exception as e:
        print(f"❌ Error generando PDF de prueba: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generando PDF de prueba: {str(e)}")

