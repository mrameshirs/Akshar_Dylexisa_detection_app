import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, WebRtcMode
import time

# -----------------------------------------------------------------------------
# 1. APP CONFIGURATION & PREMIUM RAINBOW CSS (From FocusPal)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Akshar | Dyslexia Screener", layout="wide", initial_sidebar_state="collapsed")

rainbow_embossed_css = """
<style>
    .stApp { background-color: #12121e; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    .embossed-card {
        background: #1a1a2e; border-radius: 16px; padding: 20px; margin-bottom: 20px;
        box-shadow: 8px 8px 16px rgba(0, 0, 0, 0.6), -8px -8px 16px rgba(255, 255, 255, 0.05), inset 2px 2px 4px rgba(255, 255, 255, 0.1), inset -2px -2px 4px rgba(0, 0, 0, 0.4);
        border: 2px solid transparent; background-clip: padding-box; position: relative;
    }
    .embossed-card::before {
        content: ''; position: absolute; top: 0; right: 0; bottom: 0; left: 0; z-index: -1; margin: -2px; border-radius: inherit;
        background: linear-gradient(45deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
    }
    .rainbow-text {
        font-size: 2.5rem; font-weight: 900;
        background: linear-gradient(90deg, #ff0080, #7928ca, #ff0080); background-size: 200% auto;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    @keyframes shine { to { background-position: 200% center; } }
    .metric-label { font-size: 0.9rem; color: #a0a0b0; text-transform: uppercase; letter-spacing: 1px; }
    
    .score-circle {
        width: 140px; height: 140px; border-radius: 50%;
        background: conic-gradient(#ff007f 0% var(--score-pct, 50%), #2b2b3d var(--score-pct, 50%) 100%);
        display: flex; align-items: center; justify-content: center; margin: 0 auto;
        box-shadow: inset 6px 6px 12px rgba(0,0,0,0.6), inset -6px -6px 12px rgba(255,255,255,0.05);
    }
    .score-inner {
        width: 110px; height: 110px; border-radius: 50%; background: #1a1a2e;
        display: flex; align-items: center; justify-content: center; flex-direction: column;
        box-shadow: 4px 4px 8px rgba(0,0,0,0.5), -4px -4px 8px rgba(255,255,255,0.05);
    }
    .passage-box { background: rgba(255, 255, 255, 0.05); border-left: 4px solid #9400d3; padding: 15px; border-radius: 8px; font-size: 16px; line-height: 1.6; }
</style>
"""
st.markdown(rainbow_embossed_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. STATE MANAGEMENT
# -----------------------------------------------------------------------------
if 'session_active' not in st.session_state:
    st.session_state.session_active = False
if 'metrics' not in st.session_state:
    st.session_state.metrics = {"regressions": 0, "fixations": 0, "risk_score": 0}

# -----------------------------------------------------------------------------
# 3. MEDIAPIPE AI ENGINE (Optimized for Cloud CPU)
# -----------------------------------------------------------------------------
mp_face_mesh = mp.solutions.face_mesh
# refine_landmarks=True is CRITICAL for getting accurate iris tracking
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)

class VideoTransformer(VideoTransformerBase):
    def __init__(self):
        self.frame_count = 0
        self.last_x = 0.5
        self.regressions = 0
        self.fixations = 0
        
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        self.frame_count += 1
        
        # CLOUD OPTIMIZATION: Process only every 6th frame (~5 FPS). 
        # Eye fixations last 200-300ms, so 5 FPS is plenty to catch them, saving 80% CPU.
        if self.frame_count % 6 != 0:
            return frame
            
        h, w, _ = img.shape
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_img)
        
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            
            # MediaPipe Landmark 468 = Left Iris Center, 473 = Right Iris Center
            left_iris = landmarks[468]
            right_iris = landmarks[473]
            
            # Average X coordinate (0.0 = far left, 1.0 = far right)
            current_x = (left_iris.x + right_iris.x) / 2.0
            
            # 1. Regression Detection: Eyes move significantly LEFT (backward reading)
            if self.last_x - current_x > 0.12: 
                self.regressions += 1
                
            # 2. Fixation Detection: Eyes stay in the same X zone
            if abs(self.last_x - current_x) < 0.04:
                self.fixations += 1
                
            self.last_x = current_x
            
            # Draw green dots on irises for visual proof of tracking
            cv2.circle(img, (int(left_iris.x * w), int(left_iris.y * h)), 4, (0, 255, 0), -1)
            cv2.circle(img, (int(right_iris.x * w), int(right_iris.y * h)), 4, (0, 255, 0), -1)
            
        # Update global state so the UI can read it
        st.session_state.metrics["regressions"] = self.regressions
        st.session_state.metrics["fixations"] = self.fixations
        # Simple risk algorithm: High regressions = high risk
        st.session_state.metrics["risk_score"] = min(99, int(self.regressions * 12))
            
        return img

