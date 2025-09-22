
# -*- coding: utf-8 -*-
"""
Parámetros del análisis de sensibilidad para el parque.
Edita libremente los valores, probabilidades y horizontes.
Las cifras de 'npv' se interpretan como valores presentes (VPN) ya descontados.
Si prefieres modelar flujos y una tasa de descuento, puedes agregarlo aquí y
recalcular en main.py (este borrador usa directamente los VPN suministrados).
"""

# Tasa de descuento opcional para análisis alternativo (no usada en el cálculo base)
discount_rate = 0.12  # 12% anual (solo informativo en este borrador)

# Definición de actividades
# Cada actividad posee:
# - decision_key: nombre corto para la decisión binaria (1 = se mantiene / se invierte, 0 = no)
# - horizon_years: horizonte temporal de evaluación (informativo)
# - outcomes: lista de escenarios con 'label', 'prob' (0-1) y 'npv' (valor presente del resultado)
# - concesionado: True si es concesión, False si es administración propia
#
# Nota: Puedes ajustar probabilidades y montos. Deben sumar 1.0 por actividad.
# Las actividades están duplicadas: una versión concesionada y una propia (excepto señaléticas)
activities = [
    # Alojamiento (Lodge) - Administración Propia
    {
        "name": "Alojamiento (Lodge) - Propio",
        "decision_key": "lodge_propio",
        "horizon_years": 2,
        "concesionado": False,
        "outcomes": [
            {"label": "Éxito", "prob": 0.10, "npv": 100000.0},
            {"label": "Fracaso", "prob": 0.90, "npv": -10000.0},
        ],
    },
    # Alojamiento (Lodge) - Concesión
    {
        "name": "Alojamiento (Lodge) - Concesión",
        "decision_key": "lodge_concesion",
        "horizon_years": 2,
        "concesionado": True,
        "outcomes": [
            {"label": "Éxito", "prob": 0.10, "npv": 100000.0},
            {"label": "Fracaso", "prob": 0.90, "npv": -10000.0},
        ],
    },
    # Cabalgatas - Administración Propia
    {
        "name": "Cabalgatas - Propio",
        "decision_key": "cabalgatas_propio",
        "horizon_years": 3,
        "concesionado": False,
        "outcomes": [
            {"label": "Éxito", "prob": 0.30, "npv": 15000.0},
            {"label": "Fracaso", "prob": 0.70, "npv": -60000.0},
        ],
    },
    # Cabalgatas - Concesión
    {
        "name": "Cabalgatas - Concesión",
        "decision_key": "cabalgatas_concesion",
        "horizon_years": 3,
        "concesionado": True,
        "outcomes": [
            {"label": "Éxito", "prob": 0.30, "npv": 15000.0},
            {"label": "Fracaso", "prob": 0.70, "npv": -60000.0},
        ],
    },
    # Trekking - Administración Propia
    {
        "name": "Trekking - Propio",
        "decision_key": "trekking_propio",
        "horizon_years": 2,
        "concesionado": False,
        "outcomes": [
            {"label": "Éxito Alto", "prob": 0.20, "npv": 25000.0},
            {"label": "Éxito Moderado", "prob": 0.50, "npv": 8000.0},
            {"label": "Fracaso", "prob": 0.30, "npv": -12000.0},
        ],
    },
    # Trekking - Concesión
    {
        "name": "Trekking - Concesión",
        "decision_key": "trekking_concesion",
        "horizon_years": 2,
        "concesionado": True,
        "outcomes": [
            {"label": "Éxito Alto", "prob": 0.20, "npv": 25000.0},
            {"label": "Éxito Moderado", "prob": 0.50, "npv": 8000.0},
            {"label": "Fracaso", "prob": 0.30, "npv": -12000.0},
        ],
    },
    # Mountain Bike - Administración Propia
    {
        "name": "Mountain Bike - Propio",
        "decision_key": "mtb_propio",
        "horizon_years": 3,
        "concesionado": False,
        "outcomes": [
            {"label": "Éxito", "prob": 0.35, "npv": 30000.0},
            {"label": "Neutro", "prob": 0.25, "npv": 0.0},
            {"label": "Fracaso", "prob": 0.40, "npv": -20000.0},
        ],
    },
    # Mountain Bike - Concesión
    {
        "name": "Mountain Bike - Concesión",
        "decision_key": "mtb_concesion",
        "horizon_years": 3,
        "concesionado": True,
        "outcomes": [
            {"label": "Éxito", "prob": 0.35, "npv": 30000.0},
            {"label": "Neutro", "prob": 0.25, "npv": 0.0},
            {"label": "Fracaso", "prob": 0.40, "npv": -20000.0},
        ],
    },
    # Kayak - Administración Propia
    {
        "name": "Kayak - Propio",
        "decision_key": "kayak_propio",
        "horizon_years": 2,
        "concesionado": False,
        "outcomes": [
            {"label": "Éxito", "prob": 0.25, "npv": 18000.0},
            {"label": "Neutro", "prob": 0.25, "npv": 2000.0},
            {"label": "Fracaso", "prob": 0.50, "npv": -9000.0},
        ],
    },
    # Kayak - Concesión
    {
        "name": "Kayak - Concesión",
        "decision_key": "kayak_concesion",
        "horizon_years": 2,
        "concesionado": True,
        "outcomes": [
            {"label": "Éxito", "prob": 0.25, "npv": 18000.0},
            {"label": "Neutro", "prob": 0.25, "npv": 2000.0},
            {"label": "Fracaso", "prob": 0.50, "npv": -9000.0},
        ],
    },
    # Tours Guiados - Administración Propia
    {
        "name": "Tours Guiados - Propio",
        "decision_key": "tours_guiados_propio",
        "horizon_years": 3,
        "concesionado": False,
        "outcomes": [
            {"label": "Alta Demanda", "prob": 0.25, "npv": 35000.0},
            {"label": "Demanda Moderada", "prob": 0.45, "npv": 12000.0},
            {"label": "Baja Demanda", "prob": 0.30, "npv": -8000.0},
        ],
    },
    # Tours Guiados - Concesión
    {
        "name": "Tours Guiados - Concesión",
        "decision_key": "tours_guiados_concesion",
        "horizon_years": 3,
        "concesionado": True,
        "outcomes": [
            {"label": "Alta Demanda", "prob": 0.25, "npv": 35000.0},
            {"label": "Demanda Moderada", "prob": 0.45, "npv": 12000.0},
            {"label": "Baja Demanda", "prob": 0.30, "npv": -8000.0},
        ],
    },
    # Jornadas de Educación - Administración Propia
    {
        "name": "Jornadas de Educación - Propio",
        "decision_key": "jornadas_educacion_propio",
        "horizon_years": 2,
        "concesionado": False,
        "outcomes": [
            {"label": "Éxito Académico", "prob": 0.40, "npv": 20000.0},
            {"label": "Participación Regular", "prob": 0.35, "npv": 6000.0},
            {"label": "Baja Participación", "prob": 0.25, "npv": -15000.0},
        ],
    },
    # Jornadas de Educación - Concesión
    {
        "name": "Jornadas de Educación - Concesión",
        "decision_key": "jornadas_educacion_concesion",
        "horizon_years": 2,
        "concesionado": True,
        "outcomes": [
            {"label": "Éxito Académico", "prob": 0.40, "npv": 20000.0},
            {"label": "Participación Regular", "prob": 0.35, "npv": 6000.0},
            {"label": "Baja Participación", "prob": 0.25, "npv": -15000.0},
        ],
    },
    # Eventos Especiales - Administración Propia
    {
        "name": "Eventos Especiales - Propio",
        "decision_key": "eventos_especiales_propio",
        "horizon_years": 2,
        "concesionado": False,
        "outcomes": [
            {"label": "Evento Exitoso", "prob": 0.30, "npv": 28000.0},
            {"label": "Evento Regular", "prob": 0.40, "npv": 8000.0},
            {"label": "Evento Fallido", "prob": 0.30, "npv": -12000.0},
        ],
    },
    # Eventos Especiales - Concesión
    {
        "name": "Eventos Especiales - Concesión",
        "decision_key": "eventos_especiales_concesion",
        "horizon_years": 2,
        "concesionado": True,
        "outcomes": [
            {"label": "Evento Exitoso", "prob": 0.30, "npv": 28000.0},
            {"label": "Evento Regular", "prob": 0.40, "npv": 8000.0},
            {"label": "Evento Fallido", "prob": 0.30, "npv": -12000.0},
        ],
    },
    # Arriendo de Espacios - Administración Propia
    {
        "name": "Arriendo de Espacios - Propio",
        "decision_key": "arriendo_espacios_propio",
        "horizon_years": 4,
        "concesionado": False,
        "outcomes": [
            {"label": "Alta Ocupación", "prob": 0.35, "npv": 40000.0},
            {"label": "Ocupación Moderada", "prob": 0.45, "npv": 15000.0},
            {"label": "Baja Ocupación", "prob": 0.20, "npv": -5000.0},
        ],
    },
    # Arriendo de Espacios - Concesión
    {
        "name": "Arriendo de Espacios - Concesión",
        "decision_key": "arriendo_espacios_concesion",
        "horizon_years": 4,
        "concesionado": True,
        "outcomes": [
            {"label": "Alta Ocupación", "prob": 0.35, "npv": 40000.0},
            {"label": "Ocupación Moderada", "prob": 0.45, "npv": 15000.0},
            {"label": "Baja Ocupación", "prob": 0.20, "npv": -5000.0},
        ],
    },
    # Señaléticas - Solo administración propia (no se concesiona)
    {
        "name": "Señaléticas",
        "decision_key": "senaleticas",
        "horizon_years": 1,
        "concesionado": False,
        "outcomes": [
            {"label": "Beneficio", "prob": 0.70, "npv": 5000.0},
            {"label": "Pérdida", "prob": 0.30, "npv": -5000.0},
        ],
    },
]



# Orden consistente de las decisiones para construir combinaciones (2^11)
# Primera decisión: concesionar_todo (1 = concesionar todo, 0 = administración propia)
# Luego las decisiones individuales de cada actividad
decision_order = ["concesionar_todo"] + [a["decision_key"] for a in activities]
