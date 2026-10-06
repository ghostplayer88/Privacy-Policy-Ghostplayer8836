import time

from telegram import Update
from telegram.ext import ChatMemberHandler, CommandHandler, ContextTypes, MessageHandler, filters

import storage

HELP = (
    "📈 Growth\n/rank (your XP), /top (leaderboard)\n"
    "/invite (your personal invite link; earn 50 XP per member who joins), /invites"
)
XP_PER_MSG, COOLDOWN, XP_PER_INVITE = 5, 60, 50
_last = {}


def add_xp(cid, uid, name, amount):
    board = storage.get(cid, "xp", {})
    entry = board.get(str(uid), {"name": name, "xp": 0})
    entry["name"], entry["xp"] = name, entry["xp"] + amount
    board[str(uid)] = entry
    storage.put(cid, "xp", board)


async def on_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u, c = update.effective_user, update.effective_chat
    if not u or u.is_bot or c.type == "private":
        return
    if time.time() - _last.get((c.id, u.id), 0) >= COOLDOWN:
        _last[(c.id, u.id)] = time.time()
        add_xp(c.id, u.id, u.full_name, XP_PER_MSG)


def level(xp):
    return int((xp / 50) ** 0.5) + 1


async def rank(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    e = storage.get(update.effective_chat.id, "xp", {}).get(str(update.effective_user.id))
    xp = e["xp"] if e else 0
    await update.message.reply_text(f"⭐ {xp} XP · Level {level(xp)}")


async def top(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    board = sorted(storage.get(update.effective_chat.id, "xp", {}).values(), key=lambda e: -e["xp"])[:10]
    lines = [f"{i}. {e['name']} — {e['xp']} XP" for i, e in enumerate(board, 1)]
    await update.message.reply_text("🏆 Leaderboard\n" + ("\n".join(lines) or "No activity yet."))


async def invite(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    c, u = update.effective_chat, update.effective_user
    if c.type == "private":
        return await update.message.reply_text("Use this in the group.")
    links = storage.get(c.id, "links", {})
    mine = next((url for url, uid in links.items() if uid == u.id), None)
    if not mine:
        try:
            link = await ctx.bot.create_chat_invite_link(c.id, name=f"ref:{u.id}"[:32])
        except Exception:
            return await update.message.reply_text("I need admin rights with 'invite users'.")
        mine = link.invite_link
        links[mine] = u.id
        storage.put(c.id, "links", links)
    await update.message.reply_text(f"Your invite link (earn {XP_PER_INVITE} XP per join):\n{mine}")


async def on_join(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ev = update.chat_member
    if not ev or ev.new_chat_member.status != "member" or ev.old_chat_member.status in ("member", "administrator", "creator"):
        return
    if not ev.invite_link:
        return
    cid = ev.chat.id
    inviter = storage.get(cid, "links", {}).get(ev.invite_link.invite_link)
    joiner = ev.new_chat_member.user
    if inviter and inviter != joiner.id:
        n = storage.get(cid, f"invited:{inviter}", 0) + 1
        storage.put(cid, f"invited:{inviter}", n)
        add_xp(cid, inviter, (await ctx.bot.get_chat_member(cid, inviter)).user.full_name, XP_PER_INVITE)


async def invites(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    n = storage.get(update.effective_chat.id, f"invited:{update.effective_user.id}", 0)
    await update.message.reply_text(f"You've invited {n} member(s).")


def register(app):
    app.add_handler(MessageHandler(~filters.COMMAND, on_message), group=3)
    app.add_handler(ChatMemberHandler(on_join, ChatMemberHandler.CHAT_MEMBER))
    for name, fn in (("rank", rank), ("top", top), ("invite", invite), ("invites", invites)):
        app.add_handler(CommandHandler(name, fn))
