from langchain.prompts import PromptTemplate

# Prompt 1: Contexto organizacional y Sectorial

prompt_1 = PromptTemplate(
    name="🔹 Prompt 1: Contexto organizacional y Sectorial",
    input_variables=["organization_name", "country", "website", "industry", "document"],
    template="""
        Eres un analista experto en sostenibilidad y ESG.
        Debes generar un JSON estructurado y detallado con información contextual de la empresa indicada.
        Esta información servirá como base para el análisis de doble materialidad.

        Datos de entrada:
        - Nombre de empresa: {organization_name}
        - País: {country}
        - Website: {website}
        - Industria de análisis: {industry}
        - Documento adjunto (de estar disponible): {document}

        Instrucciones obligatorias:
        1. Devuelve únicamente un JSON válido. No incluyas títulos, explicaciones, comentarios ni texto adicional fuera del JSON.
        2. Usa información pública o inferida para completar cada campo con **detalle suficiente y específico**.
        3. Si no hay información exacta disponible, infiere una descripción razonable y completa basada en el sector.
        4. Cada campo debe cumplir estrictamente con un **mínimo de caracteres**:
           - nombre_empresa → mínimo 30 caracteres
           - pais_operacion → mínimo 40 caracteres
           - industria → mínimo 60 caracteres
           - tamano_empresa → mínimo 40 caracteres
           - ubicacion_geografica → mínimo 100 caracteres
           - modelo_negocio → mínimo 150 caracteres
           - cadena_valor → mínimo 200 caracteres
           - actividades_principales → mínimo 200 caracteres
           - madurez_esg → mínimo 100 caracteres
           - stakeholders_relevantes → mínimo 200 caracteres
        5. Evita respuestas genéricas.

        Formato específico para "pais_operacion":
        - Debe **comenzar exactamente** por: "{country}. "
        - Después describe la modalidad operativa (no geografía ni turismo del país).

        Además, debes agregar un campo obligatorio:
        - **sector_sp**: Sector S&P que mejor corresponde a la empresa, según tu análisis contextual.

        Formato de salida obligatorio (sin texto adicional):

        {{
          "nombre_empresa": "string",
          "pais_operacion": "string",
          "industria": "string",
          "tamano_empresa": "string",
          "ubicacion_geografica": "string",
          "modelo_negocio": "string",
          "cadena_valor": "string",
          "actividades_principales": "string",
          "madurez_esg": "string",
          "stakeholders_relevantes": "string",
        }}
    """
)


prompt_2 = PromptTemplate(
    name="🔹 Prompt 2: Identificación de Impactos (basado en S&P)",
    template="""

        INSTRUCCIONES GLOBALES DE FORMATO
        - Devuelve únicamente un JSON válido.
        - No incluyas texto antes ni después del JSON.
        - Escapa comillas internas como: \\"texto\\".

        🎯 Objetivo  
        Extraer del PDF “materiality_map_sp_nuevo.pdf” **todas las filas** asociadas al sector S&P que coincida con la industria:
        **{industry}**

        🧩 INSTRUCCIONES ESTRICTAS
        1. Usa file_search para buscar el PDF “materiality_map_sp_nuevo.pdf”.  
           Debes leer el contenido completo del PDF.  
        2. Trae exactamente todas las filas cuyo sector tenga el mismo valor a: **{industry}**  
           (coincidencia literal o parcial, sin inventar nada).  
        3. Extrae exactamente los valores del PDF:
           - sector  
           - tema  
           - materialidad_financiera  
           - valor_materialidad_financiera  
           - Riesgos  
           - Oportunidades  
           - accion_marginal  
           - accion_moderada  
           - accion_estructural  
        4. Respeta literalmente el texto del PDF.  
           ⛔ No inventes  
           ⛔ No completes con lógica  
           ⛔ No resumas  
           ⛔ No rellenes campos  
        5. Trae **todas** las filas del sector.  
        6. Si ya no hay más filas, agrega `"exhausted": true`.  

        📦 Estructura de salida obligatoria:
        {{
            "materiality_table": [
                {{
                    "sector": "string",
                    "tema": "string",
                    "materialidad_financiera": "string (Baja, Media o Alta)",
                    "valor_materialidad_financiera": "number (0, 2.5 o 5)",
                    "Riesgos": "string",
                    "Oportunidades": "string",
                    "accion_marginal": "string",
                    "accion_moderada": "string",
                    "accion_estructural": "string"
                }}
            ],
            "exhausted": false
        }}

        IMPORTANTE:
        - Usa EXCLUSIVAMENTE el PDF.  
        - Si no encuentras filas para {industry}, devuelve:
          {{"error": "no_data_found", "materiality_table": [], "exhausted": true}}
        - No inventes nada en ningún caso.
    """
)



