import os
import time
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# CONFIGURACIÓN (lo que normalmente querrás cambiar)
# ---------------------------------------------------------------------------
# Lugar a consultar. Puedes cambiarlo aquí o definir CIUDAD / CODIGO_PAIS en tu .env
CIUDAD = os.getenv("CIUDAD", "Santiago")
CODIGO_PAIS = os.getenv("CODIGO_PAIS", "CL")  # CL, AR, PE, ES, MX, etc. ("" = sin filtrar)

# Personalidad y formato de respuesta: viven aparte de la pregunta.
# Se envían a Gemini como "system_instruction".
INSTRUCCIONES_SISTEMA = (
    "Eres un asistente del clima amable y cercano. Respondes siempre en español, "
    "de forma breve (máximo 3 frases cortas, unas 50 palabras). Respondes lo que "
    "se pregunta usando solo los datos entregados, y terminas con una recomendación "
    "breve y natural. Usa tu criterio: si la lluvia es muy probable, sugiere paraguas "
    "o impermeable; si es posible pero incierta, sugiere tener un paraguas a mano; "
    "si es poco probable, invita a disfrutar y salir. Si hace mucho frío o calor, "
    "puedes mencionar abrigo o protección solar. Si la pregunta pide algo que los "
    "datos no cubren, dilo con honestidad en vez de inventar."
)

REPETICIONES = 4
PAUSA_ENTRE_PRUEBAS = 2  # segundos, para no gatillar límites de uso
LARGO_VISTA_PREVIA = 260  # caracteres de la respuesta que se muestran

# Precios en USD por TOKEN (precio por millón / 1_000_000).
# IMPORTANTE: verifica nombres y precios vigentes en la documentación de Google.
MODELOS = {
    "gemini-3.8-flash": {"entrada": 0.00000075, "salida": 0.00000375},  # $0.75 / $3.75 por millón
    "gemini-3.6-flash": {"entrada": 0.00000075, "salida": 0.00000375},  # precios de tu código original
    "gemini-3.1-flash-lite": {"entrada": 0.00000025, "salida": 0.00000150},  # $0.25 / $1.50 por millón
}

# ---------------------------------------------------------------------------
# Constantes técnicas
# ---------------------------------------------------------------------------
URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models/"
URL_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"
URL_CLIMA = "https://api.open-meteo.com/v1/forecast"
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")

if not API_KEY:
    raise RuntimeError(
        "No se encontró la clave API. Define GEMINI_API_KEY o API_KEY en tu archivo .env."
    )


# ---------------------------------------------------------------------------
# Clima (Open-Meteo: gratis y sin clave)
# ---------------------------------------------------------------------------
def buscar_lugar(ciudad, codigo_pais=""):
    """Convierte el nombre de una ciudad en coordenadas."""
    params = {"name": ciudad, "count": 1, "language": "es"}
    if codigo_pais:
        params["countryCode"] = codigo_pais
    try:
        r = requests.get(URL_GEOCODING, params=params, timeout=15)
        r.raise_for_status()
        resultados = r.json().get("results")
    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"No se pudo buscar la ciudad: {error}")
    except ValueError:
        raise RuntimeError("La búsqueda de ciudad no devolvió un JSON válido.")

    if not resultados:
        raise RuntimeError(f"No se encontró la ciudad '{ciudad}' ({codigo_pais or 'cualquier país'}).")

    lugar = resultados[0]
    return {
        "nombre": lugar["name"],
        "pais": lugar.get("country", ""),
        "lat": lugar["latitude"],
        "lon": lugar["longitude"],
    }


DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
# Franjas del día para el detalle de hoy: (nombre, hora inicio, hora fin)
FRANJAS = [("mañana", 6, 12), ("tarde", 12, 19), ("noche", 19, 24)]


