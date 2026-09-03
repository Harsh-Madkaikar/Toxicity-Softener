import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "nlp"))
from pipeline import analyze_message

for s in [
    "Thank you for your help, this is amazing!",
    "I really like your idea.",
    "I disagree with your conclusion, but let's review the evidence.",
    "Your idea is stupid.",
    "You are an idiot.",
    "Stop wasting everyone's time.",
    "This proposal needs more work.",
]:
    print(analyze_message(s))
