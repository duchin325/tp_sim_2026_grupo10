import heapq
from core.entidades import ResultadoDia, Cliente, Servidor, Evento
from core.distribuciones import generar_tiempo_llegada, seleccionar_tipo_cliente
from core.euler import calcular_demora_corte_euler
from core.resultados import generar_resumen

DURACION_RECEPCION_MIN = 480   
TIEMPO_ESPERA_BEBIDA = 30      
PRECIO_COLORISTA = 35_000
PRECIO_PELUQUERO = 18_000
COSTO_BEBIDA = 6_500

def simular(dias: int, n_iteraciones: int, x: int, iteraciones_i: int, hora_inicio_j: float, paso_h: float) -> dict:
    resultados = []
    filas_tabla = []
    
    columnas = [
            "Nº Fila", "Día", "Evento", "Reloj", 
            "RND Lleg.", "Próx. Llegada", 
            "RND Tipo", "Serv. Elegido",
            "Color. Est", "Color. Fin", "Cola C",
            "Pel.A Est", "Pel.A Fin", "Cola A",
            "Pel.B Est", "Pel.B Fin", "Cola B",
            "Euler t", "Euler D", "Euler dD/dt",
            "Acum. Recaud.", "Cont. Clientes", "Cont. Bebidas"
    ]
    filas_tabla.append(columnas)
    
    reloj_global = 0.0
    filas_guardadas = 0

    # Contador global para el límite N
    iteraciones_totales = 0 
    limite_alcanzado = False
    ultima_fila = None

    # Parametrización de Euler (10 pasos como base temporal)
    PASOS_EULER = 10 

    for numero_dia in range(1, dias + 1):
        if limite_alcanzado:
            break

        reloj_dia = 0.0
        eventos = []
        
        colorista = Servidor("Colorista", "colorista")
        pel_a = Servidor("Peluquero A", "peluquero_a")
        pel_b = Servidor("Peluquero B", "peluquero_b")
        
        colas = {
            "colorista": [],
            "peluquero_a": [],
            "peluquero_b": []
        }
        
        resultado_dia = ResultadoDia(numero_dia=numero_dia)
        
        rnd_llegada, tiempo_llegada = generar_tiempo_llegada()
        prox_llegada = reloj_dia + tiempo_llegada
        heapq.heappush(eventos, Evento(prox_llegada, "llegada"))
        
        while eventos:
            if iteraciones_totales >= n_iteraciones:
                limite_alcanzado = True
                break

            evento = heapq.heappop(eventos)
            iteraciones_totales += 1
            reloj_dia = evento.tiempo
            reloj_global_actual = reloj_global + reloj_dia
            euler_t, euler_d, euler_deriv = "-", "-", "-"
            rnd_llegada_actual = "-" 
            rnd_tipo_actual = "-" 
            servidor_elegido_actual = "-"

            
            if evento.tipo == "llegada":
                if reloj_dia < DURACION_RECEPCION_MIN:
                    rnd_llegada_actual, t_llegada = generar_tiempo_llegada()
                    prox_llegada = reloj_dia + t_llegada
                    heapq.heappush(eventos, Evento(prox_llegada, "llegada"))
                else:
                    prox_llegada = "-"

                rnd_tipo_actual, tipo_req = seleccionar_tipo_cliente()
                if tipo_req == "colorista":
                    servidor_elegido_actual = "Colorista"
                elif tipo_req == "peluquero_a":
                    servidor_elegido_actual = "Pel. A"
                else:
                    servidor_elegido_actual = "Pel. B"
                nuevo_cliente = Cliente(numero=resultado_dia.clientes_atendidos + 1, tipo=tipo_req, tiempo_llegada=reloj_dia)
                
                # Asignación de servidor
                if tipo_req == "colorista":
                    srv_asignado = colorista
                elif tipo_req == "peluquero_a":
                    srv_asignado = pel_a
                else:
                    srv_asignado = pel_b
                    
                if not srv_asignado.ocupado:
                    srv_asignado.ocupado = True
                    nuevo_cliente.longitud_cola_al_inicio = 0
                    nuevo_cliente.tiempo_inicio_atencion = reloj_dia
                    
                    # Llamada numérica al integrador
                    demora, historial = calcular_demora_corte_euler(tipo_req, 0, paso_h, PASOS_EULER)
                    euler_t = historial[-1]['t']
                    euler_d = historial[-1]['D']
                    euler_deriv = historial[-1]['dD/dt']
                    
                    nuevo_cliente.demora_calculada = demora
                    tiempo_fin = reloj_dia + demora
                    srv_asignado.tiempo_libre = tiempo_fin  # Anotamos a qué hora se desocupará
                    heapq.heappush(eventos, Evento(tiempo_fin, f"fin_{tipo_req}", cliente=nuevo_cliente, servidor=srv_asignado))
                else:
                    colas[tipo_req].append(nuevo_cliente)
                    if len(colas[tipo_req]) > resultado_dia.max_cola_espera:
                        resultado_dia.max_cola_espera = len(colas[tipo_req])
                        
            elif evento.tipo.startswith("fin_"):
                cliente_saliente = evento.cliente
                srv_liberado = evento.servidor
                
                resultado_dia.clientes_atendidos += 1
                tiempo_espera = cliente_saliente.tiempo_inicio_atencion - cliente_saliente.tiempo_llegada
                
                if tiempo_espera > TIEMPO_ESPERA_BEBIDA:
                    resultado_dia.bebidas_entregadas += 1
                    resultado_dia.costo_bebidas += COSTO_BEBIDA
                    
                if cliente_saliente.tipo == "colorista":
                    resultado_dia.recaudacion += PRECIO_COLORISTA
                else:
                    resultado_dia.recaudacion += PRECIO_PELUQUERO
                    
                # Tirar de la cola si hay gente
                tipo_srv = srv_liberado.tipo
                if colas[tipo_srv]:
                    cliente_esperando = colas[tipo_srv].pop(0)
                    longitud_actual = len(colas[tipo_srv]) + 1 # +1 porque sacamos recién al que va a ser atendido
                    cliente_esperando.longitud_cola_al_inicio = longitud_actual
                    cliente_esperando.tiempo_inicio_atencion = reloj_dia
                    
                    demora, historial = calcular_demora_corte_euler(tipo_srv, longitud_actual, paso_h, PASOS_EULER)
                    euler_t = historial[-1]['t']
                    euler_d = historial[-1]['D']
                    euler_deriv = historial[-1]['dD/dt']
                    
                    tiempo_fin = reloj_dia + demora
                    srv_liberado.tiempo_libre = tiempo_fin
                    heapq.heappush(eventos, Evento(tiempo_fin, f"fin_{tipo_srv}", cliente=cliente_esperando, servidor=srv_liberado))
                else:
                    srv_liberado.ocupado = False
                    srv_liberado.tiempo_libre = 0.0

            # Construir la fila actual en TODAS las iteraciones
            fila_actual = [
                iteraciones_totales,
                numero_dia,
                evento.tipo,
                round(reloj_dia, 2),
                round(rnd_llegada_actual, 4) if isinstance(rnd_llegada_actual, float) else rnd_llegada_actual,
                round(prox_llegada, 2) if isinstance(prox_llegada, float) else prox_llegada,
                round(rnd_tipo_actual, 4) if isinstance(rnd_tipo_actual, float) else rnd_tipo_actual,
                servidor_elegido_actual,  # NUEVO: Queda pegado a su RND
                "Ocupado" if colorista.ocupado else "Libre",
                round(colorista.tiempo_libre, 2) if colorista.ocupado else "-", 
                len(colas["colorista"]),
                "Ocupado" if pel_a.ocupado else "Libre",
                round(pel_a.tiempo_libre, 2) if pel_a.ocupado else "-", 
                len(colas["peluquero_a"]),
                "Ocupado" if pel_b.ocupado else "Libre",
                round(pel_b.tiempo_libre, 2) if pel_b.ocupado else "-", 
                len(colas["peluquero_b"]),
                euler_t,
                euler_d,
                euler_deriv,
                resultado_dia.recaudacion,
                resultado_dia.clientes_atendidos,
                resultado_dia.bebidas_entregadas
            ]
            
            # Actualizar siempre la última fila conocida
            ultima_fila = list(fila_actual)

            # Guardar en la tabla SOLO si entra en los parámetros (i, j) solicitados
            if reloj_global_actual >= hora_inicio_j and filas_guardadas < iteraciones_i:
                filas_tabla.append(fila_actual)
                filas_guardadas += 1

        reloj_global += reloj_dia
        resultados.append(resultado_dia)

#Mostrar siempre la última fila
    if ultima_fila:
        ultima_fila[2] = "FIN SIMULACIÓN" 
        ultima_fila[17], ultima_fila[18], ultima_fila[19] = "-", "-", "-" 
        filas_tabla.append(ultima_fila)

    resumen = generar_resumen(resultados, x)
    resumen["filas_tabla"] = filas_tabla
    return resumen