def obtener_clima(lugar):
    """Pronóstico de 7 días + detalle por franjas del día de hoy.

    Así el mismo conjunto de datos sirve para preguntas sobre la semana,
    sobre hoy o sobre la tarde, sin tener que cambiar el código.
    """
    params = {
        "latitude": lugar["lat"],
        "longitude": lugar["lon"],
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "hourly": "temperature_2m,precipitation_probability",
        "timezone": "auto",
        "forecast_days": 7,
    }
    try:
        r = requests.get(URL_CLIMA, params=params, timeout=15)
        r.raise_for_status()
        datos = r.json()
        diario = datos["daily"]
        horario = datos["hourly"]

        dias = []
        for i, fecha in enumerate(diario["time"]):
            nombre = DIAS[datetime.strptime(fecha, "%Y-%m-%d").weekday()]
            dias.append(
                {
                    "fecha": fecha,
                    "dia": nombre,
                    "tmin": diario["temperature_2m_min"][i],
                    "tmax": diario["temperature_2m_max"][i],
                    "prob_lluvia": diario["precipitation_probability_max"][i],
                }
            )

        # Detalle de hoy por franja (las primeras 24 horas del pronóstico)
        temps = horario["temperature_2m"][:24]
        probs = horario["precipitation_probability"][:24]
        franjas = []
        for nombre, ini, fin in FRANJAS:
            t = [x for x in temps[ini:fin] if x is not None]
            p = [x for x in probs[ini:fin] if x is not None]
            if t and p:
                franjas.append(
                    {"franja": nombre, "tmin": min(t), "tmax": max(t), "prob_lluvia": max(p)}
                )
        return {"dias": dias, "franjas_hoy": franjas}
    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"No se pudo consultar el clima: {error}")
    except (KeyError, IndexError, ValueError, TypeError):
        raise RuntimeError("La respuesta de la API del clima no tiene el formato esperado.")


def armar_prompt(lugar, clima):
    """Pregunta del usuario + datos del clima como contexto.

    La pregunta se escribe aquí abajo; los datos se agregan automáticamente.
    Cómo responder va en INSTRUCCIONES_SISTEMA.
    """
    # ============ ESCRIBE TU PREGUNTA AQUÍ ============
    # Ejemplos:
    #   "¿Cómo estará el clima durante la semana?"
    #   "¿Cómo estará el clima hoy en la tarde?"
    #   "¿Qué día de esta semana es mejor para salir a caminar?"
    pregunta = "¿Como estara el clima durante el resto del dia?"
    # ===================================================
    hoy = clima["dias"][0]
    lineas = [
        f"{pregunta}",
        "",
        f"Datos del clima en {lugar['nombre']}, {lugar['pais']} "
        f"(hoy es {hoy['dia']} {hoy['fecha']}):",
        "Pronóstico de los próximos 7 días:",
    ]
    for d in clima["dias"]:
        lineas.append(
            f"- {d['dia']} {d['fecha']}: mín {d['tmin']} °C, máx {d['tmax']} °C, "
            f"prob. de lluvia {d['prob_lluvia']}%"
        )
    lineas.append("Detalle de hoy por franja horaria:")
    for f in clima["franjas_hoy"]:
        lineas.append(
            f"- {f['franja']}: {f['tmin']} a {f['tmax']} °C, prob. de lluvia {f['prob_lluvia']}%"
        )
    return "\n".join(lineas)


# ---------------------------------------------------------------------------
# Funciones de conexión con Gemini
# ---------------------------------------------------------------------------
def armar_peticion(modelo, pregunta):
    if not pregunta:
        raise ValueError("La pregunta no puede estar vacía.")
    # La clave va en el header (no en la URL) para que no quede en logs ni errores.
    url = f"{URL_BASE}{modelo}:generateContent"
    headers = {"x-goog-api-key": API_KEY}
    body = {
        "system_instruction": {"parts": [{"text": INSTRUCCIONES_SISTEMA}]},
        "contents": [{"parts": [{"text": pregunta}]}],
    }
    return url, headers, body


def enviar_peticion(url, headers, body):
    try:
        respuesta = requests.post(url, headers=headers, json=body, timeout=30)
    except requests.exceptions.Timeout:
        raise RuntimeError("La solicitud excedió el tiempo de espera.")
    except requests.exceptions.ConnectionError:
        raise RuntimeError("No se pudo conectar al servidor.")

    if respuesta.status_code != 200:
        raise RuntimeError(
            f"Error HTTP {respuesta.status_code}: {respuesta.text[:150]}"
        )

    try:
        return respuesta.json()
    except ValueError:
        raise RuntimeError("La respuesta del servidor no es un JSON válido.")


def extraer_texto(datos):
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("La respuesta no trae el texto en el lugar esperado.")


def calcular_costo(datos, precio_entrada, precio_salida):
    try:
        uso = datos["usageMetadata"]
        tokens_entrada = uso["promptTokenCount"]
        # Los modelos con "thinking" cobran los tokens de razonamiento como salida
        tokens_salida = uso.get("candidatesTokenCount", 0) + uso.get(
            "thoughtsTokenCount", 0
        )
    except (KeyError, TypeError):
        raise RuntimeError("La respuesta no trae información de uso (tokens).")
    return tokens_entrada * precio_entrada + tokens_salida * precio_salida


