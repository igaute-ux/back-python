"""
PDF Generation Service using Jinja2 templates and WeasyPrint
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from io import BytesIO
import logging

from jinja2 import Environment, FileSystemLoader, Template
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

logger = logging.getLogger(__name__)


class PDFGenerator:
    """
    Service for generating PDF documents using Jinja2 templates and WeasyPrint
    """

    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the PDF generator
        """
        if templates_dir is None:
            current_dir = Path(__file__).parent
            templates_dir = current_dir / "templates"

        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )

        self.font_config = FontConfiguration()

        logger.info(f"PDF Generator initialized with templates directory: {self.templates_dir}")

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a Jinja2 template with the given context
        """
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {str(e)}")
            raise

    def generate_pdf_from_template(
        self,
        template_name: str,
        context: Dict[str, Any],
        css_string: Optional[str] = None,
        css_file: Optional[str] = None,
        output_path: Optional[str] = None,
        landscape: bool = True
    ) -> Union[bytes, str]:
        """
        Generate PDF from a Jinja2 template
        """
        try:
            # Render HTML content
            html_content = self.render_template(template_name, context)
            html_doc = HTML(string=html_content)

            # Optional CSS
            css_doc = None
            if css_file:
                css_doc = CSS(filename=css_file)
            elif css_string:
                css_doc = CSS(string=css_string)

            if output_path:
                html_doc.write_pdf(output_path, stylesheets=[css_doc] if css_doc else None)
                logger.info(f"PDF generated successfully: {output_path}")
                return output_path
            else:
                pdf_bytes = html_doc.write_pdf(stylesheets=[css_doc] if css_doc else None)
                logger.info("PDF generated successfully in memory")
                return pdf_bytes

        except Exception as e:
            logger.error(f"Error generating PDF from template {template_name}: {str(e)}")
            raise

    def process_esg_pipeline_data(self, pipeline_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Procesa el pipeline ESG y normaliza las variables para que coincidan
        con las esperadas por la plantilla HTML.
        """
        try:
            if not pipeline_data or len(pipeline_data) < 11:
                raise ValueError("Pipeline data must contain at least 11 items")

            # 📌 1. Contexto organizacional (prompt 1)
            org_data = pipeline_data[0].get("response_content", {})

            # 📊 2. Matriz de impactos - Parte A (prompt 2)
            materiality_actions = pipeline_data[1].get("response_content", {}).get("materiality_table", [])

            # 📈 3. Matriz de impactos - Parte B (prompt 4)
            materiality_evaluation = pipeline_data[3].get("response_content", {}).get("materiality_table", [])


            # 🌱 3. ODS (prompt 5)
            ods_data = pipeline_data[5].get("response_content", {}).get("materiality_table", [])

            # 🧾 4. GRI (prompt 7)
            gri_data = pipeline_data[6].get("response_content", {}).get("gri", [])

            # 📈 5. SASB (prompt 9)
            sasb_data = pipeline_data[8].get("response_content", {}).get("tabla_sasb", [])

            # ⚖️ 6. Regulaciones (prompt 10)
            regulations_data = pipeline_data[9].get("response_content", {}).get("regulaciones", [])

            # 📝 7. Resumen ejecutivo (prompt 11)
            exec_summary = pipeline_data[10].get("response_content", {})

            def normalize_item(item):
                return {k.lower().replace(" ", "_"): v for k, v in item.items()}

            matriz_acciones = [normalize_item(i) for i in materiality_actions]
            matriz_evaluacion = [normalize_item(i) for i in materiality_evaluation]

            ods_table = [normalize_item(i) for i in ods_data]
            gri_table = [normalize_item(i) for i in gri_data]
            sasb_table = [normalize_item(i) for i in sasb_data]
            regulaciones_table = [normalize_item(i) for i in regulations_data]
            context = {
                "nombre_empresa": org_data.get("nombre_empresa", ""),
                "pais_operacion": org_data.get("pais_operacion", ""),
                "industria": org_data.get("industria", ""),
                "tamano_empresa": org_data.get("tamano_empresa", ""),
                "ubicacion_geografica": org_data.get("ubicacion_geografica", ""),
                "modelo_negocio": org_data.get("modelo_negocio", ""),
                "cadena_valor": org_data.get("cadena_valor", ""),
                "actividades_principales": org_data.get("actividades_principales", ""),
                "madurez_esg": org_data.get("madurez_esg", ""),
                "stakeholders_relevantes": org_data.get("stakeholders_relevantes", ""),

                # 👇 Estas son las dos tablas distintas
                "matriz_acciones": matriz_acciones,
                "matriz_evaluacion": matriz_evaluacion,

                "ods_table": ods_table,
                "gri": gri_table,
                "sasb": sasb_table,
                "regulaciones": regulaciones_table,
                "parrafo_1": exec_summary.get("parrafo_1", ""),
                "parrafo_2": exec_summary.get("parrafo_2", "")
            }


            logger.info("✅ ESG pipeline data processed and normalized successfully")
            return context

        except Exception as e:
            logger.error(f"❌ Error processing ESG pipeline data: {str(e)}")
            raise

    def generate_esg_report(
        self,
        pipeline_data: List[Dict[str, Any]],
        output_path: Optional[str] = None,
        css_string: Optional[str] = None,
        css_file: Optional[str] = None,
        landscape: bool = True
    ) -> Union[bytes, str]:
        """
        Generate ESG analysis PDF report from pipeline data
        """
        try:
            template_context = self.process_esg_pipeline_data(pipeline_data)
            result = self.generate_pdf_from_template(
                template_name="esg_analysis.html",
                context=template_context,
                css_string=css_string,
                css_file=css_file,
                output_path=output_path,
                landscape=landscape
            )
            logger.info("ESG report generated successfully")
            return result
        except Exception as e:
            logger.error(f"Error generating ESG report: {str(e)}")
            raise

    def generate_esg_report_from_file(
        self,
        json_file_path: str,
        output_path: Optional[str] = None,
        css_string: Optional[str] = None,
        css_file: Optional[str] = None,
        landscape: bool = True
    ) -> Union[bytes, str]:
        """
        Generate ESG analysis PDF report from a JSON file
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                pipeline_data = json.load(f)
            return self.generate_esg_report(
                pipeline_data=pipeline_data,
                output_path=output_path,
                css_string=css_string,
                css_file=css_file,
                landscape=landscape
            )
        except FileNotFoundError:
            logger.error(f"JSON file not found: {json_file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {json_file_path}: {str(e)}")
            raise ValueError(f"Invalid JSON in file {json_file_path}")
        except Exception as e:
            logger.error(f"Error generating ESG report from file: {str(e)}")
            raise
