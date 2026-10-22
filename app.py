from textblob import TextBlob
import streamlit as st
from PIL import Image
import json
import urllib.parse
import urllib.request


def traducir(texto, origen="es", destino="en"):
    """Traduce usando el servicio público de Google Translate (sin librerías extra)."""
    params = urllib.parse.urlencode({
        "client": "gtx", "sl": origen, "tl": destino, "dt": "t", "q": texto
    })
    url = "https://translate.googleapis.com/translate_a/single?" + params
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return "".join(parte[0] for parte in data[0] if parte[0])

# ---------- Configuración de la página ----------
st.set_page_config(page_title="Análisis de Sentimiento", page_icon="💬", layout="centered")

# ---------- Estilos ----------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(160deg, #fdfbff 0%, #eef2ff 50%, #fdf2f8 100%);
    }
    .titulo {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6366f1, #ec4899, #f59e0b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .subtitulo {
        text-align: center;
        color: #6b7280;
        font-size: 1.1rem;
        margin-top: 0.2rem;
        margin-bottom: 1.5rem;
    }
    .tarjeta {
        border-radius: 18px;
        padding: 1.4rem;
        text-align: center;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        margin-top: 1rem;
    }
    .tarjeta h2 { margin: 0; font-size: 2rem; }
    .tarjeta p  { margin: 0.3rem 0 0 0; font-size: 1.1rem; }
    .positivo { background: #dcfce7; color: #166534; border: 2px solid #86efac; }
    .negativo { background: #fee2e2; color: #991b1b; border: 2px solid #fca5a5; }
    .neutral  { background: #f3f4f6; color: #374151; border: 2px solid #d1d5db; }
    .emoji-grande { font-size: 4rem; }
    div[data-testid="stMetric"] {
        background: white;
        border-radius: 14px;
        padding: 1rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    }
</style>
""", unsafe_allow_html=True)

# ---------- Encabezado ----------
st.markdown('<p class="titulo">Análisis de Sentimiento</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitulo">Descubre si tu frase transmite alegría, tristeza o neutralidad ✨</p>',
            unsafe_allow_html=True)

try:
    image = Image.open('emoticones.jpg')
    st.image(image, use_container_width=True)
except FileNotFoundError:
    pass

# ---------- Barra lateral ----------
with st.sidebar:
    st.markdown("## 📊 Polaridad y Subjetividad")
    st.markdown("""
**🎭 Polaridad**  
Indica si el sentimiento del texto es positivo, negativo o neutral.  
Va de **-1** (muy negativo) a **1** (muy positivo); **0** es neutral.

---

**🧠 Subjetividad**  
Mide cuánto del contenido es opinión, emoción o creencia frente a hechos.  
Va de **0** (totalmente objetivo) a **1** (totalmente subjetivo).
""")
    st.markdown("---")
    st.caption("Hecho con TextBlob + Streamlit 💜")

# ---------- Análisis ----------

st.markdown("### ✍️ Escribe la frase que deseas analizar")
text = st.text_area("Tu frase:", placeholder="Ej: Hoy es un día maravilloso y me siento muy feliz",
                    height=110, label_visibility="collapsed")

if st.button("🔍 Analizar sentimiento", use_container_width=True, type="primary"):
    if not text.strip():
        st.warning("Por favor escribe una frase antes de analizar.")
    else:
        with st.spinner("Analizando tu frase..."):
            try:
                trans_text = traducir(text)
            except Exception:
                st.error("No se pudo traducir el texto. Revisa tu conexión e inténtalo de nuevo.")
                st.stop()

            blob = TextBlob(trans_text)
            polaridad = round(blob.sentiment.polarity, 2)
            subjetividad = round(blob.sentiment.subjectivity, 2)

        with st.expander("🌐 Ver traducción al inglés"):
            st.write(trans_text)

        col1, col2 = st.columns(2)
        col1.metric("🎭 Polaridad", polaridad)
        col2.metric("🧠 Subjetividad", subjetividad)

        st.caption("Polaridad (de -1 a 1)")
        st.progress((polaridad + 1) / 2)
        st.caption("Subjetividad (de 0 a 1)")
        st.progress(subjetividad)

        # Umbral pequeño para que el neutral sí pueda aparecer
        if polaridad > 0.05:
            clase, emoji, etiqueta = "positivo", "😊", "Sentimiento Positivo"
            st.balloons()
        elif polaridad < -0.05:
            clase, emoji, etiqueta = "negativo", "😔", "Sentimiento Negativo"
        else:
            clase, emoji, etiqueta = "neutral", "😐", "Sentimiento Neutral"

        st.markdown(f"""
        <div class="tarjeta {clase}">
            <div class="emoji-grande">{emoji}</div>
            <h2>{etiqueta}</h2>
            <p>Polaridad: {polaridad} · Subjetividad: {subjetividad}</p>
        </div>
        """, unsafe_allow_html=True)
