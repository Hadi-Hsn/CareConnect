"""Test the chat API with the new structured agent architecture."""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

# Test credentials (use an existing user or create one)
LOGIN_DATA = {
    "username": "admin@aub.com",
    "password": "admin123"
}

def get_auth_token():
    """Get authentication token."""
    response = requests.post(f"{BASE_URL}/auth/login", json=LOGIN_DATA)
    if response.status_code == 200:
        return response.json()["access_token"]
    print(f"Login failed: {response.status_code} - {response.text}")
    return None

def send_chat_message(message: str, token: str, user_id: int = 1):
    """Send a chat message to the agent."""
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "messages": [
            {"role": "user", "content": message}
        ],
        "user_id": user_id
    }
    
    print(f"\n{'='*80}")
    print(f"USER: {message}")
    print('='*80)
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/agent/chat", json=payload, headers=headers)
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nASSISTANT: {data['message']['content']}")
        
        if data.get('tool_calls'):
            print(f"\n📋 Tools Called ({len(data['tool_calls'])}):")
            for tool_call in data['tool_calls']:
                print(f"  • {tool_call['name']}")
                print(f"    Args: {json.dumps(tool_call['arguments'], indent=6)}")
        
        if data.get('usage'):
            usage = data['usage']
            print(f"\n📊 Usage: {usage.get('total_tokens', 0)} tokens")
        
        print(f"⏱️  Response time: {elapsed:.2f}s")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
    
    return response

def main():
    """Run test scenarios."""
    print("🚀 Testing CareConnect Structured Agent")
    print("="*80)
    
    # Get auth token
    print("\n🔐 Authenticating...")
    token = get_auth_token()
    if not token:
        print("❌ Failed to authenticate. Please check credentials.")
        return
    print("✅ Authenticated successfully!")
    
    # Test scenarios for the structured agent
    test_scenarios = [
        # Test 1: Simple greeting (general conversation)
        "Hello!",
        
        # Test 2: Information query (RAG)
        "What are your visiting hours?",
        
        # Test 3: View appointments (query_appointments)
        "Show me my appointments",
        
        # Test 4: Book appointment with specific details (book_appointment)
        "I want to book an appointment with Cardiology tomorrow at 10am",
        
        # Test 5: Book appointment with partial info (should ask for clarification)
        "I need to see a doctor next week",
        
        # Test 6: Emergency (should respond immediately)
        "I'm having chest pain!",
        
        # Test 7: Medical advice (should refuse)
        "What medicine should I take for a headache?",
    ]
    
    print("\n\n🧪 Running Test Scenarios")
    print("="*80)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n\n### TEST {i}/{len(test_scenarios)} ###")
        send_chat_message(scenario, token)
        time.sleep(1)  # Brief pause between tests
    
    print("\n\n" + "="*80)
    print("✅ All tests completed!")
    print("="*80)

if __name__ == "__main__":
    main()
