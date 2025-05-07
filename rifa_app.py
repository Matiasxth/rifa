import streamlit as st
import pandas as pd
import os

ARCHIVO_DATOS = 'rifa_data.csv'
TOTAL_NUMEROS = 20000

# Crear CSV si no existe
if not os.path.exists(ARCHIVO_DATOS):
    df_init = pd.DataFrame(columns=['Número', 'Nombre', 'Correo', 'Pagado'])
    df_init.to_csv(ARCHIVO_DATOS, index=False)

# Leer datos
df = pd.read_csv(ARCHIVO_DATOS)

st.set_page_config(page_title="Rifa 20K", layout="wide")
st.title("🎟️ Rifa de 20.000 Números")

# Calcular números disponibles
numeros_ocupados = df['Número'].tolist()
numeros_disponibles = [n for n in range(1, TOTAL_NUMEROS + 1) if n not in numeros_ocupados]

st.markdown(f"📊 Números disponibles: {len(numeros_disponibles)} / {TOTAL_NUMEROS}")

# Entrada de datos
st.header("Reserva tu número")
numeros_seleccionados = st.multiselect(
    "Selecciona tus números (puedes elegir varios):",
    options=numeros_disponibles,
    max_selections=10
)

nombre = st.text_input("Tu nombre")
correo = st.text_input("Tu correo electrónico")

if st.button("Reservar"):
    if not numeros_seleccionados:
        st.warning("Debes seleccionar al menos un número.")
    elif not nombre or not correo:
        st.warning("Completa tu nombre y correo.")
    else:
        nuevos_registros = pd.DataFrame(
            [[num, nombre, correo, False] for num in numeros_seleccionados],
            columns=df.columns
        )
        df = pd.concat([df, nuevos_registros], ignore_index=True)
        df.to_csv(ARCHIVO_DATOS, index=False)
        st.success(f"¡Has reservado los números: {', '.join(map(str, numeros_seleccionados))}!")

# ADMIN
st.header("🛠️ Admin (Confirmación de pagos)")
clave = st.text_input("Clave admin", type="password")

if clave == "admin123":
    st.dataframe(df.sort_values(by='Número'))

    numero_confirmar = st.number_input("Número a confirmar", min_value=1, max_value=TOTAL_NUMEROS)
    if st.button("Confirmar pago"):
        if numero_confirmar in df['Número'].values:
            df.loc[df['Número'] == numero_confirmar, 'Pagado'] = True
            df.to_csv(ARCHIVO_DATOS, index=False)
            st.success(f"Número {numero_confirmar} marcado como pagado.")
        else:
            st.error("Ese número aún no ha sido reservado.")
