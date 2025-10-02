from langchain.prompts import PromptTemplate

# Prompt 1: Contexto organizacional y Sectorial

prompt_1 = PromptTemplate(
    name="🔹 Prompt 1: Contexto organizacional y Sectorial",
    input_variables=["organization_name", "country", "website"],
    template="""
        🔹 Prompt 1: Contexto organizacional y Sectorial
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
        Es importante que la respuesta venga en el siguiente formato JSON y SOLO me entregues el JSON en la respuesta: {{ "nombre_empresa": "string", "pais_operacion": "string", "industria": "string", "tamano_empresa": "string", "ubicacion_geografica": "string", "modelo_negocio": "string", "cadena_valor": "string", "actividades_principales": "string", "madurez_esg": "string", "stakeholders_relevantes": "string" }}
    """
)

# Prompt 2: Identificación de Impactos (basado en S&P)
prompt_2 = PromptTemplate(
    name="🔹 Prompt 2: Identificación de Impactos (basado en S&P)",
    template="""
        🔹 Prompt 2: Identificación de Impactos (basado en S&P)
        Objetivo:
        Relacionar las actividades de la empresa con temas materiales utilizando los Materiality Maps de S&P y construir la base de la Materiality Table.
        Instrucciones:
        Utilizando la tabla “1. Acciones Materiality Map S&P V2 _ Julio 2025”, identifica los sectores S&P en los que opera la empresa (columna A).
        Si la empresa participa en más de un sector, selecciona el sector S&P más representativo, según su volumen de operación o presencia.
        Para ese sector, extrae los temas materiales y sus atributos directamente desde el Excel en exactamente el mismo formato y orden en el que estén en el excel, sin dejar fuera ningún tema asignado para el sector seleccionado.  
        Genera una tabla consolidada que incluya las siguientes columnas:
            - Sector
            - Temas
            - Materialidad financiera
            - Acción marginal
            - Acción moderada
            - Acción estructural
        Esta tabla será la base inicial para construir la Materiality Table del análisis de doble materialidad.
        Es importante que la respuesta: identifique todos los sectores posibles que encuentre, minimo 15 resultados; venga en el siguiente formato JSON y SOLO me entregues el JSON en la respuesta: {{
            "materiality_table": [
                {
                    "sector": "string",
                    "tema": "string",
                    "materialidad_financiera": "string",
                    "accion_marginal": "string",
                    "accion_moderada": "string",
                    "accion_estructural": "string"
                }
            ]
        }}
    """,
)

# Prompt 2.1: Identificación de Impactos (basado en S&P)
prompt_2_1 = PromptTemplate(
    name="🔹 Prompt 2.1: Continuación de la Identificación de Impactos (basado en S&P)",
    template="""
        🔹 Prompt 2.1: Continuación de la Identificación de Impactos (basado en S&P)
        Objetivo:
        Continuar la identificación de impactos utilizando los Materiality Maps de S&P y construir la base de la Materiality Table.
        Instrucciones:
        Anteriormente se generó la tabla de impactos donde te pedi un minimo de 15 resultados de ser posible, ahora se debe continuar con la identificación de impactos utilizando los Materiality Maps de S&P y a la tabla anterior agregar los resultados faltantes.
        Es importante que la respuesta: siga la misma estructura de la tabla de impactos anterior, venga en el siguiente formato JSON y SOLO me entregues el JSON en la respuesta: {{
            "materiality_table": [
                {
                    "sector": "string",
                    "tema": "string",
                    "materialidad_financiera": "string",
                    "accion_marginal": "string",
                    "accion_moderada": "string",
                    "accion_estructural": "string"
                }
            ]
        }}
    """
)

