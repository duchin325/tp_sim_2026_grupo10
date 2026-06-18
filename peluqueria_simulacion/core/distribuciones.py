import random


def generar_tiempo_llegada() -> float:
    # TODO: Distribución U(2, 12) — uniforme entre 2 y 12 minutos
    return random.uniform(2, 12)


def generar_tiempo_colorista() -> float:
    # TODO: Distribución U(30, 50) — uniforme entre 30 y 50 minutos
    return random.uniform(30, 50)


def generar_tiempo_peluquero_a() -> float:
    # TODO: Distribución U(21, 25) — uniforme entre 21 y 25 minutos
    return random.uniform(21, 25)


def generar_tiempo_peluquero_b() -> float:
    # TODO: Distribución U(22, 38) — uniforme entre 22 y 38 minutos
    return random.uniform(22, 38)


def seleccionar_tipo_cliente() -> str:
    # TODO: 15% colorista, 40% peluquero A, 45% peluquero B
    rnd = random.random()
    if rnd < 0.15:
        return "colorista"
    elif rnd < 0.55:
        return "peluquero_a"
    else:
        return "peluquero_b"
