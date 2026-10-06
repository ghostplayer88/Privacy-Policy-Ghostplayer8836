import importlib
import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
log = logging.getLogger("bot")

ALL_MODULES = "admin,welcome,notes,antispam,fun,utility,polls,reminders"
HELP = {}  # module name -> help text, filled by modules


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I'm a multi-purpose bot. Use /help to see what I can do.")


async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("\n\n".join(HELP.values()) or "No modules loaded.")


def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise SystemExit("Set BOT_TOKEN in .env (get one from @BotFather).")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    for name in os.environ.get("MODULES", ALL_MODULES).split(","):
        name = name.strip()
        mod = importlib.import_module(f"modules.{name}")
        mod.register(app)
        HELP[name] = mod.HELP
        log.info("loaded module %s", name)
    app.run_polling()


if __name__ == "__main__":
    main()
