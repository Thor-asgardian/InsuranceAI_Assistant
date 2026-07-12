import os
import logging

import ollama
import pymongo
from dotenv import load_dotenv
from pymongo.errors import PyMongoError

load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)
logger.info("Using Ollama model: %s", MODEL)

SYSTEM_PROMPT = """
You are Sara, the virtual customer support assistant for XYZ Insurance.

Guidelines:
- Answer only insurance-related questions.
- Be polite and professional.
- If claim information is supplied, explain it clearly.
- If you don't know something, say so instead of inventing information.
- Never say you are Qwen or Alibaba Cloud.
- Identify yourself as Sara when appropriate.
"""


def chat_with_local_model(question, history=None):
    """Send the conversation to Ollama and return the response."""

    if history is None:
        history = []

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    history = history[-5:]   # Keep only the last 5 exchanges

    for item in history:
        if item.get("question"):
            messages.append(
                {
                    "role": "user",
                    "content": item["question"],
                }
            )

        if item.get("response"):
            messages.append(
                {
                    "role": "assistant",
                    "content": item["response"],
                }
            )

    messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    try:
        logger.info("Messages sent: %d", len(messages))

        for i, msg in enumerate(messages):
            logger.info("%d | %s | %.80s", i, msg["role"], msg["content"])
        
        response = ollama.chat(
            model=MODEL,
            messages=messages,
        )

        answer = response["message"]["content"]

        conversation = {
            "question": question,
            "response": answer,
        }

        return answer, conversation

    except Exception as e:
        logger.exception("Ollama error: %s", e)

        return (
            "Sorry, I couldn't generate a response at the moment.",
            {
                "question": question,
                "response": "Ollama Error",
            },
        )


def connect_cluster(connection_string):
    client = pymongo.MongoClient(
        connection_string,
        serverSelectionTimeoutMS=5000,
    )

    client.admin.command("ping")
    logger.info("Connected to MongoDB Atlas")
    return client


def query_db(client, db_name, collection_name, query):
    try:
        return client[db_name][collection_name].find_one(query)
    except PyMongoError as e:
        logger.error("MongoDB query failed: %s", e)
        return None


def insert_record(client, db_name, collection_name, customer_id):
    client[db_name][collection_name].insert_one(
        {
            "customer_id": customer_id,
            "conversation": [],
        }
    )


def upsert_db(client, db_name, collection_name, conversation, customer_id):
    client[db_name][collection_name].update_one(
        {"customer_id": customer_id},
        {"$push": {"conversation": conversation}},
        upsert=True,
    )


def search_mongoDB_chat_base(db_name, collection_name, client, question):
    return client[db_name][collection_name].aggregate(
        [
            {
                "$search": {
                    "index": "default",
                    "text": {
                        "query": question,
                        "path": "question",
                    },
                }
            },
            {"$limit": 1},
        ]
    )


def search_mongoDB_claim(db_name, collection_name, client, claim_number):
    return client[db_name][collection_name].aggregate(
        [
            {
                "$search": {
                    "index": "default",
                    "text": {
                        "query": claim_number,
                        "path": "claim_number",
                    },
                }
            },
            {"$limit": 1},
        ]
    )
