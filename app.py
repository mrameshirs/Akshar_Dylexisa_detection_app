import streamlit as st
import time
import json
from streamlit_js_eval import streamlit_js_eval

# -----------------------------------------------------------------------------
# APP CONFIGURATION & CSS
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Akshar | Dyslexia Screener", layout="wide", page_icon="👁️")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #ffffff; font-family: 'Segoe UI', sans-serif; }
    .embossed-card {
        background: rgba(26, 26, 46, 0.8); border-radius: 16px; padding: 20px; margin: 10px 0;
        box-shadow: 8px 8px 16px rgba(0, 0, 0, 0.6), -8px -8px 16px rgba(255, 255, 255, 0.05);
        border: 2px solid transparent; background-clip: padding-box; position: relative;
    }
    .embossed-card::before {
        content: ''; position: absolute; top: 0; right: 0; bottom: 0; left: 0; z-index: -1; margin: -2px; border-radius: inherit;
        background: linear-gradient(45deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #9400d3);
    }
    .rainbow-text {
        font-size: 2.5rem; font-weight: 900;
        background: linear-gradient(90deg, #ff0080, #7928ca, #ff416c);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite;
    }
    @keyframes shine { to { background-position: 200% center; } }
    .metric-label { font-size: 0.9rem; color: #a0a0b0; text-transform: uppercase; letter-spacing: 1px; }
    .score-circle {
        width: 150px; height: 150px; border-radius: 50%;
        background: conic-gradient(from 0deg, #ff007f 0deg calc(var(--score) * 3.6deg), #2b2b3d calc(var(--score) * 3.6deg) 360deg);
        display: flex; align-items: center; justify-content: center; margin: 0 auto;
    }
    .score-inner {
        width: 120px; height: 120px; border-radius: 50%; background: #1a1a2e;
        display: flex; align-items: center; justify-content: center; flex-direction: column;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# JAVASCRIPT EYE TRACKER (Runs in Browser)
# -----------------------------------------------------------------------------
js_code = """
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/face_mesh.js" crossorigin="anonymous"></script>

<div id="video-container" style="position: relative; width: 100%; max-width: 640px; margin: 0 auto;">
    <video id="webcam" playsinline autoplay muted style="width: 100%; border-radius: 12px; transform: scaleX(-1);"></video>
    <canvas id="overlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; transform: scaleX(-1);"></canvas>
</div>
<div id="js-status" style="text-align: center; margin-top: 15px; color: #a0a0b0; font-size: 1.1rem;">Click "Start Session" to begin</div>

<script>
let faceMesh, camera, isRunning = false;
let frameCount = 0;
// Global metrics object for Streamlit to read
window.aksharMetrics = { regressions: 0, fixations: 0, risk: 0, lastX: 0.5 };

function onResults(results) {
    if (!isRunning) return;
    frameCount++;
    const canvas = document.getElementById('overlay');
    const ctx = canvas.getContext('2d');
    canvas.width = document.getElementById('webcam').videoWidth;
    canvas.height = document.getElementById('webcam').videoHeight;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    if (frameCount % 6 !== 0) return; // Process every 6th frame to save CPU
    
    if (results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) {
        const lm = results.multiFaceLandmarks[0];
        const currentX = (lm[468].x + lm[473].x) / 2;
        
        if (window.aksharMetrics.lastX - currentX > 0.12) window.aksharMetrics.regressions++;
        if (Math.abs(window.aksharMetrics.lastX - currentX) < 0.04) window.aksharMetrics.fixations++;
        window.aksharMetrics.lastX = currentX;
        window.aksharMetrics.risk = Math.min(99, Math.floor(window.aksharMetrics.regressions * 12));
        
        // Draw tracking dots
        ctx.beginPath(); ctx.arc(lm[468].x * canvas.width, lm[468].y * canvas.height, 5, 0, 2*Math.PI); ctx.fillStyle='#00ff00'; ctx.fill();
        ctx.beginPath(); ctx.arc(lm[473].x * canvas.width, lm[473].y * canvas.height, 5, 0, 2*Math.PI); ctx.fillStyle='#00ff00'; ctx.fill();
        
        document.getElementById('js-status').innerHTML = `🟢 Tracking... Regressions: <b style="color:#ff0080">${window.aksharMetrics.regressions}</b> | Risk: <b style="color:#ff416c">${window.aksharMetrics.risk}%</b>`;
    }
}

window.startAkshar = async function() {
    if (isRunning) return;
    faceMesh = new FaceMesh({locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`});
    faceMesh.setOptions({ maxNumFaces: 1, refineLandmarks: true, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5 });
    faceMesh.onResults(onResults);
    
    const video = document.getElementById('webcam');
    camera = new Camera(video, { onFrame: async () => { await faceMesh.send({image: video}); }, width: 640, height: 480 });
    await camera.start();
    isRunning = true;
}

window.stopAkshar = function() { isRunning = false; if(camera) camera.stop(); }
window.resetAkshar = function() { window.aksharMetrics = { regressions: 0, fixations: 0, risk: 0, lastX: 0.5 }; frameCount = 0; }
</script>
"""

# -----------------------------------------------------------------------------
# STATE & BRIDGE LOGIC (Fixed JSON Parsing)
# -----------------------------------------------------------------------------
if 'session_active' not in st.session_state:
    st.session_state.session_active = False

# 1. Render the JS UI using st.markdown to avoid v1.html deprecation warnings
st.markdown(js_code, unsafe_allow_html=True)

# 2. Pull JS variables into Python as a JSON string
js_raw = streamlit_js_eval(
    js_expressions="JSON.stringify(window.aksharMetrics || {regressions:0, fixations:0, risk:0})", 
    key="fetch_metrics"
)

# 3. Safely parse the JSON string into a Python dictionary
if js_raw:
    js_data = json.loads(js_raw)
else:
    js_data = {"regressions": 0, "fixations": 0, "risk": 0}

regressions = int(js_data.get("regressions", 0))
fixations = int(js_data.get("fixations", 0))
risk = int(js_data.get("risk", 0))

# -----------------------------------------------------------------------------
# STREAMLIT UI LAYOUT
# -----------------------------------------------------------------------------
st.markdown('<h1 style="text-align:center; margin-bottom: 5px;">👁️ Akshar</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#a0a0b0; margin-bottom: 30px;">AI-Powered Dyslexia Screener via Eye Movement Analysis</p>', unsafe_allow_html=True)

col1, col2 = st.columns([1.5, 1], gap="large")

with col1:
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        if st.button("▶ Start Session", use_container_width=True, type="primary"):
            st.markdown("<script>window.startAkshar();</script>", unsafe_allow_html=True)
            st.session_state.session_active = True
    with btn_col2:
        if st.button("⏹ End Session", use_container_width=True):
            st.markdown("<script>window.stopAkshar();</script>", unsafe_allow_html=True)
            st.session_state.session_active = False
    with btn_col3:
        if st.button("🔄 Reset", use_container_width=True):
            st.markdown("<script>window.resetAkshar();</script>", unsafe_allow_html=True)
            st.session_state.session_active = False

    st.markdown("""
    <div class="embossed-card" style="margin-top: 15px;">
        <b> Reading Task:</b><br>
        "The quick brown fox jumps over the lazy dog. Reading is a complex cognitive process that requires smooth eye movements across the page..."
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="embossed-card" style="text-align: center; padding: 30px;">
        <div class="score-circle" style="--score: {risk}">
            <div class="score-inner">
                <span style="font-size: 2.5rem; font-weight: 900; color: white;">{risk}</span>
                <span style="font-size: 0.7rem; color: #888;">Risk %</span>
            </div>
        </div>
        <div style="margin-top: 15px; color: #a0a0b0;">Live Session Analysis</div>
    </div>
    """, unsafe_allow_html=True)

    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f"""
        <div class="embossed-card" style="text-align: center; padding: 15px;">
            <div class="rainbow-text" style="font-size: 2rem;">{regressions}</div>
            <div class="metric-label">Regressions</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="embossed-card" style="text-align: center; padding: 15px;">
            <div class="rainbow-text" style="font-size: 2rem;">{fixations}</div>
            <div class="metric-label">Fixations</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown('<p style="text-align: center; color: #666; font-size: 0.8rem;">Nithyamithran Ramesh | Class VII B | Manav Mandir High School | INSPIRE MANAK</p>', unsafe_allow_html=True)

# Auto-refresh to update the dashboard smoothly
if st.session_state.session_active:
    time.sleep(1.5)
    st.rerun()
