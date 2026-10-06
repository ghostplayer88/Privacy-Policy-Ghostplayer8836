# Multi-purpose Telegram bot

Modular group bot. Modules (toggle with `MODULES` in `.env`):
`admin`, `welcome`, `notes`, `antispam`, `fun`, `utility`, `polls`, `reminders`, `ai`, `growth`.

## Setup
1. Create a bot with @BotFather and copy the token.
2. `cp .env.example .env` and set `BOT_TOKEN`.
3. `pip install -r requirements.txt`
4. `python main.py`
5. Add the bot to your group and make it admin (needed for ban/mute/delete).
   In @BotFather, run `/setprivacy` -> Disable so anti-spam can see messages.

## Adding a feature
Create `modules/<name>.py` with a `HELP` string and a `register(app)` function,
then add the name to `MODULES`.

## Using it
- **AI:** DM the bot, or in a group `/ask ...`, mention `@yourbot`, or reply to its messages. Admins set its personality with `/persona`.
- **Growth:** members earn XP for chatting (`/rank`, `/top`) and for inviting people via `/invite`. Needs the bot to be admin with *Invite users*.
- **AI runs locally with Ollama** (free, no subscription or API key):
  1. Install Ollama from https://ollama.com
  2. `ollama pull llama3.2:3b` (8 GB RAM) or `ollama pull qwen2.5:7b` (16 GB RAM)
  3. Set `OLLAMA_MODEL` in `.env` to match. Keep Ollama running while the bot runs.
  The laptop must stay on for AI replies to work.
