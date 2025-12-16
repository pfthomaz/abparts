
import os
import sys
import uuid
import json
import logging
from datetime import datetime, timedelta
import secrets

# Mock environment if needed
if not os.getenv("REDIS_URL"):
    os.environ["REDIS_URL"] = "redis://redis:6379/0"

try:
    from app.session_manager import session_manager
    from app import models
except ImportError:
    # Handle if run from root vs inside app
    sys.path.append(os.getcwd())
    from app.session_manager import session_manager
    from app import models

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_session_logic():
    print("--- Starting Session Logic Test ---")
    
    # 1. Create a dummy user ID
    user_id = uuid.uuid4()
    organization_id = uuid.uuid4()
    
    # Mock user object
    class MockUser:
        id = user_id
        username = "debug_user"
        organization_id = organization_id
        role = "admin"
        last_login = None
    
    user = MockUser()
    
    print(f"Creating session for user {user_id}...")
    # 2. Create a session
    try:
        session_token = session_manager.create_session(user, ip_address="127.0.0.1", user_agent="DebugUserAgent")
        print(f"Session created. Token: {session_token}")
    except Exception as e:
        print(f"FAILED to create session: {e}")
        return

    # 3. Verify it exists in Redis directly
    print("Verifying in Redis...")
    expected_key = f"{session_manager.session_prefix}{session_token}"
    raw_data = session_manager.redis_client.get(expected_key)
    if raw_data:
        print(f"SUCCESS: Raw Redis data found: {raw_data}")
    else:
        print(f"FAILURE: Key {expected_key} not found in Redis")
        return

    # 4. Try to retrieve active sessions
    print("Retrieving active sessions...")
    try:
        active_sessions = session_manager.get_active_sessions(user_id)
        print(f"Found {len(active_sessions)} active sessions.")
        if len(active_sessions) > 0:
            print("SUCCESS: Session retrieved correctly.")
            print(active_sessions[0])
        else:
            print("FAILURE: Session list is empty!")
            
            # Debug: List all keys
            print("DEBUG: All session keys in Redis:")
            all_keys = session_manager.redis_client.keys(f"{session_manager.session_prefix}*")
            print(all_keys)
            
            # Debug: Check type matching
            print(f"Searching for user_id: {str(user_id)} (Type: {type(str(user_id))})")
            data = json.loads(raw_data)
            stored_user_id = data.get("user_id")
            print(f"Stored user_id: {stored_user_id} (Type: {type(stored_user_id)})")
            print(f"Match? {stored_user_id == str(user_id)}")
            
    except Exception as e:
        print(f"FAILED during retrieval: {e}")

if __name__ == "__main__":
    test_session_logic()
