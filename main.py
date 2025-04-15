import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler, ConversationHandler, MessageHandler, filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

PRICE, COST, QTY, RENT, COMMISSION = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔢 Рассчитать", callback_data="start_calc")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Добро пожаловать в Калькулятор прибыли мастера!", reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Введите цену за штуку (₽):")
    return PRICE

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["price"] = float(update.message.text)
    await update.message.reply_text("Введите себестоимость (%):")
    return COST

async def get_cost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cost"] = float(update.message.text)
    await update.message.reply_text("Введите количество изделий:")
    return QTY

async def get_qty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["qty"] = int(update.message.text)
    await update.message.reply_text("Введите аренду (₽):")
    return RENT

async def get_rent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["rent"] = float(update.message.text)
    await update.message.reply_text("Введите комиссию (%):")
    return COMMISSION

async def get_commission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["commission"] = float(update.message.text)

    price = context.user_data["price"]
    cost_pct = context.user_data["cost"]
    qty = context.user_data["qty"]
    rent = context.user_data["rent"]
    commission_pct = context.user_data["commission"]

    revenue = price * qty
    commission = revenue * commission_pct / 100
    cost = price * cost_pct / 100 * qty
    profit = revenue - commission - cost - rent

    result = f"""🔢 <b>Калькулятор прибыли мастера</b>

💰 <b>Выручка:</b> {revenue:,.0f} ₽
💸 <b>Комиссия ({commission_pct}%):</b> {commission:,.0f} ₽
⚙️ <b>Себестоимость ({cost_pct}%):</b> {cost:,.0f} ₽
🏠 <b>Аренда:</b> {rent:,.0f} ₽
📈 <b>Чистая прибыль:</b> <b>{profit:,.0f} ₽</b>
"""
    await update.message.reply_html(result)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click, pattern="start_calc"))

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_click, pattern="start_calc")],
        states={
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_price)],
            COST: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_cost)],
            QTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_qty)],
            RENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_rent)],
            COMMISSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_commission)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    print("Бот запущен с кнопкой ✅")
    app.run_polling()
