from dotenv import load_dotenv
load_dotenv()

from langsmith import Client
from dataset import DATASET_V2

client = Client()
NAME = "ticket-triage-v2"

if client.has_dataset(dataset_name=NAME):
    print("הדאטהסט כבר קיים, מדלגים")
else:
    ds = client.create_dataset(NAME, description="Support tickets with correct category")
    client.create_examples(
        dataset_id=ds.id,
        examples=[
            {"inputs": {"ticket": t}, "outputs": {"category": c}}
            for t, c in DATASET_V2
        ],
    )
    print(f"הועלו {len(DATASET_V2)} פניות")