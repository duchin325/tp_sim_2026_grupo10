def validar_entero_positivo(valor: str, nombre_campo: str) -> tuple[bool, str]:
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


def validar_entero_no_negativo(valor: str, nombre_campo: str) -> tuple[bool, str]:
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


def validar_float_positivo(valor: str, nombre_campo: str) -> tuple[bool, str]:
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


def validar_inputs_simulacion(n_dias: str, x_cola: str, h_euler: str,
                               hora_j: str, iter_i: str) -> tuple[bool, str]:
    """
    Valida los campos de entrada de la simulación.
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
