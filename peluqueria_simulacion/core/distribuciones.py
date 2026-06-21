import random

PROB_COLORISTA = 0.15
PROB_PELUQUERO_A = 0.45
PROB_PELUQUERO_B = 0.40

LLEGADA_MIN = 2
LLEGADA_MAX = 12

def generar_tiempo_llegada() -> tuple[float, float]:
    """Retorna (rnd, tiempo_calculado)"""
    rnd = random.random()
    # Fórmula de la uniforme: a + rnd * (b - a)
    tiempo = LLEGADA_MIN + rnd * (LLEGADA_MAX - LLEGADA_MIN)
    return rnd, tiempo

def seleccionar_tipo_cliente() -> tuple[float, str]:
    """Retorna (rnd, tipo_servidor_elegido)"""
    rnd = random.random()
    if rnd < PROB_COLORISTA:
        return rnd, "colorista"
    elif rnd < PROB_COLORISTA + PROB_PELUQUERO_A:
        return rnd, "peluquero_a"
    else:
        return rnd, "peluquero_b"