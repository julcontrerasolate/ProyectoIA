from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
# respuesta = modelo.invoke("¿Qué es un token?")
# print(respuesta.content)

plantilla = PromptTemplate.from_template(
    "Explica el concepto de {tema} en un parrafo, para alguien que recien comienza en {area}."
)

# prompt = plantilla.invoke({"tema": "tokenizacion", "area": "procesamiento de texto"})

# print(prompt.text)

cadena_simple = plantilla | modelo | StrOutputParser()

respuesta = cadena_simple.invoke({"tema": "embeddings", "area": "busqueda semantica"})
print(respuesta)

plantilla_conrol = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Eres un experto en el area correspondiente vas a responder siempre con texto simple para el usuario.",
        ),
        (
            "human",
            "Explica el concepto de {tema} en un parrafo, para alguien que recien comienza en {area}.",
        ),
    ]
)