prompt_2_1 = PromptTemplate(
    name="🔹 Prompt 2.1: Continuación de la Identificación de Impactos (basado en S&P)",
    input_variables=["prev_rows"],
    template="""
    ⚠️ INSTRUCCIONES GLOBALES DE FORMATO (OBLIGATORIAS)
    Devuelve únicamente un JSON válido.
    No incluyas texto antes ni después del JSON.
    No uses markdown ni explicaciones.
    Si usas comillas internas, escápalas así: \"texto\".
    Asegúrate de que todas las comas, llaves y valores sean válidos JSON.
    Si el JSON no es válido, regenera la respuesta antes de enviarla.

    --- CONTEXTO ---
    Ya tienes una tabla parcial de materialidad con este contenido previo:
    {prev_rows}

    Esta tabla previa ya contiene una lista de filas bajo la clave "materiality_table".
    Cada fila tiene, al menos, la columna "tema".

    --- OBJETIVO ---
    Continuar la tabla generada anteriormente SOLO si todavía quedan temas/materialidades relevantes que no hayan sido cubiertos.
    
    - Revisa cuidadosamente los "tema" ya presentes en la tabla previa.
    - NO debes repetir ni duplicar ningún tema ni ninguna fila equivalente.
    - Si consideras que el prompt anterior ya trajo todas las filas relevantes posibles (es decir, no hay más temas nuevos que agregar),
      entonces NO agregues nada más y devuelve exactamente:
      {
        "materiality_table": []
      }

    --- REGLAS DE CANTIDAD ---
    - Si identificas que todavía hay temas adicionales relevantes:
      - Genera al menos 5 filas nuevas, intentando no superar 15 filas nuevas.
      - Mantén la coherencia con el sector y estilo del Prompt 2.
    - Nunca dupliques un "tema" que ya esté en las filas previas.
    - Si al intentar generar nuevas filas descubres que terminarías repitiendo temas, devuelve igualmente:
      {
        "materiality_table": []
      }

    --- FORMATO OBLIGATORIO ---
    Devuelve SIEMPRE un JSON con esta forma:

    {
        "materiality_table": [
            {
                "sector": "string",
                "tema": "string",
                "materialidad_financiera": "string (Baja, Media o Alta)",
                "valor_materialidad_financiera": "number (0, 2.5 o 5)",
                "Riesgos": "string",
                "Oportunidades": "string",
                "accion_marginal": "string",
                "accion_moderada": "string",
                "accion_estructural": "string"
            }
        ]
    }

    Requisitos adicionales:
    - Usa exactamente las claves anteriores, incluyendo mayúsculas en "Riesgos" y "Oportunidades".
    - "sector" debe ser consistente con el sector de la tabla previa.
    - No inventes sectores que no sean coherentes con el análisis inicial.
    - Respeta el mismo tono, estructura y nivel de detalle que en las filas ya existentes.
    """
)


