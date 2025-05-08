import streamlit as st
import pandas as pd
import os

ARCHIVO_DATOS = 'rifa_data.csv'
TOTAL_NUMEROS = 20000
MAX_POR_PERSONA = 10
CLAVE_ADMIN = "admin123"

# Inicializa CSV si no existe
if not os.path.exists(ARCHIVO_DATOS):
    df_init = pd.DataFrame(columns=['Número', 'Nombre', 'Correo', 'Transferencia', 'Estado'])  # Estado: pendiente, pagado
    df_init.to_csv(ARCHIVO_DATOS, index=False)

# Cargar datos
df = pd.read_csv(ARCHIVO_DATOS)

# Números ocupados (ya reservados en cualquier estado)
numeros_ocupados = df['Número'].tolist()
numeros_disponibles = [n for n in range(1, TOTAL_NUMEROS + 1) if n not in numeros_ocupados]

st.set_page_config(page_title="Rifa 20K", layout="centered")
st.title("🎟️ Rifa de 20.000 Números")

st.markdown(f"**Total disponibles:** {len(numeros_disponibles)} de {TOTAL_NUMEROS}")
st.markdown("---")

# === CLIENTE ===
st.header("🧍 Reserva tus números")

numeros_seleccionados = st.multiselect(
    f"Selecciona hasta {MAX_POR_PERSONA} números disponibles:",
    options=numeros_disponibles,
    max_selections=MAX_POR_PERSONA
)

nombre = st.text_input("Nombre completo")
correo = st.text_input("Correo electrónico")
n_transferencia = st.text_input("Número de transferencia")

if st.button("Reservar"):
    if not numeros_seleccionados:
        st.warning("⚠️ Debes seleccionar al menos un número.")
    elif not nombre.strip() or not correo.strip() or not n_transferencia.strip():
        st.warning("⚠️ Completa todos los campos.")
    else:
        nuevos = pd.DataFrame(
            [[num, nombre.strip(), correo.strip(), n_transferencia.strip(), 'pendiente'] for num in numeros_seleccionados],
            columns=df.columns
        )
        df = pd.concat([df, nuevos], ignore_index=True)
        df.to_csv(ARCHIVO_DATOS, index=False)
        st.success(f"✅ Números reservados: {', '.join(map(str, numeros_seleccionados))}\nEstado: pendiente de verificación")

st.markdown("---")

# === ADMIN ===
st.header("🔐 Panel de Administrador")
clave = st.text_input("Clave de administrador", type="password")

if clave == CLAVE_ADMIN:
    st.success("Acceso permitido")
    st.subheader("🔍 Buscar por número de transferencia")

    transferencia_admin = st.text_input("Número de transferencia recibido en banco")
    
    if transferencia_admin:
        registros = df[df['Transferencia'] == transferencia_admin]
        if not registros.empty:
            st.write("📋 Reservas con este número de transferencia:")
            st.dataframe(registros)
            if st.button("✅ Confirmar esta transferencia"):
                df.loc[df['Transferencia'] == transferencia_admin, 'Estado'] = 'pagado'
                df.to_csv(ARCHIVO_DATOS, index=False)
                st.success("✅ Todos los números asociados fueron marcados como pagados.")
            if st.button("❌ Cancelar y liberar números"):
                df = df[df['Transferencia'] != transferencia_admin]
                df.to_csv(ARCHIVO_DATOS, index=False)
                st.info("❗ Se liberaron los números de esta transferencia.")
        else:
            st.warning("No se encontraron reservas con ese número de transferencia.")

    st.subheader("📊 Todos los registros")
    st.dataframe(df.sort_values(by="Número"))