# Prompt 3: Análisis de doble materialidad
prompt_3 = PromptTemplate(
    name="🔹 Prompt 3: Evaluación de Impactos",
    template="""
        🔹 Prompt 3: Evaluación de Impactos
        Objetivo:
        Analizar los temas materiales identificados en la Materiality Table y evaluar el tipo y características del impacto que genera la empresa sobre cada uno.
        Instrucciones:
        A la tabla generada en el prompt anterior, manteniendo toda su información, agrega las siguientes columnas y asigna la respuesta más adecuada para cada tema material, basándote en el contexto y operaciones de la empresa:
        Tipo de impacto generado por la empresa – Positivo o negativo.
        Potencialidad del impacto – Real o potencial.
        Horizonte del impacto – Corto o largo plazo.
        Intencionalidad del impacto – Intencionado o no intencionado.
        Penetración del impacto – Reversible o irreversible.
        Grado de implicación con el impacto – Directo o indirecto.
        Esta evaluación permitirá enriquecer la Materiality Table con una visión más precisa de la naturaleza de los impactos ESG asociados a los temas materiales de la empresa.
        Es importante que la respuesta venga en el siguiente formato JSON y SOLO me entregues el JSON en la respuesta: {{
            "materiality_table": [
                {
                    "sector": "string",
                    "tema": "string",
                    "materialidad_financiera": "string",
                    "accion_marginal": "string",
                    "accion_moderada": "string",
                    "accion_estructural": "string",
                    "tipo_impacto": "string",
                    "potencialidad_impacto": "string",
                    "horizonte_impacto": "string",
                    "intencionalidad_impacto": "string",
                    "penetracion_impacto": "string",
                    "grado_implicacion": "string"
                }
            ]
        }}
    """
)

# Prompt 4: Análisis de doble materialidad
prompt_4 = PromptTemplate(
    name="🔹 Prompt 4: Evaluación de Impactos (doble materialidad)",
    template="""
        🔹 Prompt 4: Evaluación de Impactos (doble materialidad)
        Objetivo:
        Priorizar los impactos asociados a cada tema material utilizando una evaluación combinada de criterios ESG y financieros.
        Instrucciones:
        A la tabla generada anteriormente (Materiality Table),  manteniendo toda su información, agrega las siguientes 6 columnas y asigna el valor correspondiente a cada tema material con base en su impacto:
        - Gravedad – Evalúa la severidad del impacto negativo.
        Escala:
        0 = Nada negativo
        1 = Muy poco negativo
        2 = Poco negativo
        3 = Moderadamente negativo
        4 = Muy negativo
        5 = Extremadamente negativo
        - Probabilidad – Evalúa qué tan probable es que ocurra el impacto.
        Escala:
        0 = Nada probable
        1 = Muy poco probable
        2 = Poco probable
        3 = Moderadamente probable
        4 = Muy probable
        5 = Extremadamente probable
        - Alcance – Evalúa qué tan amplio es el impacto en términos de personas, áreas o procesos afectados.
        Escala:
        0 = Nada de alcance
        1 = Muy poco alcance
        2 = Poco alcance
        3 = Moderado alcance
        4 = Mucho alcance
        5 = Alcance extremo
        - Impacto ESG – Evalúa el nivel de impacto que el tema tiene dentro o fuera de la empresa en aspectos sociales, ambientales o de gobernanza, sin considerar el efecto financiero.
        Escala:
        0 = Ningún impacto
        1 = Muy poco impacto
        2 = Poco impacto
        3 = Impacto moderado
        4 = Alto impacto
        5 = Impacto extremo
        - Impacto financiero – Asigna un valor numérico a partir de la columna “Materialidad financiera” de la Materiality Table:
        “Baja” = 0
        “Media” = 3
        “Alta” = 5
        - Puntaje total – Calcula la suma de los cinco criterios anteriores. Este puntaje será usado para priorizar los temas materiales en el siguiente paso.
        Es importante que la respuesta venga en el siguiente formato JSON y SOLO me entregues el JSON en la respuesta: {{
            "materiality_table": [
                {
                    "sector": "string",
                    "tema": "string",
                    "materialidad_financiera": "string",
                    "accion_marginal": "string",
                    "accion_moderada": "string",
                    "accion_estructural": "string",
                    "tipo_impacto": "string",
                    "potencialidad_impacto": "string",
                    "horizonte_impacto": "string",
                    "intencionalidad_impacto": "string",
                    "penetracion_impacto": "string",
                    "grado_implicacion": "string",
                    "gravedad": integer,
                    "probabilidad": integer,
                    "alcance": integer,
                    "impacto_esg": integer,
                    "impacto_financiero": integer,
                    "puntaje_total": integer
                }
            ]
        }}
    """
)

