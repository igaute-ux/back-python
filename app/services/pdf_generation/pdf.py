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

from .filters import CUSTOM_FILTERS

logger = logging.getLogger(__name__)


class PDFGenerator:
    """
    Service for generating PDF documents using Jinja2 templates and WeasyPrint
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the PDF generator
        
        Args:
            templates_dir: Directory containing Jinja2 templates. 
                          Defaults to the templates directory in this module
        """
        if templates_dir is None:
            # Default to the templates directory in this module
            current_dir = Path(__file__).parent
            templates_dir = current_dir / "templates"
        
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        
        # Add custom filters
        self.jinja_env.filters.update(CUSTOM_FILTERS)
        
        # Font configuration for WeasyPrint
        self.font_config = FontConfiguration()
        
        logger.info(f"PDF Generator initialized with templates directory: {self.templates_dir}")
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a Jinja2 template with the given context
        
        Args:
            template_name: Name of the template file
            context: Dictionary with template variables
            
        Returns:
            Rendered HTML string
            
        Raises:
            FileNotFoundError: If template file doesn't exist
            Exception: If template rendering fails
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
        
        Args:
            template_name: Name of the template file
            context: Dictionary with template variables
            css_string: CSS as string (optional)
            css_file: Path to CSS file (optional)
            output_path: Path to save PDF file (optional). If None, returns bytes
            landscape: Whether to use landscape orientation (default: True)
            
        Returns:
            PDF bytes if output_path is None, otherwise the file path
            
        Raises:
            Exception: If PDF generation fails
        """
        try:
            # Render the template
            html_content = self.render_template(template_name, context)
            
            # Create HTML object
            html_doc = HTML(string=html_content)
            
            # Prepare CSS
            css_doc = None
            if css_string:
                css_doc = CSS(string=css_string, font_config=self.font_config)
            elif css_file:
                css_doc = CSS(filename=css_file, font_config=self.font_config)
            elif landscape:
                # Apply default landscape CSS if no custom CSS provided
                landscape_css = """
                @page {
                    size: A4 landscape;
                    margin: 8mm;
                }
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    font-size: 11px;
                    line-height: 1.3;
                }
                h1, h2 {
                    color: #2e86c1;
                    border-bottom: 2px solid #2e86c1;
                    padding-bottom: 5px;
                }
                h3 {
                    margin-top: 20px;
                    color: #1f4e79;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 10px 0;
                    font-size: 9.5px;
                    table-layout: auto;
                }
                th, td {
                    border: 1px solid #ccc;
                    padding: 4px;
                    text-align: left;
                    word-wrap: break-word;
                    white-space: normal;
                    vertical-align: top;
                }
                th {
                    background: #f5f5f5;
                    font-weight: bold;
                }
                thead {
                    display: table-header-group;
                }
                tr {
                    page-break-inside: avoid;
                }
                .page-break {
                    page-break-before: always;
                }
                .materiality-actions td:nth-child(4),
                .materiality-actions td:nth-child(5),
                .materiality-actions td:nth-child(6) {
                    max-width: 120px;
                    text-align: justify;
                }
                .footer {
                    margin-top: 40px;
                    font-size: 12px;
                    color: #555;
                    text-align: center;
                }
                """
                css_doc = CSS(string=landscape_css, font_config=self.font_config)
            
            # Generate PDF
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
    
    def generate_pdf_from_html(
        self,
        html_content: str,
        css_string: Optional[str] = None,
        css_file: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> Union[bytes, str]:
        """
        Generate PDF directly from HTML content
        
        Args:
            html_content: HTML content as string
            css_string: CSS as string (optional)
            css_file: Path to CSS file (optional)
            output_path: Path to save PDF file (optional). If None, returns bytes
            
        Returns:
            PDF bytes if output_path is None, otherwise the file path
        """
        try:
            # Create HTML object
            html_doc = HTML(string=html_content)
            
            # Prepare CSS
            css_doc = None
            if css_string:
                css_doc = CSS(string=css_string, font_config=self.font_config)
            elif css_file:
                css_doc = CSS(filename=css_file, font_config=self.font_config)
            
            # Generate PDF
            if output_path:
                html_doc.write_pdf(output_path, stylesheets=[css_doc] if css_doc else None)
                logger.info(f"PDF generated successfully: {output_path}")
                return output_path
            else:
                pdf_bytes = html_doc.write_pdf(stylesheets=[css_doc] if css_doc else None)
                logger.info("PDF generated successfully in memory")
                return pdf_bytes
                
        except Exception as e:
            logger.error(f"Error generating PDF from HTML: {str(e)}")
            raise
    
    def list_templates(self) -> list:
        """
        List available templates in the templates directory
        
        Returns:
            List of template file names
        """
        try:
            templates = []
            for file_path in self.templates_dir.glob("*.html"):
                templates.append(file_path.name)
            return sorted(templates)
        except Exception as e:
            logger.error(f"Error listing templates: {str(e)}")
            return []
    
    def template_exists(self, template_name: str) -> bool:
        """
        Check if a template exists
        
        Args:
            template_name: Name of the template file
            
        Returns:
            True if template exists, False otherwise
        """
        template_path = self.templates_dir / template_name
        return template_path.exists()
    
    def process_esg_pipeline_data(self, pipeline_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process ESG pipeline data and extract information for the template
        
        Args:
            pipeline_data: List of prompt responses from the ESG analysis pipeline
            
        Returns:
            Dictionary with processed data for the ESG template
        """
        try:
            if not pipeline_data or len(pipeline_data) < 11:
                raise ValueError("Pipeline data must contain at least 11 items")
            
            # Extract organizational context (position 0)
            org_data = pipeline_data[0].get("response_content", {})
            
            # Extract materiality table (position 5)
            materiality_data = pipeline_data[5].get("response_content", {}).get("materiality_table", [])
            
            # Extract GRI data (position 6)
            gri_data = pipeline_data[6].get("response_content", {}).get("gri", [])
            
            # Extract SASB data (position 8)
            sasb_data = pipeline_data[8].get("response_content", {}).get("tabla_sasb", [])
            
            # Extract regulations data (position 9)
            regulations_data = pipeline_data[9].get("response_content", {}).get("regulaciones", [])
            
            # Extract executive summary (position 10)
            exec_summary = pipeline_data[10].get("response_content", {})
            
            # Compile template context
            context = {
                # Organizational context
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
                
                # Tables
                "materiality_table": materiality_data,
                "gri": gri_data,
                "tabla_sasb": sasb_data,
                "regulaciones": regulations_data,
                
                # Executive summary
                "parrafo_1": exec_summary.get("parrafo_1", ""),
                "parrafo_2": exec_summary.get("parrafo_2", "")
            }
            
            logger.info("ESG pipeline data processed successfully")
            return context
            
        except Exception as e:
            logger.error(f"Error processing ESG pipeline data: {str(e)}")
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
        
        Args:
            pipeline_data: List of prompt responses from the ESG analysis pipeline
            output_path: Path to save PDF file (optional). If None, returns bytes
            css_string: CSS as string (optional)
            css_file: Path to CSS file (optional)
            landscape: Whether to use landscape orientation (default: True)
            
        Returns:
            PDF bytes if output_path is None, otherwise the file path
        """
        try:
            # Process pipeline data
            template_context = self.process_esg_pipeline_data(pipeline_data)
            
            # Generate PDF using the ESG template
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
        
        Args:
            json_file_path: Path to JSON file containing pipeline data
            output_path: Path to save PDF file (optional). If None, returns bytes
            css_string: CSS as string (optional)
            css_file: Path to CSS file (optional)
            landscape: Whether to use landscape orientation (default: True)
            
        Returns:
            PDF bytes if output_path is None, otherwise the file path
        """
        try:
            # Load JSON data
            with open(json_file_path, 'r', encoding='utf-8') as f:
                pipeline_data = json.load(f)
            
            # Generate report
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


