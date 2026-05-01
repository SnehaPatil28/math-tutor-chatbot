# 🧮 Math Tutor AI

A GenAI-powered math tutoring chatbot built with **Streamlit** and **Groq (LLaMA 3.3)**. It solves any math problem step by step, explains the *why* behind each step, highlights the final answer, and ends with a pro tip — all behind a secure login system.

---

## ✨ Features

- **Step-by-step solutions** — every answer is broken into numbered reasoning steps
- **Final answer highlight** — clearly separated from the working
- **Pro tip** — a practical insight after every solution
- **Quick topic buttons** — one-click practice problems for Algebra, Geometry, Calculus, and Statistics
- **Multi-turn memory** — ask follow-ups like *"explain step 2 again"*
- **User authentication** — signup, login, JWT sessions, bcrypt password hashing
- **Password strength indicator** — live feedback on signup
- **Secure secrets** — API key and JWT secret never exposed to the UI

---

## 🗂️ Project Structure

```
math-tutor-chatbot/
├── app.py               # Streamlit UI — login, signup, chat pages
├── auth.py              # Signup / login / JWT helpers
├── groq_client.py       # Groq API wrapper (key stays server-side)
├── requirements.txt     # Python dependencies
├── .gitignore
├── data/
│   └── users.json       # Auto-created on first signup (gitignored)
└── .streamlit/
    ├── config.toml      # Theme and server config
    └── secrets.toml     # Local secrets (gitignored — never commit)
```

---

## 🚀 Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/math-tutor-chatbot.git
cd math-tutor-chatbot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your secrets

Create `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
GROQ_MODEL   = "llama-3.3-70b-versatile"
JWT_SECRET   = "your_random_secret_string"
```

Get a free Groq API key at [console.groq.com/keys](https://console.groq.com/keys) — no credit card required.

### 4. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## ☁️ Deploy to Streamlit Cloud

1. Push your code to GitHub (make sure `secrets.toml` is gitignored)
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **"Create app"** → select your repo → set main file to `app.py`
4. Click **"Advanced settings"** → paste your secrets:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
GROQ_MODEL   = "llama-3.3-70b-versatile"
JWT_SECRET   = "your_random_secret_string"
```

5. Click **Deploy** — live in ~60 seconds

---

## 🔐 How Authentication Works

| Step | Detail |
|------|--------|
| Signup | Password hashed with **bcrypt** before storing in `data/users.json` |
| Login | bcrypt comparison — plain password never stored |
| Session | **JWT token** (7-day expiry) stored in Streamlit session state |
| Protection | Token verified on every page load — expired tokens redirect to login |

---

## 🤖 AI Design

The chatbot uses two prompting techniques:

| Technique | Implementation |
|-----------|---------------|
| **E01 — Basic Prompting** | System prompt defines the tutor persona and strict response format |
| **E02 — Chain-of-Thought** | Every answer is forced into numbered reasoning steps with explanations |

Model: `llama-3.3-70b-versatile` via [Groq](https://groq.com) — free tier, ~30 req/min.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | UI framework |
| `groq` | LLaMA 3.3 API client |
| `bcrypt` | Password hashing |
| `PyJWT` | JWT token creation and verification |

---

## ⚠️ Notes

- `data/users.json` is gitignored — user accounts are local only
- On Streamlit Cloud, the filesystem resets on redeploy (users are lost). For persistent users, swap `users.json` for a cloud database like [Supabase](https://supabase.com) or [MongoDB Atlas](https://www.mongodb.com/atlas)
- Never commit `.streamlit/secrets.toml` — it contains your API key

---

## 📄 License

MIT
