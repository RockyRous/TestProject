import csv
import logging
from app.llm import user_to_sql, rows_to_answer
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
]

OUTPUT_CSV = "test_results.csv"


def run_tests():
    results = []

    for question in TEST_QUESTIONS:
        logger.info(f"Running test: {question}")

        result = {
            "question": question,
            "generated_sql": "",
            "sql_result": "",
            "answer": "",
            "error": "",
        }

        try:
            sql = user_to_sql(question)
            result["generated_sql"] = sql

            rows = execute_query(sql)
            result["sql_result"] = rows

            answer = rows_to_answer(question, rows, sql)
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
