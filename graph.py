from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict, Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
from collections import Counter

CATEGORIES = ["billing", "shipping", "technical", "other"]
CONFIDENCE_THRESHOLD = 0.8
MAX_ATTEMPTS = 2

class Classification(BaseModel):
    category: Literal["billing", "shipping", "technical", "other"]
    confidence: float = Field(
        description="How sure you are, a number between 0 and 1"
    )


class State(TypedDict, total=False):
    ticket: str
    category: str
    confidence: float
    attempts: int
    human_decision: str
    response: str


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_retries=5, timeout=30)
classifier = llm.with_structured_output(Classification)

BASE_PROMPT = """You classify customer support tickets for an online store.
Categories:
- billing: charges, refunds, invoices, payment problems
- shipping: delivery, tracking, damaged or missing packages
- technical: website or app problems, login, errors
- other: anything else
Return the category and your confidence (0 to 1)."""

STRICT_PROMPT = BASE_PROMPT + """
Be careful: the ticket may mention more than one topic.
Choose the category of the MAIN request the customer wants resolved.
Lower your confidence if the ticket is truly ambiguous."""

PROMPT_V3 = """You classify customer support tickets for an online store.
Tickets may be in any language, may be very short, and may include pleasantries.

Categories:
- billing: charges, refunds, invoices, receipts, prices, payment problems
- shipping: delivery, tracking, shipping times and costs, damaged, lost or missing packages
- technical: website or app problems, login, errors, broken buttons or pages
- other: anything else (store information, policies, praise, suggestions, general questions)

Tie-break rules, ONLY when a ticket mentions more than one topic:
1. If money was actually charged or taken, or a refund did not arrive, choose billing, even if the website or app is also mentioned.
2. If a refund is requested because a package was lost, late or damaged, choose shipping.
3. Otherwise choose the problem the customer most needs solved.
Ignore pleasantries. Return the category and your honest confidence (0 to 1)."""


# "לפני": הניסיון הראשון והנאיבי, רק שמות הקטגוריות
MIN_PROMPT = "Classify the support ticket into one of: billing, shipping, technical, other. Return the category and your confidence (0 to 1)."

# "אחרי": פרומפט משופר, כללי הכרעה שנגזרו מהכשלים שנראו ב-traces של ה"לפני"
PROMPT_V4 = """You classify customer support tickets for an online store. Tickets may be in any language, very short, or include pleasantries (ignore them).

Categories:
- billing: money charged or taken, double charges, refunds that did not arrive, wrong card, invoice or receipt amounts and prices
- shipping: delivery, tracking, "where is it", shipping times and costs, damaged, lost or missing packages
- technical: the website or app is broken: errors, crashes, freezes, login or password problems, buttons or fields that do not work, pages that do not load
- other: store information, policies, gift wrapping, praise, suggestions, or a ticket with no clear topic at all ("help", "something is wrong")

Tie-break rules, when a ticket mentions more than one topic:
1. The customer's money was actually taken or a refund did not arrive (even to the wrong card): billing, even if the app or a late package is also mentioned.
2. A refund is requested because a package was lost, late or damaged: shipping.
3. The customer placed an order or tried to pay, the site froze, crashed or logged them out, and they are only UNSURE whether it went through (no charge is mentioned): technical. If a charge or taken money is mentioned, rule 1 applies instead: billing.
4. Short tickets with a clear topic ("refund??", "not working", "where is it", "How long does shipping take?") get that topic with normal confidence.
5. Only a ticket with NO identifiable topic at all ("help", "something is wrong with my order"): other, with LOW confidence (below 0.5).
Be honest about confidence: lower it whenever the ticket is truly ambiguous."""

def classify(state: State):
    attempts = state.get("attempts", 0)
    system = PROMPT_V4 if attempts == 0 else PROMPT_V4 + "\nBe extra careful and re-read the ticket."
    result = classifier.invoke([("system", system), ("human", state["ticket"])])
    return {
        "category": result.category,
        "confidence": result.confidence,
        "attempts": attempts + 1,
    }


def route_after_classify(state: State):
    if state["confidence"] >= CONFIDENCE_THRESHOLD:
        return "handle"
    if state["attempts"] < MAX_ATTEMPTS:
        return "classify"  # הלולאה
    return "human_review"


def human_review(state: State):
    decision = interrupt({
        "ticket": state["ticket"],
        "model_guess": state["category"],
        "confidence": state["confidence"],
        "options": CATEGORIES,
    })
    return {"category": decision, "human_decision": decision}


TEAMS = {
    "billing": "צוות חיובים",
    "shipping": "צוות משלוחים",
    "technical": "צוות תמיכה טכנית",
    "other": "שירות לקוחות כללי",
}


def handle(state: State):
    return {"response": f"הפנייה הועברה אל: {TEAMS[state['category']]}"}


builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("human_review", human_review)
builder.add_node("handle", handle)

builder.add_edge(START, "classify")
builder.add_conditional_edges(
    "classify", route_after_classify, ["classify", "human_review", "handle"]
)
builder.add_edge("human_review", "handle")
builder.add_edge("handle", END)

app = builder.compile(checkpointer=MemorySaver())