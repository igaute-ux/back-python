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
        2. NO uses Code Interpreter ni ejecutes código Python ni intentes abrir archivos adjuntos. 
        Ignora cualquier archivo asociado al thread y responde solo usando texto generado.
        3. Usa información pública o inferida para completar cada campo con **detalle suficiente y específico**.
        4. Si no hay información exacta disponible, infiere una descripción razonable y completa basada en el sector.
        5. Cada campo debe cumplir estrictamente con un **mínimo de palabras**:
           - nombre_empresa → mínimo 100 palabras
           - pais_operacion → mínimo 100 palabras
           - industria → mínimo 100 palabras
           - tamano_empresa → mínimo 100 palabras
           - ubicacion_geografica → mínimo 100 palabras
           - modelo_negocio → mínimo 50 palabras
           - cadena_valor → mínimo 300 palabras
           - actividades_principales → mínimo 300 palabras
           - madurez_esg → mínimo 300 palabras
           - stakeholders_relevantes → mínimo 100 palabras
        5. Evita respuestas genéricas.

        Formato específico para "pais_operacion":
        - Debe **comenzar exactamente** por: "{country}. "
        - Después describe la modalidad operativa (no geografía ni turismo del país).

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
        INSTRUCCIÓN OBLIGATORIA (NO IGNORAR)
        Ejecuta ESTE código EXACTO con Code Interpreter:

        ```python
        import pandas as pd
        import os
        import unicodedata
        import re
        import json

        # Definir el valor de "industry" aquí
        industry_value = "{industry}"

        # Mostrar archivos disponibles
        available_files = os.listdir("/mnt/data")
        if not available_files:
            raise Exception("No se encontraron archivos en el directorio.")

        # Detectar automáticamente el archivo Excel cargado
        excel_found = None
        for f in available_files:
            if f.endswith(".xlsx") or f.endswith(".xls"):
                excel_found = f
                break

        if excel_found is None:
            raise Exception("❌ No se encontró ningún archivo Excel dentro de /mnt/data")

        # Cargar la hoja "ROI Final"
        df = pd.read_excel("/mnt/data/" + excel_found, sheet_name="ROI Final")

        # Normalización del texto
        def normalize_text(s):
            if not isinstance(s, str):
                s = str(s)
            s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
            s = s.replace("\\xa0", " ").replace("\\u200b", "")
            s = re.sub(r"\\s+", " ", s)
            return s.strip().lower()

        # Normalizar sectores
        df["Sector_norm"] = df["Sector"].apply(normalize_text)
        target = normalize_text(industry_value)

        # Filtrar filas
        df_result = df[df["Sector_norm"] == target]

        # Quitar columna de Adaptia si existe
        if "Código Adaptia" in df_result.columns:
            df_result = df_result.drop(columns=["Código Adaptia"])

        # Convertir a JSON
        json_data = df_result.to_dict(orient="records")

        # Formatear la salida
        result_json = {{
            "materiality_table": json_data,
            "exhausted": len(df_result) == 0
        }}

        # Imprimir SOLO el JSON final
        print(json.dumps(result_json))
        ```

        Usa json_data como materiality_table.
        - NO inventes textos
        - NO completes valores
        - NO traduzcas nada
        - NO respondas sin ejecutar ese código

        OBJETIVO
        Devolver TODAS las filas donde `Sector` sea exactamente:
        **{industry}**

        COLUMNAS OBLIGATORIAS (tomadas literalmente del Excel):
        - Sector
        - Temas
        - Materialidad Financiera
        - Valor materialidad financiera
        - Riesgos
        - Oportunidades
        - Acción inicial
        - Acción moderada
        - Acción estructural

        NO incluir columna: "Código Adaptia"

        FORMATO DE SALIDA JSON (EJEMPLO):
        {{
            "materiality_table": [
                {{
                    "sector": "string",
                    "tema": "string",
                    "materialidad_financiera": "string",
                    "valor_materialidad_financiera": 0,
                    "Riesgos": "string",
                    "Oportunidades": "string",
                    "accion_inicial": "string",
                    "accion_moderada": "string",
                    "accion_estructural": "string"
                }}
            ],
            "exhausted": false
        }}
    """
)


# Prompt 3: Análisis de doble materialidad
prompt_3 = PromptTemplate(
    name="🔹 Prompt 3: Evaluación de Impactos",
   template="""


    --- INSTRUCCIONES ESPECÍFICAS DEL PROMPT ---

    ⚠️ OBLIGACIÓN CRÍTICA:
    La cantidad de filas de "materiality_table" debe ser EXACTAMENTE la misma que la tabla generada en el Prompt 2.
    ❗ No elimines filas.
    ❗ No agregues filas nuevas.
    ❗ No reordenes filas.
    ❗ Cada fila debe corresponder 1:1 con la fila original del Prompt 2.

    Analiza los temas materiales identificados en la Materiality Table y agrega las siguientes columnas:

    - tipo_impacto: Positivo o negativo
    - potencialidad_impacto: Real o potencial
    - horizonte_impacto: Corto o largo plazo
    - intencionalidad_impacto: Intencionado o no intencionado
    - penetracion_impacto: Reversible o irreversible
    - grado_implicacion: Directo o indirecto

    Además, debes incluir un campo adicional al final llamado "resumen_sector", que debe ser un párrafo conciso (mínimo 50 caracteres) explicando la selección sectorial S&P.

    Formato obligatorio de salida:
    {{
        "materiality_table": [
            {{
                "sector": "string",
                "tema": "string",
                "materialidad_financiera": "string",
                "valor_materialidad_financiera": "0",
                "tipo_impacto": "string",
                "potencialidad_impacto": "string",
                "horizonte_impacto": "string",
                "intencionalidad_impacto": "string",
                "penetracion_impacto": "string",
                "grado_implicacion": "string"
            }}
        ],
        "resumen_sector": "string"
    }}

    IMPORTANTE:
    - Devuelve EXCLUSIVAMENTE el bloque <JSON>...</JSON>.
    - No incluyas bloques ```json ni ```python.
    - No expliques nada fuera del JSON.
    """
)


# Prompt 4: Análisis de doble materialidad
prompt_4 = PromptTemplate(
    name="🔹 Prompt 4: Evaluación de Impactos (doble materialidad)",
    template="""

    --- INSTRUCCIONES ESPECÍFICAS DEL PROMPT ---

    Objetivo:
    Priorizar los impactos asociados a cada tema material utilizando una evaluación combinada de criterios ESG y financieros.

    ⚠️ OBLIGACIÓN CRÍTICA:
    La cantidad de filas de "materiality_table" debe ser EXACTAMENTE la misma que la tabla generada en el Prompt 2.
    ❗ No elimines filas.
    ❗ No agregues filas nuevas.
    ❗ No reordenes filas.

    A la tabla generada anteriormente (Materiality Table), manteniendo toda su información, agrega las siguientes 4 columnas:

        - gravedad (0 a 5)
        - probabilidad (0 a 5)
        - alcance (0 a 5)
        - materialidad_esg = valor_materialidad_financiera + gravedad + probabilidad + alcance

    📦 Formato de salida obligatorio:
    {{
        "materiality_table": [
            {{
                "sector": "string",
                "tema": "string",
                "materialidad_financiera": "string",
                "valor_materialidad_financiera": "0",
                "tipo_impacto": "string",
                "potencialidad_impacto": "string",
                "horizonte_impacto": "string",
                "intencionalidad_impacto": "string",
                "penetracion_impacto": "string",
                "grado_implicacion": "string"
                "gravedad": number,
                "probabilidad": number,
                "alcance": number,
                "materialidad_esg": number
            }}
        ]
    }}

    IMPORTANTE:
    - Devuelve EXCLUSIVAMENTE el bloque <JSON>...</JSON>.
    - No incluyas bloques ```json ni ```python.
    - No expliques nada fuera del JSON.
    """
)



#Prompt 5: Priorización de Temas
prompt_5 = PromptTemplate(
    name="🔹 Prompt 5: Priorización de Temas",
   template="""


    --- INSTRUCCIONES ESPECÍFICAS DEL PROMPT ---

        Objetivo:
        Definir los 10 temas materiales prioritarios a partir de la evaluación de impactos previamente realizada.

        Instrucciones:
         - Ordena la tabla de la Materiality Table de mayor a menor según el valor de la columna “Materialidad ESG”, sin modificar ningún valor o contenido existente en las filas.
         - Identifica los 10 temas con mayor puntaje total, los cuales serán considerados como los temas materiales priorizados del análisis.
         - Para facilitar su seguimiento en los siguientes pasos, puedes destacarlos visualmente o etiquetarlos como "Tema Material" en una nueva columna. 
         - Solo trae 10 temas materiales, ni mas ni menos.

        Formato obligatorio de salida:
        {{
            "materiality_table": [
                {{
                "sector": "string",
                "tema": "string",
                "materialidad_financiera": "string",
                "valor_materialidad_financiera": "0",
                "tipo_impacto": "string",
                "potencialidad_impacto": "string",
                "horizonte_impacto": "string",
                "intencionalidad_impacto": "string",
                "penetracion_impacto": "string",
                "grado_implicacion": "string"
                "gravedad": number,
                "probabilidad": number,
                "alcance": number,
                "materialidad_esg": number
                }}
            ]
        }}
        Importante:
        - No incluyas texto antes ni después.
        - No incluyas bloques ```json ni ```python.
        - No expliques nada.
    """
)
prompt_6 = PromptTemplate(
    name="🔹 Prompt 6: Vínculo con Objetivos de Desarrollo Sostenible (ODS)",
    template="""
    INSTRUCCIÓN OBLIGATORIA (NO IGNORAR):

    1. Debes usar Code Interpreter (herramienta de Python) para trabajar.
    2. NO generes imágenes, gráficos, tablas visuales ni archivos adjuntos. 
    3. Tu respuesta FINAL debe ser ÚNICAMENTE un bloque JSON válido rodeado por <JSON> y </JSON>, sin ningún otro texto antes ni después.
    4. Si algo falla, igualmente debes devolver un JSON con la clave "error" y la tabla de materialidad tal como esté en ese momento.

    --- DATOS DE ENTRADA ---

    Recibes la tabla de materialidad priorizada (Prompt 5) en este JSON:

    <INPUT_MATERIALITY>
    {materiality_table_json}
    </INPUT_MATERIALITY>

    IMPORTANTE:
    - El JSON de entrada contiene EXACTAMENTE 10 temas materiales ya priorizados.
    - No debes eliminar ni agregar filas.
    - Esos 10 temas materiales deben terminar con valores completos en las columnas
      "ods", "meta_ods" e "indicador_ods" (no se aceptan "NA" para esos 10 temas,
      salvo que el Excel de ODS esté vacío o no se pueda leer).

    --- TAREA CON CODE INTERPRETER (PYTHON OBLIGATORIO) ---

    Dentro de Code Interpreter debes hacer EXACTAMENTE lo siguiente usando Python:

    1. Cargar el JSON de entrada en un DataFrame de pandas:
       - `materiality_data = ...` a partir de {materiality_table_json}
       - `mat_df = pd.DataFrame(materiality_data["materiality_table"]).copy()`

    2. Asegurarte de que existan las columnas:
       - "ods"
       - "meta_ods"
       - "indicador_ods"
       Si alguna no existe, crearla con el valor por defecto "NA".

    3. Leer el Excel de ODS que ya está montado en /mnt/data:
       - Ruta fija: "/mnt/data/file-LaYZZWTh9mzsG2ni3RkpKm"
       - Usar `ods_df = pd.read_excel("/mnt/data/file-LaYZZWTh9mzsG2ni3RkpKm")` para cargarlo.
       - Considera que la primera fila de `ods_df` contiene encabezados del tipo
         "Objetivo de Desarrollo Sostenible", "Meta", "Indicador".
       - Debes crear SIEMPRE un DataFrame solo con filas de datos (sin encabezados):
           `ods_data = ods_df.iloc[1:].reset_index(drop=True)`
       - A partir de aquí, TODAS las asignaciones y referencias para ODS/meta/indicador
         se deben hacer EXCLUSIVAMENTE usando filas de `ods_data` (nunca la fila 0 de `ods_df`).
       - Usar las TRES PRIMERAS columnas de `ods_data` como:
           - columna 0 → ODS
           - columna 1 → Meta ODS
           - columna 2 → Indicador ODS
       - Está TERMINANTEMENTE PROHIBIDO usar como valores de salida textos que provengan
         de la fila de encabezados, por ejemplo:
         "Objetivo de Desarrollo Sostenible", "Meta", "Indicador".

    4. (Opcional para tu análisis interno, pero recomendado) Convertir `ods_data` a lista:
       - `ods_records = ods_data.to_dict(orient="records")`
       Esto te permite inspeccionar mentalmente todos los ODS, metas e indicadores.

    5. Para cada fila de `mat_df`:

       5.1 Identificar si es un "tema material" usando la columna "Tema Material" o "tema_material".
           - Considerar material si el valor (normalizado a minúsculas) es uno de:
             "tema material", "true", "1", "sí", "si".
           - Si NO es material:
             - Mantener "ods", "meta_ods" e "indicador_ods" como "NA" y pasar a la siguiente fila.

       5.2 ANÁLISIS GUIADO SOBRE LOS 10 TEMAS MATERIALES (USANDO TEXTO DEL EXCEL):

           - Para cada fila MATERIAL:
             - Tomar el texto del tema desde `row["tema"]` o, si no existe, desde `row["temas"]`.
             - Normalizar a minúsculas y quitar espacios extra.
             - Guardar también el tema completo en una variable, por ejemplo `tema_full`.

           - Construir previamente en Python:
             - `ods_col = ods_data.iloc[:, 0].astype(str).str.lower()`
             - `meta_col = ods_data.iloc[:, 1].astype(str).str.lower()`
             - `ind_col = ods_data.iloc[:, 2].astype(str).str.lower()`

           - Definir familias temáticas por palabras clave del tema:

             Ejemplo de lógica (debes implementarla en Python):

           - Definir familias temáticas por palabras clave del tema:

             Ejemplo de lógica (debes implementarla en Python):

             - Si el tema contiene palabras como:
                 "clima", "climático", "climatico", "cambio climático",
                 "emisiones", "emision", "huella de carbono", "co2",
                 "descarbonización", "descarbonizacion"
                   → priorizar ODS relacionados con cambio climático:
                     filas de `ods_data` donde `ods_col.str.contains("objetivo 13", na=False)` sea True
                     (y, en segunda instancia, donde contenga "objetivo 7" o "objetivo 12").

             - Si el tema contiene:
                 "residuo", "residuos", "recicl", "circular", "economía circular",
                 "basura", "envases", "embalajes", "desechos"
                   → priorizar ODS 12 (producción y consumo responsables)
                     (`ods_col.str.contains("objetivo 12", na=False)`),
                     y, si no hay buen match, ODS 11 o 6.

             - Si el tema contiene:
                 "contaminación", "contaminacion", "calidad del aire",
                 "calidad del agua", "polución", "polucion", "emisiones locales",
                 "ruido", "smog"
                   → priorizar ODS 3, 6, 11 o 15 según corresponda,
                     buscando primero "objetivo 3", luego "objetivo 6",
                     luego "objetivo 11" o "objetivo 15" en `ods_col`.

             - Si el tema contiene:
                 "agua", "recursos hídricos", "recursoshidricos",
                 "eficiencia hídrica", "escasez de agua"
                   → priorizar ODS 6 (agua limpia y saneamiento)
                     (`ods_col.str.contains("objetivo 6", na=False)`).

             - Si el tema contiene:
                 "trabajo", "laboral", "condiciones laborales", "derechos laborales",
                 "empleo", "salario", "salarios", "sindicato", "sindicatos",
                 "relaciones laborales", "huelga", "negociación colectiva"
                   → priorizar ODS 8 (trabajo decente y crecimiento económico)
                     (`ods_col.str.contains("objetivo 8", na=False)`),
                     y, en segundo lugar, ODS 5 o 10 cuando se trate
                     de igualdad, discriminación o brechas.

             - Si el tema contiene:
                 "salud", "seguridad de los trabajadores", "seguridad del cliente",
                 "seguridad y salud", "higiene y seguridad", "accidentes",
                 "enfermedades profesionales"
                   → priorizar ODS 3 (salud y bienestar)
                     (`ods_col.str.contains("objetivo 3", na=False)`),
                     y, si el foco es exclusivamente laboral, combinar con ODS 8.

             - Si el tema contiene:
                 "comunidad", "comunidades", "impacto en las comunidades",
                 "desarrollo local", "licencia social", "inclusión", "inclusion",
                 "desigualdad", "pobreza", "vulnerabilidad social"
                   → priorizar ODS 1, 10, 11 o 16:
                     primero busca "objetivo 11" (ciudades y comunidades sostenibles),
                     luego "objetivo 10" o "objetivo 16", y finalmente "objetivo 1"
                     si el foco es pobreza extrema.

             - Si el tema contiene:
                 "biodiversidad", "ecosistema", "ecosistemas", "bosques",
                 "flora", "fauna", "mares", "océanos", "oceanos",
                 "hábitat", "habitat", "deforestación", "deforestacion"
                   → priorizar ODS 14 o 15:
                     primero "objetivo 15" para biodiversidad terrestre,
                     luego "objetivo 14" si el foco es marino/costero.

             - Si el tema contiene:
                 "gobernanza", "gobernanza esg", "ética", "etica",
                 "anticorrupción", "anticorrupcion", "soborno", "transparencia",
                 "denuncias", "whistleblowing", "cumplimiento"
                   → priorizar ODS 16 (paz, justicia e instituciones sólidas),
                     buscando "objetivo 16" en `ods_col`.

             - Si el tema contiene:
                 "innovación", "innovacion", "tecnología", "tecnologia",
                 "infraestructura sostenible", "digitalización", "digitalizacion"
                   → priorizar ODS 9 (industria, innovación e infraestructura)
                     (`ods_col.str.contains("objetivo 9", na=False)`),
                     y, en segundo lugar, ODS 12 si el foco es eco-eficiencia.

             - Si el tema contiene:
                 "privacidad", "datos personales", "ciberseguridad", "ciber",
                 "seguridad de la información", "protección de datos", "proteccion de datos"
                   → priorizar ODS 9 y 16, buscando primero "objetivo 16"
                     (instituciones sólidas, marco normativo) y luego "objetivo 9"
                     (tecnología e infraestructura).

             - Si el tema contiene:
                 "cadena de suministro", "proveedores", "compras responsables",
                 "abastecimiento responsable", "supply chain"
                   → priorizar ODS 8 y 12:
                     primero "objetivo 12" (consumo y producción responsables),
                     luego "objetivo 8" (condiciones laborales en la cadena).

             - Si ninguna de las palabras clave encaja claramente en las familias anteriores:
                   → realiza una búsqueda por coincidencia general en `ods_col`,
                     `meta_col` e `ind_col` usando palabras clave del tema
                     (por ejemplo, términos principales del título del tema),
                     y elige el ODS cuya meta/indicador tenga mayor relación semántica.
                     En todo caso, NUNCA selecciones filas solo por su posición
                     secuencial en `ods_data`; la elección debe basarse siempre
                     en el contenido de texto.

           - Implementación sugerida:

             1) Para cada tema, determina su familia (clima, residuos, salud, trabajo, etc.)
                en base a las palabras clave (usando `in` sobre `tema_full`).

             2) Según la familia, genera un filtro booleano sobre `ods_col`:
                  - por ejemplo `mask = ods_col.str.contains("objetivo 13", na=False)`
                    para clima; o `ods_col.str.contains("objetivo 12", na=False)` para residuos.

             3) Obtén los índices candidatos:
                  `candidate_indices = [i for i, ok in enumerate(mask) if ok]`.

             4) Elige el PRIMER índice de `candidate_indices` que:
                  - no esté ya en `used_indices`, y
                  - cuyo texto de ODS/Meta/Indicador tenga sentido con el tema.
                Si todos los candidatos están usados, puedes usar el siguiente candidato.
                Solo si no hay candidatos para esa familia, busca en otros ODS cercanos
                (por ejemplo, si no hay nada en 13 para clima, intenta con 7 o 12, etc.).

           - Crea un conjunto `used_indices = set()` para registrar qué índices
             de `ods_data` ya fueron asignados a otros temas materiales.

           - Está TERMINANTEMENTE PROHIBIDO:
             - usar patrones tipo `idx = i`, `idx = i + 1`, `idx = i + k` que asignen
               filas consecutivas según la posición del tema en la tabla;
             - ignorar el contenido de las columnas y seleccionar filas solo por orden.

           - Una vez decidido el índice final `idx_definitivo` para el tema:
             - añadirlo a `used_indices`,
             - definir `match_row = ods_data.iloc[idx_definitivo]`.

           - Verificación final OBLIGATORIA:
             - Antes de devolver el resultado, recorre todas las filas MATERIALES de `mat_df`.
             - Si alguna tiene "ods", "meta_ods" o "indicador_ods" en "NA" o vacío:
                 * si `len(ods_data) > 0`, debes forzar una asignación usando cualquier fila
                   de `ods_data` que aún no esté en `used_indices` (y, si no quedan filas
                   libres, reutilizar alguna razonable).
                 * Después de este paso, NINGÚN tema material puede permanecer con "ods",
                   "meta_ods" o "indicador_ods" = "NA", salvo que `ods_data` esté realmente
                   vacío o la lectura del Excel haya fallado.

           d) Asignación final (solo desde `match_row`, SIN inventar textos):
              - A partir de `match_row`, escribir en `mat_df`:
                  - "ods"           = valor literal de la columna 0 de esa fila
                  - "meta_ods"      = valor literal de la columna 1 de esa fila
                  - "indicador_ods" = valor literal de la columna 2 de esa fila
              - Está TERMINANTEMENTE PROHIBIDO usar textos genéricos que no provengan
                de celdas de datos válidas del Excel, como:
                "Objetivo de Desarrollo Sostenible", "Meta", "Indicador",
                u otros placeholders. Solo se permiten valores exactos de celdas de `ods_data`.

    6. Al final:
       - Convertir `mat_df` a lista de registros con `to_dict(orient="records")`.

    --- FORMATO OBLIGATORIO DE SALIDA ---

    Tu respuesta FINAL debe ser **EXACTAMENTE**:
    <JSON>
    {{
      "materiality_table": [
        {{
          ... todas las columnas originales ...,
          "ods": "string",
          "meta_ods": "string",
          "indicador_ods": "string"
        }}
      ]
    }}
    </JSON>

    Condiciones adicionales:
    - NO expliques nada.
    - NO uses bloques ```json ni ```python.
    - NO generes imágenes ni gráficos.
    - NO escribas texto fuera del bloque <JSON>...</JSON>.

    - Para TODOS los temas marcados como materiales ("Tema Material"):
      - El input contiene exactamente 10 temas materiales priorizados, por lo que
        los 10 deben terminar con valores completos en "ods", "meta_ods" e "indicador_ods".
      - NO se permite que "ods", "meta_ods" o "indicador_ods" queden con "NA"
        en esos 10 temas, salvo que el Excel de ODS esté vacío o no se haya podido leer.
      - NO se permite usar como valores de salida textos que sean solo encabezados
        o genéricos como "Objetivo de Desarrollo Sostenible", "Meta" o "Indicador".
        Esos textos deben ser ignorados si aparecen como encabezados.
      - NO se permite asignar la MISMA fila exacta de `ods_data` (mismo ODS, misma meta,
        mismo indicador) a más de un tema material, salvo en el caso extremo en que
        el número de filas de `ods_data` sea menor que 10 y no exista ninguna otra
        opción razonable disponible.

    - Si ocurre algún error (por ejemplo al leer el Excel), devuelve:

    <JSON>
    {{
      "error": "mensaje de error aquí",
      "materiality_table": [ ... tabla tal como esté ... ]
    }}
    </JSON>
    """
)

prompt_8 = PromptTemplate(
    name="🔹 Prompt 8: Mapeo SASB Sectorial",
    template="""
    INSTRUCCIONES OBLIGATORIAS

    1. Debes usar Code Interpreter (herramienta de Python).
    2. NO uses tu conocimiento general ni internet.
    3. SOLO puedes usar el archivo CSV montado en /mnt/data.
    4. La respuesta FINAL debe ser ÚNICAMENTE un JSON válido, sin ```json ni texto extra.

    --- ARCHIVO A UTILIZAR ---

    Dentro de Code Interpreter, haz EXACTAMENTE esto en Python:

    ```python
    import os
    import pandas as pd
    import unicodedata
    import json

    # 1) Ruta FIJA del CSV de equivalencias SASB
    csv_path = "/mnt/data/file-72jxPHfYvtiA6DFfqShuhL"

    if not os.path.exists(csv_path):
        result = {
            "mapeo_sasb": [],
            "error": "No se encontró el archivo de equivalencias SASB en /mnt/data."
        }
        print(json.dumps(result, ensure_ascii=False))
        raise SystemExit()

    # 2) Cargar CSV como texto
    df = pd.read_csv(csv_path, dtype=str)

    # 3) Normalizar nombres de columnas (lower + sin acentos + strip)
    def _norm_col(name):
        s = str(name or "").strip().lower()
        s = "".join(
            ch for ch in unicodedata.normalize("NFKD", s)
            if not unicodedata.combining(ch)
        )
        return s

    df = df.rename(columns={c: _norm_col(c) for c in df.columns})

    # Ahora las columnas deben llamarse algo como:
    # 'industria sasb' y 'sector(es) s&p equivalentes'

    col_sector = "sector(es) s&p equivalentes"
    col_industria = "industria sasb"

    if col_sector not in df.columns or col_industria not in df.columns:
        result = {
            "mapeo_sasb": [],
            "error": "No se encontraron columnas esperadas en el CSV."
        }
        print(json.dumps(result, ensure_ascii=False))
        raise SystemExit()

    # 4) Normalizar texto para comparación robusta (lower + sin acentos + trim)
    def _norm_text(s):
        s = str(s or "").strip().lower()
        s = "".join(
            ch for ch in unicodedata.normalize("NFKD", s)
            if not unicodedata.combining(ch)
        )
        return s

    target_raw = "{industry}"
    target_norm = _norm_text(target_raw)

    # 5) Buscar coincidencias (primero EXACTAS normalizadas)
    df["sector_norm"] = df[col_sector].apply(_norm_text)

    exact_matches = df[df["sector_norm"] == target_norm]

    if len(exact_matches) > 0:
        matches_df = exact_matches
    else:
        # Si no hay match exacto, intentar "contiene" (subcadena)
        contains_matches = df[df["sector_norm"].str.contains(target_norm, na=False)]
        if len(contains_matches) > 0:
            matches_df = contains_matches
        else:
            result = {
                "mapeo_sasb": []
            }
            print(json.dumps(result, ensure_ascii=False))
            raise SystemExit()

    # 6) Si hay varias filas para el mismo sector S&P,
    #    elegir la industria SASB más representativa:
    #    la que más veces aparece en la tabla.
    matches_df["industria_norm"] = matches_df[col_industria].apply(_norm_text)

    if matches_df["industria_norm"].nunique() == 1:
        # Solo una industria posible → tomar la primera
        match = matches_df.iloc[0]
    else:
        # Varias industrias SASB candidatas:
        # seleccionar la de mayor frecuencia (más representativa)
        counts = matches_df["industria_norm"].value_counts()
        best_industria_norm = counts.index[0]

        subset = matches_df[matches_df["industria_norm"] == best_industria_norm]
        match = subset.iloc[0]

    sector_sp = str(match[col_sector])
    industria_sasb = str(match[col_industria])

    result = {
        "mapeo_sasb": [
            {
                "sector_sp": sector_sp,
                "industria_sasb": industria_sasb
            }
        ]
    }

    print(json.dumps(result, ensure_ascii=False))
    ```

    --- FORMATO DE RESPUESTA ---

    - No escribas NADA más que el `print(json.dumps(result, ensure_ascii=False))`.
    - No uses ```json ni markdown.
    - La salida debe ser un JSON con la forma:

    {
      "mapeo_sasb": [
        {
          "sector_sp": "...",
          "industria_sasb": "..."
        }
      ]
    }
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

    Archivo a usar obligatoriamente: **“lista_estandares_sasb_adaptia.csv”**

    REGLAS IMPORTANTES (SEGUIR AL 100%):
    - Coincidencia **EXACTA** (sensible a espacios, acentos y mayúsculas).
    - Si NO coincide exactamente, **NO** devuelvas nada.
    - NO utilices coincidencias parciales, semánticas ni aproximadas.
    - NO traduzcas, NO resumas, NO inventes textos.
    - Todo debe estar **en español**, exactamente como en el CSV.
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
    - Una vez que termines verifica en el CSV si traes todos los registros de esa industria, no puede faltar ninguna.

    """
)


prompt_10 = PromptTemplate(
    name="🔹 Prompt 10: Vinculación Normativa por Tema Material (GAIL)",
    template="""
    INSTRUCCIÓN OBLIGATORIA (NO IGNORAR):

    1. Debes usar Code Interpreter (herramienta de Python) para trabajar.
    2. NO generes imágenes, gráficos, tablas visuales ni archivos adjuntos.
    3. Tu respuesta FINAL debe ser ÚNICAMENTE un JSON válido, sin texto antes ni después (sin <JSON>, sin ```json, etc.).
    4. No expliques el proceso, no describas los pasos, no uses frases meta (“ahora que tengo el archivo…”, etc.).
    5. NO uses tu conocimiento general ni información de internet. Finge que NO tienes acceso a la web:
       todo debe salir EXCLUSIVAMENTE del JSON de entrada y del archivo CSV indicado.

    --- DATOS DE ENTRADA ---

    Recibes la tabla de materialidad priorizada (Prompt 5) en este JSON:

    <INPUT_MATERIALITY>
    {materiality_table_json}
    </INPUT_MATERIALITY>

    País de operación analizado (resultado del Prompt 1):
    <COUNTRY>
    {country}
    </COUNTRY>

    IMPORTANTE:
    - El JSON de entrada contiene hasta 10 temas materiales ya priorizados.
    - No debes inventar ni eliminar temas: usa SOLO los temas que vengan en ese JSON.
    - Cada uno de esos temas materiales debe terminar vinculado a EXACTAMENTE una regulación,
      salvo que no existan filas para ese país en el archivo de mapeo regulatorio (en cuyo caso debes devolver un JSON de error).

    --- TAREA CON CODE INTERPRETER (PYTHON OBLIGATORIO) ---

    Dentro de Code Interpreter debes hacer EXACTAMENTE lo siguiente usando Python
    (puedes organizar el código como quieras, pero la lógica debe respetar estos pasos):

    1. Cargar el JSON de entrada en un DataFrame de pandas:

       - Carga el JSON recibido en una variable (por ejemplo `materiality_data`)
         a partir de {materiality_table_json}.

       - Si el JSON tiene la forma `{"materiality_table": [...filas...]}`, crea:

           ```python
           mat_df = pd.DataFrame(materiality_data["materiality_table"]).copy()
           ```

         Si en cambio viene como una lista directa (`[...filas...]`), crea el DataFrame a partir de esa lista:

           ```python
           mat_df = pd.DataFrame(materiality_data).copy()
           ```

       - Normaliza los nombres de columnas:

           ```python
           mat_df.columns = [str(c).strip().lower() for c in mat_df.columns]
           ```

       - **TRATA TODAS LAS FILAS COMO TEMAS MATERIALES**:

           ```python
           mat_material = mat_df.copy()
           ```

       - Si `mat_material` queda vacío (sin filas):
           - Devuelve ESTE JSON y termina:

             {
               "error": "materiality_table_json está vacío, no hay temas materiales para procesar.",
               "regulaciones": []
             }

       - Identifica la columna que contiene el nombre del tema. Después de normalizar las columnas, define explícitamente:

           ```python
           tema_col = None
           for c in mat_df.columns:
               if "tema" in c:
                   tema_col = c
                   break
           ```

         Si después de este bucle `tema_col` sigue siendo `None`:

           - Devuelve ESTE JSON y termina:

             {
               "error": "No se encontró ninguna columna de tema en materiality_table_json.",
               "regulaciones": []
             }

    2. Leer el archivo de mapeo regulatorio (CSV) que ya está montado en /mnt/data:

       - El archivo de referencia está en la ruta fija:

           "/mnt/data/file-AAvFhYoCERey4rXnFR7Cyz"

       - Debes cargarlo con (IMPORTANTE: todo como texto):

           import unicodedata

           def _norm_col(name):
               # Normaliza: trim, minúsculas, sin acentos
               s = str(name or "").strip().lower()
               s = "".join(
                   ch for ch in unicodedata.normalize("NFKD", s)
                   if not unicodedata.combining(ch)
               )
               return s

           reg_df = pd.read_csv(
               "/mnt/data/file-AAvFhYoCERey4rXnFR7Cyz",
               dtype=str
           )

           # Normaliza los nombres de columna quitando acentos
           reg_df = reg_df.rename(columns={c: _norm_col(c) for c in reg_df.columns})

           # Después de esto las columnas deben ser algo como:
           # ['n', 'pais', 'tipo de regulacion', 'descripcion', 'vigencia']

           col_pais = "pais"
           col_tipo = "tipo de regulacion"
           col_desc = "descripcion"
           col_vig  = "vigencia"

           required = [col_pais, col_tipo, col_desc, col_vig]
           if any(c not in reg_df.columns for c in required):
               # NO inventes nada
               error_result = {
                   "error": "No se pudieron identificar columnas clave (país, tipo, descripción, vigencia) en el archivo de mapeo regulatorio (CSV).",
                   "regulaciones": []
               }
               import json
               print(json.dumps(error_result, ensure_ascii=False))
               return

           # A partir de aquí trabaja siempre con reg_data
           reg_data = reg_df.copy().reset_index(drop=True)

             ```

    3. Filtrar regulaciones por país:

       - Normaliza la columna de país en `reg_data[col_pais]`:

           ```python
           country_col_norm = (
               reg_data[col_pais]
               .astype(str)
               .str.strip()
               .str.lower()
           )
           ```

       - Normaliza el país de entrada:

           ```python
           target_country = "{country}".strip().lower()
           ```

           (puedes también quitar acentos para que la comparación sea más robusta).

       - Crea un DataFrame `reg_country` con SOLO las filas cuyo país corresponde al país analizado:

           ```python
           reg_country = reg_data[country_col_norm == target_country].copy().reset_index(drop=True)
           ```

       - SI `reg_country` está vacío (sin filas):
           - NO inventes regulaciones.
           - Devuelve ESTE JSON y termina:

             {
               "error": "No se encontraron filas de regulaciones para el país indicado en el archivo de mapeo regulatorio.",
               "regulaciones": []
             }

    4. Preparar columnas de texto para análisis:

       - Para `reg_country`, crea las siguientes series:

           ```python
           tipo_col = reg_country[col_tipo].astype(str)
           desc_col = reg_country[col_desc].astype(str)
           vig_col  = reg_country[col_vig].astype(str)
           ```

       - Crea también versiones normalizadas en minúsculas para análisis de texto:

           ```python
           tipo_col_norm = tipo_col.str.lower()
           desc_col_norm = desc_col.str.lower()
           ```

    5. Selección de UNA regulación POR CADA TEMA MATERIAL:

       - Inicializa la lista de salida y el conjunto de índices usados:

           ```python
           output_regs = []
           used_indices = set()
           ```

       - Para cada fila de `mat_material` (en el orden en que aparecen):

         5.1. Obtener y normalizar el tema:

               - Extrae el texto del tema desde `row[tema_col]`.
               - Convierte a string, quita espacios, pásalo a minúsculas y, opcionalmente, quita acentos.
               - Guarda el texto original en `tema_full` y la versión normalizada en `tema_norm`.

               - Si el tema está vacío, puedes saltar esa fila.

         5.2. Definir familias temáticas por palabras clave del tema (ejemplos orientativos):

               - Clima / carbono:
                 si `tema_norm` contiene alguna de:
                   "clima", "climatico", "climático", "emision", "emisiones",
                   "huella de carbono", "co2", "gases de efecto invernadero".

               - Residuos / economía circular:
                 si contiene:
                   "residuo", "residuos", "recicl", "circular", "basura", "economia circular".

               - Contaminación / calidad ambiental:
                 si contiene:
                   "contaminacion", "contaminación", "calidad del aire", "calidad del agua",
                   "aire", "agua", "emisiones".

               - Trabajo / condiciones laborales:
                 si contiene:
                   "trabajo", "laboral", "condiciones laborales", "derechos laborales",
                   "empleo", "salario", "sindicato", "trabajadores".

               - Salud y seguridad:
                 si contiene:
                   "salud", "seguridad", "higiene", "seguridad y salud",
                   "seguridad de los trabajadores", "seguridad del cliente".

               - Comunidad / impacto social:
                 si contiene:
                   "comunidad", "comunidades", "impacto en las comunidades",
                   "desarrollo local", "territorio", "social".

               - Biodiversidad / recursos naturales:
                 si contiene:
                   "biodiversidad", "ecosistema", "bosques", "mares",
                   "recursos naturales", "suelo", "agua".

               - Acceso / asequibilidad / servicios:
                 si contiene:
                   "acceso", "asequibilidad", "servicios esenciales",
                   "transporte público", "transporte publico", "tarifas".

               - Productos y servicios sostenibles:
                 si contiene:
                   "producto", "productos", "servicios sostenibles", "ecoetiqueta",
                   "eficiencia energetica", "eficiencia energética", "innovacion sostenible".

               - Si ninguna categoría aplica claramente:
                   → usa coincidencias generales entre palabras del tema y `desc_col_norm`
                     (por ejemplo, intersección de tokens entre `tema_norm` y cada descripción).

         5.3. Implementar una función de scoring:

               - Define en Python una función, por ejemplo `compute_score(tema_norm, tipo_text, desc_text)`,
                 que devuelva un número entero de puntuación.

               - El score debe considerar:
                   * número de palabras clave del tema presentes en `tipo_text` y en `desc_text`;
                   * peso extra si se activa alguna de las familias temáticas indicadas arriba
                     y la descripción contiene términos coherentes con esa familia;
                   * puedes usar tokens en minúsculas y contar coincidencias.

               - Para cada fila `i` de `reg_country`, calcula:

                   `s = compute_score(tema_norm, tipo_col_norm[i], desc_col_norm[i])`

               - Está TERMINANTEMENTE PROHIBIDO:
                   ❌ usar patrones tipo `idx = i`, `idx = i + 1`, `idx = i + k`
                       o similares basados SOLO en la posición del tema;
                   ❌ seleccionar siempre las primeras N filas sin mirar el texto.

        5.4. Selección de la fila candidata:

            - Para cada tema material, debes:

                1) Calcular un score para CADA fila `i` de `reg_country`:

                    ```python
                    scores = []
                    for i in range(len(reg_country)):
                        s = compute_score(tema_norm, tipo_col_norm.iloc[i], desc_col_norm.iloc[i])
                        scores.append(s)
                    ```

                2) Ordenar los índices por score descendente:

                    ```python
                    indices = sorted(range(len(reg_country)), key=lambda i: scores[i], reverse=True)
                    ```

                3) Buscar una fila candidata siguiendo este orden de prioridad:

                    - Primero, recorre `indices` y quédate con la
                    **primera fila que cumpla TODO**:

                    - `scores[i] > 0`
                    - `i` NO está en `used_indices` (si existen filas libres)
                    - `tipo_col.iloc[i]`, `desc_col.iloc[i]` y `vig_col.iloc[i]`
                        NO son vacíos, ni "nan", ni "none", ni "null" (después de strip+lower).

                    - Si no encuentras nada con `scores[i] > 0`:

                    - Vuelve a recorrer `indices` pero ahora aceptando `scores[i] >= 0`
                        (incluidos 0) mientras:

                        - `i` NO esté en `used_indices` (si todavía quedan índices libres).
                        - Los tres campos (`tipo`, `descripcion`, `vigencia`) no estén vacíos
                        ni sean "nan"/"none"/"null".

                    - Si aun así no encuentras nada y TODAS las filas libres tienen algún campo vacío,
                    como último recurso:

                    - Permite reutilizar filas ya usadas:
                        recorre de nuevo `indices` completos y elige la primera
                        fila con campos no vacíos, aunque `i` ya esté en `used_indices`.

                4) El índice finalmente elegido se guarda en:

                    ```python
                    idx_def = indice_elegido
                    used_indices.add(idx_def)
                    ```

                - Está TERMINANTEMENTE PROHIBIDO:

                ❌ Usar patrones tipo `idx_def = i`, `idx_def = fila_actual` basados
                    únicamente en la posición del tema.

                ❌ Ignorar el contenido de `tipo_col_norm` y `desc_col_norm` y seleccionar
                    solo por orden o por score sin revisar que los campos estén llenos.

        5.5. Extraer los valores EXACTOS desde el CSV y construir la salida:

            - A partir de `idx_def`, NO leas de nuevo las celdas manualmente desde `reg_country`.
                Debes usar EXCLUSIVAMENTE las series ya creadas:

                - `tipo_col` para el tipo de regulación
                - `desc_col` para la descripción
                - `vig_col`  para la vigencia

            - Debes ejecutar literalmente un código equivalente a:

                ```python
                tipo_reg = tipo_col.iloc[idx_def]
                desc_reg = desc_col.iloc[idx_def]
                vig_reg  = vig_col.iloc[idx_def]

                def _is_empty(v):
                    s = str(v).strip().lower()
                    return s == "" or s == "nan" or s == "none" or s == "null"

                # En este punto, POR DISEÑO de 5.4, tipo_reg / desc_reg / vig_reg
                # ya no deberían ser vacíos. Si aun así alguno lo fuera,
                # significa que no hay ninguna fila útil en el CSV: lanza error global.
                if _is_empty(tipo_reg) or _is_empty(desc_reg) or _is_empty(vig_reg):
                    result = {
                        "error": "No se encontraron filas completas (tipo, descripción, vigencia) para al menos uno de los temas materiales.",
                        "regulaciones": []
                    }
                    import json
                    print(json.dumps(result, ensure_ascii=False))
                    return
                
                registro = {
                    "tipo_regulacion": str(tipo_reg),
                    "descripcion": str(desc_reg),
                    "vigencia": str(vig_reg)
                }

                output_regs.append(registro)
                ```

            - PROHIBIDO (IMPORTANTE):

                ❌ Escribir textos literales dentro del diccionario, por ejemplo:
                    `{"descripcion": "Ley 20.780 (impuesto verde) ..."}` 
                    o `{"descripcion": "Ley 21.600. Crea el Servicio de Biodiversidad ..."}`.

                ❌ Completar, resumir, corregir o parafrasear el contenido de `desc_reg`.
                ❌ Cambiar el formato de la fecha de `vig_reg`.
                ❌ Añadir paréntesis, siglas o información que no esté en `desc_reg`
                    ni en `vig_reg`.

            - SOLO se permite construir el JSON a partir de las variables
                `tipo_reg`, `desc_reg` y `vig_reg` usando `str(...)`.
                No puedes escribir ninguna ley, número, fecha o acrónimo manualmente
                en el código.


    6. Al finalizar todos los temas materiales:

       - Debes haber iterado por TODAS las filas de `mat_material` SIN saltarte ninguna.
         Por cada fila de `mat_material` debes haber añadido EXACTAMENTE un elemento en `output_regs`.

         Es decir, al final del bucle se debe cumplir:

           `len(output_regs) == len(mat_material)`

       - Si `len(output_regs)` es distinto de `len(mat_material)`:
           - NO devuelvas una lista parcial.
           - Devuelve este JSON y termina:

             {
               "error": "El número de regulaciones generadas no coincide con el número de temas materiales de entrada.",
               "regulaciones": []
             }

       - Si coinciden y todas las regulaciones tienen campos no vacíos:

           ```python
           result = {
               "regulaciones": output_regs
           }
           import json
           print(json.dumps(result, ensure_ascii=False))
           ```

    --- FORMATO DE RESPUESTA OBLIGATORIO ---

    - NO escribas tú manualmente el JSON fuera de Python.
    - La respuesta FINAL debe ser EXCLUSIVAMENTE la salida de:

        `print(json.dumps(result, ensure_ascii=False))`

      ejecutado dentro de Code Interpreter.

    - No escribas ningún texto adicional, ni antes ni después.
    - No uses bloques ```json.
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

    --- CONTEXTO DE ANÁLISIS ESG (JSON) ---
    {previous_results_json}
    --- FIN CONTEXTO ---

    --- INSTRUCCIONES ESPECÍFICAS DEL PROMPT ---

    Objetivo:
    Generar un resumen ejecutivo en máximo 2 párrafos, basado en los 10 temas materiales priorizados.
    El texto debe redactarse como si fuera la recomendación de un consultor experto en sostenibilidad, evitando un tono descriptivo de hechos ya implementados.
    Asegúrate de mencionar explícitamente que las recomendaciones están basadas en el análisis de doble materialidad realizado.
    La redacción debe presentar las acciones como pasos estratégicos que la empresa debería seguir:
    - Acciones iniciales → recomendaciones inmediatas de ajuste operativo.
    - Acciones moderadas → procesos recomendados a integrar en el mediano plazo.
    - Acciones estructurales → transformaciones de modelo de negocio a largo plazo.
    Mantén un tono estratégico y ejecutivo, transmitiendo visión integral y ambiciosa, sin listar ni repetir extensamente. 

    Instrucciones:
    - Que el resumen sea enfocado en los 10 temas materiales, no solo en 2.
    - Usa el contexto del análisis ESG previo.
    - Redacta como consultor experto.
    - Menciona explícitamente que se basa en análisis de doble materialidad.
    - Relaciona acciones iniciales, moderadas y estructurales.
    - Minimo 600 palabras.
    - Tono estratégico, ejecutivo y conciso.

    Formato obligatorio (estructura del JSON):
    {{
        "parrafo_1": "string",
        "parrafo_2": "string"
    }}
    """
)
