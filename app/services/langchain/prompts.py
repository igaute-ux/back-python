from langchain.prompts import PromptTemplate

# Prompt 1: Contexto organizacional y Sectorial
prompt_1 = PromptTemplate(
    input_variables=["organization_name", "country", "website"],
    template="""
        Objetivo:
        Recopilar información clave y contextual de la empresa para fundamentar el análisis de doble materialidad.
        Información de la empresa: 
        Nombre de empresa: {organization_name}
        País de operación por ser analizado: {country}
        Website de la empresa: {website}
        Instrucciones:
        Utilizando la información proporcionada y complementándola con fuentes públicas, genera un análisis contextual de la empresa que sirva como base para el análisis de doble materialidad. El análisis debe incluir todos los siguientes elementos: 
        Nombre de la empresa – Nombre legal o comercial.
        País de operación – País principal donde opera o sede.
        Industria - Según lo anteriormente mencionado
        Tamaño de empresa – Micro / Pequeña / Mediana / Grande / Multinacional.
        Ubicación geográfica – Región o ciudad donde opera.
        Modelo de negocio – Breve descripción del producto/servicio y propuesta de valor.
        Cadena de valor – Áreas clave: producción, distribución, clientes, proveedores, etc.
        Actividades principales – Procesos operativos clave que generan impacto ambiental o social (por ejemplo: manufactura, logística, atención al cliente).
        Nivel de madurez ESG – ¿Se tienen reportes, artículos o informes públicos en línea? 
        Stakeholders relevantes – Grupos de interés prioritarios: clientes, comunidades, reguladores, inversionistas, proveedores.
    """
)

# Prompt 2: Identificación de Impactos (basado en S&P)
prompt_2 = PromptTemplate(
    input_variables=["organization_context"],
    template="""
        Objetivo:
        Relacionar las actividades de la empresa con temas materiales utilizando los Materiality Maps de S&P y construir la base de la Materiality Table.
        Instrucciones:
        Utilizando la tabla “1. Acciones Materiality Map S&P V2 _ Julio 2025”, identifica los sectores S&P en los que opera la empresa (columna A).
        Si la empresa participa en más de un sector, selecciona los 2 sectores S&P más representativos, según su volumen de operación o presencia.
        Para cada uno de esos sectores, extrae los temas materiales y sus atributos directamente desde el Excel.
        Genera una tabla consolidada que incluya las siguientes columnas:
            - Sector
            - Temas
            - Materialidad financiera
            - Acción marginal
            - Acción moderada
            - Acción estructural
        Esta tabla será la base inicial para construir la Materiality Table del análisis de doble materialidad.
    """
)

# Prompt 3: Análisis de doble materialidad
prompt_3 = PromptTemplate(
    input_variables=["organization_name", "country", "website"],
    template="""
    """
)

# Prompt 4: Análisis de doble materialidad
prompt_4 = PromptTemplate(
    input_variables=["organization_name", "country", "website"],
    template="""
    """
)

# Prompt 5: Análisis de doble materialidad
prompt_5 = PromptTemplate(
    input_variables=["organization_name", "country", "website"],
    template="""
    """
)