#Prompt 5: Priorización de Temas
prompt_5 = PromptTemplate(
    name="🔹 Prompt 5: Priorización de Temas",
    template="""
        🔹 Prompt 5: Priorización de Temas
        Objetivo:
        Definir los 10 temas materiales prioritarios a partir de la evaluación de impactos previamente realizada.
        Instrucciones:
        Ordena la tabla de la Materiality Table de mayor a menor según el valor de la columna “Puntaje total”, sin modificar ningún valor o contenido existente en las filas.
        Identifica los 10 temas con mayor puntaje total, los cuales serán considerados como los temas materiales priorizados del análisis.
        Para facilitar su seguimiento en los siguientes pasos, puedes destacarlos visualmente o etiquetarlos como "Material" en una nueva columna. 
        Es importante que la respuesta venga en el siguiente formato JSON y SOLO me entregues el JSON en la respuesta: {{
            "materiality_table": [
                {
                    "sector": "string",
                    "tema": "string",
                    "materialidad_financiera": "string",
                    "accion_marginal": "string",
                    "accion_moderada": "string",
                    "accion_estructural": "string",
                    "tipo_impacto": "string",
                    "potencialidad_impacto": "string",
                    "horizonte_impacto": "string",
                    "intencionalidad_impacto": "string",
                    "penetracion_impacto": "string",
                    "grado_implicacion": "string",
                    "gravedad": integer,
                    "probabilidad": integer,
                    "alcance": integer,
                    "impacto_esg": integer,
                    "impacto_financiero": integer,
                    "puntaje_total": integer,
                    "prioridad": "string"
                }
            ]
        }}
    """,
)

# Prompt 6: Análisis de doble materialidad
prompt_6 = PromptTemplate(
    name="🔹 Prompt 6: Vínculo con Objetivos de Desarrollo Sostenible (ODS)",
    template="""
        🔹 Prompt 6: Vínculo con Objetivos de Desarrollo Sostenible (ODS)
        Objetivo:
        Relacionar los 10 temas materiales priorizados con el Objetivo de Desarrollo Sostenible (ODS), su meta e indicador más directamente asociados.
        Instrucciones:
        1. Mantén intacta la tabla de la Materiality Table: no elimines columnas ni modifiques su contenido existente.
        2. Agrega tres nuevas columnas al final de la tabla:
        - ODS – El Objetivo de Desarrollo Sostenible más directamente relacionado con el tema material.
        - Meta de ODS – La meta de ese ODS más estrechamente alineada semánticamente con el tema.
        - Indicador de ODS – El indicador correspondiente a la meta seleccionada (misma fila del documento de referencia).
        3. Utiliza únicamente el documento “2. Lista de ODS _ Adaptia _ 2025” como fuente de información.
        4. Para cada uno de los 10 temas materiales (etiquetados como “Material” en la tabla):
        - Revisa los 17 ODS completos y selecciona el que tenga la relación más fuerte y directa con el tema.
        - Una vez elegido el ODS, revisa todas sus metas y selecciona la más directamente vinculada al tema.
        - Copia también el indicador que corresponde a esa meta (misma fila del documento de referencia).
        5. Para los temas que no están priorizados como “Material”:
        - No los elimines.
        - Completa las tres nuevas columnas con “NA” para indicar que no fueron analizados en esta dimensión.
        Nota:
        El vínculo debe ser único por tema (solo un ODS, una meta y un indicador), priorizando siempre la opción más específica y semánticamente cercana.
        Es importante que la respuesta venga en el siguiente formato JSON y SOLO me entregues el JSON en la respuesta: {{
            "materiality_table": [
                {
                    "sector": "string",
                    "tema": "string",
                    "materialidad_financiera": "string",
                    "accion_marginal": "string",
                    "accion_moderada": "string",
                    "accion_estructural": "string",
                    "tipo_impacto": "string",
                    "potencialidad_impacto": "string",
                    "horizonte_impacto": "string",
                    "intencionalidad_impacto": "string",
                    "penetracion_impacto": "string",
                    "grado_implicacion": "string",
                    "gravedad": integer,
                    "probabilidad": integer,
                    "alcance": integer,
                    "impacto_esg": integer,
                    "impacto_financiero": integer,
                    "puntaje_total": integer,
                    "prioridad": "string",
                    "ods": "string",
                    "meta_ods": "string",
                    "indicador_ods": "string"
                }
            ]
        }}
    """,
)


