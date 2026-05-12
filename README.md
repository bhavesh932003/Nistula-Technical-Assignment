# Nistula Messaging Integration & AI Webhook

A robust, production-ready backend system designed to normalize inbound guest messages across multiple channels, classify them using the Claude-Sonnet-4-20250514 LLM, and generate context-aware drafted responses. This system utilizes strict mathematical confidence scoring to enforce property rules, legal compliance, and safety protocols.

---

## Repository Structure

- **`app/main.py`**: The FastAPI webhook application and Anthropic LLM routing logic, featuring strict mathematical confidence scoring overrides.
- **`schema.sql`**: The PostgreSQL schema for the unified messaging platform, featuring cross-channel guest identity resolution (WhatsApp, Airbnb, Booking.com).
- **`thinking.md`**: Architectural system design, emergency handling protocols, and preventative maintenance strategies.
- **`test_runner.py`**: A lightweight 10-point sanity check test suite for basic operations.
- **`bulletproof_test_runner.py`**: A comprehensive 100-point automated red-team test suite evaluating both routing logic and AI content validation across severe edge cases.
- **`test_report.md`**: An auto-generated output report demonstrating the AI's pass rate across all 100 edge cases.
- **`.gitignore`**: Security configuration to prevent secret keys (`.env`) from being exposed.

---

## Setup Instructions

1. Clone the repository and navigate into it.
2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install required dependencies:

```bash
pip install fastapi uvicorn anthropic pydantic python-dotenv requests
```

4. Configure environment variables:

Create a `.env` file in the root directory and add your Anthropic API key:

```plaintext
ANTHROPIC_API_KEY=your_api_key_here
```

5. Run the local development server:

```bash
uvicorn app.main:app --reload
```

---

## Core Architecture: Confidence Scoring & Routing

To prevent LLM hallucinations from impacting guest safety or revenue, this system abandons "sliding scale" guidelines in favor of hard mathematical overrides mapped to specific operational risks:

- **[SCORE 0.00 to 0.40] — SEVERE ESCALATION**: Hard-coded limits for medical emergencies, security threats, legal/ADA compliance requests, and prompt-injection/jailbreak attempts.
- **[SCORE 0.41 to 0.59] — POLICY REJECTIONS**: Hard-coded limits for rule violations (e.g. over-occupancy, haggling, bringing pets) and explicit complaints.
- **[SCORE 0.60 to 0.84] — AGENT REVIEW**: Applied to logistical nuances (early check-in, third-party bookings, custom concierge requests).
- **[SCORE 0.85 to 1.00] — AUTO-SEND**: Reserved strictly for standard, safe questions explicitly answered in the provided property context.

---

## Testing Guide

This project includes multiple ways to test the AI integration, ranging from manual queries to automated red-team validation.

### 1. Manual Webhook Testing (cURL / Postman)

To test a single message, you can send a POST request to the running server. The system expects a specific JSON payload matching the Pydantic schema.

**Payload format:**

```json
{
  "source": "whatsapp",
  "guest_name": "Rahul Sharma",
  "message": "Is the villa available from April 20 to 24? What is the rate for 2 adults?",
  "timestamp": "2026-05-05T10:30:00Z",
  "booking_ref": "NIS-2024-0891",
  "property_id": "villa-b1"
}
```

**Run via cURL:**

```bash
curl -X POST http://127.0.0.1:8000/webhook/message   -H "Content-Type: application/json"   -d '{
    "source": "whatsapp",
    "guest_name": "Rahul Sharma",
    "message": "Is the villa available from April 20 to 24? What is the rate for 2 adults?",
    "timestamp": "2026-05-05T10:30:00Z",
    "booking_ref": "NIS-2024-0891",
    "property_id": "villa-b1"
  }'
```

### 2. Basic Sanity Check (`test_runner.py`)

This is a lightweight, 10-point test suite designed to verify basic functionality. It tests the happy paths (standard bookings), missing Pydantic fields (422 errors), and simple escalations.

**Run:**

```bash
python test_runner.py
```

Outputs a quick console summary of passed/failed routing logic.

### 3. Red-Team Validation Suite (`bulletproof_test_runner.py`)

This is the master test engine. It fires 100 highly specific, high-risk edge cases at the webhook to stress-test the LLM's prompt bounds.

It tests the AI against two metrics simultaneously:

- **Logic Validation**: Did the AI assign the correct numeric score and route the message to the correct action (`auto_send`, `agent_review`, `escalate`)?
- **Content Validation (Keyword Assertion)**: Did the AI include the mandatory safety protocols, exact prices, or necessary apologies in the `drafted_reply` text?

**Test categories included:**

- Standard operations and logistical nuance
- Policy violations (pets, haggling, over-occupancy)
- Extreme maintenance complaints
- Physical / medical emergencies
- Security threats (break-ins, stalkers, bomb threats)
- Environmental disasters (floods, fires, earthquakes)
- Jailbreaks, prompt injections, and SQLi attempts

**Run:**

```bash
python bulletproof_test_runner.py
```

### 4. Automated Reporting (`test_report.md`)

When you run `bulletproof_test_runner.py`, it automatically generates a formatted Markdown file named `test_report.md`.

This file acts as a permanent, readable audit log. It documents:

- The exact time the test was run.
- The raw user input message.
- The expected vs. actual routing action and confidence score.
- The exact verbatim text drafted by Claude.
- The pass/fail status for both logic and content.

(View the included `test_report.md` in this repository to see the AI's 98%+ success rate against all 100 edge cases.)
