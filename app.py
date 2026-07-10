# ---------- MUST BE FIRST ----------
import streamlit as st
st.set_page_config(page_title="🧠 HBI Platform", page_icon="🧠", layout="wide")

# ---------- Configuration ----------
try:
    API_URL = st.secrets["API_URL"]
except (FileNotFoundError, KeyError):
    API_URL = "http://localhost:8000/api/v1"

# ---------- Imports ----------
import requests
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from io import BytesIO
import base64
from fpdf import FPDF

# ---------- Session State ----------
if "token" not in st.session_state:
    st.session_state.token = None
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "batch_results" not in st.session_state:
    st.session_state.batch_results = None

# ---------- API Client ----------
def api_request(method, endpoint, data=None, files=None, form_data=None, headers=None):
    url = f"{API_URL}{endpoint}"
    if form_data:
        default_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    else:
        default_headers = {"Content-Type": "application/json"}
    if st.session_state.token:
        default_headers["Authorization"] = f"Bearer {st.session_state.token}"
    if headers:
        default_headers.update(headers)

    try:
        if method == "GET":
            r = requests.get(url, headers=default_headers)
        elif method == "POST":
            if files:
                r = requests.post(url, files=files, headers=default_headers)
            elif form_data:
                r = requests.post(url, data=form_data, headers=default_headers)
            else:
                r = requests.post(url, json=data, headers=default_headers)
        return r
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to the backend. Make sure the server is running.")
        return None

# ---------- Auto-Login ----------
def auto_login():
    email = "test@example.com"
    password = "test123"
    form_data = {"username": email, "password": password}
    r = api_request("POST", "/auth/login", form_data=form_data)
    if r and r.status_code == 200:
        st.session_state.token = r.json()["access_token"]
        return True
    else:
        st.error("❌ Auto-login failed. Please check backend or credentials.")
        return False

# ---------- Prediction ----------
def analyze_text(text, tasks):
    r = api_request("POST", "/predict/single", data={"text": text, "tasks": tasks})
    if r and r.status_code == 200:
        result = r.json()
        st.session_state.history.append({
            "text": text,
            "tasks": tasks,
            "results": result["results"],
            "timestamp": time.time()
        })
        return result
    else:
        st.error(f"❌ Prediction failed: {r.text if r else 'No response'}")
        return None

# ---------- Batch Upload ----------
def process_batch(file):
    try:
        df = pd.read_csv(file)
    except Exception as e:
        st.error(f"Error reading CSV: {e}")
        return None
    if "text" not in df.columns:
        st.error("❌ CSV must have a 'text' column.")
        return None
    progress = st.progress(0)
    results = []
    for i, row in enumerate(df.itertuples()):
        text = row.text
        r = api_request("POST", "/predict/single", data={"text": text, "tasks": ["sentiment", "emotion", "toxicity", "urgency"]})
        if r and r.status_code == 200:
            res = r.json()
            results.append({
                "text": text,
                "sentiment": res["results"].get("sentiment", {}).get("label", ""),
                "sentiment_score": res["results"].get("sentiment", {}).get("score", 0),
                "emotion": res["results"].get("emotion", {}).get("label", ""),
                "emotion_score": res["results"].get("emotion", {}).get("score", 0),
                "toxicity": res["results"].get("toxicity", {}).get("label", ""),
                "toxicity_score": res["results"].get("toxicity", {}).get("score", 0),
                "urgency": res["results"].get("urgency", {}).get("level", ""),
                "urgency_score": res["results"].get("urgency", {}).get("score", 0),
            })
        progress.progress((i + 1) / len(df))
    return pd.DataFrame(results)

# ---------- Feature 1: Sentiment Trend Chart ----------
def plot_sentiment_trend(history):
    if not history:
        return None
    data = []
    for entry in history:
        if "sentiment" in entry.get("results", {}):
            data.append({
                "time": pd.to_datetime(entry["timestamp"], unit="s"),
                "score": entry["results"]["sentiment"].get("score", 0)
            })
    if not data:
        return None
    df = pd.DataFrame(data)
    fig = px.line(df, x="time", y="score", title="Sentiment Score Over Time", labels={"score": "Confidence"})
    return fig

