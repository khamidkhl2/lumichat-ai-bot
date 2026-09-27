# 🧠 NexaChat — AI Smart Assistant & Companion

**NexaChat** is an ultra-fast, conversational AI Telegram bot powered by the **100% free Groq Cloud API** using `llama-3.3-70b-versatile` (with automatic fallback to `llama-3.1-8b-instant`).

It includes 5 specialized personas, sliding window conversation memory, daily free usage limits with Telegram Stars monetization, viral referral mechanics, mandatory sponsor channel verification, and sister-bot cross-promotion.

---

## 🌟 Key Features

1. **Lightning-Fast AI (Groq)**:
   - Primary model: `llama-3.3-70b-versatile`
   - Fallback model: `llama-3.1-8b-instant`
   - Zero cost: Powered by free Groq Cloud API keys.

2. **In-Memory Sliding Window**:
   - Maintains the last 10 messages of context per user.
   - Users can reset memory anytime using `/new` or `/clear` or inline buttons.

3. **5 Specialized AI Personas**:
   - 🧠 **General Assistant**: Daily inquiries, brainstorming, research.
   - 📚 **Homework & Math Tutor**: Step-by-step Socratic explanations of math and science.
   - 💻 **Senior Developer / Code Expert**: Clean code generation, debugging, algorithms, architecture.
   - 🌍 **Polyglot Translator**: Nuanced translations across 50+ languages preserving tone and idioms.
   - ✨ **Creative Storyteller**: Rich storytelling, worldbuilding, scripts, and poetry.
   - Switchable dynamically via `/persona` or inline buttons.

4. **Monetization & Viral Growth**:
   - **Daily Free Quota**: 15 messages/day for regular users via `db.check_daily_quota(user_id, 'chat', 15)` and `db.increment_daily_usage(user_id, 'chat')`.
   - **Telegram Stars VIP**: Users can purchase a 30-day VIP pass for unlimited requests and ad-free experience.
   - **Referral System**: Users invite 3 friends to get 30 days of VIP free.
   - **Sponsor Gating**: Mandatory subscription check via `sponsor_service.check_user_subscription`.
   - **Cross-Promotion**: Subtle tip footers (`cross_promo.get_tip_footer('chat', lang)`) and `/bots` network directory.

5. **Multi-Language Interface**:
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
