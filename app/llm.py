import logging
import time
from openai import OpenAI

from app.config import (OPENAI_API_KEY, LLM_MAX_RETRIES, LLM_RETRY_DELAY, OPENAI_MODEL_ROUTING, OPENAI_MODEL_SQL_BUILDER,
                        OPENAI_MODEL_ANSWER, OPENAI_MODEL_FREE, TEMPERATURE_ROUTING, TEMPERATURE_SQL_BUILDER,
                        TEMPERATURE_ANSWER, TEMPERATURE_FREE)
from app.prompts import SQL_SYSTEM_PROMPT, ANSWER_SYSTEM_PROMPT, ROUTER_SYSTEM_PROMPT, FREE_SYSTEM_PROMPT

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


def get_routing(user_text: str) -> str:
    logger.info("[ROUTING] Генерация развилки для обработки сообщения..")

    def _request():
        response = client.chat.completions.create(
            model=OPENAI_MODEL_ROUTING,
            messages=[
                {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Вопрос пользователя: {user_text}\n"
                },
            ],
            temperature=TEMPERATURE_ROUTING,
        )
        return response.choices[0].message.content.strip()

    answer = with_retries(_request)
    logger.info(f"[ROUTING] Выбранная развилка: {answer}")
    return answer


def user_to_sql(user_text: str) -> str | None:
    logger.info("[SQL_BUILDER] Генерация SQL для запроса пользователя")
    logger.debug(f"[SQL_BUILDER] Входной запрос: {user_text}")

    def _request():
        response = client.chat.completions.create(
            model=OPENAI_MODEL_SQL_BUILDER,
            messages=[
                {"role": "system", "content": SQL_SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            temperature=TEMPERATURE_SQL_BUILDER,
        )
        return response.choices[0].message.content.strip()

    sql = with_retries(_request)

    if sql == "NO_SQL":
        logger.info("[SQL_BUILDER] LLM решила: SQL не нужен.")
        return None

    logger.info(f"[SQL_BUILDER] Сгенерированный SQL: {sql}")
    return sql


def rows_to_answer(user_text: str, rows: list[dict], sql: str) -> str:
    logger.info("[ANSWER] Генерация ответа на основе данных из БД")
    logger.info(f"[ANSWER] Входные данные: user_text={user_text}, sql={sql}, rows={rows}")

    def _request():
        response = client.chat.completions.create(
            model=OPENAI_MODEL_ANSWER,
            messages=[
                {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Вопрос: {user_text}\n"
                               f"Был такой запрос в БД: {sql}\n"
                               f"Вернувшиеся данные из БД: {rows}",
                },
            ],
            temperature=TEMPERATURE_ANSWER,
        )
        return response.choices[0].message.content.strip()

    answer = with_retries(_request)
    logger.info(f"[ANSWER] Сгенерированный ответ: {answer}")
    return answer


def get_free_answer(user_text: str) -> str:
    logger.info("[FREE] Генерация простого ответа на сообщение..")

    def _request():
        response = client.chat.completions.create(
            model=OPENAI_MODEL_FREE,
            messages=[
                {"role": "system", "content": FREE_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Вопрос пользователя: {user_text}\n"
                },
            ],
            temperature=TEMPERATURE_FREE,
        )
        return response.choices[0].message.content.strip()

    answer = with_retries(_request)
    logger.info(f"[FREE] Ответ: {answer}")
    return answer