# Convenience function for quick PDF generation
def generate_pdf(
    template_name: str,
    context: Dict[str, Any],
    output_path: Optional[str] = None,
    templates_dir: Optional[str] = None,
    css_string: Optional[str] = None,
    css_file: Optional[str] = None,
    landscape: bool = True
) -> Union[bytes, str]:
    """
    Convenience function to generate PDF quickly
    
    Args:
        template_name: Name of the template file
        context: Dictionary with template variables
        output_path: Path to save PDF file (optional)
        templates_dir: Directory containing templates (optional)
        css_string: CSS as string (optional)
        css_file: Path to CSS file (optional)
        landscape: Whether to use landscape orientation (default: True)
        
    Returns:
        PDF bytes if output_path is None, otherwise the file path
    """
    generator = PDFGenerator(templates_dir)
    return generator.generate_pdf_from_template(
        template_name=template_name,
        context=context,
        css_string=css_string,
        css_file=css_file,
        output_path=output_path,
        landscape=landscape
    )


# Convenience function for ESG report generation
def generate_esg_report(
    pipeline_data: List[Dict[str, Any]],
    output_path: Optional[str] = None,
    templates_dir: Optional[str] = None,
    css_string: Optional[str] = None,
    css_file: Optional[str] = None,
    landscape: bool = True
) -> Union[bytes, str]:
    """
    Convenience function to generate ESG report quickly
    
    Args:
        pipeline_data: List of prompt responses from the ESG analysis pipeline
        output_path: Path to save PDF file (optional)
        templates_dir: Directory containing templates (optional)
        css_string: CSS as string (optional)
        css_file: Path to CSS file (optional)
        landscape: Whether to use landscape orientation (default: True)
        
    Returns:
        PDF bytes if output_path is None, otherwise the file path
    """
    generator = PDFGenerator(templates_dir)
    return generator.generate_esg_report(
        pipeline_data=pipeline_data,
        output_path=output_path,
        css_string=css_string,
        css_file=css_file,
        landscape=landscape
    )
