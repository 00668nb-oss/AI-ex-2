# dataset.py
DATASET = [
    # --- ברורות (17) ---
    ("I was charged twice for my order", "billing"),
    ("Where is my refund? It's been two weeks", "billing"),
    ("My invoice shows the wrong amount", "billing"),
    ("My credit card was declined at checkout", "billing"),
    ("Please send me a receipt for my last purchase", "billing"),
    ("Where is my package? Tracking hasn't updated in a week", "shipping"),
    ("My order was delivered to the wrong address", "shipping"),
    ("The courier never came, delivery says attempted", "shipping"),
    ("My package is missing items", "shipping"),
    ("How long does shipping to Israel take?", "shipping"),
    ("I can't log in to my account", "technical"),
    ("The website crashes when I open the cart", "technical"),
    ("The app shows error 500 on checkout", "technical"),
    ("Password reset email never arrives", "technical"),
    ("The product page doesn't load images", "technical"),
    ("Do you have a store in Tel Aviv?", "other"),
    ("I want to suggest a new product for your catalog", "other"),

    # --- עמומות בכוונה (8) ---
    ("The package arrived broken and I want my money back", "shipping"),
    ("I paid but the website froze and I don't know if the order went through", "technical"),
    ("My order never arrived and I want to be charged nothing for it", "shipping"),
    ("The discount code didn't work and I was charged full price", "billing"),
    ("I got a refund but to the wrong card, and the package is still late", "billing"),
    ("Your app charged me and then logged me out", "billing"),
    ("Something is wrong with my order", "other"),
    ("Help", "other"),
]

NEW = [
    ("Refund me, the courier lost my package", "shipping"),
    ("My package arrived but I was charged shipping fees twice", "billing"),
    ("The site said payment failed but my bank shows the money was taken", "billing"),
    ("I can't download my invoice, the button does nothing", "technical"),
    ("The tracking page shows an error when I enter my order number", "technical"),
    ("Do you offer gift wrapping?", "other"),
    ("What is your return policy?", "other"),
    ("Thanks, the order was great!", "other"),
    ("refund??", "billing"),
    ("not working", "technical"),
    ("where is it", "shipping"),
    ("החבילה לא הגיעה כבר שבועיים", "shipping"),
    ("חויבתי פעמיים על אותה הזמנה", "billing"),
    ("האתר קורס כשאני לוחץ על תשלום", "technical"),
    ("I love your products! But the package says delivered and it's not here", "shipping"),
    ("Thanks for the quick refund. Now the app won't open", "technical"),
    ("The discount code field is greyed out and I can't type in it", "technical"),
    ("The receipt inside the box shows a different price than I paid", "billing"),
    ("My refund was approved but the money never reached my card", "billing"),
    ("The delivery was fine but the app keeps logging me out and I can't see my orders", "technical"),
]

DATASET_V2 = DATASET + NEW