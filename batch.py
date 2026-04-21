import anthropic
import json
import csv

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
        return None


def process_csv(input_file, output_file):
    # Read the input CSV
    with open(input_file, "r") as f:
        reader = csv.DictReader(f)
        tickets = list(reader)

    print(f"Found {len(tickets)} tickets to process...\n")

    results = []

    for ticket in tickets:
        print(f"Processing ticket {ticket['id']} from {ticket['customer_name']}...")

        analysis = analyze_ticket(ticket['message'])

        if analysis:
            # Combine original ticket data with analysis
            row = {
                "id": ticket["id"],
                "customer_name": ticket["customer_name"],
                "original_message": ticket["message"],
                "category": analysis["category"],
                "urgency": analysis["urgency"],
                "sentiment": analysis["sentiment"],
                "summary": analysis["summary"],
                "suggested_response": analysis["suggested_response"],
                "needs_human": analysis["needs_human"]
            }
            results.append(row)
            print(f"  ✓ {analysis['category']} | urgency: {analysis['urgency']} | {analysis['sentiment']}")

    # Write results to output CSV
    with open(output_file, "w", newline="") as f:
        fieldnames = ["id", "customer_name", "original_message", "category", 
                      "urgency", "sentiment", "summary", "suggested_response", "needs_human"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ Done! Results saved to {output_file}")
    print(f"Total tickets processed: {len(results)}")


# --- Run it ---
process_csv("tickets.csv", "results.csv")