from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

HELP = "📊 Polls\n/poll Question | option 1 | option 2 | ..."


async def poll(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    parts = [p.strip() for p in " ".join(ctx.args).split("|") if p.strip()]
    if len(parts) < 3:
        return await update.message.reply_text("Usage: /poll Question | option 1 | option 2")
    await ctx.bot.send_poll(update.effective_chat.id, parts[0], parts[1:11], is_anonymous=False)


def register(app):
    app.add_handler(CommandHandler("poll", poll))
