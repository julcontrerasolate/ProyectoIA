# ProyectoIA: asistente del clima con Gemini

Miniaplicación en Python que consulta el pronóstico del clima de una ciudad y se lo entrega a un modelo de Gemini, que responde en español, de forma breve y con una recomendación (paraguas, abrigo, etc.).

Proyecto de Julio Contreras para la Especialización en Desarrollo con IA Generativa (Accenture).

## Estado del proyecto

> **Este proyecto está en desarrollo.** Lo que ves aquí es una versión temporal: se irán agregando más funciones y el contenido de este README cambiará a medida que avance el programa.

**Lo que hay por ahora:**

- Consulta del clima de una ciudad (Open-Meteo) y respuesta en lenguaje natural con Gemini.
- Comparación de modelos de Gemini (éxito, latencia y costo) con datos reales.
- Decisión de arquitectura documentada: por el momento se usa `gemini-3.6-flash`, pero la decisión no es definitiva.
- Banco de prompts con registro de consistencia, y pruebas básicas.

**Lo que se planea a futuro (ideas, aún no implementadas):**

- Una página web tipo Google Earth, pero con datos del clima.
- Explorar fenómenos climáticos como El Niño.
- Reevaluar el modelo a medida que el proyecto crezca (costo, calidad y nuevos modelos disponibles).

## Qué hace

1. Convierte el nombre de una ciudad en coordenadas (API de geocodificación de Open-Meteo, gratis y sin clave).
2. Obtiene el pronóstico de 7 días y el detalle de hoy por franja horaria (Open-Meteo).
3. Arma un prompt con la pregunta del usuario y esos datos.
4. Envía el prompt a la API de Gemini, con las instrucciones de personalidad separadas (`system_instruction`).
5. Muestra la respuesta, la latencia y el costo estimado de cada petición.

## Requisitos

- Python 3.10 o superior
- Una clave de API de Gemini (se obtiene en [Google AI Studio](https://aistudio.google.com/))
- Conexión a internet

## Instalación

Los comandos son para Windows (PowerShell o CMD). En macOS o Linux usa `python3` y `source venv/bin/activate`.

1. Clona el repositorio:

   ```
   git clone https://github.com/julcontrerasolate/ProyectoIA.git
   cd ProyectoIA
   ```

2. Crea y activa el entorno virtual:

   ```
   py -m venv venv
   venv\Scripts\activate
   ```

3. Instala las dependencias:

   ```
   pip install -r requirements.txt
   ```

4. Configura tus credenciales. Copia la plantilla y completa tu clave real:

   ```
   copy .env.example .env
   ```

   Luego abre `.env` y escribe tu clave:

   ```
   GEMINI_API_KEY=tu_clave_aqui
   ```

   El archivo `.env` nunca se sube al repositorio: está excluido en `.gitignore`.

## Cómo ejecutarlo

Desde la raíz del proyecto, con el entorno virtual activado:

```
py src/prueba_gemini_clima_santiago.py
```

El script consulta el clima de Santiago, Chile, y prueba varios modelos de Gemini con la misma pregunta, repitiendo cada prueba 4 veces. Al final imprime una tabla comparativa con éxito, latencia y costo promedio por modelo.

### Cambiar la ciudad

Por defecto usa Santiago (CL). Puedes cambiarla agregando estas variables a tu `.env`:

```
CIUDAD=Valparaíso
CODIGO_PAIS=CL
```

### Cambiar la pregunta

La pregunta se escribe en la función `armar_prompt` del script, en la variable `pregunta`.

## Estructura del proyecto

```
ProyectoIA/
├── docs/        Diagrama de arquitectura y decisión de modelo
├── src/         Código fuente (consumo de la API, prompts, pruebas de modelos)
├── tests/       Pruebas del código
├── .env.example Plantilla de variables de entorno (sin valores reales)
├── .gitignore   Archivos excluidos (incluye .env y el entorno virtual)
└── requirements.txt
```

### Módulos principales de `src/`

- `armar_peticion`, `enviar_peticion` y `extraer_texto`: funciones separadas que construyen la solicitud, la envían con manejo de errores (timeout, conexión, HTTP, JSON inválido) y extraen el texto de la respuesta.
- `prompts/`: banco de prompts y registro de la consistencia de cada uno.
- `excepciones.py`: errores propios del proyecto.

## Documentación

- [Decisión de arquitectura](docs/decision-arquitectura.md): modelo elegido (`gemini-3.6-flash`), tabla comparativa con datos reales, justificación y alternativa descartada.
- Diagrama de arquitectura: [docs/diagrama.drawio.png](docs/diagrama.drawio.png)

## Seguridad

- Ninguna clave va escrita en el código ni en archivos versionados.
- `.env` está en `.gitignore`; solo se sube `.env.example`, sin valores reales.
- La clave se envía en el header `x-goog-api-key`, no en la URL, para que no quede en logs ni mensajes de error.

## Problemas frecuentes

- **"No se encontró la clave API":** revisa que exista el archivo `.env` en la raíz y que tenga `GEMINI_API_KEY=...`.
- **Timeout en un modelo:** la API de Gemini puede tardar o estar saturada. Vuelve a ejecutar; en las pruebas, algunos modelos fallaron de forma intermitente.
- **Error HTTP 404 o 400:** verifica que el nombre del modelo en el script exista en la [documentación de Google](https://ai.google.dev/gemini-api/docs/models).