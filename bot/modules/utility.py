import ast
import operator as op

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

HELP = "🧰 Utility\n/id, /ping, /calc <expression>, /info (reply to a user)"
OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
       ast.Pow: op.pow, ast.Mod: op.mod, ast.USub: op.neg}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ValueError("exponent too large")
        return OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.operand))
    raise ValueError("unsupported")


async def calc(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        result = _eval(ast.parse(" ".join(ctx.args), mode="eval").body)
    except Exception:
        return await update.message.reply_text("Usage: /calc 2*(3+4)")
    await update.message.reply_text(str(result))


async def ident(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"You: {update.effective_user.id}\nChat: {update.effective_chat.id}")


async def ping(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pong 🏓")


async def info(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    u = msg.reply_to_message.from_user if msg.reply_to_message else update.effective_user
    await msg.reply_text(f"{u.full_name}\nID: {u.id}\nUsername: @{u.username or '-'}")


def register(app):
    for name, fn in (("calc", calc), ("id", ident), ("ping", ping), ("info", info)):
        app.add_handler(CommandHandler(name, fn))
