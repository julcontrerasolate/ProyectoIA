import json
import time
from prompts.banco import BANCO_DE_PROMPT
from consumir_gemini import armar_peticion, enviar_peticion, extraer_texto, parsear_respuesta_json, MODELO

registro={}

try:

    for prompt in BANCO_DE_PROMPT:
        exitos = 0
        intentos = 3
        for intento in range(intentos):
            url, body = armar_peticion(
                prompt["ejemplo_usuario"],
                prompt["system_instruction"],
                prompt["response_schema"],
                MODELO
            )
        respuesta = enviar_peticion(url, body)
        texto = extraer_texto(respuesta)
        datos = parsear_respuesta_json(texto, prompt["claves_esperadas"])
        try:
            datos = parsear_respuesta_json(texto, prompt["claves_esperadas"])
            exitos += 1
            print(f"Respuesta: {datos}")
        except ValueError as error:
            print(f" intento {intento + 1} falló: {error}")
            time.sleep(1)
        print(f"{prompt['nombre']}: {exitos}/{intentos} intentos exitosos")
        registro[prompt["nombre"]] = {"exitos": exitos, "intentos": intentos}
    #cuando termine guardar en registro_resultados.json
    with open("src/prompts/registro_resultados.json", "w", encoding="utf-8") as archivo:
        json.dump(registro, archivo, indent=2, ensure_ascii=False)


except {ValueError, RuntimeError} as error:
    print("No se pudo completar la operación: ", error)