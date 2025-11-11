"""
Advanced usage example with error handling and context manager

This example demonstrates:
1. Using the client as a context manager
2. Error handling for various scenarios
3. Rejecting requests
4. Multiple requests
"""
from aurea_client import AureaClient
import time

# Configuration
API_URL = "http://localhost:8080"
API_KEY = "aurea-demo-api-key-12345"


def main():
    print("Advanced Aurea Client Example")
    print("=" * 50)
    
    # Use client as context manager (automatically closes connection)
    with AureaClient(base_url=API_URL, api_key=API_KEY) as client:
        
        # Example 1: Create multiple requests
        print("\n1. Creating multiple orchestration requests...")
        request_ids = []
        
        tasks = [
            {
                "description": "Generate monthly sales report",
                "params": {"month": "November", "year": 2024},
                "priority": 8
            },
            {
                "description": "Optimize database queries",
                "params": {"database": "production", "analyze": True},
                "priority": 3
            },
            {
                "description": "Deploy ML model to production",
                "params": {"model_version": "v2.1.0", "environment": "prod"},
                "priority": 10
            }
        ]
        
        for task in tasks:
            try:
                response = client.request(
                    task_description=task["description"],
                    parameters=task["params"],
                    priority=task["priority"]
                )
                request_ids.append(response["request_id"])
                print(f"   ✓ Created: {task['description']}")
                print(f"     ID: {response['request_id']}")
            except Exception as e:
                print(f"   ✗ Failed to create request: {e}")
        
        # Example 2: Check status of all requests
        print(f"\n2. Checking status of {len(request_ids)} requests...")
        for req_id in request_ids:
            try:
                status_info = client.status(req_id)
                print(f"   • {status_info['task_description'][:40]}...")
                print(f"     Status: {status_info['status']} | Priority: N/A")
            except Exception as e:
                print(f"   ✗ Failed to get status for {req_id}: {e}")
        
        # Example 3: Approve high-priority request
        if request_ids:
            print("\n3. Approving high-priority request (ML deployment)...")
            try:
                high_priority_id = request_ids[2]  # ML deployment
                approval = client.approve(
                    request_id=high_priority_id,
                    approved=True,
                    comment="Critical deployment - approved by system admin"
                )
                print(f"   ✓ Approved: {approval['message']}")
            except Exception as e:
                print(f"   ✗ Failed to approve: {e}")
        
        # Example 4: Reject low-priority request
        if len(request_ids) > 1:
            print("\n4. Rejecting low-priority request...")
            try:
                low_priority_id = request_ids[1]  # Database optimization
                rejection = client.approve(
                    request_id=low_priority_id,
                    approved=False,
                    comment="Scheduled for next maintenance window"
                )
                print(f"   ✓ Rejected: {rejection['message']}")
            except Exception as e:
                print(f"   ✗ Failed to reject: {e}")
        
        # Example 5: Error handling - Invalid request ID
        print("\n5. Demonstrating error handling...")
        try:
            invalid_id = "00000000-0000-0000-0000-000000000000"
            client.status(invalid_id)
        except Exception as e:
            print(f"   ✓ Correctly caught error for invalid ID: {type(e).__name__}")
        
        # Example 6: Error handling - Double approval attempt
        if request_ids:
            print("\n6. Attempting to approve already approved request...")
            try:
                client.approve(
                    request_id=request_ids[2],
                    approved=True,
                    comment="Trying to approve again"
                )
            except Exception as e:
                print(f"   ✓ Correctly caught error: {type(e).__name__}")
        
        # Final status summary
        print("\n" + "=" * 50)
        print("Final Status Summary:")
        print("=" * 50)
        for req_id in request_ids:
            try:
                status_info = client.status(req_id)
                print(f"\n{status_info['task_description']}")
                print(f"  Status: {status_info['status']}")
                print(f"  Created: {status_info['created_at']}")
                print(f"  Updated: {status_info['updated_at']}")
                if status_info.get('result'):
                    print(f"  Result: {status_info['result']}")
            except Exception as e:
                print(f"  Error retrieving status: {e}")
    
    print("\n✅ Advanced example completed!")


if __name__ == "__main__":
    main()
