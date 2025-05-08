import streamlit as st
import pandas as pd
import os

ARCHIVO_DATOS = 'rifa_data.csv'
TOTAL_NUMEROS = 20000
MAX_POR_PERSONA = 10
CLAVE_ADMIN = "admin123"  # cambia esta clave

# Inicializa CSV si no existe
if not os.path.exists(ARCHIVO_DATOS):
    df_init = pd.DataFrame(columns=['Número', 'Nombre', 'Correo', 'Pagado'])
    df_init.to_csv(ARCHIVO_DATOS, index=False)

# Cargar datos
df = pd.read_csv(ARCHIVO_DATOS)

# Obtener números ocupados
numeros_ocupados = df['Número'].tolist()
numeros_disponibles = [n for n in range(1, TOTAL_NUMEROS + 1) if n not in numeros_ocupados]

# Configuración de la app
st.set_page_config(page_title="Rifa de 20.000 Números", layout="centered")
st.title("🎟️ Sistema de Rifa en Línea")

st.markdown(f"**📌 Total de números:** {TOTAL_NUMEROS}")
st.markdown(f"**✅ Disponibles:** {len(numeros_disponibles)}")
st.markdown("---")

# === CLIENTE ===
st.header("🧍 Reservar Números")

numeros_seleccionados = st.multiselect(
    f"Selecciona hasta {MAX_POR_PERSONA} números disponibles:",
    options=numeros_disponibles,
    max_selections=MAX_POR_PERSONA
)

nombre = st.text_input("Tu nombre completo")
correo = st.text_input("Correo electrónico")

if st.button("Reservar"):
    if not numeros_seleccionados:
        st.warning("⚠️ Debes seleccionar al menos un número.")
    elif not nombre.strip() or not correo.strip():
        st.warning("⚠️ Ingresa nombre y correo.")
    else:
        nuevos = pd.DataFrame(
            [[num, nombre.strip(), correo.strip(), False] for num in numeros_seleccionados],
            columns=df.columns
        )
        df = pd.concat([df, nuevos], ignore_index=True)
        df.to_csv(ARCHIVO_DATOS, index=False)
        st.success(f"🎉 Números reservados: {', '.join(map(str, numeros_seleccionados))}")

# === ADMIN ===
st.markdown("---")
st.header("🔐 Panel Administrador")
clave = st.text_input("Clave de administrador", type="password")

if clave == CLAVE_ADMIN:
    st.success("✅ Acceso concedido")
    st.subheader("📋 Lista completa de reservas")
    st.dataframe(df.sort_values(by="Número"))

    numero_confirmar = st.number_input("Confirmar pago para el número:", min_value=1, max_value=TOTAL_NUMEROS, step=1)
    if st.button("Confirmar pago"):
        if numero_confirmar in df['Número'].values:
            df.loc[df['Número'] == numero_confirmar, 'Pagado'] = True
            df.to_csv(ARCHIVO_DATOS, index=False)
            st.success(f"✅ Número {numero_confirmar} marcado como pagado.")
        else:
            st.error("⚠️ Ese número no ha sido reservado aún.")
