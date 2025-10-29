import streamlit as st
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def acortar_url_isgd(url_larga, utm_params):
    """
    Acorta URL usando is.gd (servicio alternativo sin vista previa)
    """
    # Agregar parámetros UTM si existen
    if utm_params:
        # Parsear la URL para manejar correctamente los parámetros existentes
        parsed_url = urlparse(url_larga)
        query_params = parse_qs(parsed_url.query)
        
        # Agregar los parámetros UTM a los parámetros existentes
        for key, value in utm_params.items():
            query_params[key] = [value]
        
        # Reconstruir la URL con los nuevos parámetros
        new_query = urlencode(query_params, doseq=True)
        url_larga = urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))
    
    try:
        response = requests.get(f'https://is.gd/create.php?format=simple&url={url_larga}')
        if response.status_code == 200:
            return response.text.strip()
        else:
            return None
    except:
        return None

# Configuración del título con HTML para tamaño personalizado
st.markdown("""
    <h1 style='text-align: center; color: #000000; font-size: 1.8rem; margin-bottom: 2rem;'>
        🔗 Hola, soy el nuevo Acortador de Links y configuro el UTM automático. 🔗
    </h1>
""", unsafe_allow_html=True)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .stSelectbox [data-testid="stMarkdownContainer"] p {
        font-weight: bold !important;
        color: #1E88E5 !important;
    }
    .stSelectbox [data-testid="stMarkdownContainer"] p:first-child {
        color: #D32F2F !important;
        font-weight: bold !important;
    }
    .custom-label {
        font-weight: bold !important;
        color: #1E88E5 !important;
        font-size: 1.1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# URL input con label en negrita
st.markdown('<p class="custom-label">Ingrese la URL que desea acortar:</p>', unsafe_allow_html=True)
url_original = st.text_input("", placeholder="https://ejemplo.com", label_visibility="collapsed")

# Define the options for the dropdown
utm_source_options = ["", "Telegram", "Facebook", "YouTube", "WhatsApp", "Twitter"]

# Create the dropdown selector con estilo personalizado
st.markdown('<p class="custom-label">Fuente UTM (Opcional):</p>', unsafe_allow_html=True)
utm_source = st.selectbox("", options=utm_source_options, key="utm_source", label_visibility="collapsed")

# Default value for UTM medium based on selected source
default_medium = "social"
st.markdown('<p class="custom-label">Medio UTM (Opcional):</p>', unsafe_allow_html=True)
utm_medium = st.text_input("", key="utm_medium", value=default_medium, label_visibility="collapsed")

# Options for UTM term - correlacionados con las fuentes
utm_term_mapping = {
    "Telegram": "telegram-app",
    "Facebook": "facebook-app", 
    "YouTube": "youtube-app",
    "WhatsApp": "whatsapp-app",
    "Twitter": "twitter-app"
}

# Auto-seleccionar el término UTM basado en la fuente seleccionada
utm_term_auto = utm_term_mapping.get(utm_source, "")
utm_term_options = [""] + list(utm_term_mapping.values())

st.markdown('<p class="custom-label">Término UTM (Opcional):</p>', unsafe_allow_html=True)
utm_term = st.selectbox("", 
                       options=utm_term_options, 
                       key="utm_term",
                       index=utm_term_options.index(utm_term_auto) if utm_term_auto in utm_term_options else 0,
                       label_visibility="collapsed")

# Construct the utm_params dictionary
utm_params = {}
if utm_source:
    utm_params["utm_source"] = utm_source.lower()
if utm_medium:
    utm_params["utm_medium"] = utm_medium.lower()
if utm_term:
    utm_params["utm_term"] = utm_term.lower()

# Mostrar preview de la URL con UTM
if url_original and utm_params:
    parsed_url = urlparse(url_original)
    query_params = parse_qs(parsed_url.query)
    for key, value in utm_params.items():
        query_params[key] = [value]
    new_query = urlencode(query_params, doseq=True)
    url_preview = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_query,
        parsed_url.fragment
    ))
    st.info(f"**URL con UTM:** {url_preview}")

# Botón de acortar con estilo mejorado
st.markdown("<br>", unsafe_allow_html=True)
if st.button("¡Acortar!", use_container_width=True, type="primary"):
    if url_original:
        with st.spinner("Acortando URL..."):
            url_final = acortar_url_isgd(url_original, utm_params)
        
        if url_final:
            st.success("¡URL acortada exitosamente!")
            st.write("**La URL acortada es:**")
            st.code(url_final, language=None)
            
            # Botones de acción
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                    <a href="{url_final}" target="_blank">
                        <button style="width:100%; background-color: #4CAF50; color: white; padding: 12px; 
                                    border: none; border-radius: 6px; cursor: pointer; font-size: 1rem;
                                    font-weight: bold;">
                            🔗 Abrir URL
                        </button>
                    </a>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("📋 Copiar URL", use_container_width=True, key="copy_button"):
                    st.code(url_final, language=None)
                    st.success("¡URL copiada al portapapeles!")
        else:
            st.error("Error al acortar la URL. Intente nuevamente.")
    else:
        st.error("Por favor, ingrese una URL para acortar.")

# Footer information
st.markdown("---")
st.markdown("""
    <div style='text-align: center;'>
        <p style='font-weight: bold; color: #666;'>Creado por Soporte TI</p>
        <p style='color: #888;'>Si tiene algún problema, comuníquese al correo <a href='mailto:gsantos@bloquedearmas.com'>gsantos@bloquedearmas.com</a></p>
    </div>
""", unsafe_allow_html=True)
