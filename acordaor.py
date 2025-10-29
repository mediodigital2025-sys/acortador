import streamlit as st
import requests

def acortar_url_isgd(url_larga, utm_params):
    """
    Acorta URL usando is.gd (servicio alternativo sin vista previa)
    """
    # Agregar parámetros UTM si existen
    if utm_params:
        url_larga += "?" + "&".join(f"{k}={v}" for k, v in utm_params.items())
    
    try:
        response = requests.get(f'https://is.gd/create.php?format=simple&url={url_larga}')
        if response.status_code == 200:
            return response.text.strip()
        else:
            return None
    except:
        return None

st.title("🔗 Hola, soy el nuevo Acortador de Links y configuro el UTM automático. 🔗")

url_original = st.text_input("Ingrese la URL que desea acortar:")

# Define the options for the dropdown
utm_source_options = ["Telegram", "Facebook", "YouTube", "WhatsApp", "Twitter"]

# Create the dropdown selector
utm_source = st.selectbox("Fuente UTM (Opcional):", options=utm_source_options, key="utm_source")

# Default value for UTM medium
default_link = "link"
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

if st.button("¡Acortar!"):
    if url_original:
        url_final = acortar_url_isgd(url_original, utm_params)
        
        if url_final:
            st.success("¡URL acortada exitosamente!")
            st.write("**La URL acortada es:**")
            st.code(url_final, language=None)
            
            # Botones de acción
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<a href="{url_final}" target="_blank"><button style="width:100%; background-color: #4CAF50; color: white; padding: 10px; border: none; border-radius: 4px; cursor: pointer;">Abrir URL</button></a>', unsafe_allow_html=True)
            with col2:
                if st.button("Copiar URL", use_container_width=True):
                    st.code(url_final, language=None)
                    st.success("¡URL copiada!")
        else:
            st.error("Error al acortar la URL. Intente nuevamente.")
    else:
        st.error("Por favor, ingrese una URL para acortar.")

# Footer information
st.write("Creado por Soporte TI")
st.write("Si tiene algún problema, comuníquese al correo [gsantos@bloquedearmas.com].")
