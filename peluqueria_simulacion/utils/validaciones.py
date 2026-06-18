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


def validar_inputs_simulacion(dias: str, x: str) -> tuple[bool, str]:
    """
    Valida los campos de entrada de la simulación (días y X).
    La validación de 'filas por página' se hace por separado en la UI
    usando validar_entero_positivo(), porque es un parámetro de display, no de simulación.
    Retorna (True, "") si son válidos, o (False, primer_error) si alguno falla.
    """
    valido, error = validar_entero_positivo(dias, "Días a simular")
    if not valido:
        return False, error

    valido, error = validar_entero_no_negativo(x, "Valor de X")
    if not valido:
        return False, error

    return True, ""
