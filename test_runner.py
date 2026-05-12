import requests

URL = "http://127.0.0.1:8000/webhook/message"

# The Master Test Suite
TESTS = [
    # --- HAPPY PATHS (Expected: auto_send) ---
    {
        "name": "Test 1: Pricing (Happy Path)",
        "expected_status": 200,
        "expected_action": "auto_send",
        "payload": {
            "source": "whatsapp", "guest_name": "Rahul", "booking_ref": "NIS-01", "property_id": "villa-b1", "timestamp": "2026-05-05T10:30:00Z",
            "message": "What is the total cost for 5 people for one night?"
        }
    },
    {
        "name": "Test 2: Check-in Details (Happy Path)",
        "expected_status": 200,
        "expected_action": "auto_send",
        "payload": {
            "source": "airbnb", "guest_name": "Sara", "booking_ref": "NIS-02", "property_id": "villa-b1", "timestamp": "2026-05-05T10:30:00Z",
            "message": "We are arriving tomorrow. What is the WiFi password and check-in time?"
        }
    },
    
    # --- AGENT REVIEW (Expected: agent_review) ---
    {
        "name": "Test 3: Early Check-in (Nuance Required)",
        "expected_status": 200,
        "expected_action": "agent_review",
        "payload": {
            "source": "direct", "guest_name": "Mike", "booking_ref": "NIS-03", "property_id": "villa-b1", "timestamp": "2026-05-05T10:30:00Z",
            "message": "Our flight lands at 9 AM. Can we check in early?"
        }
    },
    {
        "name": "Test 4: Chef Booking (Missing Price in Context)",
        "expected_status": 200,
        "expected_action": "agent_review",
        "payload": {
            "source": "whatsapp", "guest_name": "Priya", "booking_ref": "NIS-04", "property_id": "villa-b1", "timestamp": "2026-05-05T10:30:00Z",
            "message": "We want to book the chef for our entire stay. How much does it cost?"
        }
    },
    
    # --- ESCALATIONS & COMPLAINTS (Expected: escalate) ---
    {
        "name": "Test 5: Disguised Complaint",
        "expected_status": 200,
        "expected_action": "escalate",
        "payload": {
            "source": "whatsapp", "guest_name": "John", "booking_ref": "NIS-05", "property_id": "villa-b1", "timestamp": "2026-05-05T10:30:00Z",
            "message": "Why is the pool green and disgusting? Fix it now."
        }
    },
    {
        "name": "Test 6: Out of Bounds Info (Pets & Hospitals)",
        "expected_status": 200,
        "expected_action": "escalate",
        "payload": {
            "source": "instagram", "guest_name": "Emma", "booking_ref": "NIS-06", "property_id": "villa-b1", "timestamp": "2026-05-05T10:30:00Z",
            "message": "Do you allow pets? Also, how far is the nearest hospital?"
        }
    },
    {
        "name": "Test 7: Rule Breaking (Over Occupancy)",
        "expected_status": 200,
        "expected_action": "escalate", # Claude might score this low, or classify as special_request. Either way, it shouldn't auto_send.
        "payload": {
            "source": "booking_com", "guest_name": "Vikram", "booking_ref": "NIS-07", "property_id": "villa-b1", "timestamp": "2026-05-05T10:30:00Z",
            "message": "We have 8 people coming for a bachelor party, is that okay?"
        }
    },
    {
        "name": "Test 8: The 3 AM Emergency (Thinking Question Scenario)",
        "expected_status": 200,
        "expected_action": "escalate",
        "payload": {
            "source": "whatsapp", "guest_name": "Angry Guest", "booking_ref": "NIS-08", "property_id": "villa-b1", "timestamp": "2026-05-05T03:00:00Z",
            "message": "There is no hot water and we have guests arriving for breakfast in 4 hours. This is unacceptable. I want a refund for tonight."
        }
    },
    {
        "name": "Test 9: Gibberish Input",
        "expected_status": 200,
        "expected_action": "escalate",
        "payload": {
            "source": "whatsapp", "guest_name": "Bot", "booking_ref": "NIS-09", "property_id": "villa-b1", "timestamp": "2026-05-05T10:30:00Z",
            "message": "asdfghjkl123"
        }
    },

    # --- SYSTEM RESILIENCE ---
    {
        "name": "Test 10: Missing Fields (Pydantic Validation Check)",
        "expected_status": 422, # We EXPECT the server to throw a 422 Unprocessable Entity error
        "expected_action": "N/A",
        "payload": {
            "source": "whatsapp", 
            # "guest_name" is missing intentionally
            "booking_ref": "NIS-10", "property_id": "villa-b1", "timestamp": "2026-05-05T10:30:00Z",
            "message": "Hello?"
        }
    }
]

def run_tests():
    print("\n🚀 Starting Nistula Webhook Master Test Suite...\n" + "="*60)
    passed = 0

    for test in TESTS:
        print(f"Running {test['name']}...")
        try:
            response = requests.post(URL, json=test["payload"])
            
            # Check 1: Did we get the HTTP status we expected?
            if response.status_code != test["expected_status"]:
                print(f"❌ FAIL: Expected HTTP {test['expected_status']}, but got {response.status_code}")
                print(f"   Response: {response.text}\n")
                print("-" * 60)
                continue

            # If we expected an error (like 422) and got it, that's a PASS!
            if test["expected_status"] != 200:
                print(f"✅ PASS: Server correctly rejected invalid payload with HTTP {response.status_code}\n")
                passed += 1
                print("-" * 60)
                continue

            # Check 2: Did the AI logic output the correct action?
            data = response.json()
            actual_action = data.get("action")
            score = data.get("confidence_score")
            query_type = data.get("query_type")
            
            # Acceptable fallback for rule breaking (Test 7) could be agent_review
            acceptable_actions = [test["expected_action"]]
            if test["name"] == "Test 7: Rule Breaking (Over Occupancy)":
                acceptable_actions.append("agent_review")

            if actual_action in acceptable_actions:
                print(f"✅ PASS: Action '{actual_action}' (Score: {score}) [Type: {query_type}]")
                passed += 1
            else:
                print(f"❌ FAIL: Expected '{test['expected_action']}', but got '{actual_action}'. (Score: {score})")
            
            print(f"   Drafted Reply: {data.get('drafted_reply')}\n")
            print("-" * 60)

        except Exception as e:
            print(f"❌ FAIL: Could not connect to server. Error: {e}\n")
            print("-" * 60)

    print(f"\n🏁 Results: {passed}/{len(TESTS)} Tests Passed\n")

if __name__ == "__main__":
    run_tests()