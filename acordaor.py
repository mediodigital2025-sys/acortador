import streamlit as st
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import io
import pandas as pd
from datetime import datetime
import json
import os

# Sistema de contador de uso
def cargar_contador():
    """Carga el contador de uso desde un archivo JSON"""
    try:
        if os.path.exists('contador_uso.json'):
            with open('contador_uso.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Asegurarnos de que los campos existan
                if 'total_acortamientos' not in data:
                    data['total_acortamientos'] = 0
                if 'fecha_ultimo_uso' not in data:
                    data['fecha_ultimo_uso'] = "Nunca"
                return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return {"total_acortamientos": 0, "fecha_ultimo_uso": "Nunca"}

def guardar_contador(contador):
    """Guarda el contador de uso en un archivo JSON"""
    try:
        with open('contador_uso.json', 'w', encoding='utf-8') as f:
            json.dump(contador, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.warning(f"No se pudo guardar el contador: {e}")

def incrementar_contador(num_urls):
    """Incrementa el contador de uso"""
    contador = cargar_contador()
    contador["total_acortamientos"] = contador.get("total_acortamientos", 0) + num_urls
    contador["fecha_ultimo_uso"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    guardar_contador(contador)
    return contador

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
        response = requests.get(f'https://is.gd/create.php?format=simple&url={url_larga}', timeout=10)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return None
    except:
        return None

def generar_archivo_resultados(urls_acortadas, formato='txt'):
    """
    Genera un archivo con los resultados de las URLs acortadas
    """
    if formato == 'txt':
        # Formato de texto plano
        contenido = "=" * 60 + "\n"
        contenido += "GESTIÓN DE ENLACES INTELIGENTE - RESULTADOS\n"
        contenido += "=" * 60 + "\n\n"
        contenido += f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        contenido += f"Total de URLs procesadas: {len(urls_acortadas)}\n"
        contenido += "-" * 60 + "\n\n"
        
        for i, (nombre_url, url_original, url_acortada) in enumerate(urls_acortadas, 1):
            contenido += f"URL #{i}\n"
            contenido += f"{'-'*40}\n"
            contenido += f"ORIGINAL:\n{url_original}\n\n"
            contenido += f"ACORTADA CON UTM:\n{url_acortada}\n"
            contenido += "-" * 60 + "\n\n"
        
        contenido += "\n" + "=" * 60 + "\n"
        contenido += "FIN DEL REPORTE\n"
        contenido += "=" * 60 + "\n"
        
        return contenido.encode('utf-8')
    
    elif formato == 'csv':
        # Formato CSV con más información
        data = {
            'Número': [],
            'Nombre': [],
            'URL Original': [],
            'URL Acortada': [],
            'Fecha Procesamiento': []
        }
        
        fecha_procesamiento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for i, (nombre_url, url_original, url_acortada) in enumerate(urls_acortadas, 1):
            data['Número'].append(i)
            data['Nombre'].append(nombre_url)
            data['URL Original'].append(url_original)
            data['URL Acortada'].append(url_acortada)
            data['Fecha Procesamiento'].append(fecha_procesamiento)
        
        df = pd.DataFrame(data)
        return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8')
    
    else:  # txt por defecto
        return generar_archivo_resultados(urls_acortadas, 'txt')

# Cargar contador al inicio
contador_uso = cargar_contador()

# Configuración del título con HTML para tamaño personalizado
st.markdown("""
    <h1 style='text-align: center; color: #1E3A8A; font-size: 2.2rem; margin-bottom: 0.5rem;'>
        🚀 Gestión de enlaces inteligente: Acortador con etiquetado UTM automático
    </h1>
    <div style='text-align: center; color: #666; margin-bottom: 1.5rem;'>
        <small>📊 Estadísticas: {total} URLs acortadas | Último uso: {fecha}</small>
    </div>
""".format(
    total=contador_uso.get('total_acortamientos', 0),
    fecha=contador_uso.get('fecha_ultimo_uso', 'Nunca')
), unsafe_allow_html=True)

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
        color: #1E3A8A !important;
        font-size: 1.1rem !important;
        margin-bottom: 5px !important;
    }
    .url-container {
        margin-bottom: 10px;
        padding: 10px;
        border-radius: 5px;
        background-color: #f8f9fa;
    }
    .download-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        padding: 12px 24px !important;
        border-radius: 8px !important;
        border: none !important;
        cursor: pointer !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    .stats-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .result-item {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #4CAF50;
    }
    .error-message {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .success-message {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .section-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        margin-top: 20px;
        font-weight: bold;
        text-align: center;
    }
    .content-box {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        background-color: white;
    }
    .format-option {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    .format-option.selected {
        border-color: #667eea;
        background-color: #f0f7ff;
    }
    .download-section {
        background-color: #f0f7ff;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        border: 2px solid #667eea;
    }
    .url-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .url-number {
        display: inline-block;
        background-color: #667eea;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        text-align: center;
        line-height: 30px;
        font-weight: bold;
        margin-right: 10px;
    }
    .preview-url {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
        font-family: monospace;
        font-size: 0.9rem;
        overflow-x: auto;
        white-space: nowrap;
    }
    </style>
""", unsafe_allow_html=True)

# Define the options for the dropdown
utm_source_options = ["", "Telegram", "Facebook", "YouTube", "WhatsApp", "Twitter", "Instagram", "LinkedIn", "Email", "SMS", "Otro"]

# Create the dropdown selector con estilo personalizado
st.markdown('<p class="custom-label">📊 Fuente UTM (Opcional):</p>', unsafe_allow_html=True)
utm_source = st.selectbox("", options=utm_source_options, key="utm_source", label_visibility="collapsed")

# Default value for UTM medium based on selected source
default_medium = "social"
st.markdown('<p class="custom-label">🎯 Medio UTM (Opcional):</p>', unsafe_allow_html=True)
utm_medium = st.text_input("", key="utm_medium", value=default_medium, placeholder="Ej: social, email, cpc, etc.", label_visibility="collapsed")

# Options for UTM term - correlacionados con las fuentes
utm_term_mapping = {
    "Telegram": "telegram-app",
    "Facebook": "facebook-app", 
    "YouTube": "youtube-app",
    "WhatsApp": "whatsapp-app",
    "Twitter": "twitter-app",
    "Instagram": "instagram-app",
    "LinkedIn": "linkedin-app",
    "Email": "email-campaign",
    "SMS": "sms-marketing",
    "Otro": "custom-source"
}

# Auto-seleccionar el término UTM basado en la fuente seleccionada
utm_term_auto = utm_term_mapping.get(utm_source, "")
utm_term_options = [""] + list(utm_term_mapping.values())

st.markdown('<p class="custom-label">🏷️ Término UTM (Opcional):</p>', unsafe_allow_html=True)
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

# Mostrar parámetros UTM configurados
if utm_params:
    st.info(f"**Parámetros UTM configurados:** {utm_params}")

# Sección para múltiples URLs
st.markdown('<p class="custom-label">🔗 Ingrese hasta 8 URLs que desea acortar:</p>', unsafe_allow_html=True)

# Crear 8 campos de texto para URLs en 2 columnas
urls = []
url_containers = st.columns(2)

for i in range(8):
    col_idx = i % 2
    with url_containers[col_idx]:
        url = st.text_input(
            f"URL {i+1}", 
            placeholder=f"https://ejemplo.com/pagina{i+1}",
            key=f"url_{i}",
            help=f"Ingrese la URL completa con http:// o https://"
        )
        if url:
            # Validar URL básica
            if url.startswith(('http://', 'https://')):
                urls.append(url)
            else:
                st.warning(f"La URL debe comenzar con http:// o https://")

# Contador de URLs ingresadas
st.markdown(f"""
    <div style='text-align: right; color: #666; margin-bottom: 20px;'>
        📝 URLs ingresadas: <strong>{len(urls)}/8</strong>
    </div>
""", unsafe_allow_html=True)

# Botón de acortar con estilo mejorado
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🎯 ¡Acortar URLs!", use_container_width=True, type="primary", key="acortar_main"):
        if urls:
            urls_acortadas = []
            errores = []
            
            with st.spinner("🔧 Procesando URLs..."):
                progress_bar = st.progress(0)
                total_urls = len(urls)
                
                for i, url in enumerate(urls):
                    if url:  # Solo procesar URLs no vacías
                        url_final = acortar_url_isgd(url, utm_params)
                        if url_final:
                            urls_acortadas.append((f"URL {i+1}", url, url_final))
                        else:
                            errores.append(f"URL {i+1}: {url}")
                        
                        # Actualizar barra de progreso
                        progress_bar.progress((i + 1) / total_urls)
            
            if urls_acortadas or errores:
                # Actualizar contador de uso solo si hubo URLs exitosas
                if urls_acortadas:
                    incrementar_contador(len(urls_acortadas))
                
                # Mostrar resumen de resultados
                st.markdown('<div class="section-header">📊 RESULTADOS DEL PROCESAMIENTO</div>', unsafe_allow_html=True)
                
                # Estadísticas en una sola línea
                stats_col1, stats_col2, stats_col3 = st.columns(3)
                with stats_col1:
                    if urls_acortadas:
                        st.markdown(f'<div style="text-align: center; padding: 10px; background-color: #e8f5e9; border-radius: 8px; border: 2px solid #4caf50;">'
                                  f'<div style="font-size: 1.5rem; font-weight: bold; color: #2e7d32;">{len(urls_acortadas)}</div>'
                                  f'<div style="font-size: 0.9rem;">✅ Exitosas</div>'
                                  f'</div>', unsafe_allow_html=True)
                with stats_col2:
                    if errores:
                        st.markdown(f'<div style="text-align: center; padding: 10px; background-color: #ffebee; border-radius: 8px; border: 2px solid #f44336;">'
                                  f'<div style="font-size: 1.5rem; font-weight: bold; color: #c62828;">{len(errores)}</div>'
                                  f'<div style="font-size: 0.9rem;">❌ Fallidas</div>'
                                  f'</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div style="text-align: center; padding: 10px; background-color: #e8f5e9; border-radius: 8px; border: 2px solid #4caf50;">'
                                  f'<div style="font-size: 1.5rem; font-weight: bold; color: #2e7d32;">0</div>'
                                  f'<div style="font-size: 0.9rem;">❌ Fallidas</div>'
                                  f'</div>', unsafe_allow_html=True)
                with stats_col3:
                    st.markdown(f'<div style="text-align: center; padding: 10px; background-color: #e3f2fd; border-radius: 8px; border: 2px solid #2196f3;">'
                              f'<div style="font-size: 1.5rem; font-weight: bold; color: #1565c0;">{len(urls)}</div>'
                              f'<div style="font-size: 0.9rem;">📊 Total</div>'
                              f'</div>', unsafe_allow_html=True)
                
                # Guardar los resultados en session_state para acceso posterior
                st.session_state['urls_acortadas'] = urls_acortadas
                
                # MOSTRAR URLs ACORTADAS Y OPCIONES DE DESCARGA EN UNA SOLA SECCIÓN
                if urls_acortadas:
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Sección de URLs acortadas
                    st.markdown("### 🔗 URLs Acortadas")
                    
                    # Mostrar cada URL acortada en una tarjeta
                    for nombre_url, url_original, url_acortada in urls_acortadas:
                        st.markdown('<div class="url-card">', unsafe_allow_html=True)
                        
                        # Número y título
                        num = nombre_url.split()[-1]
                        st.markdown(f'<div style="display: flex; align-items: center; margin-bottom: 15px;">'
                                  f'<span class="url-number">{num}</span>'
                                  f'<span style="font-weight: bold; font-size: 1.1rem;">{nombre_url}</span>'
                                  f'</div>', unsafe_allow_html=True)
                        
                        # URLs
                        col_url1, col_url2 = st.columns(2)
                        with col_url1:
                            st.markdown("**URL Original:**")
                            st.markdown(f'<div class="preview-url">{url_original[:80]}{"..." if len(url_original) > 80 else ""}</div>', unsafe_allow_html=True)
                        with col_url2:
                            st.markdown("**URL Acortada:**")
                            st.markdown(f'<div class="preview-url">{url_acortada}</div>', unsafe_allow_html=True)
                        
                        # Botones de acción en una sola línea
                        col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 1])
                        with col_btn1:
                            st.markdown(f"""
                                <a href="{url_acortada}" target="_blank" style="text-decoration: none;">
                                    <button style="width:100%; background-color: #4CAF50; color: white; padding: 10px; 
                                                border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: bold;">
                                        🔗 Abrir URL
                                    </button>
                                </a>
                            """, unsafe_allow_html=True)
                        with col_btn2:
                            st.code(url_acortada, language="text")
                        with col_btn3:
                            if st.button("📋", key=f"copy_{hash(url_acortada)}", use_container_width=True, 
                                        help=f"Copiar {nombre_url}"):
                                st.success(f"¡{nombre_url} copiada!")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # SECCIÓN DE DESCARGA - INTEGRADA EN LA MISMA VISTA
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown('<div class="download-section">', unsafe_allow_html=True)
                    
                    st.markdown("### 📥 Descargar Resultados Completos")
                    st.markdown("Selecciona el formato y descarga todos los resultados en un archivo.")
                    
                    # Opciones de formato
                    st.markdown("#### 📁 Seleccionar Formato de Archivo")
                    
                    col_format1, col_format2 = st.columns(2)
                    formato_seleccionado = None
                    
                    with col_format1:
                        formato_txt_seleccionado = st.checkbox("📄 Archivo de texto (.txt)", value=True, key="txt_format")
                        if formato_txt_seleccionado:
                            formato_seleccionado = "txt"
                    
                    with col_format2:
                        formato_csv_seleccionado = st.checkbox("📊 Archivo CSV (.csv)", value=False, key="csv_format")
                        if formato_csv_seleccionado:
                            formato_seleccionado = "csv"
                    
                    # Si ambos están seleccionados o ninguno, usar txt por defecto
                    if not formato_seleccionado:
                        formato_seleccionado = "txt"
                        formato_txt_seleccionado = True
                    
                    # Mostrar información del archivo seleccionado
                    extension = '.txt' if formato_seleccionado == 'txt' else '.csv'
                    
                    st.info(f"""
                    **📋 Información del archivo seleccionado:**
                    - **Formato:** {formato_seleccionado.upper()}
                    - **Extensión:** {extension}
                    - **URLs incluidas:** {len(urls_acortadas)}
                    - **Fecha de generación:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    """)
                    
                    # Generar y descargar archivo
                    archivo_resultados = generar_archivo_resultados(urls_acortadas, formato_seleccionado)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    nombre_archivo = f"enlaces_acortados_{timestamp}{extension}"
                    
                    # Botón de descarga grande
                    st.download_button(
                        label=f"⬇️ DESCARGAR ARCHIVO ({formato_seleccionado.upper()})",
                        data=archivo_resultados,
                        file_name=nombre_archivo,
                        mime="text/plain" if formato_seleccionado == 'txt' else "text/csv",
                        use_container_width=True,
                        key="descargar_resultados",
                        help=f"Haz clic para descargar el archivo {formato_seleccionado.upper()} con todos los resultados"
                    )
                    
                    # Vista previa del archivo
                    with st.expander("👁️ Ver vista previa del archivo"):
                        if formato_seleccionado == 'txt':
                            contenido_preview = generar_archivo_resultados(urls_acortadas, 'txt').decode('utf-8')
                            st.text_area(
                                "Contenido del archivo:",
                                value=contenido_preview[:800] + ("\n[...]" if len(contenido_preview) > 800 else ""),
                                height=200,
                                disabled=True
                            )
                        else:
                            df_preview = pd.DataFrame({
                                'Número': list(range(1, len(urls_acortadas)+1)),
                                'URL Original': [url[1] for url in urls_acortadas],
                                'URL Acortada': [url[2] for url in urls_acortadas],
                                'Fecha': [datetime.now().strftime("%Y-%m-%d")] * len(urls_acortadas)
                            })
                            st.dataframe(df_preview, use_container_width=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Mostrar errores si los hay
                if errores:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("### ⚠️ URLs con Errores")
                    for error in errores:
                        st.error(f"**{error}** - No se pudo acortar esta URL. Verifica que sea válida.")
                
            else:
                st.error("❌ No se pudo acortar ninguna URL. Verifica las URLs e intenta nuevamente.")
                
        else:
            st.error("❌ Por favor, ingrese al menos una URL para acortar.")
    else:
        # Mostrar estado de preparación
        if urls:
            st.info(f"✅ Listo para procesar {len(urls)} URLs")
        else:
            st.warning("⚠️ Ingresa al menos una URL para comenzar")

# Información adicional
st.markdown("---")
st.markdown("""
    <div style='background-color: #f0f7ff; padding: 20px; border-radius: 10px; margin-top: 20px;'>
        <h3 style='color: #1E3A8A;'>💡 ¿Qué es el etiquetado UTM?</h3>
        <p>Los parámetros UTM son etiquetas que puedes agregar a tus URLs para rastrear el rendimiento 
        de tus campañas en herramientas como Google Analytics. Esta herramienta automáticamente:</p>
        <ul>
            <li><strong>utm_source:</strong> Identifica la fuente del tráfico (ej: facebook, telegram)</li>
            <li><strong>utm_medium:</strong> Especifica el medio de marketing (ej: social, email)</li>
            <li><strong>utm_term:</strong> Identifica las palabras clave pagadas o términos específicos</li>
        </ul>
    </div>
""", unsafe_allow_html=True)

# Footer information
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <div style='display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 10px 20px; border-radius: 20px; margin-bottom: 10px;'>
            <strong>🚀 Herramienta de Gestión de Enlaces Inteligente</strong>
        </div>
        <p style='font-weight: bold; color: #666; margin-top: 10px;'>Creado por Soporte TI</p>
        <p style='color: #888; font-size: 0.9rem;'>Si tiene algún problema, comuníquese al correo 
        <a href='mailto:gsantos@bloquedearmas.com' style='color: #1E88E5;'>gsantos@bloquedearmas.com</a></p>
    </div>
""", unsafe_allow_html=True)