#Prompt 7: Mapeo de Contenidos GRI
prompt_7 = PromptTemplate(
    name="🔹 Prompt 7: Mapeo de Contenidos GRI",
    template="""
        🔹 Prompt 7: Mapeo de Contenidos GRI
        Objetivo
        Identificar y documentar los contenidos GRI relacionados con los 10 temas materiales priorizados en la Materiality Table, seleccionando de forma exhaustiva y fundamentada el disclosure más relevante y específico para cada tema.
        Instrucciones
        1. Alcance
        Trabaja únicamente con los 10 temas con mayor puntaje total (etiquetados como “Material” en la tabla).
        2. Fuente
        Usa la base “3. Lista de Estándares GRI _ Adaptia _ 2025”. Ignora las filas 2 a 7 de encabezados.
        3. Búsqueda de candidatos
        Para cada tema material:
        - Revisa toda la lista de estándares y disclosures GRI.
        - Identifica todos los estándares/disclosures semánticamente relevantes (considera nombre del estándar, título del disclosure y texto del requirement).
        4. Reglas de selección (en este orden de prioridad)
        a) Alineación temática directa con el enunciado del tema.
        b) Especificidad del disclosure respecto al tema (evita opciones genéricas).
        c) Requirement más detallado y accionable como desempate.
        d) Si hay empate entre un disclosure temático (series 300/400/200) y uno general (GRI 2), elige el temático.
        5. Restricción explícita sobre GRI 2 (General Disclosures)
        - No selecciones GRI 2 salvo que el tema sea de gobernanza/gestión organizacional general (p. ej., estructura, políticas generales, gobierno, participación de stakeholders).
        - Nunca uses GRI 2-7 (Employees) para temas de salud y seguridad del cliente, productos/servicios sostenibles, riesgo de transición climática, residuos/reciclaje, privacidad/protección de datos o impactos en comunidades.
        - Para temas de personal utiliza los estándares GRI 401–404 (empleo, formación) y GRI 403 (SST), GRI 405 (diversidad), etc., según corresponda.
        5. Evitar duplicados
        - Si más de un tema material se alinea con el mismo estándar y disclosure GRI, manténlo una sola vez en la tabla final.
        - La tabla resultante debe tener solo estándares únicos, sin repeticiones.
        6. Salida (una sola opción final por tema, sin duplicados)
        De la lista de candidatos, selecciona solo el disclosure más alineado y completa con exactamente estas columnas y textos:
        - Estándard GRI – Nombre completo del estándar, incluyendo número y nombre.
        - Contenido GRI (disclosure) – Código y nombre del disclosure.
        - Descripción del indicador (requirement) – Texto completo del requirement, tal como aparece en el documento.
        7. Exclusiones
        No incluyas temas que no estén priorizados como “Material”. No agregues columnas adicionales.
        8. Control de calidad
        Antes de cerrar: verifica que el disclosure elegido mencione explícitamente el objeto del tema o su mecanismo de impacto. Si no, vuelve al paso 4 y selecciona el disclosure más específico disponible.
        Es importante que la respuesta venga en el siguiente formato JSON y SOLO me entregues el JSON en la respuesta: {{
            "gri": [
                {
                    "estandar_gri": "string",
                    "contenido_gri": "string",
                    "descripcion_indicador": "string"
                }
            ]
        }}
    """,
)

#Prompt 8: Mapeo SASB Sectorial
prompt_8 = PromptTemplate(
    name="🔹 Prompt 8: Mapeo SASB Sectorial",
    template="""
        🔹 Prompt 8: Mapeo SASB Sectorial
        Objetivo:
        Identificar los temas e indicadores SASB relevantes para hasta 2 industrias asociadas.
        Instrucciones:
        Utilizando el documento “4. Equivalencias SASB + S&P _ Junio 2025”, identifica las industrias SASB equivalentes a los sectores S&P seleccionados previamente para la empresa.
        Para cada sector S&P identificado, selecciona una sola industria SASB: la más cercana o representativa según la tabla de equivalencias.
        El resultado final debe incluir un máximo de 2 industrias SASB.
        Es importante que la respuesta venga en el siguiente formato JSON y SOLO me entregues el JSON en la respuesta: {{
            "mapeo_sasb": [
                {
                    "sector_s&p": "string",
                    "industria_sasb": "string"
                }
            ]
        }}
    """,
)

#Prompt 9: Tabla SASB Sectorial
prompt_9 = PromptTemplate(
    name="🔹 Prompt 9: Tabla SASB Sectorial",
    template="""
        🔹 Prompt 9: Tabla SASB Sectorial. Objetivo: Detallar los temas, métricas y códigos SASB aplicables a las industrias seleccionadas previamente. Instrucciones: Utilizando el documento “5. Lista estándares SASB _ Noviembre 2024”, identifica todas las filas correspondientes a las industrias SASB relevantes definidas en el paso anterior. A partir de esa información, genera una tabla que incluya las siguientes columnas tal como aparecen en el Excel: - Industria - Tema - Parámetro de contabilidad - Categoría - Unidad de medida - Código. Extrae los datos directamente del archivo, sin modificar su redacción ni estructura. Incluye todas las filas relevantes para cada industria SASB seleccionada, ya que esta tabla servirá como insumo para el siguiente paso de asignación de estándares.
        Es importante que la respuesta venga en el siguiente formato JSON y SOLO me entregues el JSON en la respuesta: {{
            "tabla_sasb": [
                {
                    "industria": "string",
                    "tema": "string",
                    "parametro_contabilidad": "string",
                    "categoria": "string",
                    "unidad_medida": "string",
                    "codigo": "string"
                }
            ]
        }}
    """,
)

