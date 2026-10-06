import random

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

HELP = "🎲 Fun\n/roll [sides], /flip, /8ball <question>, /choose a, b, c"
BALL = ["Yes.", "No.", "Maybe.", "Definitely.", "Ask again later.", "Doubtful.", "Without a doubt."]


async def roll(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    sides = int(ctx.args[0]) if ctx.args and ctx.args[0].isdigit() and int(ctx.args[0]) > 1 else 6
    await update.message.reply_text(f"🎲 {random.randint(1, sides)} (d{sides})")


async def flip(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(random.choice(["Heads", "Tails"]))


async def eightball(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎱 " + random.choice(BALL))


async def choose(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    opts = [o.strip() for o in " ".join(ctx.args).split(",") if o.strip()]
    await update.message.reply_text(random.choice(opts) if len(opts) > 1 else "Usage: /choose a, b, c")


def register(app):
    for name, fn in (("roll", roll), ("flip", flip), ("8ball", eightball), ("choose", choose)):
        app.add_handler(CommandHandler(name, fn))
