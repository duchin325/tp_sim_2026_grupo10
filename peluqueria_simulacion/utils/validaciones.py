from typing import Tuple

def validar_entero_positivo(valor: str, nombre_campo: str) -> Tuple[bool, str]:
    """
    Verifica que `valor` sea un entero mayor a 0.
    Retorna (True, "") si es válido, o (False, mensaje_error) si no lo es.
    """
    try:
        numero = int(valor)
    except ValueError:
        return False, f"El campo '{nombre_campo}' debe ser un número entero."
    if numero <= 0:
        return False, f"El campo '{nombre_campo}' debe ser mayor a 0."
    return True, ""


def validar_entero_no_negativo(valor: str, nombre_campo: str) -> Tuple[bool, str]:
    """
    Verifica que `valor` sea un entero >= 0.
    Retorna (True, "") si es válido, o (False, mensaje_error) si no lo es.
    """
    try:
        numero = int(valor)
    except ValueError:
        return False, f"El campo '{nombre_campo}' debe ser un número entero."
    if numero < 0:
        return False, f"El campo '{nombre_campo}' no puede ser negativo."
    return True, ""


def validar_float_positivo(valor: str, nombre_campo: str) -> Tuple[bool, str]:
    """
    Verifica que `valor` sea un float mayor a 0.
    Retorna (True, "") si es válido, o (False, mensaje_error) si no lo es.
    """
    try:
        numero = float(valor)
    except ValueError:
        return False, f"El campo '{nombre_campo}' debe ser un número."
    if numero <= 0:
        return False, f"El campo '{nombre_campo}' debe ser mayor a 0."
    return True, ""


def validar_float_no_negativo(valor: str, nombre_campo: str) -> Tuple[bool, str]:
    """
    Verifica que `valor` sea un float >= 0.
    Retorna (True, "") si es válido, o (False, mensaje_error) si no lo es.
    """
    try:
        numero = float(valor)
    except ValueError:
        return False, f"El campo '{nombre_campo}' debe ser un número."
    if numero < 0:
        return False, f"El campo '{nombre_campo}' no puede ser negativo."
    return True, ""


def validar_porcentajes(porc_colorista_str: str, porc_peluquero_a_str: str) -> Tuple[bool, str]:
    """
    Valida los porcentajes de atención.
    - Ambos deben ser números entre 0 y 100.
    - La suma no debe superar 100.
    """
    try:
        porc_col = float(porc_colorista_str)
    except ValueError:
        return False, "El campo '% Colorista' debe ser un número."
    try:
        porc_pa = float(porc_peluquero_a_str)
    except ValueError:
        return False, "El campo '% Peluquero A' debe ser un número."

    if porc_col < 0 or porc_col > 100:
        return False, "El '% Colorista' debe estar entre 0 y 100."
    if porc_pa < 0 or porc_pa > 100:
        return False, "El '% Peluquero A' debe estar entre 0 y 100."
    if porc_col + porc_pa > 100:
        return False, f"La suma de % Colorista ({porc_col}) + % Peluquero A ({porc_pa}) no puede superar 100."

    return True, ""


def validar_limites_llegada(a_str: str, b_str: str) -> Tuple[bool, str]:
    """
    Valida los límites A y B de la distribución uniforme de llegadas.
    - Ambos deben ser positivos.
    - A debe ser menor que B.
    """
    try:
        a = float(a_str)
    except ValueError:
        return False, "El campo 'A (Llegada mín)' debe ser un número."
    try:
        b = float(b_str)
    except ValueError:
        return False, "El campo 'B (Llegada máx)' debe ser un número."

    if a < 0:
        return False, "'A (Llegada mín)' no puede ser negativo."
    if b <= 0:
        return False, "'B (Llegada máx)' debe ser mayor a 0."
    if a >= b:
        return False, f"'A' ({a}) debe ser menor que 'B' ({b})."

    return True, ""


def validar_t_euler(t_col_str: str, t_pel_str: str) -> Tuple[bool, str]:
    """
    Valida los valores de T para el método de Euler.
    Ambos deben ser enteros positivos.
    """
    valido, error = validar_entero_positivo(t_col_str, "T Colorista")
    if not valido:
        return False, error
    valido, error = validar_entero_positivo(t_pel_str, "T Peluqueros")
    if not valido:
        return False, error
    return True, ""


def validar_inputs_simulacion(n_dias: str, x_cola: str, h_euler: str,
                               hora_j: str, iter_i: str) -> Tuple[bool, str]:
    """
    Valida los campos de entrada básicos de la simulación.
    Retorna (True, "") si son válidos, o (False, primer_error) si alguno falla.
    """
    valido, error = validar_entero_positivo(n_dias, "Días a simular (N)")
    if not valido:
        return False, error

    valido, error = validar_entero_no_negativo(x_cola, "Umbral cola (X)")
    if not valido:
        return False, error

    valido, error = validar_float_positivo(h_euler, "Paso Euler (h)")
    if not valido:
        return False, error

    valido, error = validar_entero_no_negativo(hora_j, "Hora desde (j)")
    if not valido:
        return False, error

    valido, error = validar_entero_positivo(iter_i, "Iteraciones a mostrar (i)")
    if not valido:
        return False, error

    return True, ""
