import streamlit as st
from pyshorteners import Shortener

def acortar_url(url_larga, utm_params):
    """
    Acorta una URL larga y agrega parámetros UTM.

    Args:
        url_larga: La URL larga a acortar.
        utm_params: Un diccionario con los parámetros UTM (opcional).

    Returns:
        La URL acortada con los parámetros UTM (si se proporcionan).
    """
    s = Shortener()
    if utm_params:
        url_larga += "?" + "&".join(f"{k}={v}" for k, v in utm_params.items())
    return s.tinyurl.short(url_larga)

st.title("🔗 Hola, soy el nuevo Acortador de Links y configuro el UTM  automático. 🔗")

url_original = st.text_input("Ingrese la URL que desea acortar:")

# Define the options for the dropdown
utm_source_options = ["Telegram", "Facebook", "YouTube", "WhatsApp", "Twitter"]

# Create the dropdown selector
utm_source = st.selectbox("Fuente UTM (Opcional):", options=utm_source_options, key="utm_source")

# Default value for UTM medium
default_link = "link"  # Replace with your desired default link
utm_medium = st.text_input("Medio UTM (Opcional):", key="utm_medium", value=default_link)

# Options for UTM term
utm_term_options = ["telegram-app", "Facebook-app", "YouTube-app", "WhatsApp-app", "Twitter-app"]
utm_term = st.selectbox("Término UTM (Opcional):", options=utm_term_options, key="utm_term")

# Construct the utm_params dictionary
utm_params = {}
if utm_source:
    utm_params["utm_source"] = utm_source
if utm_medium:
    utm_params["utm_medium"] = utm_medium
if utm_term:
    utm_params["utm_term"] = utm_term

# Button to generate the short URL
if st.button("¡Acortar!"):
    url_final = acortar_url(url_original, utm_params)
    st.write("La URL acortada es:", url_final)

# Footer information
st.write("Creado por Soporte TI")
st.write("Si tiene algún problema, comuníquese al correo [gsantos@bloquedearmas.com].")