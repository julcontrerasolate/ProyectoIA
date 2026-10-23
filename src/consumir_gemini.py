import os
import requests
from dotenv import load_dotenv

import time
import json
import re

load_dotenv()

# Constantes
MODELO = "gemini-3.6-flash"
URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models/"
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")

if not API_KEY:
    raise RuntimeError(
        "No se encontró la clave API. Define GEMINI_API_KEY o API_KEY en tu archivo .env."
    )


# funcion para crear la solicitud
def armar_peticion(
    pregunta, system_instruction=None, response_schema=None, modelo=MODELO
):
    if not pregunta:
        raise ValueError("La pregunta no puede estar vacía.")
    url = f"{URL_BASE}{modelo}:generateContent?key={API_KEY}"
    body = {"contents": [{"parts": [{"text": pregunta}]}]}
    if system_instruction:
        body["systemInstruction"] = {"parts": [{"text": system_instruction}]}
    # Salida estructurada: obliga al modelo a responder JSON con este esquema
    if response_schema is not None:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }
    return url, body


# funcion envia la solicitud
def enviar_peticion(url, body):
    try:
        respuesta = requests.post(url, json=body, timeout=30)
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "No se pudo conectar al servidor. Intenta de nuevo más tarde."
        )
    except requests.exceptions.Timeout:
        raise RuntimeError(
            "La solicitud ha excedido el tiempo de espera. Intenta de nuevo más tarde."
        )
    if respuesta.status_code in (400, 401, 403):
        raise RuntimeError(
            "Error de autenticación. Verifica tu clave API y los permisos."
        )
    if respuesta.status_code >= 500:
        raise RuntimeError(
            "Error del servidor. Intenta de nuevo más tarde."
        )

    if respuesta.status_code == 429:
        segundos = respuesta.headers.get("Retry-After")
        raise RuntimeError(
            f"Límite de solicitudes alcanzado. Reintentar en {segundos} segundos." if segundos else "Límite excedido"
        )

    if respuesta.status_code != 200:
        raise RuntimeError(
            f"Error en la solicitud: {respuesta.status_code} - {respuesta.text}"
        )

    try:
        return respuesta.json()
    except (ValueError, requests.exceptions.JSONDecodeError):
        raise RuntimeError("La respuesta del servidor no es un JSON válido.")


# funcion procesa y extrae datos
def extraer_texto(datos):  # Gemini
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError(
            "La respuesta no recibe el texto generado en el lugar definido."
        )


def calcular_costo(datos, precio_entrada, precio_salida):
    uso = datos["usageMetadata"]
    tokens_entrada = uso["promptTokenCount"]
    tokens_salida = uso["candidatesTokenCount"]
    # Si el modelo no usó razonamiento, el campo puede no venir
    tokens_razonamiento = uso.get("thoughtsTokenCount", 0)
    costo = (tokens_entrada * precio_entrada) + (
        (tokens_salida + tokens_razonamiento) * precio_salida
    )
    return costo


def parsear_respuesta_json(texto, claves_requeridas=None):
    """
    Convierte el texto del modelo en un dict.
    claves_requeridas = ["categoria", "nivel"]
    """
    texto_limpio = texto.strip()
    texto_limpio = re.sub(r"^```(?:json)?\s*", "", texto_limpio)
    texto_limpio = re.sub(r"\s*```$", "", texto_limpio)

    try:
        datos = json.loads(texto_limpio)
    except json.JSONDecodeError:
        raise ValueError("La respuesta del modelo no es JSON válido.")

    if claves_requeridas:
        if not isinstance(datos, dict):
            raise ValueError("La respuesta no tiene la estructura esperada.")
        faltantes = [clave for clave in claves_requeridas if clave not in datos]
        if faltantes:
            raise ValueError("La respuesta no tiene la estructura esperada.")

    return datos


def obtener_datos(pregunta):
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "categoria": {"type": "STRING"},
            "nivel": {"type": "NUMBER"},
        },
        "required": ["categoria", "nivel"],
    }
    system_instruction = "Eres un asistente amigable y respondes en máximo 2 palabras."
    url, body = armar_peticion(pregunta, system_instruction, response_schema)
    inicio = time.perf_counter()
    datos = enviar_peticion(url, body)
    fin = time.perf_counter()
    latencia = fin - inicio
    print(f"Latencia de la solicitud: {latencia:.2f} segundos")
    print(f"Tiempo de ejecución: {fin - inicio:.2f} segundos")
    costo = calcular_costo(datos, precio_entrada=0.00000075, precio_salida=0.00000375)
    print(f"Costo estimado de la solicitud: ${costo:.6f} USD")
    texto = extraer_texto(datos)
    return parsear_respuesta_json(texto, ["categoria", "nivel"])


try:
    print(obtener_datos("Confirma en una frase corta que esta conexión funciona"))
except (ValueError, RuntimeError) as error:
    print("No se pudo completar la operación: ", error)


"""
Ejecute 4 veces la MISMA petición con 1 modelo
y ante cada petición se calcule e imprima: Latencia, Costo, Respuesta

Vuelvo a hacer lo mismo con un modelo distinto

3 modelos a comparar

OBJETIVO: Elijas el mejor modelo para tu proyecto

Prompt sea algo relacionado con tu proyecto.
"""
