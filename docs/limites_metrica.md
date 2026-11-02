# Límites de la métrica de evaluación

## Qué mide

Cuenta cuántas palabras de la respuesta aparecen también en la
respuesta de referencia. Con eso calcula precisión, cobertura y F1.
No entiende el significado, solo compara palabras.

## Modos de falla conocidos

- **Respuestas correctas con puntaje bajo.** Si el modelo repite
  los datos de la pregunta o usa otras palabras, el F1 baja aunque
  esté bien. Ejemplo: "Sí, lleva abrigo porque la mínima será de
  4 °C y la máxima de 15 °C" sacó 0.31 y era correcta. "No es
  posible saberlo porque los datos solo muestran temperatura y
  probabilidad de lluvia" sacó 0.25 y también.
- **Respuestas incompletas que no se distinguen.** Ante "¿Qué me
  recomiendas?" con 33 °C, el modelo solo repitió la temperatura
  y no recomendó nada. Sacó 0.0, pero la métrica no distingue
  una respuesta vacía de una correcta con otras palabras.
- **Errores con puntaje medio.** A "¿Va a llover a comienzos de
  semana?" con 10%, 15% y 5%, el modelo respondió "Sí, lloverá".
  Es falso y contradice la referencia, pero sacó 0.36, más que
  cuatro respuestas correctas de la muestra. Se repitió en las
  tres corridas.
- **Matices que cambian el tono.** Ante 90% de lluvia, el modelo
  dijo "No se puede asegurar, pero hay un 90%". No contradice la
  referencia ("Sí, es muy probable"), pero suena más dudosa, y
  sacó 0.18.

## Muestra revisada

Revisé a mano 10 casos de 23 respuestas generadas: los 5 con
menor F1 y los 5 con mayor F1, con la rúbrica de tres preguntas
(corrección factual, completitud, contradicción).

- En los 10 casos no encontré errores factuales ni
  contradicciones. De los 5 peores, 4 eran correctas y completas,
  y solo la de 33 °C era incompleta.
- Los 5 mejores eran todos correctos. No encontré un falso
  positivo en los extremos.
- El único error real de las 23 respuestas estaba en el medio
  del ranking (F1 0.36), y lo revisé aparte. Mirar solo los
  extremos no lo habría encontrado.

## Recomendación de uso

Usar el F1 solo para comparar muchas respuestas entre versiones
del cliente. Un F1 bajo no significa que la respuesta esté mal, y
un F1 medio no significa que esté bien. Revisar a mano las
respuestas con sí/no, cifras, días o recomendaciones, y no solo
las de F1 más bajo y más alto.
