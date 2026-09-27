# 🤝 Project Handoff: LumiChat AI Assistant Bot

This document contains everything needed to resume, maintain, and scale **LumiChat** ([@lumichat_ai_bot](https://t.me/lumichat_ai_bot)).

---

## 📌 Executive Summary & Key Credentials

| Property | Value |
| :--- | :--- |
| **Bot Name** | `LumiChat` |
| **Telegram Handle** | **`@lumichat_ai_bot`** |
| **Bot ID** | `8378863082` |
| **Bot Token** | `8378863082:AAF-G0IRE1Q1aQwNBFZwntDlThnKp7Dd4CM` |
| **Owner / Admin ID** | `5831301324` |
| **Groq API Key** | Configured in Vercel & local `.env` (`gsk_...`) |
| **Primary AI Model** | `openai/gpt-oss-120b` (fallback: `openai/gpt-oss-20b`) |
| **GitHub Repository** | [github.com/khamidkhl2/lumichat-ai-bot](https://github.com/khamidkhl2/lumichat-ai-bot) |
| **Live Webhook URL** | `https://lumichat-ai-bot.vercel.app/` |
| **Local Project Path** | `/Users/khamid/Documents/tg_bots/ai-chat-bot` |
| **Deployment Platform**| Vercel Serverless (Python 3.11) |

---

## 🚀 Current System Status

* **Status:** ✅ **LIVE & FULLY OPERATIONAL**
* **Deployment Workflow:** Connected to GitHub `main` branch. Any `git push` automatically redeploys on Vercel within ~20 seconds.
* **Telegram Webhook:** Configured and active. Updates are delivered instantly to `https://lumichat-ai-bot.vercel.app/`.
* **Profile Picture:** Configured with a clean, flat 2D vector app icon (full-bleed dark obsidian background, electric cyan and purple neural brain circuits, and crisp "LUMI CHAT AI" typography).

---

## 🛠️ Key Handlers & Logic

### 1. Telegram Mobile Response Engineering
- **Concise Formatting**: Persona prompts strictly enforce 2–4 direct, high-value sections or bullet lists without walls of text or asking 100 questions.
- **Table Interceptor (`services/telegram_formatter.py`)**: Intercepts raw Markdown tables (`|---|---|`) and transforms them into clean bullet points (`📌 <b>Category</b> • <i>Detail</i>`).
- **Native HTML Sending**: Messages are sent with `parse_mode="HTML"`. The tip footer `<i>Tip:...</i>` renders in genuine italics without raw HTML code.
- **Fast Token Generation**: Default `GROQ_MAX_TOKENS = 750` for fast, snappy mobile responses.

### 2. Session & Memory Persistence (`services/memory_service.py`)
- Conversations are stored in the shared SQLite database (`/tmp/shared_empire.db` on Vercel) in the `chat_history` table.
- Context persists reliably across serverless Lambda invocations.
- Users can reset memory anytime using `/new`, `/clear`, or the inline button `🧹 Clear Memory`.

### 3. AI Personas (`services/personas.py`)
Five switchable personas via `/persona` or inline buttons:
1. 🧠 **General Assistant** (`general`): Daily tasks, brainstorming, answers.
2. 📚 **Homework & Math Tutor** (`tutor`): Clear, step-by-step problem solver.
3. 💻 **Senior Developer** (`developer`): Clean code, architecture, and debugging.
4. 🌍 **Polyglot Translator** (`translator`): Nuanced multilingual translation.
5. ✨ **Creative Storyteller** (`storyteller`): Engaging stories and creative writing.
Persona preference is saved in SQLite (`user_personas` table).

### 4. Monetization & Quota Engine
- **Daily Free Limit**: 15 messages/day for regular users (`db.check_daily_quota(user_id, 'chat', 15)`).
- **Telegram Stars VIP**: 50 Stars for 30 days of unlimited requests and ad-free experience (`/vip`).
- **Referrals**: 3 friend invites grant 30 days of free VIP (`/referral`).
- **Cross-Promotion**: Subtle tip footer promoting sister bots (`@velo_save_bot` and `@VoxifyVoiceBot`).

---

## 📁 Repository Structure

```text
ai-chat-bot/
├── api/
│   └── index.py            # Vercel Serverless Function entry point
├── assets/
│   └── logo.jpg            # Clean 2D flat minimalist profile icon
├── handlers/
│   ├── chat.py             # Message router, HTML formatter, memory calls, tip footer
│   ├── persona.py          # /persona command and persona switcher callbacks
│   ├── start.py            # /start, /help, /vip, /lang, /referral, /bots
│   └── sponsor_gate.py     # Channel subscription check
├── keyboards/
│   └── inline.py           # Persona selector and chat action buttons
├── services/
│   ├── groq_service.py     # Groq Cloud API caller with automatic fallback model
│   ├── memory_service.py   # Multi-turn history management backed by SQLite
│   ├── personas.py         # System prompt definitions with strict Telegram formatting
│   └── telegram_formatter.py # Markdown-to-HTML parser & table-to-bullet converter
├── shared/                 # Symlinked/synchronized core shared modules
├── config.py               # Bot token, Groq settings, quotas
├── vercel.json             # Vercel routing configuration
└── requirements.txt        # aiogram, groq, aiohttp, etc.
```

---

## 📋 Next Session Action Plan

1. **Traffic Launch**: Promote LumiChat in study groups, developer communities, and language learner channels.
2. **Sponsor Campaigns**: Add partner channels via `/add_sponsor` to monetize free conversational requests.
