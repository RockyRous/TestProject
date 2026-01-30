import sqlite3
import logging
import time

from app.config import DB_PATH, DB_MAX_RETRIES, DB_RETRY_DELAY

logger = logging.getLogger(__name__)


def get_connection():
    for attempt in range(1, DB_MAX_RETRIES + 1):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row  # удобная работа с dict-like rows
            return conn
        except Exception as e:
            logger.warning(f"DB connection attempt {attempt}/{DB_MAX_RETRIES} failed: {e}")
            if attempt < DB_MAX_RETRIES:
                time.sleep(DB_RETRY_DELAY)
            else:
                logger.exception("Failed to connect to DB after multiple attempts")
                raise

def execute_query(sql: str, params: tuple = ()):
    logger.info(f"Executing SQL: {sql}")
    if params:
        logger.debug(f"With params: {params}")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)

        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        dict_rows = [dict(zip(columns, row)) for row in rows] if columns else []

        logger.info(f"Query returned {len(dict_rows)} rows")
        logger.debug(f"Rows: {dict_rows}")

        return dict_rows
    except Exception:
        logger.exception("SQL execution failed")
        raise
    finally:
        conn.close()

