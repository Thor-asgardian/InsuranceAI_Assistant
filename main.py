from flask import Flask, request, render_template
import logging
import os

from dotenv import load_dotenv
import chatter

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
CUSTOMER_ID = os.getenv("CUSTOMER_ID", "111")
DB_NAME = os.getenv("DB_NAME", "XYZ-Corp")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8080))
MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI is missing from the .env file.")

logger.info("Connecting to MongoDB Atlas...")
conn = chatter.connect_cluster(MONGODB_URI)
logger.info("MongoDB connected successfully.")

# Verify Insurance collection
intro_context = chatter.query_db(
    conn,
    DB_NAME,
    "Insurance",
    {"type": "Intro"}
)

if intro_context is None:
    logger.warning("Insurance Intro document not found.")

# Ensure customer exists
customer = chatter.query_db(
    conn,
    DB_NAME,
    "Customer",
    {"customer_id": CUSTOMER_ID}
)

if customer is None:
    chatter.insert_record(
        conn,
        DB_NAME,
        "Customer",
        CUSTOMER_ID
    )


@app.route("/")
def homepage():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat_with_ai():
    try:
        question = request.form.get("question", "").strip()

        if not question:
            return "Please enter a valid question.", 400

        logger.info("Question: %s", question)

        # Load conversation history
        customer = chatter.query_db(
            conn,
            DB_NAME,
            "Customer",
            {"customer_id": CUSTOMER_ID}
        )

        history = customer.get("conversation", []) if customer else []

        # Claim lookup
        if len(question) == 5 and question.isdigit():
            try:
                results = chatter.search_mongoDB_claim(
                    DB_NAME,
                    "Claims",
                    conn,
                    question
                )

                claim = next(results, None)

                if claim:
                    question += (
                        f"\n\nClaim Information:\n"
                        f"Claim Number: {claim.get('claim_number')}\n"
                        f"Status: {claim.get('Claim_status')}\n"
                        f"Amount: {claim.get('Claim_amount')}"
                    )
            except Exception as e:
                logger.warning("Claim lookup failed: %s", e)

        # Knowledge Base Search
        try:
            results = chatter.search_mongoDB_chat_base(
                DB_NAME,
                "chat-search",
                conn,
                question
            )

            item = next(results, None)

            if item and item.get("Answer"):
                question += (
                    "\n\nRelevant Knowledge Base Information:\n"
                    + item["Answer"]
                )

        except Exception as e:
            logger.warning("Knowledge search failed: %s", e)

        logger.info("Sending request to Ollama...")

        response_text, conversation = chatter.chat_with_local_model(
            question,
            history
        )

        logger.info("Received response from Ollama.")

        chatter.upsert_db(
            conn,
            DB_NAME,
            "Customer",
            conversation,
            CUSTOMER_ID
        )

        return response_text

    except Exception:
        logger.exception("Chat failed")
        return (
            "The AI service is currently unavailable. "
            "Please ensure Ollama is running and try again."
        ), 500


@app.route("/health")
def health():
    return {"status": "healthy"}, 200


if __name__ == "__main__":
    app.run(
    host=HOST,
    port=PORT,
    debug=False,
    use_reloader=False
)
