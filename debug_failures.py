from dotenv import load_dotenv
load_dotenv()

from graph import classifier, BASE_PROMPT  # שני את "graph" לשם הקובץ שבו נמצא הגרף שלך
from dataset import DATASET

for ticket, truth in DATASET:
    try:
        r = classifier.invoke([("system", BASE_PROMPT), ("human", ticket)])
        print(f"OK   {r.category:10} {r.confidence:.2f}  {ticket[:50]}")
    except Exception as e:
        print(f"FAIL {ticket[:50]}\n     {type(e).__name__}: {e}")