# ---------- Feature 2: Explainability ----------
def explain_text(text, result):
    if not result or "sentiment" not in result:
        return None
    positive_words = ["love", "happy", "great", "good", "amazing", "excellent", "best", "wonderful", "awesome", "nice"]
    negative_words = ["hate", "sad", "bad", "terrible", "awful", "worst", "horrible", "disappointed", "poor", "useless"]
    words = text.split()
    explained = []
    for word in words:
        clean = word.strip(".,!?")
        if clean.lower() in positive_words:
            explained.append(f"🟢 {word}")
        elif clean.lower() in negative_words:
            explained.append(f"🔴 {word}")
        else:
            explained.append(word)
    return " ".join(explained)

# ---------- Feature 3: Radar Chart ----------
def plot_radar(result):
    if not result:
        return None
    tasks = result.get("results", {})
    if not tasks:
        return None
    scores = {}
    if "sentiment" in tasks:
        scores["sentiment"] = tasks["sentiment"].get("score", 0) if tasks["sentiment"].get("label") == "POSITIVE" else 1 - tasks["sentiment"].get("score", 0)
    if "emotion" in tasks:
        emo = tasks["emotion"].get("label", "")
        if emo in ["joy", "love"]:
            scores["emotion"] = tasks["emotion"].get("score", 0)
        else:
            scores["emotion"] = 1 - tasks["emotion"].get("score", 0)
    if "toxicity" in tasks:
        scores["toxicity"] = 1 - tasks["toxicity"].get("score", 0)
    if "urgency" in tasks:
        u = tasks["urgency"].get("level", "LOW")
        scores["urgency"] = {"HIGH": 0, "MEDIUM": 0.5, "LOW": 1}.get(u, 0.5)
    if not scores:
        return None
    categories = list(scores.keys())
    values = list(scores.values())
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        marker=dict(color='rgba(129, 140, 248, 0.8)'),
        line=dict(color='#818cf8')
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title="Multi-Task Analysis Radar",
        showlegend=False,
        height=400
    )
    return fig

# ---------- Feature 4: Word Cloud (with fallback if error) ----------
def generate_wordcloud(texts):
    if not texts:
        return None
    combined = " ".join(texts)
    try:
        wordcloud = WordCloud(background_color="white", colormap="viridis", width=800, height=400).generate(combined)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        return fig
    except Exception as e:
        st.warning(f"⚠️ WordCloud could not be generated: {e}")
        return None

# ---------- Feature 5: PDF Report ----------
def generate_pdf_report(history, batch_df=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="HBI Platform - Analysis Report", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, txt=f"Generated on: {time.strftime('%Y-%m-%d %H:%M')}", ln=True, align="L")
    pdf.ln(10)
    if history:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, txt="Recent Predictions", ln=True)
        pdf.set_font("Arial", "", 10)
        for entry in history[-5:]:
            txt = f"- {entry['text'][:50]}... Sent: {entry['results'].get('sentiment', {}).get('label', 'N/A')}"
            pdf.cell(200, 8, txt=txt, ln=True)
    pdf.ln(10)
    if batch_df is not None and not batch_df.empty:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, txt="Batch Results Summary", ln=True)
        pdf.set_font("Arial", "", 10)
        for _, row in batch_df.head(10).iterrows():
            txt = f"- {row['text'][:40]}... Sent: {row['sentiment']} | Emo: {row['emotion']}"
            pdf.cell(200, 8, txt=txt, ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt="End of Report", ln=True, align="C")
    return pdf.output(dest="S").encode("latin-1")

