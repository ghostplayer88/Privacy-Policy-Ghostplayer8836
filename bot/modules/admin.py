from datetime import datetime, timedelta, timezone

from telegram import ChatPermissions, Update
from telegram.ext import CommandHandler, ContextTypes

import storage
from .util import is_admin, target_user

HELP = (
    "🛡 Admin (reply to a user's message)\n"
    "/ban, /unban, /kick, /mute [minutes], /unmute\n"
    "/warn [reason], /warns, /resetwarns (3 warns = ban)"
)
MAX_WARNS = 3


def guard(fn):
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.type == "private":
            return await update.message.reply_text("Group-only command.")
        if not await is_admin(update, ctx):
            return await update.message.reply_text("Admins only.")
        user = target_user(update)
        if not user:
            return await update.message.reply_text("Reply to the user's message.")
        if await is_admin(update, ctx, user.id):
            return await update.message.reply_text("I won't act on an admin.")
        await fn(update, ctx, user)
    return wrapper


@guard
async def ban(update, ctx, user):
    await ctx.bot.ban_chat_member(update.effective_chat.id, user.id)
    await update.message.reply_text(f"🔨 Banned {user.mention_html()}", parse_mode="HTML")


@guard
async def unban(update, ctx, user):
    await ctx.bot.unban_chat_member(update.effective_chat.id, user.id, only_if_banned=True)
    await update.message.reply_text("Unbanned.")


@guard
async def kick(update, ctx, user):
    await ctx.bot.ban_chat_member(update.effective_chat.id, user.id)
    await ctx.bot.unban_chat_member(update.effective_chat.id, user.id)
    await update.message.reply_text("👢 Kicked.")


@guard
async def mute(update, ctx, user):
    until = None
    if ctx.args and ctx.args[0].isdigit():
        until = datetime.now(timezone.utc) + timedelta(minutes=int(ctx.args[0]))
    await ctx.bot.restrict_chat_member(
        update.effective_chat.id, user.id, ChatPermissions(can_send_messages=False), until_date=until
    )
    await update.message.reply_text("🔇 Muted" + (f" for {ctx.args[0]} min." if until else "."))


@guard
async def unmute(update, ctx, user):
    await ctx.bot.restrict_chat_member(
        update.effective_chat.id,
        user.id,
        ChatPermissions(can_send_messages=True, can_send_other_messages=True,
                        can_add_web_page_previews=True, can_send_polls=True),
    )
    await update.message.reply_text("🔊 Unmuted.")


@guard
async def warn(update, ctx, user):
    chat_id, key = update.effective_chat.id, f"warns:{user.id}"
    count = storage.get(chat_id, key, 0) + 1
    storage.put(chat_id, key, count)
    reason = " ".join(ctx.args) or "no reason"
    if count >= MAX_WARNS:
        await ctx.bot.ban_chat_member(chat_id, user.id)
        storage.delete(chat_id, key)
        return await update.message.reply_text(f"⚠️ {count}/{MAX_WARNS} ({reason}). Banned.")
    await update.message.reply_text(f"⚠️ Warned {count}/{MAX_WARNS} ({reason}).")


@guard
async def warns(update, ctx, user):
    n = storage.get(update.effective_chat.id, f"warns:{user.id}", 0)
    await update.message.reply_text(f"{n}/{MAX_WARNS} warnings.")


@guard
async def resetwarns(update, ctx, user):
    storage.delete(update.effective_chat.id, f"warns:{user.id}")
    await update.message.reply_text("Warnings cleared.")


def register(app):
    for fn in (ban, unban, kick, mute, unmute, warn, warns, resetwarns):
        app.add_handler(CommandHandler(fn.__name__, fn))
