# 🧠 LumiChat — AI Smart Assistant & Companion

**LumiChat** ([@lumichat_ai_bot](https://t.me/lumichat_ai_bot)) is an ultra-fast, conversational AI Telegram bot powered by the **100% free Groq Cloud API** using `openai/gpt-oss-120b` (with automatic fallback to `openai/gpt-oss-20b`).

It features 5 specialized personas, persistent SQLite multi-turn conversation memory, mobile-optimized Telegram HTML formatting, daily free usage limits with Telegram Stars monetization, viral referral mechanics, mandatory sponsor channel verification, and sister-bot cross-promotion.

---

## 🌟 Key Features

1. **Lightning-Fast AI (Groq)**:
   - Primary model: `openai/gpt-oss-120b`
   - Fallback model: `openai/gpt-oss-20b`
   - Zero cost: Powered by free Groq Cloud API keys.

2. **Persistent Multi-Turn Sessions**:
   - Maintains conversation context across serverless Lambda invocations using SQLite (`/tmp/shared_empire.db`).
   - Users can reset memory anytime using `/new`, `/clear`, or the inline button `🧹 Clear Memory`.

3. **Telegram-Native Mobile Formatting**:
   - Prompt engineering restricts responses to 2–4 concise, direct, high-value sections.
   - Built-in `telegram_formatter.py` intercepts raw Markdown tables and renders clean bullet points.
   - Sent via native Telegram HTML so italic tips and code blocks format cleanly.

4. **5 Specialized AI Personas**:
   - 🧠 **General Assistant**: Daily inquiries, brainstorming, research.
   - 📚 **Homework & Math Tutor**: Step-by-step problem solver.
   - 💻 **Senior Developer / Code Expert**: Clean code generation, debugging, algorithms, architecture.
   - 🌍 **Polyglot Translator**: Nuanced translations across 50+ languages preserving tone and idioms.
   - ✨ **Creative Storyteller**: Rich storytelling, worldbuilding, scripts, and poetry.
   - Switchable dynamically via `/persona` or inline buttons.

5. **Monetization & Viral Growth**:
   - **Daily Free Quota**: 15 messages/day for regular users via `db.check_daily_quota(user_id, 'chat', 15)`.
   - **Telegram Stars VIP**: 30-day VIP pass for unlimited requests and ad-free experience.
   - **Referral System**: Users invite 3 friends to get 30 days of VIP free.
   - **Sponsor Gating**: Mandatory subscription check via `sponsor_service.check_user_subscription`.
   - **Cross-Promotion**: Subtle tip footers promoting sister bots (`@velo_save_bot` and `@VoxifyVoiceBot`).

6. **Multi-Language Interface**:
   - English 🇬🇧, Russian 🇷🇺, Uzbek 🇺🇿, Spanish 🇪🇸.

---

## 📋 Commands

- `/start` — Start bot, register account, show welcome menu
- `/persona` — Switch AI persona & specialization
- `/new` or `/clear` — Reset conversation memory
- `/vip` — Purchase VIP Pass with Telegram Stars
- `/referral` — View personal invite link & referral stats
- `/bots` — Discover our sister AI & media bots
- `/lang` — Change interface language
- `/help` — How to use NexaChat

---

## 🚀 Setup & Installation

### 1. Clone & Setup Python Virtual Environment

```bash
cd tg_bots/ai-chat-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create `.env` (or configure the root `tg_bots/.env`):

```bash
cp .env.example .env
```

Fill in:
- `BOT_TOKEN_CHAT` (or `BOT_TOKEN`): From [@BotFather](https://t.me/BotFather)
- `GROQ_API_KEY`: 100% free from [Groq Console](https://console.groq.com)
- `ADMIN_IDS`: Your Telegram ID (comma-separated)
- `VIP_PRICE_STARS`: Default 50 Stars

### 3. Run the Bot

```bash
python3 main.py
```

---

## 🐳 Docker Deployment

Build and run with Docker:

```bash
docker build -t nexachat-bot .
docker run -d --name nexachat-bot --env-file .env nexachat-bot
```
