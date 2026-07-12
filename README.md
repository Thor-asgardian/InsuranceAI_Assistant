# Local AI Customer Service Chatbot

A customer service chatbot built with **Flask**, **MongoDB Atlas**, and **Ollama**. The application uses a locally hosted Large Language Model (LLM) through Ollama (`qwen2.5:3b`) and MongoDB Atlas Search to provide intelligent responses for insurance-related customer queries.

The chatbot acts as **Sara**, a virtual customer support representative for **XYZ-Corp**, and can assist users with policy information, claim status, and frequently asked insurance questions.

---

## Features

- Local AI inference using **Ollama**
- MongoDB Atlas integration
- Atlas Search-based knowledge retrieval
- Insurance claim lookup
- Customer conversation history stored in MongoDB
- Flask web interface
- No Google Cloud or external AI services required

---

## Project Architecture

```
Customer
     │
     ▼
Flask Web Application
     │
     ├──────────────► MongoDB Atlas
     │                  │
     │                  ├── Customer
     │                  ├── Insurance
     │                  ├── Claims
     │                  └── chat-search
     │
     ▼
Ollama (qwen2.5:3b)
     │
     ▼
AI Response
```

---

# Prerequisites

Install:

- Python 3.11+
- MongoDB Atlas Account
- Ollama

Install Ollama from:

https://ollama.com/download

---

# Install the AI Model

After installing Ollama, download the model:

```bash
ollama pull qwen2.5:3b
```

Start the Ollama server:

```bash
ollama serve
```

---

# Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd Google-Cloud-Generative-AI-Chatbot
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Configure Environment Variables

Create a `.env` file in the project root.

```env
OLLAMA_MODEL=qwen2.5:3b

MONGODB_URI=mongodb+srv://<USERNAME>:<PASSWORD>@cluster0.c9sy6ag.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0

DB_NAME=XYZ-Corp

CUSTOMER_ID=111

HOST=0.0.0.0

PORT=8080
```

---

# MongoDB Atlas Setup

Create the following collections inside the **XYZ-Corp** database.

## Customer

```json
{
    "customer_id":"111",
    "conversation":[],
    "Name":"Venkatesh Shanbhag"
}
```

---

## Insurance

```json
{
    "context":"You are Sara, a customer support representative working for XYZ-Corp. Respond only to insurance-related queries. Never fabricate claim or policy details.",
    "type":"Intro"
}
```

---

## Claims

```json
{
    "claim_number":"12345",
    "Name":"Venkatesh Shanbhag",
    "Claim_amount":10000,
    "Currency":"USD",
    "Claim_status":"In Progress",
    "customer_id":"111"
}
```

---

## Atlas Search

Create an Atlas Search index named:

```
default
```

on the **Claims** collection.

---

## chat-search Collection

Insert the following sample documents.

```json
{"question":"claim","Answer":"Please provide your 5-digit claim number."}

{"question":"status of a claim","Answer":"Please provide your 5-digit claim number."}

{"question":"Not resolved","Answer":"Would you like to speak with a customer support representative?"}

{"question":"bad experience","Answer":"Would you like to connect with customer care?"}

{"question":"Not good","Answer":"Would you like to connect with customer care?"}

{"question":"Company Policy","Answer":"XYZ-Corp provides property insurance covering hospitals, offices, apartments and shops against fire and earthquake hazards."}
```

---

# Run the Application

Start Ollama first.

```bash
ollama serve
```

Run the Flask application.

```bash
python main.py
```

Open your browser.

```
http://localhost:8080
```

---

# Example Questions

- Hello
- What insurance policies do you offer?
- How do I file a claim?
- What documents are required?
- What is covered under my policy?
- 12345
- What is the status of my claim?
- Explain company policy.
- I had a bad experience.
- I want to speak with an agent.

---

# Project Structure

```
Google-Cloud-Generative-AI-Chatbot/

│── main.py
│── chatter.py
│── requirements.txt
│── .env
│── README.md

├── templates/
│      └── index.html

├── static/

├── images/

└── __pycache__/
```

---

# Technologies Used

- Python
- Flask
- MongoDB Atlas
- Atlas Search
- Ollama
- Qwen 2.5 3B
- HTML
- CSS
- JavaScript

---

# Future Improvements

- Multi-user authentication
- Conversation summarization
- Voice interaction
- Retrieval-Augmented Generation (RAG)
- Streaming AI responses
- Docker deployment
- User feedback collection

---

# Disclaimer

This project is intended for educational and demonstration purposes only. It is not intended for production use without additional security, authentication, validation, and deployment improvements.