import io
import json

import requests
import streamlit as st
from PIL import Image

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
API_BASE = "http://localhost:8000"

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Smart Agriculture",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — Botanical Field Journal × Precision Agri-Tech
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,600&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

    /* ── CSS Variables ── */
    :root {
        --soil:        #1c1408;
        --bark:        #2a1f0e;
        --moss-deep:   #1a2e10;
        --moss:        #243d16;
        --fern:        #2f5120;
        --leaf:        #3d6b28;
        --sage:        #5a8c3a;
        --spring:      #7ab648;
        --lime:        #a8d062;
        --dew:         #c8e89a;
        --parchment:   #f4ede0;
        --cream:       #faf6ee;
        --sand:        #e8dcc8;
        --clay:        #c4a882;
        --amber:       #d4880a;
        --rust:        #b8421a;
        --text-dark:   #1c1408;
        --text-mid:    #3d3020;
        --text-soft:   #6b5840;
        --text-muted:  #9c8870;
        --white:       #ffffff;
    }

    /* ── Global reset ── */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        background-color: var(--cream);
        color: var(--text-dark);
    }

    /* ── Leaf-vein SVG background texture on body ── */
    .main {
        background-image:
            radial-gradient(ellipse at 0% 0%, rgba(90,140,58,0.06) 0%, transparent 60%),
            radial-gradient(ellipse at 100% 100%, rgba(45,90,27,0.05) 0%, transparent 60%),
            url("data:image/svg+xml,%3Csvg width='120' height='120' viewBox='0 0 120 120' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M60 10 Q80 30 60 60 Q40 30 60 10Z' fill='none' stroke='%233d6b28' stroke-width='0.4' opacity='0.12'/%3E%3Cpath d='M60 10 L60 110' stroke='%233d6b28' stroke-width='0.3' opacity='0.08'/%3E%3Cpath d='M60 35 Q80 40 90 55' fill='none' stroke='%233d6b28' stroke-width='0.25' opacity='0.1'/%3E%3Cpath d='M60 35 Q40 40 30 55' fill='none' stroke='%233d6b28' stroke-width='0.25' opacity='0.1'/%3E%3Cpath d='M60 55 Q75 58 85 68' fill='none' stroke='%233d6b28' stroke-width='0.2' opacity='0.08'/%3E%3Cpath d='M60 55 Q45 58 35 68' fill='none' stroke='%233d6b28' stroke-width='0.2' opacity='0.08'/%3E%3C/svg%3E");
        background-attachment: fixed;
    }

    /* ── Main container ── */
    .main .block-container {
        padding: 2rem 3rem 4rem 3rem;
        max-width: 1260px;
    }

    /* ── Header banner ── */
    .header-banner {
        background:
            linear-gradient(150deg, var(--soil) 0%, var(--bark) 20%, var(--moss-deep) 55%, var(--fern) 100%);
        border-radius: 20px;
        padding: 3rem 3.5rem;
        margin-bottom: 2.5rem;
        position: relative;
        overflow: hidden;
        box-shadow:
            0 20px 60px rgba(28,20,8,0.4),
            0 4px 16px rgba(28,20,8,0.2),
            inset 0 1px 0 rgba(255,255,255,0.06);
    }

    /* Decorative botanical orbs */
    .header-banner::before {
        content: '';
        position: absolute;
        top: -80px; right: -80px;
        width: 320px; height: 320px;
        background: radial-gradient(circle, rgba(122,182,72,0.15) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    .header-banner::after {
        content: '';
        position: absolute;
        bottom: -100px; left: 10%;
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(90,140,58,0.08) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    /* Leaf watermark inside header */
    .header-leaf-mark {
        position: absolute;
        right: 3rem; top: 50%;
        transform: translateY(-50%);
        font-size: 7rem;
        opacity: 0.07;
        line-height: 1;
        pointer-events: none;
        filter: blur(1px);
    }

    .header-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(168,208,98,0.15);
        border: 1px solid rgba(168,208,98,0.3);
        color: var(--lime);
        border-radius: 100px;
        padding: 5px 16px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }
    .header-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 3rem;
        font-weight: 700;
        color: var(--cream);
        margin: 0;
        letter-spacing: -1px;
        line-height: 1.1;
    }
    .header-title span {
        color: var(--lime);
        font-style: italic;
    }
    .header-subtitle {
        font-size: 0.95rem;
        color: var(--dew);
        margin-top: 0.6rem;
        font-weight: 300;
        letter-spacing: 0.2px;
        opacity: 0.8;
        max-width: 480px;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, var(--soil) 0%, var(--bark) 30%, #1e2a12 100%) !important;
        border-right: 1px solid rgba(90,140,58,0.2) !important;
    }
    [data-testid="stSidebar"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Ccircle cx='30' cy='30' r='28' fill='none' stroke='%235a8c3a' stroke-width='0.3' opacity='0.12'/%3E%3C/svg%3E");
        background-size: 60px 60px;
        pointer-events: none;
        opacity: 0.4;
    }
    [data-testid="stSidebar"] * {
        color: #c8d8b0 !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 1.25rem !important;
        color: var(--lime) !important;
        letter-spacing: 0.5px;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(90,140,58,0.2) !important;
        margin: 1rem 0 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 0.9rem !important;
        font-weight: 400 !important;
        letter-spacing: 0.2px;
    }
    [data-testid="stSidebar"] .stSlider > div > div > div {
        background-color: var(--sage) !important;
    }
    [data-testid="stSidebar"] .stSlider [data-testid="stTickBar"] {
        color: var(--text-muted) !important;
    }
    /* Sidebar disease tags */
    .disease-tag {
        display: inline-block;
        padding: 4px 8px;
        font-size: 0.9rem;
        line-height: 1.7;
        margin-bottom: 5px;
        border-radius: 6px;
        background: rgba(0,0,0,0.1);
        border: 1px solid rgba(122,182,72,0.1);
        width: 100%;
    }

    /* ── Upload zone ── */
    [data-testid="stFileUploader"] {
        background: rgba(61,107,40,0.04);
        border: 1.5px dashed rgba(90,140,58,0.45);
        border-radius: 14px;
        padding: 1.2rem;
        transition: all 0.25s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: var(--sage);
        background: rgba(61,107,40,0.07);
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, var(--moss) 0%, var(--leaf) 50%, var(--sage) 100%) !important;
        color: var(--cream) !important;
        border: 1px solid rgba(122,182,72,0.3) !important;
        border-radius: 10px !important;
        padding: 0.65rem 2rem !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        letter-spacing: 0.6px !important;
        box-shadow:
            0 4px 20px rgba(45,81,32,0.35),
            inset 0 1px 0 rgba(255,255,255,0.1) !important;
        transition: all 0.22s ease !important;
        position: relative;
        overflow: hidden;
    }
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
        transition: left 0.4s;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow:
            0 8px 28px rgba(45,81,32,0.45),
            inset 0 1px 0 rgba(255,255,255,0.15) !important;
    }
    .stButton > button:hover::before {
        left: 100%;
    }

    /* ── Download button ── */
    .stDownloadButton > button {
        background: transparent !important;
        color: var(--leaf) !important;
        border: 1.5px solid var(--sage) !important;
        border-radius: 10px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(61,107,40,0.06) !important;
        border-color: var(--leaf) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Section titles ── */
    .section-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--moss);
        display: flex;
        align-items: center;
        gap: 8px;
        padding-bottom: 0.6rem;
        margin-bottom: 1.2rem;
        border-bottom: 1px solid rgba(90,140,58,0.2);
        position: relative;
    }
    .section-title::after {
        content: '';
        position: absolute;
        bottom: -1px; left: 0;
        width: 48px; height: 2px;
        background: linear-gradient(90deg, var(--sage), transparent);
        border-radius: 2px;
    }

    /* ── Stats row ── */
    .stat-box {
        background: var(--white);
        border-radius: 14px;
        padding: 1.2rem 1rem;
        text-align: center;
        box-shadow:
            0 2px 12px rgba(28,20,8,0.07),
            0 1px 4px rgba(28,20,8,0.04);
        border: 1px solid rgba(196,168,130,0.25);
        position: relative;
        overflow: hidden;
    }
    .stat-box::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--sage), var(--spring));
    }
    .stat-number {
        font-family: 'Cormorant Garamond', serif;
        font-size: 2.4rem;
        font-weight: 700;
        color: var(--moss);
        line-height: 1;
    }
    .stat-label {
        font-size: 0.72rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 5px;
        font-weight: 500;
    }

    /* ── Result cards ── */
    .result-card {
        background: var(--white);
        border-radius: 12px;
        padding: 1rem 1.3rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 12px rgba(28,20,8,0.06);
        border: 1px solid rgba(196,168,130,0.2);
        position: relative;
        overflow: hidden;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }
    .result-card:hover {
        transform: translateX(3px);
        box-shadow: 0 4px 20px rgba(28,20,8,0.1);
    }
    .result-card::before {
        content: '';
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, var(--sage), var(--spring));
        border-radius: 4px 0 0 4px;
    }
    .result-card.diseased::before {
        background: linear-gradient(180deg, var(--rust), var(--amber));
    }
    .result-card .disease-name {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--text-dark);
        margin: 0 0 0.15rem 0;
        letter-spacing: 0.2px;
    }
    .result-card .confidence-text {
        font-size: 0.82rem;
        color: var(--text-muted);
        font-family: 'DM Mono', monospace;
        margin: 0;
    }
    .confidence-bar-bg {
        background: rgba(200,185,160,0.25);
        border-radius: 100px;
        height: 6px;
        margin-top: 8px;
        overflow: hidden;
    }
    .confidence-bar-fill {
        height: 6px;
        border-radius: 100px;
        transition: width 0.6s ease;
    }

    /* ── Healthy badge ── */
    .healthy-badge {
        background:
            linear-gradient(135deg, var(--moss-deep) 0%, var(--fern) 50%, var(--leaf) 100%);
        color: var(--dew);
        border-radius: 14px;
        padding: 1.4rem 1.8rem;
        text-align: center;
        border: 1px solid rgba(122,182,72,0.2);
        box-shadow:
            0 4px 24px rgba(26,46,16,0.3),
            inset 0 1px 0 rgba(255,255,255,0.06);
        position: relative;
        overflow: hidden;
    }
    .healthy-badge::before {
        content: '🌿';
        position: absolute;
        right: 1.5rem; top: 50%;
        transform: translateY(-50%);
        font-size: 2.5rem;
        opacity: 0.2;
    }
    .healthy-badge-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    .healthy-badge-sub {
        font-size: 0.82rem;
        opacity: 0.7;
        letter-spacing: 0.3px;
    }

    /* ── Info / warning box ── */
    .info-box {
        background: rgba(61,107,40,0.05);
        border: 1px solid rgba(90,140,58,0.25);
        border-left: 3px solid var(--sage);
        border-radius: 10px;
        padding: 0.9rem 1.2rem;
        font-size: 0.875rem;
        color: var(--text-mid);
        margin-top: 1rem;
        line-height: 1.6;
    }

    /* ── Empty state ── */
    .empty-state {
        text-align: center;
        padding: 3.5rem 1rem;
        color: var(--text-muted);
    }
    .empty-state-icon {
        font-size: 3.5rem;
        margin-bottom: 0.75rem;
        display: block;
        filter: saturate(0.6);
    }
    .empty-state-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.15rem;
        font-weight: 600;
        color: var(--text-soft);
        margin-bottom: 0.35rem;
    }
    .empty-state-sub {
        font-size: 0.83rem;
        color: var(--text-muted);
        letter-spacing: 0.2px;
    }

    /* ── Image captions ── */
    [data-testid="stImage"] > figcaption {
        font-family: 'DM Mono', monospace !important;
        font-size: 0.73rem !important;
        color: var(--text-muted) !important;
        text-align: center;
        margin-top: 4px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    /* ── Spinner ── */
    .stSpinner > div {
        border-top-color: var(--sage) !important;
    }

    /* ── Alerts ── */
    .stAlert {
        border-radius: 10px !important;
        font-size: 0.88rem !important;
    }

    /* ── Footer divider ── */
    .footer-rule {
        border: none;
        border-top: 1px solid rgba(196,168,130,0.3);
        margin: 2rem 0 1.5rem 0;
    }

    /* ── Hide Streamlit chrome ── */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 1.2rem 0 0.4rem 0; text-align:center;">
            <div style="font-size:2.5rem; margin-bottom:0.3rem;">🌿</div>
            <div style="font-family:'Cormorant Garamond',serif; font-size:1.5rem;
                        font-weight:700; color:#a8d062; letter-spacing:-0.5px;">
                Smart Agriculture
            </div>
            <div style="font-size:0.72rem; color:#6b8c50; letter-spacing:2px;
                        text-transform:uppercase; margin-top:2px;">
                Crop Health AI
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown("### Analysis Mode")
    mode = st.radio(
        "",
        ["🔍 Object Detection", "🧬 Segmentation"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### Settings")
    conf_threshold = st.slider("Confidence Threshold", 0.10, 0.95, 0.25, 0.05)

    st.markdown("---")
    st.markdown("### Output Categories")
    diseases = [
        ("Healthy", "✦", "#a8d062"),
        ("Affected", "◈", "#b87a6a"),
    ]
    for name, icon, color in diseases:
        st.markdown(
            f'<div class="disease-tag" style="color:{color};">'
            f'<span style="margin-right:8px; font-size:0.8rem;">{icon}</span>'
            f'<strong>{name}</strong></div>',
            unsafe_allow_html=True,
        )
    
    st.markdown(
        """
        <div style="font-size:0.75rem; color:#8c9b7a; margin-top:10px; line-height:1.4;">
            <em>*The 'Affected' category acts as an aggregate class, identifying 12 distinct foliar anomalies and diseases tracked by our core YOLO model.</em>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.72rem; color:#4a6b32; text-align:center; "
        "font-family:DM Mono,monospace; letter-spacing:0.5px;'>"
        "v1.0 · YOLOv11 · Field Edition"
        "</div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="header-banner">
        <div class="header-leaf-mark">🍃</div>
        <div class="header-eyebrow">
            <span>⬡</span> AI-Powered Crop Health Analysis
        </div>
        <div class="header-title">Smart <span>Agriculture</span></div>
        <div class="header-subtitle">
            Upload a leaf photograph to instantly analyze plant health and visually isolate affected regions.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------
upload_col, result_col = st.columns(2, gap="large")

with upload_col:
    st.markdown('<div class="section-title">📸 Upload Leaf Image</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop your image here or click to browse",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        original_image = Image.open(uploaded_file)
        st.image(original_image, caption="ORIGINAL SPECIMEN", use_container_width=True)

        st.markdown("")
        run_btn = st.button(
            f"{'🔍 Run Detection' if 'Detection' in mode else '🧬 Run Segmentation'}",
            use_container_width=True,
        )
    else:
        st.markdown(
            """
            <div class="empty-state">
                <span class="empty-state-icon">🌱</span>
                <div class="empty-state-title">No specimen uploaded</div>
                <div class="empty-state-sub">Supports JPG · JPEG · PNG</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        run_btn = False

# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------
with result_col:
    st.markdown('<div class="section-title">📊 Analysis Results</div>', unsafe_allow_html=True)

    if uploaded_file and run_btn:
        endpoint = "/detect" if "Detection" in mode else "/segment"

        with st.spinner("🌱 Analyzing crop health..."):
            try:
                uploaded_file.seek(0)
                files = {"file": (uploaded_file.name, uploaded_file.read(), uploaded_file.type)}
                params = {"conf": conf_threshold}
                response = requests.post(f"{API_BASE}{endpoint}", files=files, timeout=30)
                response.raise_for_status()

                annotated_img = Image.open(io.BytesIO(response.content))
                predictions = json.loads(response.headers.get("X-Predictions", "[]"))

                st.image(annotated_img, caption="ANNOTATED RESULT", use_container_width=True)
                st.markdown("")

                # Stats row
                total = len(predictions)
                healthy = sum(1 for p in predictions if p.get("label") == "Healthy")
                affected = total - healthy  # Renamed from diseased to affected
                avg_conf = (
                    round(sum(p["confidence"] for p in predictions) / total * 100, 1)
                    if total else 0
                )

                s1, s2, s3 = st.columns(3)
                with s1:
                    st.markdown(
                        f'<div class="stat-box">'
                        f'<div class="stat-number">{total}</div>'
                        f'<div class="stat-label">Detections</div></div>',
                        unsafe_allow_html=True,
                    )
                with s2:
                    st.markdown(
                        f'<div class="stat-box">'
                        f'<div class="stat-number">{affected}</div>'
                        f'<div class="stat-label">Affected</div></div>', # Updated to match binary API
                        unsafe_allow_html=True,
                    )
                with s3:
                    st.markdown(
                        f'<div class="stat-box">'
                        f'<div class="stat-number">{avg_conf}%</div>'
                        f'<div class="stat-label">Avg Confidence</div></div>',
                        unsafe_allow_html=True,
                    )

                st.markdown("<br>", unsafe_allow_html=True)

                # Prediction cards
                if predictions:
                    all_healthy = all(p.get("label") == "Healthy" for p in predictions)
                    if all_healthy:
                        st.markdown(
                            '<div class="healthy-badge">'
                            '<div class="healthy-badge-title">✦ Crop Appears Healthy</div>'
                            '<div class="healthy-badge-sub">No disease detected above threshold</div>'
                            '</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            "<div style='font-size:0.8rem; font-weight:600; color:#6b5840; "
                            "text-transform:uppercase; letter-spacing:1.2px; "
                            "margin-bottom:0.75rem;'>Detected Conditions</div>",
                            unsafe_allow_html=True,
                        )
                        for p in predictions:
                            label = p.get("label", "Unknown")
                            conf = p.get("confidence", 0)
                            bar_width = int(conf * 100)
                            is_healthy = label == "Healthy"
                            card_class = "result-card" if is_healthy else "result-card diseased"
                            status_icon = "✦" if is_healthy else "◈"
                            bar_color = (
                                "linear-gradient(90deg, #5a8c3a, #a8d062)"
                                if is_healthy
                                else "linear-gradient(90deg, #b8421a, #d4880a)"
                            )
                            st.markdown(
                                f"""
                                <div class="{card_class}">
                                    <div class="disease-name">{status_icon} {label}</div>
                                    <div class="confidence-text">{conf*100:.1f}% confidence</div>
                                    <div class="confidence-bar-bg">
                                        <div class="confidence-bar-fill"
                                             style="width:{bar_width}%; background:{bar_color};">
                                        </div>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                else:
                    st.markdown(
                        '<div class="info-box">⚠ No detections found above the confidence threshold. '
                        'Try lowering the threshold in the sidebar.</div>',
                        unsafe_allow_html=True,
                    )

                # Download
                st.markdown("<br>", unsafe_allow_html=True)
                buf = io.BytesIO()
                annotated_img.save(buf, format="JPEG", quality=92)
                st.download_button(
                    label="⬇ Download Annotated Image",
                    data=buf.getvalue(),
                    file_name=f"cropguard_{uploaded_file.name}",
                    mime="image/jpeg",
                    use_container_width=True,
                )

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to the API. Make sure the FastAPI server is running on port 8000.")
            except requests.exceptions.Timeout:
                st.error("⏱ Request timed out. The image may be too large or the server is busy.")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

    elif not uploaded_file:
        st.markdown(
            """
            <div class="empty-state">
                <span class="empty-state-icon">🔬</span>
                <div class="empty-state-title">Results will appear here</div>
                <div class="empty-state-sub">Upload an image and run analysis to begin</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown('<hr class="footer-rule">', unsafe_allow_html=True)
st.markdown(
    """
    <div class="info-box">
        <strong>How to use —</strong> Upload a clear photograph of a leaf, choose between
        <em>Object Detection</em> (bounding boxes) or <em>Segmentation</em> (precise masks),
        adjust the confidence threshold in the sidebar, then click Run.
        Results include the annotated image and a per-condition breakdown with confidence scores.
    </div>
    """,
    unsafe_allow_html=True,
)