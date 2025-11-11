"""
Basic usage example for Aurea Client SDK

This example demonstrates the basic workflow:
1. Create a client with authentication
2. Submit a request
3. Check status
4. Approve the request
"""
from aurea_client import AureaClient

# Configuration
API_URL = "http://localhost:8080"
API_KEY = "aurea-demo-api-key-12345"


def main():
    # Initialize the client
    print("Initializing Aurea Client...")
    client = AureaClient(base_url=API_URL, api_key=API_KEY)
    
    try:
        # Step 1: Submit a new orchestration request
        print("\n1. Submitting a new orchestration request...")
        response = client.request(
            task_description="Analyze customer sentiment from recent reviews",
            parameters={
                "source": "product_reviews",
                "period": "last_30_days",
                "sentiment_threshold": 0.5
            },
            priority=5
        )
        
        request_id = response["request_id"]
        print(f"   ✓ Request submitted successfully!")
        print(f"   Request ID: {request_id}")
        print(f"   Status: {response['status']}")
        print(f"   Message: {response['message']}")
        
        # Step 2: Check the status of the request
        print("\n2. Checking request status...")
        status_info = client.status(request_id)
        print(f"   ✓ Status retrieved!")
        print(f"   Request ID: {status_info['request_id']}")
        print(f"   Status: {status_info['status']}")
        print(f"   Task: {status_info['task_description']}")
        print(f"   Created: {status_info['created_at']}")
        
        # Step 3: Approve the request
        print("\n3. Approving the request...")
        approval_response = client.approve(
            request_id=request_id,
            approved=True,
            comment="Approved for sentiment analysis processing"
        )
        print(f"   ✓ Request approved!")
        print(f"   Status: {approval_response['status']}")
        print(f"   Message: {approval_response['message']}")
        
        # Step 4: Check status after approval
        print("\n4. Checking updated status...")
        updated_status = client.status(request_id)
        print(f"   ✓ Updated status retrieved!")
        print(f"   Status: {updated_status['status']}")
        if updated_status['result']:
            print(f"   Result: {updated_status['result']}")
        
        print("\n✅ Example completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Clean up
        client.close()


if __name__ == "__main__":
    main()
