from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

import storage
from .util import is_admin

HELP = (
    "📝 Rules & notes\n"
    "/rules, /setrules <text>\n"
    "/save <name> <text> (admin), /get <name>, /notes, /clear <name> (admin)"
)


async def rules(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(storage.get(update.effective_chat.id, "rules", "No rules set."))


async def setrules(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, ctx):
        return await update.message.reply_text("Admins only.")
    storage.put(update.effective_chat.id, "rules", " ".join(ctx.args) or "No rules set.")
    await update.message.reply_text("Rules saved.")


async def save(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, ctx):
        return await update.message.reply_text("Admins only.")
    if len(ctx.args) < 2:
        return await update.message.reply_text("Usage: /save <name> <text>")
    cid = update.effective_chat.id
    notes = storage.get(cid, "notes", {})
    notes[ctx.args[0].lower()] = " ".join(ctx.args[1:])
    storage.put(cid, "notes", notes)
    await update.message.reply_text(f"Saved '{ctx.args[0]}'.")


async def get(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        return await update.message.reply_text("Usage: /get <name>")
    notes = storage.get(update.effective_chat.id, "notes", {})
    await update.message.reply_text(notes.get(ctx.args[0].lower(), "No such note."))


async def notes_list(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    notes = storage.get(update.effective_chat.id, "notes", {})
    await update.message.reply_text("\n".join(f"• {k}" for k in notes) or "No notes saved.")


async def clear(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, ctx):
        return await update.message.reply_text("Admins only.")
    cid = update.effective_chat.id
    notes = storage.get(cid, "notes", {})
    if ctx.args and notes.pop(ctx.args[0].lower(), None) is not None:
        storage.put(cid, "notes", notes)
        return await update.message.reply_text("Deleted.")
    await update.message.reply_text("No such note.")


def register(app):
    for name, fn in (("rules", rules), ("setrules", setrules), ("save", save),
                     ("get", get), ("notes", notes_list), ("clear", clear)):
        app.add_handler(CommandHandler(name, fn))