# Prompt 3: Análisis de doble materialidad
prompt_3 = PromptTemplate(
    name="🔹 Prompt 3: Evaluación de Impactos",
   template="""
    ⚠️ INSTRUCCIONES GLOBALES DE FORMATO (OBLIGATORIAS)

    Devuelve únicamente un JSON válido.
    No incluyas texto antes ni después del JSON.
    No incluyas explicaciones, títulos, markdown, comentarios ni caracteres adicionales.
    Si usas comillas internas, escápalas así: \"texto\".
    No uses saltos de línea innecesarios dentro de valores extensos.
    Si detectas que el JSON no es válido, regenera automáticamente la respuesta antes de enviarla.
    Prohibido usar cualquier tipo de markdown (incluyendo triple backticks, #, negritas, etc.).
    Asegúrate de que todas las comas, llaves y corchetes estén correctamente colocados.
    Si no puedes cumplir el formato, vuelve a generar la respuesta hasta que sea válida.


    --- INSTRUCCIONES ESPECÍFICAS DEL PROMPT ---

    Analiza los temas materiales identificados en la Materiality Table y agrega las siguientes columnas:

    - tipo_impacto: Positivo o negativo
    - potencialidad_impacto: Real o potencial
    - horizonte_impacto: Corto o largo plazo
    - intencionalidad_impacto: Intencionado o no intencionado
    - penetracion_impacto: Reversible o irreversible
    - grado_implicacion: Directo o indirecto

    Además, debes incluir un campo adicional al final llamado "resumen_sector", que debe ser un párrafo conciso (mínimo 50 caracteres) explicando la selección sectorial S&P.

    Formato obligatorio de salida:
    {
        "materiality_table": [
            {
                "sector": "string",
                "tema": "string",
                "materialidad_financiera": "string",
                "valor_materialidad_financiera": "decimal",
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
        ],
        "resumen_sector": "string"
    }

    IMPORTANTE:
    - Tiene que tener la misma cantidad de columnas que en el prompt 2.
    - No elimines columnas previas.
    - No devuelvas texto adicional ni explicaciones fuera del JSON.
    - "resumen_sector" debe justificar brevemente el sector elegido.
    - Asegúrate de que el JSON sea válido y contenga todas las comas necesarias.
    - No uses decimales donde deben ir enteros.
    """
)


# Prompt 4: Análisis de doble materialidad
prompt_4 = PromptTemplate(
    name="🔹 Prompt 4: Evaluación de Impactos (doble materialidad)",
   template="""
    ⚠️ INSTRUCCIONES GLOBALES DE FORMATO (OBLIGATORIAS)

    Devuelve únicamente un JSON válido.
    No incluyas texto antes ni después del JSON.
    No incluyas explicaciones, títulos, markdown, comentarios ni caracteres adicionales.
    Si usas comillas internas, escápalas así: \"texto\".
    No uses saltos de línea innecesarios dentro de valores extensos.
    Si detectas que el JSON no es válido, regenera automáticamente la respuesta antes de enviarla.
    Prohibido usar cualquier tipo de markdown (incluyendo triple backticks, #, negritas, etc.).
    Asegúrate de que todas las comas, llaves y corchetes estén correctamente colocados.
    Si no puedes cumplir el formato, vuelve a generar la respuesta hasta que sea válida.


    --- INSTRUCCIONES ESPECÍFICAS DEL PROMPT ---

        Objetivo:
        Priorizar los impactos asociados a cada tema material utilizando una evaluación combinada de criterios ESG y financieros.

        Instrucciones:
        A la tabla generada anteriormente (Materiality Table), manteniendo toda su información, agrega las siguientes 4 columnas y asigna el valor correspondiente a cada tema material con base en su impacto:

        - Gravedad – Evalúa la severidad del impacto negativo. (0 a 5)
        - Probabilidad – Evalúa qué tan probable es que ocurra el impacto. (0 a 5)
        - Alcance – Evalúa qué tan amplio es el impacto. (0 a 5)

        - Materialidad ESG – Suma: valor_materialidad_financiera + gravedad + probabilidad + alcance


        📦 Formato de salida obligatorio:
        {
            "materiality_table": [
                {
                    "sector": "string",
                    "tema": "string",
                    "tipo_impacto": "string",
                    "materialidad_financiera": "string (Baja, Media o Alta)",
                    "potencialidad_impacto": "string",
                    "horizonte_impacto": "string",
                    "intencionalidad_impacto": "string",
                    "penetracion_impacto": "string",
                    "grado_implicacion": "string",
                    "gravedad": number,
                    "probabilidad": number,
                    "alcance": number,
                    "materialidad_esg": number
                }
            ],
        }

        ⚠️ Importante:
        - Tiene que tener la misma cantidad de columnas que en el prompt 2.
        - No elimines columnas previas.
        - No devuelvas texto adicional ni explicaciones fuera del JSON.

        ⚙️ Verificación final:
        Asegúrate de que el JSON sea válido y contenga todas las comas necesarias.
        No uses puntos decimales en campos enteros.
    """
)


