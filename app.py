import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load .env variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Azure OpenAI Config
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Azure OpenAI client
client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

# In-memory expenses store
expenses = []

# -------------------------------
# Route: Add Expense
# -------------------------------
@app.route("/add_expense", methods=["POST"])
def add_expense():
    data = request.json
    if not data or "category" not in data or "amount" not in data:
        return jsonify({"error": "Invalid data"}), 400

    category = data["category"]
    amount = float(data["amount"])
    date = data.get("date")

    # Check if category already exists
    for expense in expenses:
        if expense["category"] == category:
            expense["amount"] += amount
            # Optionally update date to latest
            if date:
                expense["date"] = date
            return jsonify({"message": "Expense added to existing category", "expense": expense}), 201

    # If not found, create new
    expense = {
        "category": category,
        "amount": amount,
        "date": date  # optional
    }
    expenses.append(expense)
    return jsonify({"message": "Expense added", "expense": expense}), 201


# -------------------------------
# Route: Get Expenses
# -------------------------------
@app.route("/get_expenses", methods=["GET"])
def get_expenses():
    return jsonify(expenses), 200   # return as list directly


# -------------------------------
# Route: Chat with AI
# -------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are a finance assistant helping with budgeting."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=200
        )

        ai_reply = response.choices[0].message.content
        return jsonify({"reply": ai_reply}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_RUN_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_RUN_PORT", 5000))
    )
