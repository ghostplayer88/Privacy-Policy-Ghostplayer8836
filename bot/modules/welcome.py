from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

import storage
from .util import is_admin

HELP = "👋 Welcome\n/setwelcome <text> ({name} = member name), /welcome off"
DEFAULT = "Welcome, {name}! 👋"


async def greet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = storage.get(update.effective_chat.id, "welcome", DEFAULT)
    if not text:
        return
    for m in update.message.new_chat_members:
        if not m.is_bot:
            await update.message.reply_text(text.replace("{name}", m.full_name))


async def setwelcome(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, ctx):
        return await update.message.reply_text("Admins only.")
    if not ctx.args:
        return await update.message.reply_text("Usage: /setwelcome <text>")
    storage.put(update.effective_chat.id, "welcome", " ".join(ctx.args))
    await update.message.reply_text("Welcome message saved.")


async def welcome(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if await is_admin(update, ctx) and ctx.args and ctx.args[0] == "off":
        storage.put(update.effective_chat.id, "welcome", "")
        await update.message.reply_text("Welcome messages off.")


def register(app):
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet))
    app.add_handler(CommandHandler("setwelcome", setwelcome))
    app.add_handler(CommandHandler("welcome", welcome))
