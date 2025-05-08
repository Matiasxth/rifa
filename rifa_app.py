import streamlit as st
import pandas as pd
import os

ARCHIVO_DATOS = 'rifa_data.csv'
TOTAL_NUMEROS = 20000
MAX_POR_PERSONA = 10
CLAVE_ADMIN = "admin123"

# Crear CSV si no existe
if not os.path.exists(ARCHIVO_DATOS):
    df_init = pd.DataFrame(columns=['Número', 'Nombre', 'RUT', 'Correo', 'Transferencia', 'Estado'])
    df_init.to_csv(ARCHIVO_DATOS, index=False)

# Cargar CSV
df = pd.read_csv(ARCHIVO_DATOS)

# Calcular disponibles
numeros_ocupados = df['Número'].tolist()
numeros_disponibles = [n for n in range(1, TOTAL_NUMEROS + 1) if n not in numeros_ocupados]

st.set_page_config(page_title="Rifa 20.000 Números", layout="centered")
st.title("🎟️ Rifa de 20.000 Números")

st.markdown("---")
menu = st.sidebar.radio("Menú", ["Reservar Números", "Ingresar Transferencia", "Admin"])

# === ETAPA 1: RESERVA ===
if menu == "Reservar Números":
    st.header("🧍 Reserva tus números")

    numeros = st.multiselect(
        f"Selecciona hasta {MAX_POR_PERSONA} números disponibles:",
        options=numeros_disponibles,
        max_selections=MAX_POR_PERSONA
    )

    nombre = st.text_input("Nombre completo")
    rut = st.text_input("RUT (ej: 18.123.456-K)")
    correo = st.text_input("Correo electrónico")

    if st.button("Reservar"):
        if not numeros or not nombre.strip() or not rut.strip() or not correo.strip():
            st.warning("⚠️ Todos los campos son obligatorios.")
        else:
            nuevos = pd.DataFrame(
                [[num, nombre.strip(), rut.strip(), correo.strip(), "", "pendiente"] for num in numeros],
                columns=df.columns
            )
            df = pd.concat([df, nuevos], ignore_index=True)
            df.to_csv(ARCHIVO_DATOS, index=False)
            st.success(f"✅ Números reservados: {', '.join(map(str, numeros))}. Ahora ingresa tu número de transferencia.")

# === ETAPA 2: INGRESO TRANSFERENCIA ===
elif menu == "Ingresar Transferencia":
    st.header("💸 Ingresar número de transferencia")

    rut_transferencia = st.text_input("Tu RUT usado al reservar")
    num_transferencia = st.text_input("Número de transferencia")

    if st.button("Enviar Transferencia"):
        if not rut_transferencia.strip() or not num_transferencia.strip():
            st.warning("⚠️ Debes ingresar tu RUT y el número de transferencia.")
        else:
            indices = df[(df['RUT'] == rut_transferencia.strip()) & (df['Estado'] == 'pendiente')].index
            if len(indices) == 0:
                st.error("No se encontraron reservas pendientes con ese RUT.")
            else:
                df.loc[indices, 'Transferencia'] = num_transferencia.strip()
                df.to_csv(ARCHIVO_DATOS, index=False)
                st.success("✅ Transferencia asociada. Ahora espera la confirmación del administrador.")

# === ETAPA 3: ADMIN ===
elif menu == "Admin":
    st.header("🔐 Panel de Administrador")
    clave = st.text_input("Clave admin", type="password")

    if clave == CLAVE_ADMIN:
        st.success("Acceso concedido")
        transferencia_admin = st.text_input("Buscar por número de transferencia")

        if transferencia_admin:
            registros = df[df['Transferencia'] == transferencia_admin]
            if not registros.empty:
                st.write("📋 Registros asociados:")
                st.dataframe(registros)

                if st.button("✅ Confirmar esta transferencia"):
                    df.loc[df['Transferencia'] == transferencia_admin, 'Estado'] = 'pagado'
                    df.to_csv(ARCHIVO_DATOS, index=False)
                    st.success("🎉 Transferencia confirmada y números marcados como pagados.")

                if st.button("❌ Rechazar y liberar números"):
                    df = df[df['Transferencia'] != transferencia_admin]
                    df.to_csv(ARCHIVO_DATOS, index=False)
                    st.info("🗑️ Números liberados.")

        st.markdown("---")
        st.subheader("📊 Vista completa de reservas")
        st.dataframe(df.sort_values(by="Número"))
