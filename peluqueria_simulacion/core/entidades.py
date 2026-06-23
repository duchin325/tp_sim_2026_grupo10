from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Cliente:
    numero: int
    tipo: str  # "colorista", "peluquero_a", "peluquero_b"
    tiempo_llegada: float = 0.0
    tiempo_inicio_atencion: float = 0.0
    tiempo_fin_atencion: float = 0.0
    tiempo_espera: float = 0.0
    servidor_asignado: Optional[str] = None
    # Longitud de la cola del servidor asignado al momento de iniciar el corte (C en la ED)
    longitud_cola_al_inicio: int = 0
    # Resultado de la integración RK4: duración del corte en minutos
    demora_calculada: float = 0.0
    # True si esperó más de 30 minutos → recibe bebida gratis
    recibio_bebida: bool = False
    hora_refrigerio: float = 0.0
    en_cola: bool = False

@dataclass
class Servidor:
    nombre: str          # "Colorista", "Peluquero A", "Peluquero B"
    tipo: str            # "colorista", "peluquero_a", "peluquero_b"
    ocupado: bool = False
    tiempo_libre: float = 0.0
    clientes_atendidos: int = 0


@dataclass
class Evento:
    tiempo: float
    tipo: str            # "llegada", "fin_atencion_colorista", "fin_atencion_peluquero_a", "fin_atencion_peluquero_b" "refrigerio_cliente"
    cliente: Optional[Cliente] = None
    servidor: Optional[Servidor] = None

    def __lt__(self, otro: "Evento") -> bool:
        return self.tiempo < otro.tiempo


@dataclass
class ResultadoDia:
    numero_dia: int
    recaudacion: float = 0.0
    clientes_atendidos: int = 0
    bebidas_entregadas: int = 0
    costo_bebidas: float = 0.0
    max_cola_espera: int = 0
    # Lista de snapshots del estado de la simulación para la tabla de eventos
    filas_tabla: list = field(default_factory=list)