#Prompt 10: Vinculación Normativa por Tema Material (GAIL)
prompt_10 = PromptTemplate(
    name="🔹 Prompt 10: Vinculación Normativa por Tema Material (GAIL)",
    template="""
        🔹 Prompt 10: Vinculación Normativa por Tema Material (GAIL)
        Objetivo
        Identificar las normativas o regulaciones nacionales o sectoriales más relevantes que se relacionan directamente con los 10 temas materiales priorizados de la empresa.
        Instrucciones
        - Utiliza el archivo “7. Mapeo Regulatorio LATAM GAIL _ Junio 2025”.
        - Filtra la información por el país de operación analizado (segun resultado del prompt #1).
        - Para cada uno de los 10 temas materiales priorizados:
        1. Revisa todas las regulaciones disponibles para Chile.
        2. Evalúa la coincidencia semántica entre el enunciado del tema material y la descripción de cada normativa.
        3. Selecciona únicamente las 3 normativas con mayor relevancia para ese tema (máximo 3 filas por tema).
        4. Asegúrate de cubrir todos los temas materiales priorizados, no solo los relacionados con condiciones laborales.
        Criterios de relevancia
        - Mayor alineación temática entre el nombre del tema y la normativa.
        - Especificidad: prefiere regulaciones que hagan referencia directa al área de impacto (ej. emisiones, privacidad de datos, residuos).
        - Si varias normativas empatan en relevancia, selecciona la más reciente o de mayor aplicabilidad nacional.
        Salida
        Genera una tabla con las siguientes columnas:
        - Tema material – Tal como aparece en la Materiality Table.
        - Tipo de regulación – Tal como aparece en el Excel de referencia.
        - Descripción – Tal como aparece en el Excel de referencia.
        - Vigencia –Tal como aparece en el Excel de referencia.
        - Relevancia – Breve explicación de por qué esta normativa está directamente vinculada con el tema material.
        Es importante que la respuesta venga en el siguiente formato JSON y SOLO me entregues el JSON en la respuesta: {{
            "regulaciones": [
                {
                    "tema_material": "string",
                    "tipo_regulacion": "string",
                    "descripcion": "string",
                    "vigencia": "string",
                    "relevancia": "string"
                }
            ]
        }}
    """
)

prompt_11 = PromptTemplate(
    name="🔹 Prompt 11: Estrategia de Sostenibilidad (Resumen Ejecutivo)",
    template="""
        🔹 Prompt 11: Estrategia de Sostenibilidad (Resumen Ejecutivo)
        Objetivo
        Generar un resumen ejecutivo en un máximo de 2 párrafos que sintetice la estrategia de sostenibilidad recomendada para la empresa, a partir de los 10 temas materiales priorizados en la Materiality Table.
        Instrucciones
        - Utiliza como insumo las acciones marginales, moderadas y estructurales previamente definidas en la Materiality Table para los 10 temas materiales priorizados.
        - El texto debe redactarse como si fuera la recomendación de un consultor experto en sostenibilidad, evitando un tono descriptivo de hechos ya implementados.
        - Asegúrate de mencionar explícitamente que las recomendaciones están basadas en el análisis de doble materialidad realizado.
        - La redacción debe presentar las acciones como pasos estratégicos que la empresa debería seguir:
            - Acciones marginales → recomendaciones inmediatas de ajuste operativo.
            - Acciones moderadas → procesos recomendados a integrar en el mediano plazo.
            - Acciones estructurales → transformaciones de modelo de negocio a largo plazo.
        - Mantén un tono estratégico y ejecutivo, transmitiendo visión integral y ambiciosa, sin listar ni repetir extensamente.
        - El resultado final debe ser conciso, máximo dos párrafos.
        Es importante que la respuesta venga en el siguiente formato JSON y SOLO me entregues el JSON en la respuesta: {{
            "parrafo_1": "string",
            "parrafo_2": "string"
        }}
    """
)