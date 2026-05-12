# Nistula Messaging Integration

A webhook-based backend system to normalize inbound guest messages, classify them using Claude LLM, and generate context-aware drafted responses with confidence scoring.

## Tech Stack
* Python 3.10+
* FastAPI
* Uvicorn
* Anthropic Python SDK

## Setup Instructions
1. Clone the repository and navigate into it.
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment: 
   * Windows: `venv\Scripts\activate`
   * Mac/Linux: `source venv/bin/activate`
4. Install requirements: `pip install fastapi uvicorn anthropic pydantic python-dotenv`
5. Copy `.env.example` to `.env` and add your Anthropic API key.
6. Run the server: `uvicorn app.main:app --reload`
7. Send a POST request to `http://localhost:8000/webhook/message`

## Confidence Scoring Logic
The confidence score (0.0 to 1.0) dictates whether a message is auto-sent, queued for review, or escalated. The logic is delegated to the LLM via prompt engineering, strictly bound by these rules:
1. **Context Matching (0.85 - 1.0):** If the guest's question is explicitly answered by the provided property context (e.g., standard pricing, availability, check-in times), the score is high.
2. **Partial/Ambiguous Context (0.60 - 0.84):** If the query asks for something vaguely covered, or combines a standard question with a minor special request (e.g., "Can I check in early?"), the score drops into the human-review tier.
3. **Escalation & Constraints (0.0 - 0.59):** 
   * Any query classified as a `complaint` is hard-capped at a maximum score of `0.59` to guarantee an `escalate` action. 
   * Severe issues, requests outside the property's capability, or completely unrelated inquiries also default to this tier.