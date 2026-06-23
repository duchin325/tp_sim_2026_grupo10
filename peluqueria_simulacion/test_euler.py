#!/usr/bin/env python3
"""
Script para testear los cálculos de Euler con diferentes tamaños de cola.
"""
from core.euler import calcular_demora_corte

print("=" * 70)
print("TEST DE CÁLCULOS EULER - DEMORA SEGÚN COLA (C)")
print("=" * 70)

# Parámetros de prueba
h_values = [10, 50, 100]  # Número de iteraciones
tipos = ["colorista", "peluquero_a"]
colas = [0, 1, 2, 5, 10]  # Diferentes tamaños de cola

for h in h_values:
    print(f"\n{'─' * 70}")
    print(f"h (iteraciones max) = {h}")
    print(f"{'─' * 70}")
    
    for tipo in tipos:
        print(f"\n{tipo.upper()}:")
        print(f"{'C (Cola)':<15} {'Demora (min)':<20} {'Pasos aprox':<15}")
        print(f"{'-'*50}")
        
        for c in colas:
            demora, pasos = calcular_demora_corte(tipo, c, h=h, con_detalle=True)
            num_pasos = len(pasos)
            print(f"{c:<15} {demora:<20.2f} {num_pasos:<15}")

print("\n" + "=" * 70)
print("CONCLUSIÓN: La demora debe AUMENTAR con la cola (C)")
print("Si no lo hace, hay un error en los cálculos")
print("=" * 70)
