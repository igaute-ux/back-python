import json
import re

def clean_and_parse_json(output: str) -> dict:
    """
    Limpia un string que contiene un bloque de JSON envuelto en ```json ... ```
    y lo convierte a un diccionario de Python.
    """
    # 1. Eliminar los delimitadores de bloque de código ```json ... ```
    cleaned = re.sub(r"^```json\s*|\s*```$", "", output.strip(), flags=re.MULTILINE)
    
    # 2. Parsear a JSON
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error al parsear JSON: {e}\nTexto limpio: {cleaned}")