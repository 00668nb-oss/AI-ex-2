from dotenv import load_dotenv
load_dotenv()

import uuid
from langsmith import evaluate
from langgraph.types import Command

from graph import app, classifier, MIN_PROMPT   # שני את "graph" לשם הקובץ שלך
from dataset import DATASET_V2

DATASET_NAME = "ticket-triage-v2"
TRUTH = {t: c for t, c in DATASET_V2}


# ---------- "לפני": קריאה אחת, בלי לולאה ----------
def baseline(inputs: dict) -> dict:
    result = classifier.invoke([("system", MIN_PROMPT), ("human", inputs["ticket"])])
    return {
        "category": result.category,
        "model_category": result.category,   # מה שהמודל עצמו בחר
        "reached_human": False,
    }


# ---------- "אחרי": הגרף המלא עם העקביות ----------
def full_graph(inputs: dict) -> dict:
    ticket = inputs["ticket"]
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    out = app.invoke({"ticket": ticket}, config)
    model_category = out.get("category")     # הניחוש של המודל, לפני האדם
    reached_human = "__interrupt__" in out

    if reached_human:
        # אדם מושלם: מחזיר את התווית הנכונה
        out = app.invoke(Command(resume=TRUTH[ticket]), config)

    return {
        "category": out["category"],
        "model_category": model_category,
        "reached_human": reached_human,
    }


# ---------- מדדים ----------
def accuracy(outputs: dict, reference_outputs: dict) -> dict:
    """דיוק סופי (כולל תיקון של האדם)."""
    return {"key": "accuracy",
            "score": int(outputs["category"] == reference_outputs["category"])}


def human_rate(outputs: dict) -> dict:
    """האם הפנייה הגיעה לאדם."""
    return {"key": "reached_human", "score": int(outputs["reached_human"])}


def accuracy_auto(outputs: dict, reference_outputs: dict) -> dict:
    """דיוק רק על פניות שהמודל טיפל בהן לבד. המדד ההוגן.
    פניות שהגיעו לאדם מוחזרות בלי score, ולכן לא נכנסות לממוצע."""
    if outputs["reached_human"]:
        return {"key": "accuracy_auto", "score": None}
    return {"key": "accuracy_auto",
            "score": int(outputs["category"] == reference_outputs["category"])}


def model_accuracy(outputs: dict, reference_outputs: dict) -> dict:
    """דיוק של הניחוש הגולמי של המודל על כל 25 הפניות, בלי האדם.
    מראה כמה האדם באמת תרם."""
    return {"key": "model_accuracy",
            "score": int(outputs["model_category"] == reference_outputs["category"])}


EVALUATORS = [accuracy, human_rate, accuracy_auto, model_accuracy]


if __name__ == "__main__":
    for name, target in [
        ("before-naive-prompt", baseline),
        ("after-improved-graph", full_graph),
    ]:
        evaluate(
            target,
            data=DATASET_NAME,
            evaluators=EVALUATORS,
            experiment_prefix=name,
            max_concurrency=1,
        )