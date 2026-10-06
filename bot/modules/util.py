from telegram import Update
from telegram.ext import ContextTypes


async def is_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE, user_id=None) -> bool:
    chat = update.effective_chat
    if chat.type == "private":
        return True
    uid = user_id or update.effective_user.id
    member = await ctx.bot.get_chat_member(chat.id, uid)
    return member.status in ("administrator", "creator")


def target_user(update: Update):
    """User being replied to, or None."""
    msg = update.message
    return msg.reply_to_message.from_user if msg and msg.reply_to_message else None
