import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a helpdesk ticket routing assistant.
Given a ticket title, description, and optionally some similar past tickets as context,
return a JSON object with exactly these fields:

{
  "category": "<one of: billing, technical, hr, account, general>",
  "priority": "<one of: low, medium, high>",
  "summary": "<one sentence explaining the issue>"
}

Priority rules:
- high   → system down, data loss, security issue, urgent payment problem
- medium → something broken but has a workaround, billing question
- low    → general question, feature request, minor inconvenience

If similar past tickets are provided, use them as examples to guide your classification.
Return ONLY the JSON object. No explanation, no markdown.
"""


def build_context(similar_tickets: list) -> str:
    """
    Format similar past tickets into a readable context block for the LLM.
    """
    if not similar_tickets:
        return ""

    context = "Here are similar past tickets for reference:\n\n"
    for i, ticket in enumerate(similar_tickets, 1):
        context += f"Past ticket {i}:\n"
        context += f"  Title: {ticket.title}\n"
        context += f"  Category: {ticket.category}\n"
        context += f"  Priority: {ticket.priority}\n"
        context += f"  Summary: {ticket.ai_summary}\n\n"

    return context


def classify_ticket(title: str, description: str, similar_tickets: list = []) -> dict:
    """
    Classify a ticket using Groq.
    If similar_tickets are provided, they are injected as context (RAG).
    """
    # Build context from similar past tickets
    context = build_context(similar_tickets)

    # Combine context + current ticket into one user message
    user_message = ""
    if context:
        user_message += context
        user_message += "Now classify this new ticket using the above as context:\n\n"

    user_message += f"Title: {title}\nDescription: {description}"

    try:
        print(f"[AI Router] Classifying: {title}", flush=True)
        if similar_tickets:
            print(f"[AI Router] Using {len(similar_tickets)} similar tickets as context", flush=True)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message},
            ],
            temperature=0.1,
            max_tokens=200,
        )

        raw = response.choices[0].message.content.strip()
        print(f"[AI Router] Response: {raw}", flush=True)

        result = json.loads(raw)

        category = result.get("category", "general")
        priority = result.get("priority", "medium")
        summary  = result.get("summary", "No summary available.")

        valid_categories = {"billing", "technical", "hr", "account", "general"}
        valid_priorities = {"low", "medium", "high"}

        if category not in valid_categories:
            category = "general"
        if priority not in valid_priorities:
            priority = "medium"

        return {"category": category, "priority": priority, "ai_summary": summary}

    except json.JSONDecodeError:
        print(f"[AI Router] Failed to parse JSON: {raw}", flush=True)
        return {"category": "general", "priority": "medium", "ai_summary": "Could not classify ticket."}

    except Exception as e:
        print(f"[AI Router] ERROR: {type(e).__name__}: {e}", flush=True)
        return {"category": "general", "priority": "medium", "ai_summary": "AI classification unavailable."}

# import os
# import json
# from groq import Groq

# client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# SYSTEM_PROMPT = """
# You are a helpdesk ticket routing assistant. 
# Given a ticket title and description, return a JSON object with exactly these fields:

# {
#   "category": "<one of: billing, technical, hr, account, general>",
#   "priority": "<one of: low, medium, high>",
#   "summary": "<one sentence explaining the issue>"
# }

# Priority rules:
# - high   → system down, data loss, security issue, urgent payment problem
# - medium → something broken but has a workaround, billing question
# - low    → general question, feature request, minor inconvenience

# Return ONLY the JSON object. No explanation, no markdown.
# """


# def classify_ticket(title: str, description: str) -> dict:
#     user_message = f"Title: {title}\n\nDescription: {description}"

#     try:
#         print(f"[AI Router] Sending to Groq: {title}", flush=True)

#         response = client.chat.completions.create(
#             model="llama-3.1-8b-instant",
#             messages=[
#                 {"role": "system", "content": SYSTEM_PROMPT},
#                 {"role": "user",   "content": user_message},
#             ],
#             temperature=0.1,
#             max_tokens=200,
#         )

#         raw = response.choices[0].message.content.strip()
#         print(f"[AI Router] Groq raw response: {raw}", flush=True)

#         result = json.loads(raw)

#         category = result.get("category", "general")
#         priority = result.get("priority", "medium")
#         summary  = result.get("summary", "No summary available.")

#         valid_categories = {"billing", "technical", "hr", "account", "general"}
#         valid_priorities = {"low", "medium", "high"}

#         if category not in valid_categories:
#             category = "general"
#         if priority not in valid_priorities:
#             priority = "medium"

#         return {
#             "category": category,
#             "priority": priority,
#             "ai_summary": summary,
#         }

#     except json.JSONDecodeError:
#         print(f"[AI Router] Failed to parse JSON: {raw}", flush=True)
#         return {"category": "general", "priority": "medium", "ai_summary": "Could not classify ticket."}

#     except Exception as e:
#         print(f"[AI Router] ERROR: {type(e).__name__}: {e}", flush=True)
#         return {"category": "general", "priority": "medium", "ai_summary": "AI classification unavailable."}