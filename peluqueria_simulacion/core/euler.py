"""
Ecuación diferencial: dD/dt = C + 0.2·T + t²
"""

T_COLORISTA = 180
T_PELUQUEROS = 130

def derivada_demora(t: float, D: float, C: int, T: int) -> float:

    return C + 0.2 * T + t ** 2

def integrar_euler(f, t0: float, D0: float, h: float, pasos: int, C: int, T: int):
    t = t0
    D = D0
    historial = []

    for _ in range(pasos):
        derivada = f(t, D, C, T)

        historial.append({
            "t": round(t, 4),
            "D": round(D, 4),
            "dD/dt": round(derivada, 4)
        })
        
        # Fórmula de Euler: y_(n+1) = y_n + h * f(t_n, y_n)
        D = D + h * derivada
        t = t + h

    historial.append({
        "t": round(t, 4),
        "D": round(D, 4),
        "dD/dt": round(f(t, D, C, T), 4)
    })

    return D, historial

def calcular_demora_corte_euler(tipo_servidor: str, longitud_cola_inicial: int, h: float, pasos: int) -> tuple[float, list]:

    if tipo_servidor == "colorista":
        T = T_COLORISTA
    elif tipo_servidor in ("peluquero_a", "peluquero_b"):
        T = T_PELUQUEROS
    else:
        raise ValueError(f"Tipo de servidor desconocido: '{tipo_servidor}'")

    C = longitud_cola_inicial
    t0 = 0.0
    D0 = 0.0  

    demora_final, historial_integracion = integrar_euler(derivada_demora, t0, D0, h, pasos, C, T)
    
    return demora_final, historial_integracion