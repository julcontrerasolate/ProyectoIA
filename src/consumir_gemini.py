import os
import requests
from dotenv import load_dotenv

load_dotenv()

#Constantes
MODELO="gemini-3.6-flash"
URL_BASE="https://generativelanguage.googleapis.com/v1beta/models/"
API_KEY=os.getenv("GEMINI_API_KEY")

# funcion para crear la solicitud
def armar_peticion(pregunta):
    url = f"{URL_BASE}{MODELO}:generateContent?key={API_KEY}"
    body = { "contents":[{"parts":[{"text": pregunta}]}]}
    return url, body

# funcion envia la solicitud
def enviar_peticion(url, body):
    respuesta = requests.post(url, json=body)
    return respuesta.json()


# funcion procesa y extrae datos
def extraer_texto(datos): #Gemini 
    return datos["candidates"][0]["content"]["parts"][0]["text"]

def obtener_datos(pregunta):
    url, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, body)
    return extraer_texto(datos)

print(obtener_datos("Confirma en una frase corta si mi conexion esta funcionando"))


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
