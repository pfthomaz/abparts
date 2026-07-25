#!/usr/bin/env python3
"""
Test OpenAI API Key Configuration
This script tests if the OpenAI API key is working correctly.
"""

import os
import asyncio
import sys
from openai import AsyncOpenAI

async def test_openai_api():
    """Test OpenAI API key and connectivity."""
    
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        return False
    
    if not api_key.startswith('sk-'):
        print(f"❌ Invalid API key format: {api_key[:10]}...")
        print("OpenAI API keys should start with 'sk-'")
        return False
    
    print(f"✅ API key format looks correct: {api_key[:10]}...")
    
    try:
        # Initialize OpenAI client
        client = AsyncOpenAI(api_key=api_key)
        
        print("🔄 Testing OpenAI API connectivity...")
        
        # Test with a simple completion
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello, API test successful!'"}
            ],
            max_tokens=20
        )
        
        if response.choices and response.choices[0].message:
            content = response.choices[0].message.content
            print(f"✅ OpenAI API test successful!")
            print(f"Response: {content}")
            print(f"Model used: {response.model}")
            print(f"Tokens used: {response.usage.total_tokens}")
            return True
        else:
            print("❌ OpenAI API returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        
        # Provide specific error guidance
        error_str = str(e).lower()
        if "invalid api key" in error_str or "unauthorized" in error_str:
            print("💡 The API key appears to be invalid or expired")
            print("   Check your API key at https://platform.openai.com/api-keys")
        elif "insufficient_quota" in error_str or "quota" in error_str:
            print("💡 Your OpenAI account has insufficient credits")
            print("   Check your billing at https://platform.openai.com/account/billing")
        elif "rate_limit" in error_str:
            print("💡 Rate limit exceeded - try again in a moment")
        else:
            print("💡 Check OpenAI service status at https://status.openai.com/")
        
        return False
    
    finally:
        await client.close()

def main():
    """Main function."""
    print("🧪 Testing OpenAI API Configuration")
    print("===================================")
    
    # Load environment variables from .env if available
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Loaded environment variables from .env")
    except ImportError:
        print("⚠️  python-dotenv not available, using system environment")
    
    # Run the test
    success = asyncio.run(test_openai_api())
    
    if success:
        print("\n🎉 OpenAI API configuration is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ OpenAI API configuration has issues")
        print("\n🔧 To fix:")
        print("1. Get a valid API key from https://platform.openai.com/api-keys")
        print("2. Add credits to your account at https://platform.openai.com/account/billing")
        print("3. Update your .env file with: OPENAI_API_KEY=your_actual_key_here")
        print("4. Restart the AI Assistant service")
        sys.exit(1)

if __name__ == "__main__":
    main()