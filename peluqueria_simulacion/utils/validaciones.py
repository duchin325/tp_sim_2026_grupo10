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


def validar_inputs_simulacion(dias: str, x: str, cantidad_filas: str) -> tuple[bool, str]:
    """
    Valida todos los campos de entrada de la UI antes de llamar a la simulación.
    Retorna (True, "") si todos son válidos, o (False, primer_error) si alguno falla.
    """
    for valor, nombre in [(dias, "Días a simular"), (cantidad_filas, "Cantidad de filas")]:
        valido, error = validar_entero_positivo(valor, nombre)
        if not valido:
            return False, error

    valido, error = validar_entero_no_negativo(x, "Valor de X")
    if not valido:
        return False, error

    return True, ""