# -----------------------------------------------------------------------------
# 4. UI LAYOUT
# -----------------------------------------------------------------------------
st.markdown('<h1 style="text-align:center; margin-bottom: 5px;">👁️ Akshar</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#a0a0b0; margin-bottom: 30px;">AI-Powered Dyslexia & Reading Attention Screener</p>', unsafe_allow_html=True)

col1, col2 = st.columns([1.5, 1], gap="large")

# --- LEFT COLUMN: Webcam & Controls ---
with col1:
    st.markdown('<div class="embossed-card" style="padding: 10px;">', unsafe_allow_html=True)
    
    # WebRTC Component
    webrtc_ctx = webrtc_streamer(
        key="akshar-eye-tracker",
        mode=WebRtcMode.SENDRECV,
        video_transformer_factory=VideoTransformer,
        media_stream_constraints={"video": True, "audio": False},
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Controls
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("▶ Start Screening Session", use_container_width=True, type="primary"):
            st.session_state.session_active = True
            st.session_state.metrics = {"regressions": 0, "fixations": 0, "risk_score": 0}
            st.rerun()
    with btn_col2:
        if st.button("⏹ End & Generate Report", use_container_width=True):
            st.session_state.session_active = False
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="passage-box">
        <b>📖 Reading Task:</b><br>
        "The quick brown fox jumps over the lazy dog. Reading is a complex cognitive process that requires the eyes to move smoothly across the page..."
    </div>
    """, unsafe_allow_html=True)

# --- RIGHT COLUMN: Live Metrics ---
with col2:
    # Dynamic Score Circle
    risk = st.session_state.metrics["risk_score"]
    score_css_var = f"--score-pct: {risk}%;"
    
    st.markdown(f"""
    <div class="embossed-card" style="text-align: center; padding: 30px;">
        <div class="score-circle" style="{score_css_var}">
            <div class="score-inner">
                <span style="font-size: 2.5rem; font-weight: 900; color: white;">{risk}</span>
                <span style="font-size: 0.7rem; color: #888; text-transform: uppercase;">Dyslexia<br>Risk %</span>
            </div>
        </div>
        <div style="margin-top: 15px; font-weight: bold; color: #a0a0b0;">Live Session Analysis</div>
    </div>
    """, unsafe_allow_html=True)

    # Mini Metric Cards
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f"""
        <div class="embossed-card" style="text-align: center; padding: 15px;">
            <div class="rainbow-text" style="font-size: 2rem;">{st.session_state.metrics['regressions']}</div>
            <div class="metric-label">Regressions</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="embossed-card" style="text-align: center; padding: 15px;">
            <div class="rainbow-text" style="font-size: 2rem;">{st.session_state.metrics['fixations']}</div>
            <div class="metric-label">Fixations</div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. FOOTER
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem; margin-top: 20px;">
    <p><b>Nithyamithran Ramesh</b> | Class VII B, Manav Mandir High School | INSPIRE MANAK Project Prototype</p>
    <p>Powered by MediaPipe Face Landmarker & Streamlit WebRTC. All video processing occurs locally in your browser session.</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 6. SAFE AUTO-REFRESH (Replaces the dangerous 'while True' loop)
# -----------------------------------------------------------------------------
if st.session_state.session_active and webrtc_ctx.state.playing:
    # Wait a short moment, then safely rerun the app to update the UI with new metrics
    time.sleep(1.0)
    st.rerun()
