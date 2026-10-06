import re

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

HELP = "⏰ Reminders\n/remind 10m take a break  (units: s, m, h, d; lost on restart)"
UNITS = {"s": 1, "m": 60, "h": 3600, "d": 86400}


async def fire(ctx: ContextTypes.DEFAULT_TYPE):
    d = ctx.job.data
    await ctx.bot.send_message(d["chat"], f"⏰ {d['mention']}: {d['text']}", parse_mode="HTML")


async def remind(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    m = re.fullmatch(r"(\d+)([smhd])", ctx.args[0]) if ctx.args else None
    if not m or len(ctx.args) < 2:
        return await update.message.reply_text("Usage: /remind 10m text")
    secs = int(m[1]) * UNITS[m[2]]
    if secs > 30 * 86400:
        return await update.message.reply_text("Max 30 days.")
    ctx.job_queue.run_once(fire, secs, data={
        "chat": update.effective_chat.id,
        "mention": update.effective_user.mention_html(),
        "text": " ".join(ctx.args[1:]).replace("<", "&lt;"),
    })
    await update.message.reply_text(f"Okay, I'll remind you in {ctx.args[0]}.")


def register(app):
    app.add_handler(CommandHandler("remind", remind))
