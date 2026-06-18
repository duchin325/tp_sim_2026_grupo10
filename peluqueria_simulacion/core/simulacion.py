from typing import List
from core.entidades import ResultadoDia


def simular(dias: int, x: int, cantidad_filas: int) -> dict:
    """
    Punto de entrada principal de la simulación.

    Parámetros:
        dias          -- cantidad de días a simular
        x             -- umbral para calcular P(cola > x personas)
        cantidad_filas -- número de filas/eventos a incluir en la tabla de salida

    Retorna un diccionario con los resultados agregados y las filas para la tabla.
    """
    # TODO: Ejecutar _simular_dia() para cada día y acumular ResultadoDia en una lista
    resultados: List[ResultadoDia] = []
    for numero_dia in range(1, dias + 1):
        resultado = _simular_dia(numero_dia, cantidad_filas)
        resultados.append(resultado)

    # TODO: Llamar a core.resultados.generar_resumen() con la lista de ResultadoDia
    # Por ahora se devuelven valores mock para que la UI pueda renderizarse
    filas_mock = _generar_filas_mock(cantidad_filas)

    return {
        "promedio_recaudacion": 0.0,       # TODO: reemplazar con valor real
        "probabilidad_mas_de_x": 0.0,      # TODO: reemplazar con valor real
        "clientes_atendidos": 0,            # TODO: reemplazar con valor real
        "bebidas_entregadas": 0,            # TODO: reemplazar con valor real
        "costo_total_bebidas": 0.0,         # TODO: reemplazar con valor real
        "filas_tabla": filas_mock,
    }


def _simular_dia(numero_dia: int, cantidad_filas: int) -> ResultadoDia:
    """
    Simula un único día de operación de la peluquería.

    El día tiene dos fases:
      1. Recepción activa: 8 horas (480 minutos) en que llegan nuevos clientes.
      2. Cierre: se deja de recibir clientes pero se atiende a todos los que quedaron.
    """
    resultado = ResultadoDia(numero_dia=numero_dia)

    # TODO: Inicializar el reloj de simulación en 0
    # TODO: Inicializar la lista de eventos con el primer evento de llegada
    # TODO: Inicializar los 3 servidores (Colorista, Peluquero A, Peluquero B)
    # TODO: Inicializar las colas de espera para cada servidor
    # TODO: Inicializar contadores (recaudación, bebidas, etc.)

    # TODO: Bucle principal — mientras haya eventos en la lista:
    #   - Extraer el evento de menor tiempo (priority queue)
    #   - Avanzar el reloj al tiempo del evento
    #   - Si es "llegada":
    #       - Determinar tipo de cliente (seleccionar_tipo_cliente)
    #       - Asignar a servidor libre o encolar
    #       - Si tiempo_reloj < 480 min: generar próxima llegada y agregarla
    #   - Si es "fin_atencion_*":
    #       - Registrar cliente finalizado (recaudación, bebida)
    #       - Si hay cola: asignar el siguiente cliente al servidor
    #       - Si no: marcar servidor como libre
    #   - Guardar snapshot del estado en resultado.filas_tabla si corresponde

    return resultado


def _generar_filas_mock(cantidad_filas: int) -> list:
    """Genera filas de ejemplo para mostrar en la tabla mientras no hay simulación real."""
    columnas = [
        "Evento", "Reloj", "RND Llegada", "Próx. Llegada",
        "Colorista Estado", "Colorista Fin", "Cola Colorista",
        "Pel.A Estado", "Pel.A Fin", "Cola Pel.A",
        "Pel.B Estado", "Pel.B Fin", "Cola Pel.B",
    ]
    filas = [columnas]
    for i in range(1, cantidad_filas + 1):
        fila = [str(i), "-", "-", "-", "Libre", "-", "0", "Libre", "-", "0", "Libre", "-", "0"]
        filas.append(fila)
    return filas
