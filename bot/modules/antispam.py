import re
import time
from collections import defaultdict, deque

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

import storage
from .util import is_admin

HELP = "🚫 Anti-spam\n/antilink on|off (delete links from non-admins)\nFlood control: >6 msgs in 10s deletes extras."
LINK = re.compile(r"(https?://|t\.me/|www\.)", re.I)
_recent = defaultdict(lambda: deque(maxlen=6))


async def check(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or update.effective_chat.type == "private":
        return
    if await is_admin(update, ctx):
        return
    cid, uid = update.effective_chat.id, update.effective_user.id
    if storage.get(cid, "antilink", False) and LINK.search(msg.text or msg.caption or ""):
        return await msg.delete()
    q = _recent[(cid, uid)]
    now = time.time()
    q.append(now)
    if len(q) == q.maxlen and now - q[0] < 10:
        await msg.delete()


async def antilink(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, ctx) or not ctx.args:
        return await update.message.reply_text("Admins only. Usage: /antilink on|off")
    storage.put(update.effective_chat.id, "antilink", ctx.args[0] == "on")
    await update.message.reply_text(f"Anti-link {ctx.args[0]}.")


def register(app):
    app.add_handler(CommandHandler("antilink", antilink))
    app.add_handler(MessageHandler(~filters.COMMAND & ~filters.StatusUpdate.ALL, check), group=1)
