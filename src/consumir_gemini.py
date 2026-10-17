import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Constantes
MODELO = "gemini-3.6-flash"
URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models/"
API_KEY = os.getenv("GEMINI_API_KEY")


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
    except requests.exceptions.connectionError:
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
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError("La respuesta del servidor no es un JSON válido.")


# funcion procesa y extrae datos
def extraer_texto(datos):  # Gemini
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError(
            "La respuesta no recibe el texto generado en el lugar definido."
        )


def obtener_datos(pregunta):
    url, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, body)
    return extraer_texto(datos)


try:
    print(obtener_datos("Confirma en una frase corta si mi conexion esta funcionando"))
except (ValueError, RuntimeError) as error:
    print("La pregunta no puede estar vacía.", error)


# def obtener_datos_prueba(pregunta):
#     api_key = os.getenv("GEMINI_API_KEY")
#     modelo = "gemini-flash-latest"
#     url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
#     body = {
#         "contents": [
#             {"parts": [{"text": pregunta}]}
#         ]
#     }
#     respuesta = requests.post(url, json=body)
#     datos = respuesta.json()
#     return datos["candidates"][0]["content"]["parts"][0]["text"]


# print(obtener_datos_prueba("Confirma en una frase corta si mi conexion esta funcionando"))
