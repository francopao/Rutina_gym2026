# -*- coding: utf-8 -*-
"""
App de entrenamiento — para Monita
Streamlit. Un solo archivo.
"""

import json
import os
from datetime import date, timedelta

import pandas as pd
import streamlit as st

# ============================================================
# CONFIG GENERAL
# ============================================================

st.set_page_config(page_title="Tu plan, Monita", page_icon="🌱", layout="wide")

ARCHIVO_REGISTRO = "registro.json"

COLOR_1 = "#7C4D8B"
COLOR_2 = "#E8A0BF"
COLOR_3 = "#F5EAF2"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: #FFFDFE; }}
    h1, h2, h3 {{ color: {COLOR_1}; }}
    .caja {{
        background-color: {COLOR_3};
        border-left: 6px solid {COLOR_2};
        padding: 16px 20px;
        border-radius: 8px;
        margin-bottom: 14px;
    }}
    .caja-fuerte {{
        background-color: {COLOR_1};
        color: white;
        padding: 18px 22px;
        border-radius: 10px;
        margin-bottom: 14px;
    }}
    .caja-fuerte h3 {{ color: white; margin-top: 0; }}
    .chiquito {{ font-size: 0.86rem; color: #6B5B66; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 1. CALENDARIO REAL (UPC 2026-2) — FECHAS REFERENCIALES
# ============================================================
# Las fechas son una guía, no una cárcel. Si una semana se corre, se corre.

BLOQUES = [
    {
        "nombre": "Vacaciones — bloque fuerte",
        "inicio": date(2026, 7, 27),
        "fin": date(2026, 8, 23),
        "escenario": "vacaciones",
        "resumen": "Es la etapa con más tiempo libre del año, así que es donde más se avanza. "
                   "Acá se entrena más seguido y se aprovecha para dejar bien fina la técnica.",
    },
    {
        "nombre": "Ciclo normal — primera parte",
        "inicio": date(2026, 8, 24),
        "fin": date(2026, 10, 4),
        "escenario": "semestre",
        "resumen": "Empiezan las clases. Bajamos a 3 días fijos y el objetivo cambia: "
                   "ya no es entrenar más, es que cada sesión rinda más.",
    },
    {
        "nombre": "Parciales — semanas suaves",
        "inicio": date(2026, 10, 5),
        "fin": date(2026, 10, 18),
        "escenario": "examenes",
        "resumen": "Parciales UPC del 11 al 18 de octubre. Acá la prioridad son los exámenes. "
                   "El gym baja a 1 o 2 días cortitos, solo para no perder lo ganado.",
    },
    {
        "nombre": "Ciclo normal — segunda parte",
        "inicio": date(2026, 10, 19),
        "fin": date(2026, 11, 29),
        "escenario": "semestre",
        "resumen": "Segunda ola de progreso, la más larga del año. Acá es donde se ven los cambios "
                   "de verdad si se sostiene.",
    },
    {
        "nombre": "Finales — cierre del año",
        "inicio": date(2026, 11, 30),
        "fin": date(2026, 12, 15),
        "escenario": "examenes",
        "resumen": "Finales del 6 al 15 de diciembre. Mismo esquema que parciales: 1 o 2 días, "
                   "cortito, sin exigirte. Cerramos el año sin desgastarte.",
    },
]

FIN_MACRO = BLOQUES[-1]["fin"]
INICIO_MACRO = BLOQUES[0]["inicio"]

# ============================================================
# 2. RUTINAS POR ESCENARIO
# ============================================================
# "Esfuerzo" está escrito en cristiano: cuántas reps te deberían sobrar.

ESFUERZO = {
    "pesado_suave": "Te deben sobrar 2-3 reps (no lo lleves al límite)",
    "pesado_medio": "Te deben sobrar 2 reps",
    "pesado_duro": "Te debe sobrar 1 rep, máximo 2",
    "maquina": "Casi al límite: te sobra 1 rep o ninguna",
    "maquina_suave": "Te debe sobrar 1 rep",
    "facil": "Cómodo: te sobran 3-4 reps",
}

RUTINAS = {
    "vacaciones": {
        "dias_semana": [0, 1, 2, 3, 5],  # lun, mar, mié, jue, sáb
        "dias": [
            {
                "titulo": "Día 1 — Cuádriceps (parte de adelante de la pierna)",
                "dia_sugerido": "Lunes",
                "ejercicios": [
                    ("Sentadilla", "4 x 8", ESFUERZO["pesado_suave"], "2:30 a 3 min"),
                    ("Prensa", "4 x 8-10", ESFUERZO["pesado_medio"], "2 min"),
                    ("Extensión de cuádriceps", "4 x 8", ESFUERZO["maquina"], "60-90 seg"),
                ],
                "nota": "La sentadilla es el ejercicio más técnico de todo el plan. "
                        "Si un día no la sientes bien, mejor bajar peso y hacerla limpia.",
            },
            {
                "titulo": "Día 2 — Glúteo y femoral (la prioridad del plan)",
                "dia_sugerido": "Martes",
                "ejercicios": [
                    ("Peso muerto rumano", "4 x 8", ESFUERZO["pesado_suave"], "2:30 a 3 min"),
                    ("Hip thrust (o puente de glúteo si hay cola)", "4 x 8", ESFUERZO["pesado_medio"], "2:30 min"),
                    ("Curl femoral en máquina", "4 x 10-12", ESFUERZO["maquina"], "60-90 seg"),
                    ("Patada de glúteo en polea", "3 x 12-15", ESFUERZO["maquina_suave"], "60-90 seg"),
                    ("Hiperextensión con mancuerna", "3 x 10-12", ESFUERZO["maquina_suave"], "60 seg"),
                    ("Elevación de piernas colgada", "3 x 12-15", ESFUERZO["maquina_suave"], "60 seg"),
                    ("Plancha o rueda abdominal", "3 x 30-40 seg", ESFUERZO["maquina_suave"], "60 seg"),
                ],
                "nota": "Este es EL día. Si una semana solo pudieras entrenar una vez, sería esta.",
            },
            {
                "titulo": "Día 3 — Espalda y bíceps",
                "dia_sugerido": "Miércoles",
                "ejercicios": [
                    ("Jalón al pecho / dominadas asistidas", "4 x 8-10", ESFUERZO["pesado_medio"], "2 min"),
                    ("Remo en máquina o mancuerna", "4 x 10", ESFUERZO["pesado_duro"], "90 seg a 2 min"),
                    ("Curl de bíceps", "3 x 10-12", ESFUERZO["maquina"], "60-90 seg"),
                ],
                "nota": "Día corto. Si tienes energía de sobra, después van 20 min de caminadora en pendiente.",
            },
            {
                "titulo": "Día 4 — Pecho y bíceps",
                "dia_sugerido": "Jueves",
                "ejercicios": [
                    ("Press de banca (barra, mancuerna o máquina)", "4 x 8-10", ESFUERZO["pesado_medio"], "2 min"),
                    ("Aperturas o press inclinado", "3 x 10-12", ESFUERZO["maquina_suave"], "90 seg"),
                    ("Curl martillo", "3 x 10-12", ESFUERZO["maquina"], "60 seg"),
                    ("Elevación de piernas colgada", "3 x 12-15", ESFUERZO["maquina_suave"], "60 seg"),
                    ("Plancha o rueda abdominal", "3 x 30-40 seg", ESFUERZO["maquina_suave"], "60 seg"),
                ],
                "nota": "El día más liviano de la semana. Sirve para no perder lo del tren superior.",
            },
            {
                "titulo": "Día 5 — Extra de glúteo/femoral (opcional)",
                "dia_sugerido": "Sábado",
                "ejercicios": [
                    ("Hip thrust", "4 x 10", ESFUERZO["pesado_medio"], "2:30 min"),
                    ("Curl femoral en máquina", "4 x 12", ESFUERZO["maquina"], "60-90 seg"),
                    ("Patada de glúteo en polea", "3 x 15", ESFUERZO["maquina_suave"], "60 seg"),
                    ("Escaladora o caminadora en pendiente", "20-25 min", "Ritmo conversable", "-"),
                ],
                "nota": "Este día es 100% opcional. Si el sábado se da, se usa acá o para cardio. "
                        "Si no se da, la semana igual está completa y bien hecha.",
            },
        ],
    },
    "semestre": {
        "dias_semana": [0, 1, 2],  # lun, mar, mié
        "dias": [
            {
                "titulo": "Día 1 — Cuádriceps",
                "dia_sugerido": "Lunes",
                "ejercicios": [
                    ("Sentadilla", "4 x 8", ESFUERZO["pesado_suave"], "2:30 a 3 min"),
                    ("Prensa", "4 x 8-10", ESFUERZO["pesado_medio"], "2 min"),
                    ("Extensión de cuádriceps", "4 x 8", ESFUERZO["maquina"], "60-90 seg"),
                ],
                "nota": "Si el gym está lleno y no hay rack, la prensa cubre casi todo. No pasa nada.",
            },
            {
                "titulo": "Día 2 — Glúteo y femoral (la prioridad)",
                "dia_sugerido": "Martes",
                "ejercicios": [
                    ("Peso muerto rumano", "4 x 8", ESFUERZO["pesado_suave"], "2:30 a 3 min"),
                    ("Hip thrust", "4 x 8", ESFUERZO["pesado_medio"], "2:30 min"),
                    ("Curl femoral en máquina", "4 x 10-12", ESFUERZO["maquina"], "60-90 seg"),
                    ("Patada de glúteo en polea", "3 x 12-15", ESFUERZO["maquina_suave"], "60-90 seg"),
                    ("Elevación de piernas colgada", "3 x 12-15", ESFUERZO["maquina_suave"], "60 seg"),
                    ("Plancha o rueda abdominal", "3 x 30-40 seg", ESFUERZO["maquina_suave"], "60 seg"),
                ],
                "nota": "Con 3 días, este es el día que más pesa en el resultado final.",
            },
            {
                "titulo": "Día 3 — Espalda y bíceps",
                "dia_sugerido": "Miércoles",
                "ejercicios": [
                    ("Jalón al pecho / dominadas asistidas", "4 x 8-10", ESFUERZO["pesado_medio"], "2 min"),
                    ("Remo en máquina o mancuerna", "4 x 10", ESFUERZO["pesado_duro"], "90 seg a 2 min"),
                    ("Curl de bíceps", "3 x 10-12", ESFUERZO["maquina"], "60-90 seg"),
                    ("Aperturas o press de banca (opcional)", "3 x 10-12", ESFUERZO["maquina_suave"], "90 seg"),
                ],
                "nota": "Si el sábado se da, se usa para repetir el Día 2 o para 25 min de cardio. Nunca para meter algo nuevo.",
            },
        ],
    },
    "examenes": {
        "dias_semana": [0, 3],  # lun y jue como sugerencia
        "dias": [
            {
                "titulo": "Día único — lo esencial",
                "dia_sugerido": "El día que puedas (1 o 2 veces en la semana)",
                "ejercicios": [
                    ("Peso muerto rumano", "3 x 8", ESFUERZO["facil"], "2:30 min"),
                    ("Hip thrust", "3 x 8", ESFUERZO["facil"], "2:30 min"),
                    ("Curl femoral en máquina", "3 x 10", ESFUERZO["pesado_medio"], "60-90 seg"),
                    ("Sentadilla o prensa (la que prefieras ese día)", "3 x 8", ESFUERZO["facil"], "2 min"),
                ],
                "nota": "45 minutos y afuera. No trates de compensar en un día lo que no hiciste en la semana: "
                        "eso solo te deja cansada para estudiar y no suma nada.",
            },
        ],
    },
}

# ============================================================
# 3. PERSISTENCIA (memoria de entrenos)
# ============================================================


def cargar_datos():
    if os.path.exists(ARCHIVO_REGISTRO):
        try:
            with open(ARCHIVO_REGISTRO, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"entrenos": [], "fecha_regla": None}


def guardar_datos(datos):
    try:
        with open(ARCHIVO_REGISTRO, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


if "datos" not in st.session_state:
    st.session_state.datos = cargar_datos()

datos = st.session_state.datos

# ============================================================
# 4. LÓGICA DE FECHAS
# ============================================================


def bloque_de(fecha):
    for b in BLOQUES:
        if b["inicio"] <= fecha <= b["fin"]:
            return b
    if fecha < INICIO_MACRO:
        return BLOQUES[0]
    return None


def semana_dentro_del_bloque(fecha, bloque):
    dias = (fecha - bloque["inicio"]).days
    total = (bloque["fin"] - bloque["inicio"]).days + 1
    return max(1, dias // 7 + 1), max(1, (total + 6) // 7)


def exigencia_de_la_semana(sem, total_sem, escenario):
    """Devuelve cómo debería sentirse la semana. Sube y baja sola."""
    if escenario == "examenes":
        return ("Semana suave", "Nada cerca del límite. Te deben sobrar 3-4 reps siempre.")
    if sem == 1:
        return ("Reacomodo", "Semana de volver al ritmo. Sin récords, sin apuro.")
    if sem == total_sem:
        return ("Bajada", "Última del bloque: quita 1 serie de los ejercicios de máquina y llega entera al siguiente.")
    if sem >= total_sem - 1:
        return ("Semana fuerte", "El punto más exigente. Acá sí se aprieta un poco.")
    return ("Progreso", "Sube un poquito el peso o una rep respecto a la semana pasada.")


def lunes_de(fecha):
    return fecha - timedelta(days=fecha.weekday())


NOMBRE_DIA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "setiembre", "octubre", "noviembre", "diciembre"]


def fecha_bonita(f):
    return f"{NOMBRE_DIA[f.weekday()]} {f.day} de {MESES[f.month - 1]}"


# ============================================================
# 5. SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("### Tu plan")
    hoy = st.date_input("Ver el plan del día", value=date.today(), format="DD/MM/YYYY")
    st.markdown("---")
    st.markdown(
        "<div class='chiquito'>Las fechas son referencias, no reglas. "
        "Si una semana se corre, se corre y ya. Lo único que importa de verdad "
        "es que la mayoría de semanas se cumplan.</div>",
        unsafe_allow_html=True,
    )

bloque = bloque_de(hoy)

if bloque is None:
    st.title("Terminaste el plan, Monita")
    st.markdown(
        "<div class='caja-fuerte'><h3>Se acabó el macrociclo</h3>"
        "Del 27 de julio al 15 de diciembre, completo. Cuando quieras armamos el siguiente."
        "</div>",
        unsafe_allow_html=True,
    )
    st.stop()

escenario = bloque["escenario"]
sem_actual, sem_totales = semana_dentro_del_bloque(hoy, bloque)
tag_sem, desc_sem = exigencia_de_la_semana(sem_actual, sem_totales, escenario)

# ============================================================
# 6. CABECERA
# ============================================================

st.title("Hola Monita")
st.markdown(
    f"<div class='caja'>Hoy es {fecha_bonita(hoy)}. Estás en <b>{bloque['nombre']}</b>, "
    f"semana {sem_actual} de {sem_totales}.<br>"
    f"<b>{tag_sem}:</b> {desc_sem}</div>",
    unsafe_allow_html=True,
)

tabs = st.tabs([
    "Qué toca hoy",
    "La rutina completa",
    "El mapa del plan",
    "Cómo vas",
    "Tu ciclo",
    "Dudas de palabras raras",
])

# ============================================================
# TAB 1 — QUÉ TOCA HOY
# ============================================================

with tabs[0]:
    rutina = RUTINAS[escenario]
    dias_activos = rutina["dias_semana"]
    wd = hoy.weekday()

    if escenario == "examenes":
        dia_hoy = rutina["dias"][0]
        toca = True
    elif wd in dias_activos:
        idx = dias_activos.index(wd)
        dia_hoy = rutina["dias"][min(idx, len(rutina["dias"]) - 1)]
        toca = True
    else:
        dia_hoy = None
        toca = False

    if toca:
        st.markdown(
            f"<div class='caja-fuerte'><h3>{dia_hoy['titulo']}</h3>{dia_hoy['nota']}</div>",
            unsafe_allow_html=True,
        )
        df = pd.DataFrame(
            dia_hoy["ejercicios"],
            columns=["Ejercicio", "Series x reps", "Qué tan fuerte", "Descanso entre series"],
        )
        st.dataframe(df, use_container_width=True, hide_index=True)

        if escenario != "examenes":
            st.markdown(
                "<div class='caja'>Después de pierna, si te queda cuerda: 20-25 minutos de caminadora "
                "en pendiente o escaladora, a un ritmo en el que todavía podrías hablar entrecortado. "
                "Nunca antes de entrenar, siempre después.</div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            "<div class='caja-fuerte'><h3>Hoy toca descansar</h3>"
            "En serio. El músculo no crece en el gym, crece descansando. "
            "Un día libre bien tomado vale más que uno forzado.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("**Si igual quieres moverte:** una caminata larga o 20 min de caminadora suave y nada más.")

    st.markdown("---")
    st.markdown("### Marca que entrenaste")
    c1, c2 = st.columns([1, 2])
    with c1:
        if st.button("Sí, entrené hoy", use_container_width=True, type="primary"):
            iso = hoy.isoformat()
            if iso not in datos["entrenos"]:
                datos["entrenos"].append(iso)
                guardar_datos(datos)
                st.success("Anotado, Makisita. Bien ahí.")
            else:
                st.info("Ese día ya estaba marcado.")
    with c2:
        if hoy.isoformat() in datos["entrenos"]:
            if st.button("Borrar la marca de hoy", use_container_width=True):
                datos["entrenos"].remove(hoy.isoformat())
                guardar_datos(datos)
                st.rerun()

# ============================================================
# TAB 2 — RUTINA COMPLETA (3 ESCENARIOS)
# ============================================================

with tabs[1]:
    st.markdown("### Tu rutina, en los tres escenarios de la vida real")
    st.markdown(
        "<div class='caja'>No hay una sola rutina: hay tres, según cuánto tiempo tengas esa semana. "
        "Las tres están bien hechas. La de exámenes no es 'la rutina mala', es la correcta para esa semana.</div>",
        unsafe_allow_html=True,
    )

    etiquetas = {
        "vacaciones": "Vacaciones — 4 o 5 días",
        "semestre": "Ciclo normal — 3 días",
        "examenes": "Exámenes o semanas locas — 1 o 2 días",
    }

    sel = st.radio("Elige el escenario", list(etiquetas.keys()),
                   format_func=lambda k: etiquetas[k],
                   index=list(etiquetas.keys()).index(escenario),
                   horizontal=True)

    if sel == escenario:
        st.success("Este es el escenario en el que estás ahora mismo.")

    for d in RUTINAS[sel]["dias"]:
        with st.expander(f"{d['titulo']}  ·  {d['dia_sugerido']}", expanded=(sel == "examenes")):
            df = pd.DataFrame(
                d["ejercicios"],
                columns=["Ejercicio", "Series x reps", "Qué tan fuerte", "Descanso entre series"],
            )
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.markdown(f"<div class='chiquito'>{d['nota']}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        "<div class='caja'><b>Sobre los abdominales, para que no te vendan humo:</b> hacer abs "
        "no quema la grasa de la barriga. Eso no existe, la grasa baja de forma general con el déficit, "
        "no por zona. Los abs igual valen la pena por fuerza de core y por cómo se ve la zona, "
        "pero la cintura la define lo que comes, no las planchas.</div>",
        unsafe_allow_html=True,
    )

# ============================================================
# TAB 3 — MAPA DEL PLAN
# ============================================================

with tabs[2]:
    st.markdown("### De acá a diciembre, todo el mapa")

    filas = []
    for b in BLOQUES:
        activo = "◀ acá estás" if b is bloque else ""
        semanas = ((b["fin"] - b["inicio"]).days + 1) // 7
        filas.append({
            "Etapa": b["nombre"],
            "Desde": fecha_bonita(b["inicio"]).capitalize(),
            "Hasta": fecha_bonita(b["fin"]).capitalize(),
            "Semanas": semanas,
            "Días por semana": {"vacaciones": "4-5", "semestre": "3", "examenes": "1-2"}[b["escenario"]],
            "": activo,
        })
    st.dataframe(pd.DataFrame(filas), use_container_width=True, hide_index=True)

    for b in BLOQUES:
        with st.expander(b["nombre"], expanded=(b is bloque)):
            st.write(b["resumen"])

    st.markdown("---")
    st.markdown(
        "<div class='caja'><b>Y si entran las prácticas:</b> si en algún momento te toca estudiar "
        "y trabajar a la vez, esas semanas se tratan como semana de exámenes aunque el calendario "
        "diga otra cosa. 1 o 2 días, lo esencial, y punto. El plan se acomoda a tu vida, no al revés.</div>",
        unsafe_allow_html=True,
    )

# ============================================================
# TAB 4 — CÓMO VAS
# ============================================================

with tabs[3]:
    st.markdown("### Cómo vas, Monita")

    entrenos = sorted(set(datos["entrenos"]))
    entrenos_d = [date.fromisoformat(e) for e in entrenos]

    lun = lunes_de(hoy)
    esta_sem = [e for e in entrenos_d if lun <= e <= lun + timedelta(days=6)]
    pasada = [e for e in entrenos_d if lun - timedelta(days=7) <= e < lun]

    meta = {"vacaciones": 4, "semestre": 3, "examenes": 1}[escenario]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Esta semana", f"{len(esta_sem)} / {meta}")
    c2.metric("Semana pasada", len(pasada))
    c3.metric("Total del plan", len([e for e in entrenos_d if e >= INICIO_MACRO]))
    dias_faltan = (FIN_MACRO - hoy).days
    c4.metric("Días hasta cerrar", max(0, dias_faltan))

    st.markdown("#### Avance de esta etapa")
    total_b = (bloque["fin"] - bloque["inicio"]).days + 1
    trans = max(0, min(total_b, (hoy - bloque["inicio"]).days + 1))
    st.progress(trans / total_b)
    st.caption(f"{trans} de {total_b} días de «{bloque['nombre']}». "
               f"Te quedan {max(0, total_b - trans)} días en esta etapa.")

    st.markdown("#### Avance del plan completo")
    total_m = (FIN_MACRO - INICIO_MACRO).days + 1
    trans_m = max(0, min(total_m, (hoy - INICIO_MACRO).days + 1))
    st.progress(trans_m / total_m)
    st.caption(f"{round(trans_m / total_m * 100)}% del camino de julio a diciembre.")

    if len(esta_sem) >= meta:
        st.success("Semana cumplida. Ya está, lo demás es bonus. Bien hecho, bb.")
    elif len(esta_sem) > 0:
        st.info(f"Vas {len(esta_sem)}. Te faltan {meta - len(esta_sem)} para cerrar la semana.")

    if entrenos_d:
        st.markdown("#### Últimas 12 semanas")
        conteo = {}
        for e in entrenos_d:
            k = lunes_de(e)
            conteo[k] = conteo.get(k, 0) + 1
        semanas = [lun - timedelta(weeks=i) for i in range(11, -1, -1)]
        serie = pd.DataFrame(
            {"Entrenos": [conteo.get(s, 0) for s in semanas]},
            index=[f"{s.day}/{s.month}" for s in semanas],
        )
        st.bar_chart(serie, color=COLOR_2)

        with st.expander("Ver todos los días marcados"):
            st.write(", ".join(fecha_bonita(e) for e in reversed(entrenos_d[-40:])))

    st.markdown("---")
    st.markdown(
        "<div class='caja'><b>Lo que es realista esperar de acá a diciembre:</b> vas a ver "
        "mejoras claras de fuerza y de técnica en peso muerto rumano y sentadilla, desarrollo "
        "progresivo del femoral, y mantenimiento del resto. Entrenando en déficit eso es "
        "exactamente lo esperable, no es poco. Cambiar composición corporal es cosa de meses, "
        "no de semanas: esto es un tramo del camino, no la meta final.</div>",
        unsafe_allow_html=True,
    )

# ============================================================
# TAB 5 — CICLO
# ============================================================

with tabs[4]:
    st.markdown("### Tu ciclo también entra en el plan")
    st.markdown(
        "<div class='caja'>Esto no está en ninguna rutina genérica de internet y debería. "
        "Tu cuerpo no rinde igual todos los días del mes, y eso no es falta de ganas ni de "
        "disciplina: es fisiología. La idea acá no es cambiarte la rutina cada semana, es que "
        "sepas qué esperar para que no te frustres cuando un día el mismo peso se sienta el doble.</div>",
        unsafe_allow_html=True,
    )

    guardada = datos.get("fecha_regla")
    valor = date.fromisoformat(guardada) if guardada else hoy
    f_regla = st.date_input("Primer día de tu última regla", value=valor, format="DD/MM/YYYY")
    largo = st.number_input("Cada cuántos días te suele venir", 21, 40, 28)

    if st.button("Guardar"):
        datos["fecha_regla"] = f_regla.isoformat()
        guardar_datos(datos)
        st.success("Guardado.")

    dia_ciclo = (hoy - f_regla).days % largo + 1

    if dia_ciclo <= 5:
        fase = "Regla"
        msg = ("Si te sientes mal, no entrenas y no pasa absolutamente nada. Si te sientes bien, "
               "entrena normal: no hay ninguna razón para no hacerlo, y a mucha gente hasta le "
               "baja el cólico moverse. Tú decides, sin culpa por ninguno de los dos lados.")
    elif dia_ciclo <= largo // 2:
        fase = "Primera mitad del ciclo"
        msg = ("Suele ser la parte donde mejor te vas a sentir y donde más suele rendir el cuerpo. "
               "Si vas a intentar subir peso en el peso muerto rumano o el hip thrust, "
               "estos días son buen momento.")
    elif dia_ciclo <= largo // 2 + 3:
        fase = "Mitad del ciclo"
        msg = ("Días de buen rendimiento en general. Un detalle: por el tema hormonal la rodilla "
               "y el tobillo pueden estar un poquito más laxos, así que en sentadilla cuida "
               "que la rodilla no se te vaya hacia adentro. Nada alarmante, solo atención.")
    elif dia_ciclo <= largo - 4:
        fase = "Segunda mitad del ciclo"
        msg = ("Puede que te sientas algo más pesada, con más calor y más hambre. Es normal. "
               "Mantén el plan, pero si el peso de siempre se siente más duro, no fuerces: "
               "baja un poquito y ya.")
    else:
        fase = "Días previos a la regla"
        msg = ("Acá es donde más se suele sentir la caída: más cansancio, menos paciencia, "
               "todo pesa más. NO midas tu progreso estos días, te va a dar una foto falsa. "
               "Deja 3-4 reps en recámara en todo y cumple la sesión sin heroísmos.")

    st.markdown(
        f"<div class='caja-fuerte'><h3>Día {dia_ciclo} — {fase}</h3>{msg}</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='chiquito'>Nota honesta: la evidencia sobre programar el entrenamiento "
        "según el ciclo todavía es floja y mixta. Por eso esto no te cambia la rutina, solo "
        "te da contexto para autorregularte. Y si tomas anticonceptivos hormonales, esta parte "
        "aplica bastante menos, avísame y la sacamos.</div>",
        unsafe_allow_html=True,
    )

# ============================================================
# TAB 6 — GLOSARIO
# ============================================================

with tabs[5]:
    st.markdown("### Palabras que aparecen y que nadie te explicó nunca")

    glosario = [
        ("«Te deben sobrar 2 reps»",
         "Es la forma medible de decir cuánto apretar. Terminas la serie sintiendo que podrías "
         "hacer 2 más con buena técnica, y ahí paras. Reemplaza al «hasta que duela», que no "
         "significa nada y cambia según el día que tengas."),
        ("Ejercicio compuesto / pesado",
         "Los que mueven varias articulaciones a la vez: sentadilla, peso muerto rumano, hip thrust, "
         "prensa, press de banca. Cansan todo el cuerpo, no solo el músculo. Por eso en estos "
         "nunca vas al límite y descansas 2:30-3 minutos entre series."),
        ("Ejercicio de máquina / aislamiento",
         "Los que trabajan un músculo solito: curl femoral, extensión de cuádriceps, patada de "
         "polea, curl de bíceps. Cansan poco en general, así que acá SÍ vale llegar casi al límite. "
         "Con 60-90 segundos de descanso alcanza."),
        ("Volumen",
         "Cuánto trabajo total haces: series por ejercicio, ejercicios por sesión, sesiones por semana. "
         "Más volumen no siempre es mejor; es mejor solo si te recuperas de él."),
        ("Deload / semana suave",
         "Una semana a propósito más fácil, cada 4-6 semanas. No es perder el tiempo: es cuando "
         "el cuerpo termina de asimilar lo anterior. En tu plan las semanas de exámenes cumplen "
         "justo ese rol, así que el calendario de la U te lo regala solo."),
        ("Progresión",
         "Que semana a semana subas algo: un poquito de peso, una rep más, o la misma serie mejor "
         "ejecutada. Las tres cuentan. Y en déficit calórico, sostener el peso ya es ganar."),
        ("Déficit calórico",
         "Comer un poco menos de lo que gastas. Es lo único que baja grasa. En ese contexto lo "
         "realista es que la fuerza se sostenga más que dispararse, y eso está perfecto. "
         "Referencia de proteína que se usa seguido: entre 1.6 y 2.2 g por kilo de tu peso al día."),
        ("Por qué el peso muerto rumano aparece siempre",
         "Porque es el que más te va a mover la aguja en glúteo y femoral, que es tu prioridad. "
         "Si algún día tienes que recortar la sesión, ese se queda."),
    ]
    for t, d in glosario:
        with st.expander(t):
            st.write(d)

    st.markdown("---")
    st.markdown(
        "<div class='caja-fuerte'>Y si algún día no tienes ganas, no pasa nada. "
        "Esto está armado para aguantar semanas malas sin romperse. "
        "Lo hice para que te sea fácil, no para que te sea una obligación más.<br><br>"
        "t lobo, Makisita.</div>",
        unsafe_allow_html=True,
    )
