import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(
    page_title="Akshar | Dyslexia Screener",
    page_icon="👁️",
    layout="wide",
)

# ---------------------------------------------------------------------
# PAGE CSS
# ---------------------------------------------------------------------

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }

    .main-title {
        text-align: center;
        font-size: 3.2rem;
        font-weight: 900;
        margin-bottom: 0;
        background: linear-gradient(
            90deg,
            #ff0080,
            #7928ca,
            #ff416c
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle {
        text-align: center;
        color: #aaaabd;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }

    .card {
        background: rgba(26, 26, 46, 0.85);
        border-radius: 18px;
        padding: 25px;
        margin-bottom: 18px;
        box-shadow:
            8px 8px 18px rgba(0,0,0,0.55),
            -5px -5px 15px rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
    }

    .metric-card {
        background: rgba(26, 26, 46, 0.9);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .metric-number {
        font-size: 2.4rem;
        font-weight: 900;
        background: linear-gradient(90deg, #ff0080, #7928ca);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .metric-label {
        color: #aaaabd;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.8rem;
    }

    .risk-low {
        color: #00e676;
    }

    .risk-medium {
        color: #ffca28;
    }

    .risk-high {
        color: #ff416c;
    }

    .disclaimer {
        font-size: 0.78rem;
        color: #888;
        text-align: center;
        margin-top: 25px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------

st.markdown(
    '<div class="main-title">👁️ Akshar</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-Powered Eye-Movement Reading Screening Prototype'
    '</div>',
    unsafe_allow_html=True
)


# ---------------------------------------------------------------------
# READING PASSAGE
# ---------------------------------------------------------------------

reading_text = """
The quick brown fox jumps over the lazy dog.

Reading is a complex cognitive process that requires coordinated
eye movements across words and sentences. During normal reading,
the eyes move forward through the text using a sequence of fixations
and rapid eye movements called saccades.

Sometimes the eyes move backward to previously viewed words.
These backward movements are called regressions. The frequency,
duration, and pattern of these movements can provide useful
information for research into reading behaviour.
"""


# ---------------------------------------------------------------------
# BROWSER COMPONENT
# ---------------------------------------------------------------------

component_html = f"""
<!DOCTYPE html>
<html>
<head>

<meta charset="UTF-8">

<script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/face_mesh.js"></script>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    background: transparent;
    color: white;
    font-family: Arial, sans-serif;
}}

.wrapper {{
    width: 100%;
    max-width: 1100px;
    margin: auto;
}}

.grid {{
    display: grid;
    grid-template-columns: 1.5fr 1fr;
    gap: 22px;
}}

.card {{
    background: rgba(26,26,46,0.90);
    border-radius: 18px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow:
        7px 7px 15px rgba(0,0,0,0.5),
        -4px -4px 12px rgba(255,255,255,0.03);
}}

.controls {{
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}}

button {{
    flex: 1;
    border: none;
    border-radius: 10px;
    padding: 13px 10px;
    font-size: 15px;
    font-weight: bold;
    cursor: pointer;
    color: white;
    background: #302b63;
}}

button:hover {{
    opacity: 0.85;
}}

.start {{
    background: linear-gradient(90deg,#ff0080,#7928ca);
}}

.stop {{
    background: #5a2334;
}}

.reset {{
    background: #34344e;
}}

.reading {{
    font-size: 20px;
    line-height: 2.0;
    letter-spacing: 0.3px;
    color: #eeeeee;
    background: rgba(10,10,25,0.5);
    padding: 20px;
    border-radius: 12px;
    min-height: 280px;
}}

.video-box {{
    position: relative;
    width: 100%;
    background: #080812;
    border-radius: 14px;
    overflow: hidden;
}}

video {{
    width: 100%;
    display: block;
    transform: scaleX(-1);
}}

canvas {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    transform: scaleX(-1);
}}

.status {{
    margin-top: 12px;
    text-align: center;
    color: #aaaabd;
    font-size: 15px;
}}

.risk-container {{
    text-align: center;
    padding: 20px;
}}

.risk-circle {{
    width: 170px;
    height: 170px;
    border-radius: 50%;
    margin: auto;
    display: flex;
    align-items: center;
    justify-content: center;

    background:
        conic-gradient(
            #ff0080 0deg,
            #7928ca var(--angle),
            #29293b var(--angle),
            #29293b 360deg
        );
}}

.risk-inner {{
    width: 135px;
    height: 135px;
    border-radius: 50%;
    background: #1a1a2e;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
}}

.risk-number {{
    font-size: 42px;
    font-weight: 900;
}}

.risk-label {{
    color: #999;
    font-size: 13px;
}}

.metrics {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-top: 20px;
}}

.metric {{
    background: rgba(15,15,35,0.7);
    border-radius: 12px;
    padding: 15px;
    text-align: center;
}}

.metric-number {{
    font-size: 30px;
    font-weight: bold;
    color: #ff0080;
}}

.metric-label {{
    color: #999;
    font-size: 12px;
    text-transform: uppercase;
}}

@media(max-width: 800px) {{
    .grid {{
        grid-template-columns: 1fr;
    }}
}}

</style>

</head>

<body>

<div class="wrapper">

<div class="grid">

<!-- ============================================================
     LEFT SIDE
============================================================ -->

<div>

<div class="card">

<div class="controls">

<button class="start" onclick="startSession()">
▶ Start Session
</button>

<button class="stop" onclick="stopSession()">
⏹ End Session
</button>

<button class="reset" onclick="resetSession()">
🔄 Reset
</button>

</div>


<div class="reading">
{reading_text}
</div>

</div>


<div class="card">

<div class="video-box">

<video
    id="webcam"
    autoplay
    muted
    playsinline>
</video>

<canvas id="overlay"></canvas>

</div>

<div id="status" class="status">
⚪ Camera not started
</div>

</div>

</div>


<!-- ============================================================
     RIGHT SIDE
============================================================ -->

<div>

<div class="card risk-container">

<div
    id="riskCircle"
    class="risk-circle"
    style="--angle: 0deg;"
>

<div class="risk-inner">

<div id="riskNumber" class="risk-number">
0
</div>

<div class="risk-label">
Risk %
</div>

</div>

</div>

<h3>Live Session Analysis</h3>

<div id="riskText" style="color:#999;">
Session not started
</div>

</div>


<div class="card">

<div class="metrics">

<div class="metric">

<div id="regressions" class="metric-number">
0
</div>

<div class="metric-label">
Regressions
</div>

</div>


<div class="metric">

<div id="fixations" class="metric-number">
0
</div>

<div class="metric-label">
Fixations
</div>

</div>


<div class="metric">

<div id="saccades" class="metric-number">
0
</div>

<div class="metric-label">
Saccades
</div>

</div>


<div class="metric">

<div id="duration" class="metric-number">
0
</div>

<div class="metric-label">
Seconds
</div>

</div>

</div>

</div>

</div>

</div>

</div>


<script>

/* ================================================================
   AKSHAR EYE TRACKER
================================================================ */

let faceMesh = null;
let camera = null;

let running = false;

let frameCount = 0;

let startTime = null;

let lastX = null;

let lastY = null;

let regressions = 0;

let fixations = 0;

let saccades = 0;

let stableFrames = 0;


/* ================================================================
   METRIC OBJECT
================================================================ */

let metrics = {{
    regressions: 0,
    fixations: 0,
    saccades: 0,
    duration: 0,
    risk: 0
}};


/* ================================================================
   STREAMLIT COMPONENT MESSAGE
================================================================ */

function sendToStreamlit() {{

    try {{

        window.parent.postMessage(
            {{
                isStreamlitMessage: true,
                type: "streamlit:setComponentValue",
                value: JSON.stringify(metrics)
            }},
            "*"
        );

    }} catch (e) {{

        console.log(e);

    }}

}}


/* ================================================================
   UPDATE UI
================================================================ */

function updateUI() {{

    document.getElementById("regressions").innerText =
        metrics.regressions;

    document.getElementById("fixations").innerText =
        metrics.fixations;

    document.getElementById("saccades").innerText =
        metrics.saccades;

    document.getElementById("duration").innerText =
        metrics.duration;

    document.getElementById("riskNumber").innerText =
        metrics.risk;

    document.getElementById("riskCircle").style
        .setProperty(
            "--angle",
            (metrics.risk * 3.6) + "deg"
        );

    let riskText = "";

    if (metrics.risk < 30) {{

        riskText = "Low observed reading-movement risk";

    }} else if (metrics.risk < 60) {{

        riskText = "Moderate observed reading-movement risk";

    }} else {{

        riskText = "Higher observed reading-movement risk";

    }}

    document.getElementById("riskText").innerText =
        riskText;

}}


/* ================================================================
   FACE MESH RESULTS
================================================================ */

function onResults(results) {{

    if (!running)
        return;

    frameCount++;

    const video =
        document.getElementById("webcam");

    const canvas =
        document.getElementById("overlay");

    const ctx =
        canvas.getContext("2d");

    canvas.width =
        video.videoWidth || 640;

    canvas.height =
        video.videoHeight || 480;

    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );


    /*
       Process approximately every 5th frame.
    */

    if (frameCount % 5 !== 0)
        return;


    if (
        results.multiFaceLandmarks &&
        results.multiFaceLandmarks.length > 0
    ) {{

        const lm =
            results.multiFaceLandmarks[0];


        /*
           MediaPipe iris landmarks:

           468 = left iris
           473 = right iris

           We use the average horizontal position.
        */

        const x =
            (lm[468].x + lm[473].x) / 2;

        const y =
            (lm[468].y + lm[473].y) / 2;


        /*
           Draw iris points
        */

        ctx.fillStyle = "#00ff88";

        ctx.beginPath();

        ctx.arc(
            lm[468].x * canvas.width,
            lm[468].y * canvas.height,
            5,
            0,
            Math.PI * 2
        );

        ctx.fill();


        ctx.beginPath();

        ctx.arc(
            lm[473].x * canvas.width,
            lm[473].y * canvas.height,
            5,
            0,
            Math.PI * 2
        );

        ctx.fill();


        /*
           First valid point
        */

        if (lastX === null) {{

            lastX = x;
            lastY = y;

            return;

        }}


        const dx = x - lastX;

        const dy = y - lastY;

        const distance =
            Math.sqrt(dx * dx + dy * dy);


        /*
           Forward movement.

           Note:
           Because webcam coordinates are mirrored,
           direction can vary by implementation.
        */

        if (Math.abs(dx) > 0.025) {{

            saccades++;

        }}


        /*
           Regression detection.

           A significant movement in the opposite
           horizontal direction is counted.
        */

        if (dx > 0.08) {{

            regressions++;

        }}


        /*
           Fixation detection.

           Small movement over consecutive frames.
        */

        if (Math.abs(dx) < 0.015) {{

            stableFrames++;

            if (stableFrames === 4) {{

                fixations++;

            }}

        }} else {{

            stableFrames = 0;

        }}


        lastX = x;

        lastY = y;


        /*
           Calculate risk.

           This is a prototype research score,
           NOT a clinical diagnostic score.
        */

        let risk =
            (regressions * 8) +
            (fixations > 80 ? 10 : 0) +
            (saccades > 100 ? 10 : 0);


        risk =
            Math.max(
                0,
                Math.min(99, Math.round(risk))
            );


        metrics.regressions =
            regressions;

        metrics.fixations =
            fixations;

        metrics.saccades =
            saccades;

        metrics.risk =
            risk;


        if (startTime !== null) {{

            metrics.duration =
                Math.floor(
                    (Date.now() - startTime) / 1000
                );

        }}


        updateUI();

    }}

}}


/* ================================================================
   START SESSION
================================================================ */

async function startSession() {{

    if (running)
        return;


    document.getElementById("status").innerHTML =
        "🟡 Requesting camera permission...";


    try {{

        /*
           Explicitly request camera permission.
        */

        const stream =
            await navigator.mediaDevices.getUserMedia({{
                video: {{
                    width: 640,
                    height: 480,
                    facingMode: "user"
                }},
                audio: false
            }});


        const video =
            document.getElementById("webcam");

        video.srcObject =
            stream;


        await video.play();


        /*
           Check MediaPipe.
        */

        if (typeof FaceMesh === "undefined") {{

            throw new Error(
                "MediaPipe FaceMesh failed to load."
            );

        }}


        if (typeof Camera === "undefined") {{

            throw new Error(
                "MediaPipe Camera utility failed to load."
            );

        }}


        faceMesh =
            new FaceMesh({{
                locateFile: function(file) {{

                    return (
                        "https://cdn.jsdelivr.net/npm/"
                        + "@mediapipe/face_mesh/"
                        + file
                    );

                }}
            }});


        faceMesh.setOptions({{
            maxNumFaces: 1,
            refineLandmarks: true,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5
        }});


        faceMesh.onResults(
            onResults
        );


        camera =
            new Camera(
                video,
                {{
                    onFrame: async function() {{

                        if (running) {{

                            await faceMesh.send({{
                                image: video
                            }});

                        }}

                    }},

                    width: 640,
                    height: 480
                }}
            );


        running = true;

        startTime =
            Date.now();


        document.getElementById("status").innerHTML =
            "🟢 Tracking active";


        document.getElementById("riskText").innerText =
            "Eye movement analysis in progress";


        camera.start();


    }} catch (error) {{

        console.error(error);

        document.getElementById("status").innerHTML =
            "🔴 Camera error: " + error.message;

    }}

}}


/* ================================================================
   STOP SESSION
================================================================ */

function stopSession() {{

    running = false;


    if (camera) {{

        try {{
            camera.stop();
        }} catch(e) {{}}

    }}


    const video =
        document.getElementById("webcam");


    if (video.srcObject) {{

        const tracks =
            video.srcObject.getTracks();

        tracks.forEach(
            track => track.stop()
        );

        video.srcObject = null;

    }}


    if (startTime !== null) {{

        metrics.duration =
            Math.floor(
                (Date.now() - startTime) / 1000
            );

    }}


    updateUI();

    sendToStreamlit();


    document.getElementById("status").innerHTML =
        "🔵 Session ended";

    document.getElementById("riskText").innerText =
        "Session completed";

}}


/* ================================================================
   RESET
================================================================ */

function resetSession() {{

    stopSession();


    regressions = 0;

    fixations = 0;

    saccades = 0;

    stableFrames = 0;

    frameCount = 0;

    lastX = null;

    lastY = null;

    startTime = null;


    metrics = {{
        regressions: 0,
        fixations: 0,
        saccades: 0,
        duration: 0,
        risk: 0
    }};


    updateUI();

    sendToStreamlit();


    document.getElementById("status").innerHTML =
        "⚪ Ready for a new session";

}}


/* ================================================================
   INITIALIZE
================================================================ */

updateUI();

</script>

</body>
</html>
"""


# ---------------------------------------------------------------------
# RUN COMPONENT
# ---------------------------------------------------------------------

result = components.html(
    component_html,
    height=760,
    scrolling=False,
)


# ---------------------------------------------------------------------
# RECEIVE FINAL METRICS
# ---------------------------------------------------------------------

metrics = {
    "regressions": 0,
    "fixations": 0,
    "saccades": 0,
    "duration": 0,
    "risk": 0,
}


if result:

    try:

        if isinstance(result, str):

            metrics = json.loads(result)

        elif isinstance(result, dict):

            metrics = result

    except Exception:

        pass


# ---------------------------------------------------------------------
# STREAMLIT SUMMARY
# ---------------------------------------------------------------------

st.markdown("---")

st.markdown(
    '<div style="text-align:center; color:#aaa;">'
    'Session Results'
    '</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-number">
                {metrics.get("regressions", 0)}
            </div>
            <div class="metric-label">
                Regressions
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-number">
                {metrics.get("fixations", 0)}
            </div>
            <div class="metric-label">
                Fixations
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-number">
                {metrics.get("saccades", 0)}
            </div>
            <div class="metric-label">
                Saccades
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-number">
                {metrics.get("risk", 0)}%
            </div>
            <div class="metric-label">
                Observed Risk
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------------------------------------------------------------
# DISCLAIMER
# ---------------------------------------------------------------------

st.markdown(
    """
    <div class="disclaimer">
    ⚠️ Akshar is a research/educational screening prototype.
    Eye-movement measurements alone cannot diagnose dyslexia.
    Results should not be interpreted as a medical diagnosis.
    </div>

    <div style="
        text-align:center;
        color:#666;
        font-size:0.8rem;
        margin-top:20px;
    ">
        Nithyamithran Ramesh |
        Class VII B |
        Manav Mandir High School |
        INSPIRE MANAK
    </div>
    """,
    unsafe_allow_html=True
)
