import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

from app.config import TELEGRAM_BOT_TOKEN, LOG_LEVEL
from app.llm import user_to_sql, rows_to_answer
from app.db import execute_query

# logger
logging.basicConfig(
    level=LOG_LEVEL,
    format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Обработчик сообщений """
    user_text = update.message.text
    user = update.message.from_user
    logger.info(f"Message from {user.id} ({user.username}): {user_text}")

    try:
        # Генерация SQL
        sql = user_to_sql(user_text)

        if sql is None:  # Вопрос не про БД
            # fixme: Тут можно добавить генерацию ответов от ЛЛМ
            answer = "Я могу помочь только с выбором аэрогрилей и вопросами по ним"
        else:
            # Выполнение запроса к БД
            rows = execute_query(sql)
            # Формирование ответа
            answer = rows_to_answer(user_text, rows, sql)

    except Exception:
        logger.exception(f"Error processing message from user {user.id}")
        answer = "Произошла ошибка при обработке запроса"

    await update.message.reply_text(answer)

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