#Prompt 5: Priorización de Temas
prompt_5 = PromptTemplate(
    name="🔹 Prompt 5: Priorización de Temas",
   template="""
    ⚠️ INSTRUCCIONES GLOBALES DE FORMATO (OBLIGATORIAS)

    Devuelve únicamente un JSON válido.
    No incluyas texto antes ni después del JSON.
    No incluyas explicaciones, títulos, markdown, comentarios ni caracteres adicionales.
    Si usas comillas internas, escápalas así: \"texto\".
    No uses saltos de línea innecesarios dentro de valores extensos.
    Si detectas que el JSON no es válido, regenera automáticamente la respuesta antes de enviarla.
    Prohibido usar cualquier tipo de markdown (incluyendo triple backticks, #, negritas, etc.).
    Asegúrate de que todas las comas, llaves y corchetes estén correctamente colocados.
    Si no puedes cumplir el formato, vuelve a generar la respuesta hasta que sea válida.


    --- INSTRUCCIONES ESPECÍFICAS DEL PROMPT ---

        Objetivo:
        Definir los 10 temas materiales prioritarios a partir de la evaluación de impactos previamente realizada.

        Instrucciones:
         - Ordena la tabla de la Materiality Table de mayor a menor según el valor de la columna “Materialidad ESG”, sin modificar ningún valor o contenido existente en las filas.
         - Identifica los 10 temas con mayor puntaje total, los cuales serán considerados como los temas materiales priorizados del análisis.
         - Para facilitar su seguimiento en los siguientes pasos, puedes destacarlos visualmente o etiquetarlos como "Tema Material" en una nueva columna. 

        Formato obligatorio de salida:
        {
            "materiality_table": [
                {
                    "sector": "string",
                    "tema": "string",
                    "tipo_impacto": "string",
                    "materialidad_financiera": "string (Baja, Media o Alta)",
                    "potencialidad_impacto": "string",
                    "horizonte_impacto": "string",
                    "intencionalidad_impacto": "string",
                    "penetracion_impacto": "string",
                    "grado_implicacion": "string",
                    "gravedad": number,
                    "probabilidad": number,
                    "alcance": number,
                    "materialidad_esg": number
                }
            ]
        }
    """
)

