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
    .url-container {
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

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

# Sección para múltiples URLs
st.markdown('<p class="custom-label">Ingrese hasta 8 URLs que desea acortar:</p>', unsafe_allow_html=True)

# Crear 8 campos de texto para URLs
urls = []
for i in range(8):
    url = st.text_input(
        f"URL {i+1}", 
        placeholder=f"https://ejemplo.com/url{i+1}",
        key=f"url_{i}",
        label_visibility="collapsed"
    )
    if url:
        urls.append(url)

# Mostrar preview de la primera URL con UTM (si existe)
if urls and utm_params:
    first_url = urls[0]
    parsed_url = urlparse(first_url)
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
    st.info(f"**Ejemplo de URL con UTM:** {url_preview}")

# Botón de acortar con estilo mejorado
st.markdown("<br>", unsafe_allow_html=True)
if st.button("¡Acortar URLs!", use_container_width=True, type="primary"):
    if urls:
        urls_acortadas = []
        with st.spinner("Acortando URLs..."):
            for i, url in enumerate(urls):
                if url:  # Solo procesar URLs no vacías
                    url_final = acortar_url_isgd(url, utm_params)
                    if url_final:
                        urls_acortadas.append((f"URL {i+1}", url, url_final))
        
        if urls_acortadas:
            st.success(f"¡Se acortaron {len(urls_acortadas)} URLs exitosamente!")
            
            # Mostrar resultados en una tabla
            st.write("**Resultados:**")
            
            for nombre_url, url_original, url_acortada in urls_acortadas:
                with st.expander(f"{nombre_url}: {url_acortada}"):
                    st.write(f"**Original:** {url_original}")
                    st.write(f"**Acortada:** `{url_acortada}`")
                    
                    # Botones de acción para cada URL
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                            <a href="{url_acortada}" target="_blank">
                                <button style="width:100%; background-color: #4CAF50; color: white; padding: 8px; 
                                            border: none; border-radius: 4px; cursor: pointer; font-size: 0.9rem;">
                                    🔗 Abrir URL
                                </button>
                            </a>
                        """, unsafe_allow_html=True)
                    with col2:
                        if st.button("📋 Copiar", key=f"copy_{url_acortada}", use_container_width=True):
                            st.code(url_acortada, language=None)
                            st.success(f"¡{nombre_url} copiada!")
            
            # Botón para copiar todas las URLs
            st.markdown("---")
            if st.button("📋 Copiar todas las URLs acortadas", use_container_width=True):
                todas_las_urls = "\n".join([url_acortada for _, _, url_acortada in urls_acortadas])
                st.code(todas_las_urls, language=None)
                st.success("¡Todas las URLs copiadas al portapapeles!")
                
        else:
            st.error("Error al acortar las URLs. Intente nuevamente.")
    else:
        st.error("Por favor, ingrese al menos una URL para acortar.")

# Footer information
st.markdown("---")
st.markdown("""
    <div style='text-align: center;'>
        <p style='font-weight: bold; color: #666;'>Creado por Soporte TI</p>
        <p style='color: #888;'>Si tiene algún problema, comuníquese al correo <a href='mailto:gsantos@bloquedearmas.com'>gsantos@bloquedearmas.com</a></p>
    </div>
""", unsafe_allow_html=True)
