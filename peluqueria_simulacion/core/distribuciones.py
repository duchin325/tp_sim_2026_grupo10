import random

# Probabilidades de tipo de cliente (deben sumar 1.0)
PROB_COLORISTA = 0.15
PROB_PELUQUERO_A = 0.45
PROB_PELUQUERO_B = 0.40

# Límites de la distribución de llegadas
LLEGADA_MIN = 2
LLEGADA_MAX = 5


def generar_tiempo_llegada() -> float:
    """Tiempo entre llegadas consecutivas: U(2, 12) minutos."""
    return random.uniform(LLEGADA_MIN, LLEGADA_MAX)


def seleccionar_tipo_cliente() -> str:
    """
    Retorna el tipo de servidor que requiere el cliente:
      - "colorista"   con probabilidad 15%
      - "peluquero_a" con probabilidad 45%
      - "peluquero_b" con probabilidad 40%
    """
    rnd = random.random()
    if rnd < PROB_COLORISTA:
        return "colorista"
    elif rnd < PROB_COLORISTA + PROB_PELUQUERO_A:
        return "peluquero_a"
    else:
        return "peluquero_b"
