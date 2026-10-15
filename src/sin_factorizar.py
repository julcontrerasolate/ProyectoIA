# ==========================================
# CÓDIGO ORIGINAL
# ==========================================

def calc(a, b):
    if b == 1:
        resultado = a - (a * 0.1)
        print("--- Ejecutando código antiguo ---")
        print("Cliente Tipo 1 detectado.")
        print(f"Precio inicial: ${a} | Descuento: 10% | Total: ${resultado}")
        return resultado
    elif b == 2:
        resultado = a - (a * 0.25)
        print("--- Ejecutando código antiguo ---")
        print("Cliente Tipo 2 detectado.")
        print(f"Precio inicial: ${a} | Descuento: 25% | Total: ${resultado}")
        return resultado
    
    print("--- Ejecutando código antiguo ---")
    print("Cliente Desconocido.")
    print(f"Precio inicial: ${a} | Descuento: 0% | Total: ${a}")
    return a

# Pruebas en terminal
calc(100, 1)
calc(100, 2)
calc(100, 3)
