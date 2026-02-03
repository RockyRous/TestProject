import csv
import logging
from app.llm import user_to_sql, rows_to_answer, get_routing, get_free_answer
from app.db import execute_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEST_QUESTIONS = [
    "Какие модели имеют 2 ТЭНа?",
    "Показать аэрогрили объемом больше 10 литров",
    "В каких моделях есть программа для йогурта?",
    "Что входит в комплектацию модели DK-1416?",
    "Сравните мощность моделей темно-серого цвета",
    "Какая сегодня погода?",  # Вопрос не по теме
    "Привет",
    "что лучше 2200 или 2400",
    "Что такое sanders?",
    "Какие есть модели?",
    "Что лучше DK-2400 или DK-2200",
    "Какая модель подойдет на большую семью?",
    "Как называется 1416",
    "Кто ты?",
    "С чем ты работаешь?",
]

OUTPUT_CSV = "test_results.csv"


def run_tests():
    results = []

    for question in TEST_QUESTIONS:
        logger.info(f"Running test: {question}")

        result = {
            "question": question,
            "routing": "",
            "generated_sql": "",
            "sql_result": "",
            "answer": "",
            "error": "",
        }

        try:
            routing = get_routing(question)
            result["routing"] = routing

            if routing == "SQL":
                # Генерация SQL
                sql = user_to_sql(question)
                result["generated_sql"] = sql
                # Выполнение запроса к БД
                rows = execute_query(sql)
                result["sql_result"] = rows
                # Формирование ответа
                answer = rows_to_answer(question, rows, sql)
            else:  # routing == "FREE"
                answer = get_free_answer(question)
            result["answer"] = answer

        except Exception as e:
            logger.exception("Test failed")
            result["error"] = str(e)

        results.append(result)

    write_results(results)


def write_results(results):
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "question",
                "routing",
                "generated_sql",
                "sql_result",
                "answer",
                "error",
            ],
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Test results saved to {OUTPUT_CSV}")
    print(f"✅ Total tests: {len(results)}")


if __name__ == "__main__":
    run_tests()
