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
        INSTRUCCIONES GLOBALES DE FORMATO (OBLIGATORIAS)
        Devuelve únicamente un JSON válido.
        No incluyas texto antes ni después del JSON.
        Si usas comillas internas, escápalas así: \\"texto\\".


        Objetivo:  
        Relacionar las actividades de la empresa con temas materiales utilizando los Materiality Maps de S&P y construir la base de la Materiality Table.
        Asegúrate de que todas las comas, llaves y valores sean válidos JSON.

        INSTRUCCIONES ESTRICTAS:
        1. Utilizando la tabla “materiality_map_sp”, identifica ellos sectores S&P en los que opera la empresa (columna BA) tal y como fue definido en el prompt #1.
        2. El análisis debe de realizarse de solamente 1 sector - el que fue definido en el prompt #1.
        3. La tabla debe contener como **mínimo 10 registros (filas)**. Este es un requerimiento obligatorio.Evita repeticiones exactas.
        4. Para ese sector, extrae los temas materiales y sus atributos directamente desde el PDF en exactamente el mismo formato y orden en el que estén en el PDF, sin dejar fuera ningún tema asignado para el sector seleccionado.
        4. **Debes incluir obligatoriamente los tres niveles de materialidad financiera**:
             - Al menos **un conjunto representativo de temas con materialidad financiera "Baja"**,  
             - Al menos **un conjunto representativo con "Media"**,  
             - Y al menos **un conjunto representativo con "Alta"**.  
           No excluyas ninguno de los tres niveles bajo ninguna circunstancia, aunque no aparezcan con la misma frecuencia en la fuente original.
        5. Si tras ampliar no existen más temas disponibles en la fuente original, agrega el campo adicional `"exhausted": true` y devuelve todos los registros disponibles.
        6. Si sí existen más temas, debes completar la tabla hasta llegar a 10 filas. **No devuelvas menos de 10 filas sin `"exhausted": true"`.**
        7. No devuelvas texto explicativo, comentarios ni Markdown. Solo JSON válido.

        Estructura requerida de salida:
            {{
                "materiality_table": [
                    "sector": "string",
                    "tema": "string",
                    "materialidad_financiera": "string (Baja, Media o Alta)",
                    "valor_materialidad_financiera": "decimal (0, 2.5 o 5)",
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
        - No inventes datos, solo trae lo que te pido del PDF "1.materiality_map_sp."
        - Devuelve mas de 10 filas sin excepcion.
        - Mantén el orden exacto de las columnas.
        - No uses sinónimos ni resumas textos de la fuente.
        - **No omitas ningún nivel de materialidad financiera (Baja, Media, Alta).**
        - No devuelvas nada más que el JSON requerido.
    """
)




prompt_2_1 = PromptTemplate(
    name="🔹 Prompt 2.1: Continuación de la Identificación de Impactos (basado en S&P)",
    input_variables=["prev_rows"],
    template="""
    ⚠️ INSTRUCCIONES GLOBALES DE FORMATO (OBLIGATORIAS)
    Devuelve únicamente un JSON válido.
    No incluyas texto antes ni después del JSON.
    Si usas comillas internas, escápalas así: \"texto\".
    Asegúrate de que todas las comas, llaves y valores sean válidos JSON.

    --- INSTRUCCIONES ---
    Continúa la tabla generada anteriormente.
    Ya tienes estas filas previas:
    {prev_rows}

    Genera **al menos 5 filas adicionales**, siguiendo exactamente la misma estructura y estilo.

    Formato obligatorio:
    {{
        "materiality_table": [
            {{
                "sector": "string",
                "tema": "string",
                "materialidad_financiera": "string (Baja, Media o Alta)",
                "valor_materialidad_financiera": "decimal (0, 2.5 o 5)",
                "riesgos": "string",
                "oportunidades": "string",
                "accion_marginal": "string",
                "accion_moderada": "string",
                "accion_estructural": "string"
            }}
        ]
    }}
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

        Además:
        Incluye un campo adicional `resumen_sector` (mínimo 50 caracteres) explicando por qué se seleccionó este sector para la empresa analizada.

        📦 Formato de salida obligatorio:
        {
            "materiality_table": [
                {
                    "sector": "string",
                    "tema": "string",
                    "tipo_impacto": "string",
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
            "resumen_sector": "string"
        }

        ⚠️ Importante:
        - Tiene que tener la misma cantidad de columnas que en el prompt 2.
        - No elimines columnas previas.
        - No devuelvas texto adicional ni explicaciones fuera del JSON.
        - El campo "resumen_sector" debe contener un texto conciso que resuma la justificación sectorial.

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

        🔹 Prompt 5: Priorización de Temas
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

        ⚠️ Importante:
        - Tiene que tener la misma cantidad de columnas que en el prompt 2.
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
        Relacionar los 10 temas materiales priorizados con el ODS, meta e indicador más relevantes.

        . Antes de comenzar, usa el pdf “2._Lista_de_ODS_Adaptia_Noviembre_2025”.
        . No inventes ningún contenido.

        Instrucciones:
        1. Mantén intacta la tabla de la Materiality Table: no elimines columnas ni modifiques su contenido existente.
        2. Agrega estas columnas al final:
            - "ods" – El Objetivo de Desarrollo Sostenible más directamente relacionado con el tema material.
            - "meta_ods" – La meta de ese ODS más estrechamente alineada semánticamente con el tema.
            - "indicador_ods" – El indicador correspondiente a la meta seleccionada (misma fila del documento de referencia).
        3. Para cada uno de los 10 temas materiales (etiquetados como “Material” en la tabla):
            - Revisa los 17 ODS completos y selecciona el que tenga la relación más fuerte y directa con el tema.
            - Una vez elegido el ODS, revisa todas sus metas y selecciona la más directamente vinculada al tema.
            - Copia también el indicador que corresponde a esa meta (misma fila del documento de referencia).
        4. Para los temas NO priorizados:
            - coloca "NA" en las tres columnas nuevas.
        .5 Para los temas que no están priorizados como “Material”:
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


# 🔹 Prompt 7: Mapeo de Contenidos GRI (versión actualizada - Noviembre 2025)
prompt_7 = PromptTemplate(
    name="🔹 Prompt 7: Mapeo de Contenidos GRI",
   template="""
    INSTRUCCIONES GLOBALES DE FORMATO (OBLIGATORIAS)

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

        . Antes de comenzar, usa el pdf “3._Lista_de_Est_ndares_GRI_Adaptia_Noviembre_2025”.
        . No inventes ningún contenido.

        Objetivo:
        Identificar y documentar los contenidos GRI vinculados con los 10 temas materiales priorizados
        en la Materiality Table, utilizando la columna “Tema S&P” como criterio de coincidencia directa.

        Alcance:
        - Trabaja únicamente con los 10 temas materiales priorizados (los de mayor puntaje total).
        - Cada tema material puede vincularse con múltiples contenidos GRI.
        - La tabla de salida debe incluir todas las coincidencias encontradas, sin límite de número de filas.

        Estructura:
        Cada fila contiene:
        - Tema S&P (col A)
        - Estándar GRI (col B)
        - # de Contenido (col C)
        - Contenido (col D)
        - Requerimiento (col E)

        Instrucciones
        - Toma los 10 temas materiales priorizados desde la tabla de materialidad (columna “Tema material”).
        - Para cada tema, revisa las 122 filas del archivo fuente.
        - Identifica todas las filas donde la columna A (Tema S&P) contenga ese tema material, total o parcialmente (búsqueda por palabra o fragmento coincidente, sin distinguir mayúsculas/minúsculas).
        - Extrae las columnas B, C, D y E de todas las filas coincidentes.
        - No modifiques el texto ni el formato original.
        - No renombres las columnas.
        - Repite este proceso para los 10 temas materiales.


        Formato obligatorio de salida:
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

        Salida esperada:
        - Genera una tabla con las siguientes columnas, en el mismo orden y nombres exactos del archivo fuente:
          | Estándar GRI | # de Contenido | Contenido | Requerimiento |
        - Cada fila corresponde a un contenido GRI identificado como vinculado a alguno de los temas materiales.
        - Incluye todas las coincidencias encontradas (pueden existir repeticiones entre temas).
        - No agregues columnas ni resúmenes adicionales.

        Control de calidad:
        Antes de cerrar, verifica que:
        - Todos los 10 temas materiales tienen al menos una coincidencia.
        - No se omitieron filas relevantes (la búsqueda revisó las 122 filas del archivo).
        - El texto de las columnas B–E se copió exactamente como aparece en el archivo fuente.
        - Si hay resultados compartidos entre varios temas, elimina los duplicados y solamente manten el resultado una vez. 

    """
)


#Prompt 8: Mapeo SASB Sectorial
prompt_8 = PromptTemplate(
    name="🔹 Prompt 8: Mapeo SASB Sectorial",
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

        🔹 Prompt 8: Mapeo SASB Sectorial  
        Objetivo:
        Identificar los temas e indicadores SASB relevantes para una industriaa asociada.

        Instrucciones:
        - Usa el documento “4._Equivalencia_SASB_S_P_Noviembre_2025”.
        - Identifica las industrias SASB equivalentes a los sectores S&P seleccionados previamente para la empresa.
        - Para cada sector S&P identificado, selecciona una sola industria SASB. Si hay más de una industria equivalente, selecciona la más cercana o representativa según la tabla de equivalencias y el contexto organizacional.
        - El resultado final debe incluir un máximo de una2 industrias SASB.
        - No inventes industrias adicionales.
        - No modifiques los nombres del archivo fuente.

        Formato obligatorio de salida:
        {
            "mapeo_sasb": [
                {
                    "sector_s&p": "string",
                    "industria_sasb": "string"
                }
            ]
        }
    """
)

#Prompt 9: Tabla SASB Sectorial
prompt_9 = PromptTemplate(
    name="🔹 Prompt 9: Tabla SASB Sectorial",
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

        🔹 Prompt 9: Tabla SASB Sectorial
        Objetivo:
        Detallar todos los temas, métricas y códigos SASB aplicables a las industrias seleccionadas previamente.

        Instrucciones:
        Utilizando el documento “5._Lista_de_Est_ndares_SASB__Noviembre_2025”, identifica **todas las filas correspondientes** a las industrias SASB relevantes definidas en el paso anterior (máximo 2 industrias).

        Instrucciones:
        - Incluye **todas** las filas relevantes.
        - NO limites la respuesta a un número específico de filas.
        - No agrupes ni combines registros.
        - Copia EXACTAMENTE los textos de la fuente.
        - No elimines columnas.
        - Si hay muchos indicadores → la tabla debe ser extensa.

        📦 Formato obligatorio:
        {
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
        }
        Importante:
        - Extrae los datos directamente del archivo, sin modificar su redacción ni estructura. Incluye todas las filas relevantes para lacada industria SASB seleccionada.
        
    """
)


#Prompt 10: Vinculación Normativa por Tema Material (GAIL)
prompt_10 = PromptTemplate(
    name="🔹 Prompt 10: Vinculación Normativa por Tema Material (GAIL)",
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
        Identificar regulaciones nacionales/sectoriales relevantes para los 10 temas materiales priorizados.

        Instrucciones:
        - Usa “6._Mapeo_Regulatorio_LATAM_GAIL_Noviembre_2025”.
        - Filtra la información por el país de operación analizado (según resultado del prompt #1).
        - Para cada uno de los 10 temas materiales priorizados:
            1. Revisa todas las regulaciones disponibles para el país siendo analizado.
            2. Evalúa la coincidencia semántica entre nombre del tema material y la descripción de cada normativa (columna D - Descripción).
            3. Selecciona SOLO una normativa, la de mayor relevancia para este tema.
        - Asegúrate de cubrir todos los temas materiales priorizados.

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