def vista_previa(texto):
    """Deja la respuesta en una sola línea y la recorta."""
    limpio = " ".join(texto.split())
    if len(limpio) > LARGO_VISTA_PREVIA:
        return limpio[:LARGO_VISTA_PREVIA] + "..."
    return limpio


# ---------------------------------------------------------------------------
# Una prueba individual
# ---------------------------------------------------------------------------
def ejecutar_prueba(modelo, precios, pregunta):
    """Devuelve un diccionario con el resultado de una sola petición."""
    inicio = time.perf_counter()
    try:
        url, headers, body = armar_peticion(modelo, pregunta)
        datos = enviar_peticion(url, headers, body)
        latencia = time.perf_counter() - inicio
        costo = calcular_costo(datos, precios["entrada"], precios["salida"])
        texto = extraer_texto(datos)
        return {"ok": True, "latencia": latencia, "costo": costo, "respuesta": texto}
    except (ValueError, RuntimeError) as error:
        latencia = time.perf_counter() - inicio
        return {"ok": False, "latencia": latencia, "costo": 0.0, "error": str(error)}


# ---------------------------------------------------------------------------
# Resumen por modelo
# ---------------------------------------------------------------------------
def resumir(resultados):
    exitosos = [r for r in resultados if r["ok"]]
    n_ok = len(exitosos)
    resumen = {
        "total": len(resultados),
        "exitosas": n_ok,
        "fallidas": len(resultados) - n_ok,
        "latencia_prom": None,
        "costo_prom": None,
        "costo_total": sum(r["costo"] for r in exitosos),
    }
    # Los promedios se calculan solo con las pruebas que funcionaron
    if n_ok:
        resumen["latencia_prom"] = sum(r["latencia"] for r in exitosos) / n_ok
        resumen["costo_prom"] = resumen["costo_total"] / n_ok
    return resumen


def imprimir_resumen(modelo, resumen):
    print(f"\n  >> Resumen {modelo}")
    print(
        f"     Resultado: {resumen['exitosas']} de {resumen['total']} pruebas exitosas "
        f"({resumen['fallidas']} fallaron)"
    )
    if resumen["exitosas"]:
        print(f"     Latencia promedio: {resumen['latencia_prom']:.2f} s")
        print(f"     Costo promedio:    ${resumen['costo_prom']:.6f} USD")
    else:
        print("     Sin datos para promediar (todas fallaron).")


def imprimir_tabla_final(resumenes):
    print("\n" + "=" * 78)
    print("COMPARACIÓN FINAL")
    print("=" * 78)
    print(f"{'Modelo':<24}{'Exitosas':<12}{'Latencia prom.':<18}{'Costo prom. (USD)'}")
    print("-" * 78)
    for modelo, r in resumenes.items():
        exitos = f"{r['exitosas']}/{r['total']}"
        lat = f"{r['latencia_prom']:.2f} s" if r["latencia_prom"] is not None else "—"
        costo = f"${r['costo_prom']:.6f}" if r["costo_prom"] is not None else "—"
        print(f"{modelo:<24}{exitos:<12}{lat:<18}{costo}")
    print("=" * 78)
    print("Recuerda: además de latencia y costo, compara la calidad de las respuestas.")


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
def main():
    try:
        lugar = buscar_lugar(CIUDAD, CODIGO_PAIS)
        clima = obtener_clima(lugar)
    except RuntimeError as error:
        print("No se pudo preparar la prueba:", error)
        return

    prompt = armar_prompt(lugar, clima)
    print(f"Instrucciones de sistema:\n{INSTRUCCIONES_SISTEMA}\n")
    print(f"Prompt:\n{prompt}\n")
    resumenes = {}

    for modelo, precios in MODELOS.items():
        print("=" * 78)
        print(f"MODELO: {modelo}")
        print("=" * 78)
        resultados = []

        for i in range(1, REPETICIONES + 1):
            r = ejecutar_prueba(modelo, precios, prompt)
            resultados.append(r)

            if r["ok"]:
                print(
                    f"  Prueba {i}: OK    | {r['latencia']:.2f} s | "
                    f"${r['costo']:.6f} | {vista_previa(r['respuesta'])}"
                )
            else:
                print(f"  Prueba {i}: FALLÓ | {r['latencia']:.2f} s | {r['error']}")

            if i < REPETICIONES:
                time.sleep(PAUSA_ENTRE_PRUEBAS)

        resumenes[modelo] = resumir(resultados)
        imprimir_resumen(modelo, resumenes[modelo])
        print()

    imprimir_tabla_final(resumenes)


if __name__ == "__main__":
    main()