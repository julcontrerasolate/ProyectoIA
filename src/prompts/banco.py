BANCO_DE_PROMPT = [
    {
        "nombre": "Cual es el clima hoy en Santiago",
        "system_instruction": (
            "Eres un asistente del clima para personas que viven en Santiago de Chile. "
            "Resume el clima en una frase y asigna un nivel de abrigo del 1 (muy liviano) "
            "al 5 (muy abrigado)."
        ),
        "ejemplo_usuario": "¿Cómo estará el clima hoy en Santiago?",
        "claves_esperadas": ["resumen", "nivel_abrigo"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "resumen": {"type": "STRING"},
                "nivel_abrigo": {"type": "NUMBER"},
            },
            "required": ["resumen", "nivel_abrigo"],
        },
    },
    {
        "nombre": "Necesito paraguas hoy",
        "system_instruction": (
            "Eres un asistente del clima. Decide si el usuario necesita paraguas "
            "y explica el motivo en una frase corta."
        ),
        "ejemplo_usuario": "¿Necesito paraguas para salir hoy en Santiago?",
        "claves_esperadas": ["necesita_paraguas", "motivo"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "necesita_paraguas": {"type": "BOOLEAN"},
                "motivo": {"type": "STRING"},
            },
            "required": ["necesita_paraguas", "motivo"],
        },
    },
    {
        "nombre": "Que actividad hacer segun el clima",
        "system_instruction": (
            "Eres un asistente que recomienda actividades según el clima en Santiago de Chile. "
            "Indica si el día es apto para actividades al aire libre y sugiere una actividad concreta."
        ),
        "ejemplo_usuario": "¿Qué puedo hacer este fin de semana en Santiago según el clima?",
        "claves_esperadas": ["apto_exterior", "actividad_recomendada"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "apto_exterior": {"type": "BOOLEAN"},
                "actividad_recomendada": {"type": "STRING"},
            },
            "required": ["apto_exterior", "actividad_recomendada"],
        },
    },
]