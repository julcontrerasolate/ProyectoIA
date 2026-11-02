from collections import Counter
from .pipeline_limpieza import procesar_texto
from .cliente import consultar_modelo
import json


def contar_coincidencias(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> int:
    """Cuenta las coincidencias entre referencia y respuesta."""
    conteo_referencia = Counter(tokens_referencia)
    conteo_respuesta = Counter(tokens_respuesta)
    interseccion = conteo_referencia & conteo_respuesta
    return sum(interseccion.values())


def calcular_precision_cobertura_f1(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> dict[str, float]:
    """Calcula precisión, cobertura y F1 de dos listas de tokens."""
    coincidencias = contar_coincidencias(tokens_referencia, tokens_respuesta)

    if not tokens_respuesta or not tokens_referencia:
        return {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}

    precision = coincidencias / len(tokens_respuesta)
    cobertura = coincidencias / len(tokens_referencia)

    if precision + cobertura == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * cobertura / (precision + cobertura)

    resultado = {
        "precision": precision,
        "cobertura": cobertura,
        "f1": f1,
    }

    return resultado


def calcular_metricas(texto_referencia, texto_respuesta):
    tokens_referencia = procesar_texto(texto_referencia)
    tokens_respuesta = procesar_texto(texto_respuesta)

    return calcular_precision_cobertura_f1(tokens_referencia, tokens_respuesta)


casos = [
    (
        "El domingo hay 90% de probabilidad de lluvia. ¿Va a llover el domingo?",
        "Sí, el domingo es muy probable que llueva.",
    ),
    (
        "El sábado hay 0% de probabilidad de lluvia. ¿Necesito paraguas el sábado?",
        "No, el sábado no se espera lluvia y no necesitas paraguas.",
    ),
    (
        "Mañana la mínima será de 4 °C y la máxima de 15 °C. ¿Debo llevar abrigo?",
        "Sí, mañana hará frío y conviene llevar abrigo.",
    ),
    (
        "Hoy la máxima será de 33 °C y no hay nubes. ¿Qué me recomiendas?",
        "Hará mucho calor, conviene usar protector solar y tomar agua.",
    ),
    (
        "El lunes tendrá 40% de probabilidad de lluvia. ¿Es seguro que llueva?",
        "No, el lunes es posible que llueva pero no es seguro.",
    ),
    (
        "El martes hay 80% de lluvia y el miércoles 20%. ¿Qué día es mejor para salir?",
        "El miércoles es mejor para salir porque tiene menos probabilidad de lluvia.",
    ),
    (
        "El jueves la máxima será de 25 °C y el viernes de 28 °C. ¿Qué día hará más calor?",
        "El viernes hará más calor, con una máxima de 28 grados.",
    ),
    (
        "Hoy en la mañana habrá 8 °C y en la tarde 21 °C. ¿Cuándo hará más frío?",
        "En la mañana hará más frío, con 8 grados.",
    ),
    (
        "Esta noche la mínima será de -2 °C. ¿Puede haber helada?",
        "Sí, con una mínima de menos 2 grados puede haber helada.",
    ),
    (
        "Mañana habrá viento de 60 km/h. ¿Es un día tranquilo para salir?",
        "No, el viento de 60 km/h es fuerte y conviene tener precaución.",
    ),
    (
        "Hoy hay 70% de lluvia en la tarde y 10% en la noche. ¿Cuándo conviene salir?",
        "Conviene salir en la noche, cuando casi no hay probabilidad de lluvia.",
    ),
    (
        "El pronóstico dice sol y 22 °C el sábado. ¿Es buen día para un picnic?",
        "Sí, el sábado es buen día para un picnic por el sol y los 22 grados.",
    ),
    (
        "La humedad hoy es de 95% y hay niebla. ¿Cómo estará la visibilidad?",
        "La visibilidad será baja por la niebla.",
    ),
    (
        "Hoy la máxima es de 18 °C y mañana será de 12 °C. ¿Mañana estará más frío?",
        "Sí, mañana estará más frío que hoy, con una máxima de 12 grados.",
    ),
    (
        "Los datos solo muestran temperatura y probabilidad de lluvia. ¿Cuántos milímetros caerán mañana?",
        "No lo sé, los datos no indican cuántos milímetros caerán.",
    ),
    (
        "Tengo datos del clima de Santiago. ¿Cómo estará el clima en Valparaíso?",
        "No tengo datos de Valparaíso, solo de Santiago.",
    ),
    (
        "De lunes a miércoles la lluvia será de 10%, 15% y 5%. ¿Va a llover a comienzos de semana?",
        "No, de lunes a miércoles la probabilidad de lluvia es baja.",
    ),
    (
        "El viernes tendrá una mínima de 10 °C, una máxima de 24 °C y 0% de lluvia. ¿Cómo estará el viernes?",
        "El viernes estará despejado, con entre 10 y 24 grados y sin lluvia.",
    ),
    (
        "Hoy en la tarde habrá 35 °C y 5% de lluvia. ¿Necesito paraguas?",
        "No, no necesitas paraguas porque casi no hay probabilidad de lluvia.",
    ),
    (
        "El miércoles tendrá 60% de lluvia y 9 °C de mínima. ¿Qué debo llevar?",
        "Lleva paraguas y algo de abrigo porque habrá lluvia y frío.",
    ),
    (
        "El jueves tendrá 15% de lluvia y 26 °C de máxima. ¿Cómo estará el jueves?",
        "El jueves estará agradable, con máxima de 26 grados y poca probabilidad de lluvia.",
    ),
    (
        "Mañana habrá 3 °C de mínima y 85% de lluvia. ¿Qué debo llevar?",
        "Lleva abrigo y paraguas porque habrá frío y mucha probabilidad de lluvia.",
    ),
    (
        "Hoy hay 0% de lluvia y 30 °C en la tarde. ¿Necesito paraguas?",
        "No, no necesitas paraguas porque no se espera lluvia.",
    ),
]

resultados = []

for consulta, referencia in casos:
    try:
        respuesta = consultar_modelo(
            consulta,
            system_instruction="Responde en español en una sola oración de máximo 20 palabras, usando solo los datos entregados. Sin listas ni introducciones.",
        )
    except RuntimeError as error:
        print("Falló:", consulta, "->", error)
        continue

    metricas = calcular_metricas(referencia, respuesta)

    print("Consulta:", consulta)
    print("Respuesta:", respuesta)
    print("Métricas:", metricas)

    resultados.append(
        {
            "consulta": consulta,
            "referencia": referencia,
            "respuesta": respuesta,
            **metricas,
        }
    )

resultados = sorted(resultados, key=lambda r: r["f1"])

with open("resultados_metricas.json", "w", encoding="utf-8") as archivo:
    json.dump(resultados, archivo, indent=2, ensure_ascii=False)

print(f"\nCasos completados: {len(resultados)} de {len(casos)}")


def resumir_metricas(resultados):
    if not resultados:
        return {
            "precision_promedio": 0,
            "cobertura_promedio": 0,
            "f1_promedio": 0,
        }
    n = len(resultados)
    return {
        "precision_promedio": sum(r["precision"] for r in resultados) / n,
        "cobertura_promedio": sum(r["cobertura"] for r in resultados) / n,
        "f1_promedio": sum(r["f1"] for r in resultados) / n,
    }


print("Promedios")
print(resumir_metricas(resultados))

# peores_casos = sorted(resultados, key=lambda r: r["f1"])

# for caso in peores_casos[:3]:
#     print(caso["consulta"], caso["f1"])

peores_casos = sorted(resultados, key=lambda r: r["f1"])

muestra_para_revisar = peores_casos[:5] + peores_casos[-5:]

with open("muestra_para_revisar.json", "w", encoding="utf-8") as archivo:
    json.dump(muestra_para_revisar, archivo, indent=2, ensure_ascii=False)


for caso in muestra_para_revisar:

    print(caso["consulta"], caso["f1"])


# referencia = procesar_texto(
#     "Python es un lenguaje de programación interpretado."
# )

# texto_respuesta = consultar_modelo("¿Qué es Python?",
#                                    system_instruction="Responde en español con una definición breve, en una sola oración de máximo 15 palabras. Sin listas, ejemplos ni introducciones.")

# respuesta = procesar_texto(texto_respuesta)
# resultado = calcular_precision_cobertura_f1(referencia, respuesta)

# print("Respuesta:", texto_respuesta)
# print("Tokens de referencia:", len(referencia))
# print("Tokens de respuesta:", len(respuesta))
# print(resultado)
