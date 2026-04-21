import csv
from collections import Counter

def generate_report(results_file):
    # Read the results CSV
    with open(results_file, "r") as f:
        reader = csv.DictReader(f)
        tickets = list(reader)

    total = len(tickets)

    # Count categories
    categories = Counter(t["category"] for t in tickets)

    # Count sentiments
    sentiments = Counter(t["sentiment"] for t in tickets)

    # Count how many need human
    needs_human = sum(1 for t in tickets if t["needs_human"].strip().lower() == "true")

    # Calculate average urgency
    urgencies = [int(t["urgency"]) for t in tickets]
    avg_urgency = sum(urgencies) / len(urgencies)

    # Find highest urgency tickets
    high_urgency = [t for t in tickets if int(t["urgency"]) >= 8]

    # Print the report
    print("=" * 50)
    print("       SUPPORT TICKET SUMMARY REPORT")
    print("=" * 50)

    print(f"\n📊 OVERVIEW")
    print(f"  Total tickets processed: {total}")
    print(f"  Average urgency score:   {avg_urgency:.1f} / 10")
    print(f"  Needs human escalation:  {needs_human} of {total} tickets")

    print(f"\n📁 TICKETS BY CATEGORY")
    for category, count in categories.most_common():
        percentage = (count / total) * 100
        print(f"  {category:<12} {count} tickets  ({percentage:.0f}%)")

    print(f"\n😊 TICKETS BY SENTIMENT")
    for sentiment, count in sentiments.most_common():
        percentage = (count / total) * 100
        print(f"  {sentiment:<12} {count} tickets  ({percentage:.0f}%)")

    print(f"\n🚨 HIGH URGENCY TICKETS (8+)")
    for t in high_urgency:
        print(f"  [{t['urgency']}] {t['customer_name']}: {t['summary']}")

    print(f"\n👤 NEEDS HUMAN ESCALATION")
    for t in tickets:
        if t["needs_human"].strip().lower() == "true":
            print(f"  {t['customer_name']} — {t['category']} — urgency {t['urgency']}")

    print("\n" + "=" * 50)
    print("END OF REPORT")
    print("=" * 50)


# --- Run it ---
generate_report("results.csv")