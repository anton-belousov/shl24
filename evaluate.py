import json
from logging import getLogger

from llama_index.core.evaluation import CorrectnessEvaluator, EvaluationResult

from rag.app import configure_logging
from rag.llm import get_llm
from rag.llm.yandex import YandexLLM
from rag.modules import router

configure_logging()
dataset = []
logger = getLogger(__name__)

with open("tests/question-answers.jsonl", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        dataset.append(data)

logger.debug("dataset=%s", dataset)
llm: YandexLLM = get_llm()
evaluator = CorrectnessEvaluator(llm)
avg_score: float = 0

for data in dataset:
    logger.debug("> %s", data["question"])
    result: EvaluationResult = evaluator.evaluate(
        query=data["question"],
        response=router.run(data["question"]),
        reference=data["answer"],
    )
    logger.debug("result.score=%s, result.passing=%s", result.score, result.passing)
    avg_score += result.score

logger.debug("avg_score=%s", avg_score / len(dataset))