# Prompt 6: Análisis de doble materialidad
prompt_6 = PromptTemplate(
    name="🔹 Prompt 6: Vínculo con Objetivos de Desarrollo Sostenible (ODS)",
   template="""
    ⚠️ INSTRUCCIONES GLOBALES DE FORMATO (OBLIGATORIAS)

    Devuelve únicamente un JSON válido.
    No incluyas texto antes ni después del JSON.
    No incluyas explicaciones, títulos, markdown, comentarios ni caracteres adicionales.
    Si usas comillas internas, escápalas así: \"texto\".
    No uses saltos de línea innecesarios dentro de valores extensos.
    Si detectas que el JSON no es válido, regenera automáticamente la respuesta antes de enviarla.
    Prohibido usar cualquier tipo de markdown (incluyendo triple backticks, #, negritas, etc.).
    Asegúrate de que todas las comas, llaves y corchetes estén correctamente colocados.
    Si no puedes cumplir el formato, vuelve a generar la respuesta hasta que sea válida.


    --- INSTRUCCIONES ESPECÍFICAS DEL PROMPT ---

        Objetivo:
        Relacionar los 10 temas materiales priorizados con el Objetivo de Desarrollo Sostenible (ODS), su meta e indicador más directamente asociados.

        Instrucciones:
        1. Mantén intacta la tabla de la Materiality Table: no elimines columnas ni modifiques su contenido existente.
        2. Agrega estas columnas al final:
            - "ods" – El Objetivo de Desarrollo Sostenible más directamente relacionado con el tema material.
            - "meta_ods" – La meta de ese ODS más estrechamente alineada semánticamente con el tema.
        3. Utiliza únicamente el documento “lista_ods_adaptia.pdf” como fuente de información. 
            - "indicador_ods" – El indicador correspondiente a la meta seleccionada (misma fila del documento de referencia).
        4. Para cada uno de los 10 temas materiales (etiquetados como “Material” en la tabla):
            - Revisa los 17 ODS completos y selecciona el que tenga la relación más fuerte y directa con el tema.
            - Una vez elegido el ODS, revisa todas sus metas y selecciona la más directamente vinculada al tema.
            - Copia también el indicador que corresponde a esa meta (misma fila del documento de referencia).
        5.  Para los temas que no están priorizados como “Material”:
        - No los elimines.
        - Completa las tres nuevas columnas con “NA” para indicar que no fueron analizados en esta dimensión.

        Nota:
        El vínculo debe ser único por tema (solo un ODS, una meta y un indicador), priorizando siempre la opción más específica y semánticamente cercana.

        Formato obligatorio de salida:
        {
            "materiality_table": [
                {
                    "tema": "string",
                    "prioridad": "string",
                    "meta_ods": "string",
                    "indicador_ods": "string"
                }
            ]
        }
        Importante:
        - En prioridad me tenes que traer de la misma fila seleccionada todo lo que dice sin resumir en Ogjetivo de desarrollo sostenible
        - En meta_ods traeme tal cual dice en la fuente de informacion sin resumir nada.
        . En indicador_ods trame tal cual dice en la fuente de informacion sin resumir nada y que sea de la mima fila que meta_ods.
    """
)


