"""
Authentication example for Aurea Client SDK

This example demonstrates:
1. Successful authentication with valid API key
2. Failed authentication with invalid API key
3. Missing API key scenario
"""
from aurea_client import AureaClient
import requests

# Configuration
API_URL = "http://localhost:8080"
VALID_API_KEY = "aurea-demo-api-key-12345"
INVALID_API_KEY = "invalid-key-xyz"


def example_valid_auth():
    """Example with valid authentication"""
    print("\n1. Valid Authentication Example")
    print("-" * 40)
    
    try:
        client = AureaClient(base_url=API_URL, api_key=VALID_API_KEY)
        
        # Try to submit a request
        response = client.request(
            task_description="Test task with valid auth",
            parameters={"test": True}
        )
        
        print(f"   ✓ Authentication successful!")
        print(f"   ✓ Request created: {response['request_id']}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        return False


def example_invalid_auth():
    """Example with invalid authentication"""
    print("\n2. Invalid Authentication Example")
    print("-" * 40)
    
    try:
        client = AureaClient(base_url=API_URL, api_key=INVALID_API_KEY)
        
        # Try to submit a request
        response = client.request(
            task_description="Test task with invalid auth",
            parameters={"test": True}
        )
        
        print(f"   ✗ Should have failed but didn't!")
        client.close()
        return False
        
    except requests.HTTPError as e:
        if e.response.status_code == 401:
            print(f"   ✓ Correctly rejected with 401 Unauthorized")
            print(f"   ✓ Error message: {e.response.json().get('detail', 'N/A')}")
            return True
        else:
            print(f"   ✗ Unexpected HTTP error: {e}")
            return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        return False


def example_no_auth():
    """Example with missing authentication"""
    print("\n3. Missing Authentication Example")
    print("-" * 40)
    
    try:
        client = AureaClient(base_url=API_URL, api_key="")
        
        # Try to submit a request
        response = client.request(
            task_description="Test task with no auth",
            parameters={"test": True}
        )
        
        print(f"   ✗ Should have failed but didn't!")
        client.close()
        return False
        
    except requests.HTTPError as e:
        if e.response.status_code == 401:
            print(f"   ✓ Correctly rejected with 401 Unauthorized")
            print(f"   ✓ Error message: {e.response.json().get('detail', 'N/A')}")
            return True
        else:
            print(f"   ✗ Unexpected HTTP error: {e}")
            return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        return False


def example_custom_headers():
    """Example showing custom header authentication"""
    print("\n4. Custom Headers Example")
    print("-" * 40)
    
    try:
        # Direct API call with custom headers
        headers = {
            "X-API-Key": VALID_API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{API_URL}/request",
            json={
                "task_description": "Direct API call with headers",
                "parameters": {"direct": True},
                "priority": 1
            },
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        print(f"   ✓ Direct API call successful!")
        print(f"   ✓ Request created: {data['request_id']}")
        print(f"   ✓ Headers used: X-API-Key = {VALID_API_KEY[:10]}...")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def main():
    print("=" * 50)
    print("Aurea Client SDK - Authentication Examples")
    print("=" * 50)
    
    results = []
    
    # Run all examples
    results.append(("Valid Auth", example_valid_auth()))
    results.append(("Invalid Auth", example_invalid_auth()))
    results.append(("No Auth", example_no_auth()))
    results.append(("Custom Headers", example_custom_headers()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Summary:")
    print("=" * 50)
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n✅ All authentication examples completed successfully!")
    else:
        print("\n⚠️  Some examples failed. Review the output above.")


if __name__ == "__main__":
    main()
