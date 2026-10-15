# ==========================================
# CÓDIGO REFACTORIZADO
# ==========================================

def calcular_precio_final(precio_base, tipo_cliente):
    # Cambiamos números mágicos (1 y 2) por nombres claros de texto
    # Centralizamos el porcentaje de descuento en una sola variable
    if tipo_cliente == "NORMAL":
        porcentaje_descuento = 0.10
    elif tipo_cliente == "VIP":
        porcentaje_descuento = 0.25
    else:
        porcentaje_descuento = 0.0

    # Toda la matemática y los prints se hacen una sola vez al final
    ahorro = precio_base * porcentaje_descuento
    precio_neto = precio_base - ahorro

    print("--- Nueva versión refactorizada ---")
    print(f"Cliente: {tipo_cliente}")
    print(f"Precio Base: ${precio_base:.2f}")
    print(f"Descuento:   ${ahorro:.2f} ({porcentaje_descuento * 100}%)")
    print(f"Neto a Pagar:${precio_neto:.2f}\n")
    
    return precio_neto

# Pruebas en terminal (ahora usando palabras en lugar de números)
calcular_precio_final(100, "NORMAL")
calcular_precio_final(100, "VIP")
calcular_precio_final(100, "INVITADO")