prompt_7 = PromptTemplate(
    name="🔹 Prompt 7: Mapeo de Contenidos GRI",
    template="""
    --- INSTRUCCIONES ESPECÍFICAS DEL PROMPT ---

    . Antes de comenzar, usa exclusivamente el PDF: “lista_adaptia_gri_blocks.pdf”.
    . No inventes ningún contenido.
    . Recibes como entrada la tabla JSON generada por Prompt 5 (materiality_table_priorizada).

    Objetivo:
    A partir de los 10 temas materiales priorizados en Prompt 5 (campo: "tema"),
    realizar una búsqueda exhaustiva en el PDF y recuperar TODOS los contenidos GRI relacionados.

    Lo que recibes (ejemplo estructural):
    {
        "materiality_table_priorizada": [
            { "tema": "Riesgo climático físico", ... },
            { "tema": "Protección de la privacidad", ... },
            ...
            (10 temas)
        ]
    }

    Alcance:
    - Procesar exactamente los 10 temas materiales recibidos.
    - Por cada tema, buscar coincidencias en la columna A del PDF (Tema S&P).
    - La búsqueda debe ser:
        • NO sensible a mayúsculas/minúsculas  
        • por coincidencia total o parcial  
        • permite buscar por palabras clave o fragmentos del tema  
    - Extraer TODAS las filas coincidentes (no un máximo de 1), incluso si son 20, 30 o más.

    Estructura del PDF (columnas):
        A → Tema S&P  
        B → Estándar GRI  
        C → # de Contenido  
        D → Contenido  
        E → Requerimiento  

    Instrucciones:
    1. Itera cada uno de los 10 temas recibidos en materiality_table_priorizada.
    2. Para cada tema:
        - Buscar en TODAS las filas del PDF.
        - Identificar cuales filas tienen coincidencias con el texto del “tema”.
        - Extraer columnas B, C, D y E.
        - NO modificar el texto, respetar 100% lo que dice el PDF.
    3. Agregar todos los resultados a un solo arreglo final
       (sin repetir filas idénticas).
    4. Verificar que cada uno de los 10 temas tenga al menos una coincidencia.
       Si no hay coincidencias, incluir:
         { "estandar_gri": "no_matches_for_this_topic" }
       para ese tema, pero NO inventar contenido.

    Formato de salida obligatorio:
    {
        "gri_mapping": [
            {
                "estandar_gri": "string",
                "numero_contenido": "string",
                "contenido": "string",
                "requerimiento": "string"
            }
        ]
    }

    Control de calidad:
    - Revisar todas las filas (122 o más, según PDF).
    - Respetar texto EXACTO.
    - Eliminar duplicados.
    - Debe haber resultados para los 10 temas.
    """
)


prompt_8 = PromptTemplate(
    name="🔹 Prompt 8: Mapeo SASB Sectorial",
    template="""

    --- INSTRUCCIONES ESPECÍFICAS DEL PROMPT (RESPONDE SOLO JSON) ---

    Objetivo:
    A partir del SECTOR S&P recibido, seleccionar EXACTAMENTE UNA industria SASB,
    utilizando EXCLUSIVAMENTE la columna “industria” del archivo:

        ➜ “equivalencia_sasbs_adaptia.pdf”

    IMPORTANTE:
    - El valor devuelto en “industria_sasb” debe coincidir EXACTAMENTE con
      el contenido de la columna “industria”.
    - NO inventes variaciones, NO traduzcas, NO infieras nada.
    - NO uses similitud semántica.
    - Si el sector S&P coincide con varias filas, elige SOLO la coincidencia exacta.
    - Máximo 1 industria SASB.

    Entrada:
        sector_s&p_recibido = "{industry}"

    Formato obligatorio de salida (SOLO JSON):
    {{
        "mapeo_sasb": [
            {{
                "sector_s&p": "{industry}",
                "industria_sasb": "VALOR EXACTO DE LA COLUMNA industria"
            }}
        ]
    }}
    """
)


prompt_9 = PromptTemplate(
    name="🔹 Prompt 9: Tabla SASB Sectorial",
    template="""

    --- INSTRUCCIONES ESPECÍFICAS DEL PROMPT (RESPONDE SOLO JSON) ---

    🔹 Prompt 9: Tabla SASB Sectorial  
    Objetivo:
    Extraer **TODAS** las paginas cuya "INDUSTRIA" coincida con:

    👉 **{industry}**

    Archivo a usar obligatoriamente: **“list_sasb_adaptia.pdf”**

    REGLAS IMPORTANTES (SEGUIR AL 100%):
    - Coincidencia **EXACTA** (sensible a espacios, acentos y mayúsculas).
    - Si NO coincide exactamente, **NO** devuelvas nada.
    - NO utilices coincidencias parciales, semánticas ni aproximadas.
    - NO traduzcas, NO resumas, NO inventes textos.
    - Todo debe estar **en español**, exactamente como en el PDF.
    - Incluye absolutamente **todas** las paginas donde la "INDUSTRIA"
      sea exactamente igual a **{industry}**.
    - NO mezcles otras industrias (ej: no mezclar hardware si no coincide).

    Formato de salida OBLIGATORIO (SOLO JSON):
    {{
        "tabla_sasb": [
            {{
                "industria": "string",
                "tema": "string",
                "parametro_contabilidad": "string",
                "categoria": "string",
                "unidad_medida": "string",
                "codigo": "string"
            }}
        ]
    }}
    Importante:
    - Una vez que termines verifica en el pdf si traes todos los registros de esa industria, no puede faltar ninguna.

    """
)



