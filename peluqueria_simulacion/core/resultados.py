from typing import List
from core.entidades import ResultadoDia


def calcular_promedio_recaudacion(resultados: List[ResultadoDia]) -> float:
    # TODO: Calcular el promedio de recaudación diaria sobre todos los días simulados
    if not resultados:
        return 0.0
    return sum(r.recaudacion for r in resultados) / len(resultados)


def calcular_probabilidad_mas_de_x(resultados: List[ResultadoDia], x: int) -> float:
    # TODO: Calcular la proporción de eventos en que la cola de espera superó X personas
    # Se debe recorrer la tabla de filas de cada día y contar cuántas veces la cola > x
    if not resultados:
        return 0.0
    return 0.0


def calcular_total_clientes_atendidos(resultados: List[ResultadoDia]) -> int:
    # TODO: Sumar clientes atendidos en todos los días simulados
    return sum(r.clientes_atendidos for r in resultados)


def calcular_total_bebidas(resultados: List[ResultadoDia]) -> int:
    # TODO: Sumar bebidas entregadas en todos los días simulados
    return sum(r.bebidas_entregadas for r in resultados)


def calcular_costo_total_bebidas(resultados: List[ResultadoDia]) -> float:
    # TODO: Sumar el costo de bebidas de todos los días simulados
    return sum(r.costo_bebidas for r in resultados)


def generar_resumen(resultados: List[ResultadoDia], x: int) -> dict:
    # TODO: Consolidar todos los indicadores en un único diccionario de resultados
    return {
        "promedio_recaudacion": calcular_promedio_recaudacion(resultados),
        "probabilidad_mas_de_x": calcular_probabilidad_mas_de_x(resultados, x),
        "clientes_atendidos": calcular_total_clientes_atendidos(resultados),
        "bebidas_entregadas": calcular_total_bebidas(resultados),
        "costo_total_bebidas": calcular_costo_total_bebidas(resultados),
    }
