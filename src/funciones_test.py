def suma(a, b):  # a = 5 , b = 6
    resultado = a + b
    return resultado  # return devuelve valor de retorno


print(suma(5, 6))

# El nombre de la estudiante
# La calificación del curso
# El titulo de la segunda tarea
# Si la primera tarea está completada

estudiante = {
    "nombre": "Ana",
    "edad": 24,
    "curso": {"nombre": "Python", "calificacion": 92},
    "tareas": [
        {"titulo": "Variables", "completada": True},
        {"titulo": "Consumo de APIs", "completada": False},
    ],
}

print(f"Nombre de la estudiante: {estudiante['nombre']}")  # El nombre de la estudiante
print(f"Calificación del curso: {estudiante['curso']['calificacion']}")  # La calificación del curso
print(f"Segunda tarea: {estudiante['tareas'][1]['titulo']}")  # El título de la segunda tarea

if estudiante["tareas"][0]["completada"]:  # Si la primera tarea está completada
    print("La primera tarea está completada.")
else:
    print("La primera tarea está pendiente.")