#Prompt 10: Vinculación Normativa por Tema Material (GAIL)
prompt_10 = PromptTemplate(
    name="🔹 Prompt 10: Vinculación Normativa por Tema Material (GAIL)",
   template="""
    --- INSTRUCCIONES ESPECÍFICAS DEL PROMPT ---

        Objetivo:
        Identificar regulaciones nacionales/sectoriales relevantes para los 10 temas materiales priorizados.

        Instrucciones:
        - Usa “mapeo_regulatorio_adaptia.pdf”.
        - Filtra la información por el país de operación analizado (según resultado del prompt #1).
        - Para cada uno de los 10 temas materiales priorizados:
            1. Revisa todas las regulaciones disponibles para el país siendo analizado.
            2. Evalúa la coincidencia semántica entre nombre del tema material y la descripción de cada normativa (Descripción).
            3. Selecciona SOLO una normativa, la de mayor relevancia para este tema.
        - Asegúrate de cubrir todos los temas materiales priorizados.
        - No inventes palabras, no recortes palabras, solo saca la informacion completa obtenida del pdf.

        Criterios de relevancia:
        - Mayor alineación temática entre el nombre del tema y la normativa.
        - Especificidad: prefiere regulaciones que hagan referencia directa al área de impacto (ej. emisiones, privacidad de datos, residuos).
        - Si varias normativas empatan en relevancia, selecciona la más reciente o de mayor aplicabilidad nacional.


        Formato obligatorio:
        {
            "regulaciones": [
                {
                    "tipo_regulacion": "string",
                    "descripcion": "string",
                    "vigencia": "string",
                }
            ]
        }
    """
)


prompt_11 = PromptTemplate(
    name="🔹 Prompt 11: Estrategia de Sostenibilidad (Resumen Ejecutivo)",
   template="""
    ⚠️ INSTRUCCIONES GLOBALES DE FORMATO (OBLIGATORIAS)

    Devuelve únicamente un JSON válido.
    No incluyas texto antes ni después del JSON.
    No incluyas explicaciones, títulos, markdown, comentarios ni caracteres adicionales.
    Si usas comillas internas, escápalas así: \"texto\".
    No uses saltos de línea innecesarios dentro de valores extensos.
    Si detectas que el JSON no es válido, regenera automáticamente la respuesta antes de enviarla.
    Prohibido usar cualquier tipo de markdown (incluyendo triple backticks, #, negritas, etc.).
    Asegúrate de que todas las comas, llaves y corchetes estén correctamente colocados.
    Si no puedes cumplir el formato, vuelve a generar la respuesta hasta que sea válida.


    --- INSTRUCCIONES ESPECÍFICAS DEL PROMPT ---

        🔹 Prompt 11: Estrategia de Sostenibilidad (Resumen Ejecutivo)
        Objetivo:
        Generar un resumen ejecutivo en máximo 2 párrafos, basado en los 10 temas materiales priorizados.

        Instrucciones:
        - Usa el contexto del análisis ESG previo.
        - Redacta como consultor experto.
        - Menciona explícitamente que se basa en análisis de doble materialidad.
        - Relaciona acciones marginales, moderadas y estructurales.
        - Máximo 300 palabras.
        - Tono estratégico, ejecutivo y conciso.

        Formato obligatorio:
        {
            "parrafo_1": "string",
            "parrafo_2": "string"
        }
    """
)
