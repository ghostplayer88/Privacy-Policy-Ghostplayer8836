import os
from collections import defaultdict, deque
import time

from anthropic import AsyncAnthropic
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

import storage
from .util import is_admin

HELP = (
    "🤖 AI\n/ask <question>, or mention/reply to me in a group (any message in DMs)\n"
    "/persona <text> (admin: set my personality), /resetai (clear memory)"
)
MODEL = os.environ.get("AI_MODEL", "claude-sonnet-5-5")
DEFAULT_PERSONA = "You are a friendly, helpful assistant in a Telegram group. Keep answers concise."
_client = None
_history = defaultdict(lambda: deque(maxlen=12))  # per chat, last 12 turns
_last = {}  # per-user rate limit


def client():
    global _client
    _client = _client or AsyncAnthropic()  # reads ANTHROPIC_API_KEY
    return _client


async def answer(update: Update, ctx: ContextTypes.DEFAULT_TYPE, text: str):
    uid, cid = update.effective_user.id, update.effective_chat.id
    if time.time() - _last.get(uid, 0) < 3:
        return
    _last[uid] = time.time()
    await ctx.bot.send_chat_action(cid, ChatAction.TYPING)
    hist = _history[cid]
    hist.append({"role": "user", "content": f"{update.effective_user.first_name}: {text}"})
    msgs = list(hist)
    while msgs and msgs[0]["role"] != "user":
        msgs.pop(0)
    try:
        resp = await client().messages.create(
            model=MODEL, max_tokens=700,
            system=storage.get(cid, "persona", DEFAULT_PERSONA), messages=msgs,
        )
        reply = resp.content[0].text
    except Exception:
        hist.pop()
        return await update.message.reply_text("AI is unavailable right now. Try again later.")
    hist.append({"role": "assistant", "content": reply})
    await update.message.reply_text(reply[:4000])


async def ask(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        return await update.message.reply_text("Usage: /ask <question>")
    await answer(update, ctx, " ".join(ctx.args))


async def chat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg, me = update.message, ctx.bot
    if not msg or not msg.text:
        return
    private = update.effective_chat.type == "private"
    mentioned = f"@{me.username}".lower() in msg.text.lower()
    replied = msg.reply_to_message and msg.reply_to_message.from_user.id == me.id
    if private or mentioned or replied:
        await answer(update, ctx, msg.text.replace(f"@{me.username}", "").strip())


async def persona(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, ctx):
        return await update.message.reply_text("Admins only.")
    storage.put(update.effective_chat.id, "persona", " ".join(ctx.args) or DEFAULT_PERSONA)
    await update.message.reply_text("Persona updated.")


async def resetai(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    _history.pop(update.effective_chat.id, None)
    await update.message.reply_text("Memory cleared.")


def register(app):
    app.add_handler(CommandHandler("ask", ask))
    app.add_handler(CommandHandler("persona", persona))
    app.add_handler(CommandHandler("resetai", resetai))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat), group=2)
