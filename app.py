import anthropic
import json
import csv
import streamlit as st
from collections import Counter
import io

import os
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

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
        return json.loads(clean)
    except json.JSONDecodeError:
        return None


# --- Page config ---
st.set_page_config(page_title="Support Ticket Analyzer", page_icon="🎫", layout="wide")

st.title("🎫 AI Support Ticket Analyzer")
st.markdown("Powered by Claude AI — analyze, categorize, and prioritize support tickets instantly.")

# --- Tabs ---
tab1, tab2 = st.tabs(["Single Ticket", "Batch Upload"])


# ---- TAB 1: Single Ticket ----
with tab1:
    st.subheader("Analyze a Single Ticket")

    ticket_input = st.text_area("Paste customer message here:", height=150,
                                 placeholder="e.g. I've been charged twice and no one is helping me!")

    if st.button("Analyze Ticket", type="primary"):
        if ticket_input.strip() == "":
            st.warning("Please enter a ticket message first.")
        else:
            with st.spinner("Analyzing..."):
                result = analyze_ticket(ticket_input)

            if result:
                st.success("Analysis Complete!")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Category", result["category"].upper())
                with col2:
                    st.metric("Urgency", f"{result['urgency']} / 10")
                with col3:
                    st.metric("Sentiment", result["sentiment"].capitalize())

                st.markdown(f"**📝 Summary:** {result['summary']}")
                st.markdown(f"**💬 Suggested Response:**")
                st.info(result["suggested_response"])

                if result["needs_human"]:
                    st.error("🚨 This ticket needs human escalation")
                else:
                    st.success("✅ This ticket can be handled automatically")


# ---- TAB 2: Batch Upload ----
with tab2:
    st.subheader("Upload a CSV File")
    st.markdown("CSV must have columns: `id`, `customer_name`, `message`")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file and st.button("Process All Tickets", type="primary"):
        reader = csv.DictReader(io.StringIO(uploaded_file.getvalue().decode("utf-8")))
        tickets = list(reader)

        st.info(f"Found {len(tickets)} tickets. Processing...")

        results = []
        progress = st.progress(0)

        for i, ticket in enumerate(tickets):
            analysis = analyze_ticket(ticket["message"])
            if analysis:
                results.append({
                    "id": ticket["id"],
                    "customer_name": ticket["customer_name"],
                    "original_message": ticket["message"],
                    "category": analysis["category"],
                    "urgency": analysis["urgency"],
                    "sentiment": analysis["sentiment"],
                    "summary": analysis["summary"],
                    "suggested_response": analysis["suggested_response"],
                    "needs_human": analysis["needs_human"]
                })
            progress.progress((i + 1) / len(tickets))

        st.success(f"✅ Done! Processed {len(results)} tickets")

        # --- Summary Report ---
        st.subheader("📊 Summary Report")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tickets", len(results))
        with col2:
            avg_urgency = sum(int(r["urgency"]) for r in results) / len(results)
            st.metric("Avg Urgency", f"{avg_urgency:.1f} / 10")
        with col3:
            needs_human = sum(1 for r in results if str(r["needs_human"]).lower() == "true")
            st.metric("Needs Escalation", needs_human)

        categories = Counter(r["category"] for r in results)
        st.markdown("**Tickets by Category:**")
        for cat, count in categories.most_common():
            st.markdown(f"- {cat}: {count} tickets")

        # --- Results Table ---
        st.subheader("📋 Full Results")
        st.dataframe(results)

        # --- Download Button ---
        output = io.StringIO()
        fieldnames = ["id", "customer_name", "original_message", "category",
                      "urgency", "sentiment", "summary", "suggested_response", "needs_human"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

        st.download_button(
            label="⬇️ Download Results as CSV",
            data=output.getvalue(),
            file_name="results.csv",
            mime="text/csv"
        )