import logging
import time
from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL, LLM_MAX_RETRIES, LLM_RETRY_DELAY
from app.prompts import SQL_SYSTEM_PROMPT, ANSWER_SYSTEM_PROMPT


# logger
logger = logging.getLogger(__name__)

# OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)


def with_retries(func, *args, **kwargs):
    """ Вспомогательная функция с ретраями """
    for attempt in range(1, LLM_MAX_RETRIES + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Ошибка при запросе к OpenAI (попытка {attempt}/{LLM_MAX_RETRIES}): {e}")
            if attempt < LLM_MAX_RETRIES:
                time.sleep(LLM_RETRY_DELAY)
            else:
                logger.exception("Превышено число попыток, выбрасываем исключение")
                raise


def user_to_sql(user_text: str) -> str | None:
    logger.info("Генерация SQL для запроса пользователя")
    logger.debug(f"Входной запрос: {user_text}")

    def _request():
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SQL_SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            temperature=0,
        )
        return response.choices[0].message.content.strip()

    sql = with_retries(_request)

    if sql == "NO_SQL":
        logger.info("LLM решила: SQL не нужен.")
        return None

    logger.info(f"Сгенерированный SQL: {sql}")
    return sql


def rows_to_answer(user_text: str, rows: list[dict], sql: str) -> str:
    logger.info("Генерация ответа на основе данных из БД")
    logger.debug(f"Входные данные: user_text={user_text}, sql={sql}, rows={rows}")

    def _request():
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Вопрос: {user_text}\n"
                               f"Был такой запрос в БД: {sql}\n"
                               f"Вернувшиеся данные из БД: {rows}",
                },
            ],
        )
        return response.choices[0].message.content.strip()

    answer = with_retries(_request)
    logger.info(f"Сгенерированный ответ: {answer}")
    return answer
