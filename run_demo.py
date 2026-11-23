from langgraph.types import Command
from graph import app


def run_ticket(ticket: str, thread_id: str):
    cfg = {"configurable": {"thread_id": thread_id}}
    result = app.invoke({"ticket": ticket}, cfg)

    if "__interrupt__" in result:
        info = result["__interrupt__"][0].value
        print("\n--- נדרשת הכרעה אנושית ---")
        print("פנייה:", info["ticket"])
        print("ניחוש המודל:", info["model_guess"], "| ביטחון:", info["confidence"])
        print("אפשרויות:", info["options"])
        choice = input("בחרי קטגוריה: ").strip()
        result = app.invoke(Command(resume=choice), cfg)

    return result


if __name__ == "__main__":
    tickets = [
        ("t1", "I was charged twice for my order, please refund me"),
        ("t2", "The package arrived broken and I want my money back"),
    ]
    for tid, text in tickets:
        print("\n==========")
        print("Ticket:", text)
        out = run_ticket(text, tid)
        print("קטגוריה:", out["category"], "| ניסיונות:", out["attempts"])
        print(out["response"])