# ---------- UI: Custom CSS ----------
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%); color: #e0e0e0; }
    .main > div { padding: 1rem 2rem; }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 1.5rem;
        padding: 1.75rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    .glass-card:hover { border-color: rgba(99, 102, 241, 0.3); box-shadow: 0 8px 32px rgba(99, 102, 241, 0.1); }
    .result-card {
        background: rgba(255, 255, 255, 0.04);
        border-left: 4px solid #818cf8;
        border-radius: 0.75rem;
        padding: 1.25rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    .result-card:hover { background: rgba(255, 255, 255, 0.08); transform: translateY(-2px); }
    .confidence-bar {
        height: 8px;
        border-radius: 4px;
        background: rgba(255, 255, 255, 0.1);
        margin-top: 0.5rem;
        overflow: hidden;
    }
    .confidence-bar-fill {
        height: 100%;
        border-radius: 4px;
        background: linear-gradient(90deg, #818cf8, #a78bfa, #c084fc);
        transition: width 1s ease-out;
    }
    .task-label { font-weight: 600; text-transform: capitalize; color: #a0a0b0; font-size: 0.85rem; letter-spacing: 0.05em; }
    .value-label { font-weight: 700; font-size: 1.1rem; color: #e0e0e0; }
    .stTextArea textarea {
        background: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 1rem !important;
        color: #000000 !important;
        font-size: 1rem !important;
        padding: 1rem !important;
        caret-color: #818cf8 !important;
    }
    .stTextArea textarea::placeholder { color: #9ca3af !important; opacity: 1 !important; }
    .stTextArea textarea:focus { border-color: #818cf8 !important; box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.2) !important; outline: none !important; }
    .stTextArea textarea:not(:placeholder-shown) { color: #000000 !important; }
    .stButton button {
        background: linear-gradient(135deg, #818cf8, #a78bfa) !important;
        color: white !important;
        border: none !important;
        border-radius: 0.75rem !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    .stButton button:hover { transform: scale(1.02) !important; box-shadow: 0 4px 20px rgba(129, 140, 248, 0.4) !important; }
    .stButton button:disabled { opacity: 0.5 !important; cursor: not-allowed !important; transform: none !important; }
    .stMultiSelect [data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 0.75rem !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #818cf8; border-radius: 8px; }
    .header-icon { font-size: 2.5rem; margin-right: 0.75rem; }
</style>
""", unsafe_allow_html=True)

# ---------- Auto-login ----------
if not st.session_state.token:
    if auto_login():
        st.success("✅ Automatically logged in")
        st.rerun()
    else:
        st.stop()

# ---------- HEADER ----------
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown('<span class="header-icon">🧠</span>', unsafe_allow_html=True)
with col2:
    st.markdown('<h1 style="font-size: 2.5rem; margin: 0; color: #a78bfa; font-weight: 800;">Human Behavior Intelligence</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #a0a0b0; font-size: 0.9rem; margin-top: -0.25rem;">Advanced text analysis powered by AI · Sentiment · Emotion · Toxicity · Urgency</p>', unsafe_allow_html=True)

st.markdown("---")

# ---------- Input ----------
with st.container():
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📝 Enter text to analyze")
        text_input = st.text_area("", height=120, placeholder="Try: I love this product, but I'm worried about the price...", key="text_input", label_visibility="collapsed")
    with col2:
        st.markdown("### 🧩 Select tasks")
        tasks = st.multiselect("", options=["sentiment", "emotion", "toxicity", "urgency"], default=["sentiment", "emotion"], key="tasks_select", label_visibility="collapsed")
        if st.button("🚀 Analyze", type="primary", use_container_width=True):
            if text_input.strip() and tasks:
                with st.spinner("🔄 Analyzing..."):
                    result = analyze_text(text_input, tasks)
                    if result:
                        st.session_state.last_result = result
                        st.rerun()
            elif not text_input.strip():
                st.warning("⚠️ Please enter some text.")
            else:
                st.warning("⚠️ Please select at least one task.")

st.markdown("---")

# ---------- Results ----------
if st.session_state.last_result:
    result = st.session_state.last_result
    st.markdown("### 📊 Analysis Results")
    emoji_map = {
        "sentiment": {"POSITIVE": "😊", "NEGATIVE": "😞"},
        "emotion": {"joy": "😄", "sadness": "😢", "anger": "😡", "fear": "😨", "love": "❤️", "surprise": "😲"},
        "toxicity": {"toxic": "☠️", "non-toxic": "✅"},
        "urgency": {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
    }
    color_map = {
        "sentiment": {"POSITIVE": "#4ade80", "NEGATIVE": "#f87171"},
        "emotion": {"joy": "#fbbf24", "sadness": "#60a5fa", "anger": "#f87171", "fear": "#a78bfa", "love": "#f472b6", "surprise": "#fcd34d"},
        "toxicity": {"toxic": "#f87171", "non-toxic": "#4ade80"},
        "urgency": {"HIGH": "#f87171", "MEDIUM": "#fbbf24", "LOW": "#4ade80"}
    }
    cols = st.columns(min(len(result["results"]), 4))
    for i, (task, data) in enumerate(result["results"].items()):
        with cols[i % len(cols)]:
            emoji = emoji_map.get(task, {}).get(data["label"], "📌")
            color = color_map.get(task, {}).get(data["label"], "#818cf8")
            score = data["score"] * 100
            st.markdown(f"""
            <div class="result-card" style="border-left-color: {color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="task-label">{task}</span>
                    <span style="font-size: 1.5rem;">{emoji}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.25rem;">
                    <span class="value-label">{data["label"]}</span>
                    <span style="font-size: 0.85rem; color: #a0a0b0;">{score:.1f}%</span>
                </div>
                <div class="confidence-bar">
                    <div class="confidence-bar-fill" style="width: {score:.0f}%; background: {color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Explainability
    if "sentiment" in result["results"]:
        explained = explain_text(text_input, result)
        if explained:
            st.markdown("**💡 Explanation (word highlights):**")
            st.markdown(f"<div style='background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 0.75rem;'>{explained}</div>", unsafe_allow_html=True)

    # Radar Chart
    if len(result["results"]) >= 2:
        radar_fig = plot_radar(result)
        if radar_fig:
            st.plotly_chart(radar_fig, use_container_width=True)

# ---------- Sentiment Trend ----------
if len(st.session_state.history) >= 2:
    trend_fig = plot_sentiment_trend(st.session_state.history)
    if trend_fig:
        st.markdown("### 📈 Sentiment Trend Over Time")
        st.plotly_chart(trend_fig, use_container_width=True)

# ---------- History ----------
if st.session_state.history:
    with st.expander("📜 Prediction History", expanded=False):
        df = pd.DataFrame(st.session_state.history)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        df["timestamp"] = df["timestamp"].dt.strftime("%H:%M:%S")
        st.dataframe(df[["text", "tasks", "timestamp"]], use_container_width=True, height=200)
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.history = []
                st.session_state.last_result = None
                st.rerun()
        with col2:
            if st.button("📄 Export PDF Report", use_container_width=True):
                pdf_data = generate_pdf_report(st.session_state.history, st.session_state.batch_results)
                b64 = base64.b64encode(pdf_data).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="hbi_report.pdf">Download PDF</a>'
                st.markdown(href, unsafe_allow_html=True)

# ---------- Batch Upload ----------
st.markdown("---")
st.markdown("### 📁 Batch Upload (CSV)")
st.caption("Upload a CSV file with a `text` column. Each row will be analyzed automatically.")
with st.container():
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"], label_visibility="collapsed")
    if uploaded_file:
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("📊 Process Batch", type="primary", use_container_width=True):
                with st.spinner("🔄 Processing all rows..."):
                    results_df = process_batch(uploaded_file)
                    if results_df is not None and not results_df.empty:
                        st.session_state.batch_results = results_df
                        st.rerun()
        if st.session_state.batch_results is not None and not st.session_state.batch_results.empty:
            df = st.session_state.batch_results
            st.success(f"✅ Processed {len(df)} rows.")
            st.dataframe(df, use_container_width=True, height=300)
            # Word Cloud (with fallback)
            if "text" in df.columns:
                wc_fig = generate_wordcloud(df["text"].tolist())
                if wc_fig:
                    st.markdown("### ☁️ Word Cloud from Batch")
                    st.pyplot(wc_fig)
            csv = df.to_csv(index=False)
            st.download_button("📥 Download Results as CSV", data=csv, file_name=f"predictions_{int(time.time())}.csv", mime="text/csv", use_container_width=True)

# ---------- Footer ----------
st.markdown("---")
st.caption("🧠 Human Behavior Intelligence Platform · Built with Streamlit + FastAPI + HuggingFace")