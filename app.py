"""
app.py — Math Tutor Chatbot (Streamlit)
Run with: streamlit run app.py
"""

import re
import os

import streamlit as st
from auth import signup, login, verify_token
from groq_client import chat

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Math Tutor AI",
    page_icon="🧮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Session state defaults ────────────────────────────────────
if "token"    not in st.session_state: st.session_state.token    = None
if "user"     not in st.session_state: st.session_state.user     = None
if "messages" not in st.session_state: st.session_state.messages = []
if "page"     not in st.session_state: st.session_state.page     = "login"

# ── Global styles ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── App background ── */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}
[data-testid="stHeader"] { background: transparent; }

/* ── Auth card ── */
.auth-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 36px 32px;
    max-width: 420px;
    margin: 40px auto;
    backdrop-filter: blur(12px);
}
.auth-title {
    text-align: center;
    font-size: 2rem;
    margin-bottom: 4px;
}
.auth-heading {
    text-align: center;
    color: #fff;
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 4px;
}
.auth-sub {
    text-align: center;
    color: rgba(255,255,255,0.5);
    font-size: 0.88rem;
    margin-bottom: 24px;
}

/* ── Chat header ── */
.chat-header {
    background: linear-gradient(90deg, #6c63ff, #48cfad);
    border-radius: 16px;
    padding: 16px 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}
.chat-header-left { display: flex; align-items: center; gap: 12px; }
.chat-header h1   { color: #fff; font-size: 1.3rem; margin: 0; }
.chat-header p    { color: rgba(255,255,255,0.8); font-size: 0.78rem; margin: 0; }
.user-pill {
    background: rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 6px 14px;
    color: #fff;
    font-size: 0.8rem;
    font-weight: 600;
}

/* ── Message bubbles ── */
.msg-bot {
    background: rgba(255,255,255,0.08);
    border-radius: 18px 18px 18px 4px;
    padding: 14px 18px;
    margin: 8px 0;
    color: #e8e8f0;
    font-size: 0.92rem;
    line-height: 1.7;
}
.msg-user {
    background: linear-gradient(135deg, #6c63ff, #5a52d5);
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    margin: 8px 0 8px 60px;
    color: #fff;
    font-size: 0.92rem;
    line-height: 1.6;
}

/* ── Answer sections ── */
.final-answer {
    background: linear-gradient(135deg,rgba(72,207,173,0.15),rgba(108,99,255,0.15));
    border: 1px solid rgba(72,207,173,0.4);
    border-radius: 12px;
    padding: 12px 16px;
    margin-top: 12px;
}
.final-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #48cfad;
    margin-bottom: 4px;
}
.final-value { font-size: 1rem; font-weight: 700; color: #fff; }

.pro-tip {
    background: rgba(245,87,108,0.1);
    border-left: 3px solid #f5576c;
    border-radius: 0 10px 10px 0;
    padding: 10px 14px;
    margin-top: 10px;
    font-size: 0.83rem;
    color: #ffb3be;
}
.tip-label { font-weight: 700; color: #f5576c; margin-right: 4px; }

/* ── Step list ── */
.step { display: flex; gap: 10px; margin-bottom: 10px; align-items: flex-start; }
.step-num {
    background: rgba(108,99,255,0.4);
    color: #c4bfff;
    font-size: 0.72rem;
    font-weight: 700;
    min-width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
}

/* ── Topic buttons ── */
.stButton > button {
    background: rgba(108,99,255,0.25) !important;
    border: 1px solid rgba(108,99,255,0.5) !important;
    color: #c4bfff !important;
    border-radius: 20px !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    padding: 6px 16px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(108,99,255,0.55) !important;
    color: #fff !important;
}

/* ── Primary button (login/signup) ── */
.primary-btn > button {
    background: linear-gradient(135deg,#6c63ff,#48cfad) !important;
    border: none !important;
    color: #fff !important;
    border-radius: 12px !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    width: 100% !important;
    padding: 12px !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextInput > div > div > input:focus {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 12px !important;
    color: #e8e8f0 !important;
    font-size: 0.95rem !important;
}
label { color: rgba(255,255,255,0.7) !important; font-size: 0.82rem !important; }

/* ── Error / success alerts ── */
.stAlert { border-radius: 10px !important; }

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────

TOPIC_PROMPTS = {
    "📐 Algebra":    "Give me a challenging algebra practice problem involving quadratic equations and solve it step by step.",
    "📏 Geometry":   "Give me a geometry practice problem involving circles or triangles and solve it step by step.",
    "∫ Calculus":    "Give me a calculus practice problem involving derivatives or integrals and solve it step by step.",
    "📊 Statistics": "Give me a statistics practice problem involving probability or normal distribution and solve it step by step.",
}


def parse_response(text: str) -> dict:
    """Split AI response into intro, steps, final answer, and pro tip."""
    final_match = re.search(r"FINAL ANSWER:\s*([\s\S]+?)(?=\nPRO TIP:|$)", text, re.IGNORECASE)
    tip_match   = re.search(r"PRO TIP:\s*([\s\S]+?)$", text, re.IGNORECASE)

    final_answer = final_match.group(1).strip() if final_match else None
    pro_tip      = tip_match.group(1).strip()   if tip_match   else None

    body = text
    if final_match:
        body = body[:text.lower().find("final answer:")].strip()

    # Extract numbered steps
    step_pattern = re.compile(r"(\d+)\.\s+([\s\S]+?)(?=\n\d+\.|$)")
    first_step   = re.search(r"^\d+\.\s", body, re.MULTILINE)
    intro        = body[:first_step.start()].strip() if first_step else body
    steps_body   = body[first_step.start():] if first_step else ""
    steps        = [(m.group(1), m.group(2).strip()) for m in step_pattern.finditer(steps_body)]

    return {"intro": intro, "steps": steps, "final": final_answer, "tip": pro_tip}


def render_bot_message(text: str):
    """Render a structured bot response."""
    parsed = parse_response(text)

    html = '<div class="msg-bot">'

    if parsed["intro"]:
        html += f'<p style="margin-bottom:10px;">{parsed["intro"]}</p>'

    if parsed["steps"]:
        for num, content in parsed["steps"]:
            html += f'''<div class="step">
                <div class="step-num">{num}</div>
                <div>{content}</div>
            </div>'''

    if parsed["final"]:
        html += f'''<div class="final-answer">
            <div class="final-label">✅ Final Answer</div>
            <div class="final-value">{parsed["final"]}</div>
        </div>'''

    if parsed["tip"]:
        html += f'''<div class="pro-tip">
            <span class="tip-label">💡 Pro Tip:</span>{parsed["tip"]}
        </div>'''

    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_user_message(text: str):
    st.markdown(f'<div class="msg-user">{text}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  PAGE: LOGIN
# ─────────────────────────────────────────────────────────────

def page_login():
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.markdown('<div class="auth-title">🧮</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-heading">Welcome Back</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">Log in to continue learning</div>', unsafe_allow_html=True)

    email    = st.text_input("Email",    placeholder="you@example.com", key="login_email")
    password = st.text_input("Password", placeholder="••••••••",        key="login_password", type="password")

    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    if st.button("Log In", key="login_btn", use_container_width=True):
        if not email or not password:
            st.error("Please fill in all fields.")
        else:
            result = login(email, password)
            if result["ok"]:
                st.session_state.token    = result["token"]
                st.session_state.user     = result["user"]
                st.session_state.messages = []
                st.session_state.page     = "chat"
                st.rerun()
            else:
                st.error(result["error"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Don't have an account? Sign up →", key="go_signup"):
            st.session_state.page = "signup"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  PAGE: SIGNUP
# ─────────────────────────────────────────────────────────────

def page_signup():
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.markdown('<div class="auth-title">🧮</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-heading">Create Account</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">Start solving math problems step by step</div>', unsafe_allow_html=True)

    name     = st.text_input("Full Name", placeholder="John Doe",          key="signup_name")
    email    = st.text_input("Email",     placeholder="you@example.com",   key="signup_email")
    password = st.text_input("Password",  placeholder="Min. 6 characters", key="signup_password", type="password")

    # Password strength
    if password:
        strength = sum([
            len(password) >= 6,
            len(password) >= 10,
            bool(re.search(r"[A-Z]", password)),
            bool(re.search(r"[0-9]", password)),
            bool(re.search(r"[^A-Za-z0-9]", password)),
        ])
        labels = ["", "Weak 🔴", "Fair 🟠", "Good 🟡", "Strong 🟢", "Very Strong 💪"]
        st.caption(f"Password strength: **{labels[strength]}**")

    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
    if st.button("Create Account", key="signup_btn", use_container_width=True):
        if not name or not email or not password:
            st.error("Please fill in all fields.")
        else:
            result = signup(name, email, password)
            if result["ok"]:
                st.session_state.token    = result["token"]
                st.session_state.user     = result["user"]
                st.session_state.messages = []
                st.session_state.page     = "chat"
                st.rerun()
            else:
                st.error(result["error"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Already have an account? Log in →", key="go_login"):
            st.session_state.page = "login"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
#  PAGE: CHAT
# ─────────────────────────────────────────────────────────────

def page_chat():
    user = st.session_state.user

    # ── Header ──
    st.markdown(f"""
    <div class="chat-header">
        <div class="chat-header-left">
            <span style="font-size:2rem;">🧮</span>
            <div>
                <h1>Math Tutor</h1>
                <p>Step-by-step solutions with explanations</p>
            </div>
        </div>
        <div class="user-pill">👤 {user["name"]}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick topic buttons ──
    cols = st.columns(4)
    for i, (label, prompt) in enumerate(TOPIC_PROMPTS.items()):
        with cols[i]:
            if st.button(label, key=f"topic_{i}"):
                _send_message(prompt)

    st.markdown("---")

    # ── Chat history ──
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align:center;padding:40px 20px;color:rgba(255,255,255,0.45);">
            <div style="font-size:3rem;margin-bottom:12px;">✏️</div>
            <div style="font-size:1.1rem;color:rgba(255,255,255,0.7);margin-bottom:8px;">Welcome to Math Tutor!</div>
            <div style="font-size:0.88rem;line-height:1.7;">
                Ask me any math problem — algebra, calculus, geometry, or statistics.<br>
                I'll walk you through every step and explain the <em>why</em> behind each one.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                render_user_message(msg["content"])
            else:
                render_bot_message(msg["content"])

    # ── Input ──
    with st.form(key="chat_form", clear_on_submit=True):
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            user_input = st.text_input(
                "message",
                placeholder="Type a math problem… e.g. Solve 3x² - 7x + 2 = 0",
                label_visibility="collapsed",
                key="chat_input",
            )
        with col_btn:
            submitted = st.form_submit_button("➤", use_container_width=True)

    if submitted and user_input.strip():
        _send_message(user_input.strip())

    # ── Logout ──
    st.markdown("---")
    col1, col2, col3 = st.columns([3, 1, 3])
    with col2:
        if st.button("⏻ Logout", key="logout"):
            st.session_state.token    = None
            st.session_state.user     = None
            st.session_state.messages = []
            st.session_state.page     = "login"
            st.rerun()


def _send_message(text: str):
    """Add user message, call Groq, append reply, rerun."""
    st.session_state.messages.append({"role": "user", "content": text})

    with st.spinner("Thinking…"):
        try:
            reply = chat(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"AI error: {e}")
            st.session_state.messages.pop()  # remove the user message on failure

    st.rerun()


# ─────────────────────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────────────────────

# Validate stored token on every load
if st.session_state.token:
    if not verify_token(st.session_state.token):
        st.session_state.token = None
        st.session_state.user  = None
        st.session_state.page  = "login"

# Route to correct page
if st.session_state.token and st.session_state.user:
    page_chat()
elif st.session_state.page == "signup":
    page_signup()
else:
    page_login()
