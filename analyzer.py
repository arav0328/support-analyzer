import anthropic
import json

client = anthropic.Anthropic()

def analyze_ticket(ticket_text):
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        temperature=0.0,
        system="""You are a customer support AI assistant.

Respond ONLY with valid JSON in exactly this format, no other text:
{
  "category": "billing, technical, account, general, or refund",
  "urgency": 8,
  "sentiment": "frustrated, neutral, or happy",
  "summary": "one sentence description of the issue",
  "suggested_response": "a professional response to the customer",
  "needs_human": true
}""",
        messages=[
            {"role": "user", "content": f"Analyze this support ticket: {ticket_text}"}
        ]
    )

    raw = response.content[0].text

    try:
        clean = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(clean)
        return parsed
    except json.JSONDecodeError:
        print("Error: Claude didn't return valid JSON")
        print("Raw response:", raw)
        return None


# --- Test tickets ---
tickets = [
    "I've been charged twice this month and no one is helping me!!",
    "Hey just wondering how I change my email address on my account?",
    "Your app keeps crashing every time I try to upload a file. Very frustrating."
]

for i, ticket in enumerate(tickets):
    print(f"\n--- Ticket {i+1} ---")
    print(f"Message: {ticket}")
    print("Analysis:")

    result = analyze_ticket(ticket)

    if result:
        for key, value in result.items():
            print(f"  {key}: {value}")