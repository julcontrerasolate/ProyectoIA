import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Constantes
MODELO = "gemini-3.8-flash"
URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models/"
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")

if not API_KEY:
    raise RuntimeError(
        "No se encontró la clave API. Define GEMINI_API_KEY o API_KEY en tu archivo .env."
    )


# funcion para crear la solicitud
def armar_peticion(pregunta):
    if not pregunta:
        raise ValueError("La pregunta no puede estar vacía.")
    url = f"{URL_BASE}{MODELO}:generateContent?key={API_KEY}"
    body = {"contents": [{"parts": [{"text": pregunta}]}]}
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

    if respuesta.status_code != 200:
        raise RuntimeError(
            f"Error en la solicitud: {respuesta.status_code} - {respuesta.text}"
        )

    try:
        return respuesta.json()
    except ValueError:
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
    costo = (tokens_entrada * precio_entrada) + (tokens_salida * precio_salida)
    return costo


def obtener_datos(pregunta):
    url, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, body)
    costo = calcular_costo(datos, precio_entrada=0.00000075, precio_salida=0.00000375)
    print(f"Costo estimado de la solicitud: ${costo:.6f} USD")
    return extraer_texto(datos)


try:
    print(obtener_datos("Confirma en una frase corta que esta conexión funciona"))
except (ValueError, RuntimeError) as error:
    print("No se pudo completar la operación: ", error)