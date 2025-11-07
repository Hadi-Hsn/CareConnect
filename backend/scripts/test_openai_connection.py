"""Test OpenAI API connection and configuration."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import AsyncOpenAI
from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


async def test_openai_connection():
    """Test OpenAI API connection."""
    settings = get_settings()
    
    # Check if API key is set
    if not settings.openai_api_key or settings.openai_api_key == "":
        logger.error("❌ OpenAI API key is not set!")
        print("\n❌ ERROR: OPENAI_API_KEY is not configured in your .env file")
        print("\nPlease add the following to your .env file:")
        print("OPENAI_API_KEY=sk-your-api-key-here")
        return False
    
    # Mask API key for logging
    masked_key = f"{settings.openai_api_key[:10]}...{settings.openai_api_key[-4:]}" if len(settings.openai_api_key) > 14 else "***"
    print(f"✓ API Key found: {masked_key}")
    print(f"✓ Model: {settings.openai_model}")
    print(f"✓ Embedding Model: {settings.openai_embedding_model}")
    print()
    
    # Initialize client
    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        print("✓ OpenAI client initialized")
    except Exception as e:
        logger.error("client_init_failed", error=str(e))
        print(f"❌ Failed to initialize OpenAI client: {e}")
        return False
    
    # Test chat completion
    print("\nTesting chat completion...")
    try:
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": "Say 'Connection successful!' if you can read this."}],
            max_tokens=50
        )
        
        content = response.choices[0].message.content
        print(f"✅ Chat completion successful!")
        print(f"   Response: {content}")
        print(f"   Model used: {response.model}")
        print(f"   Tokens: {response.usage.total_tokens if response.usage else 'N/A'}")
    except Exception as e:
        logger.error("chat_completion_failed", error=str(e), error_type=type(e).__name__)
        print(f"❌ Chat completion failed: {type(e).__name__}: {e}")
        
        # Provide specific error messages
        if "authentication" in str(e).lower() or "api_key" in str(e).lower():
            print("\n⚠️  This appears to be an authentication error.")
            print("   Please check that your OPENAI_API_KEY is valid and active.")
        elif "connection" in str(e).lower() or "timeout" in str(e).lower():
            print("\n⚠️  This appears to be a network connectivity error.")
            print("   Please check your internet connection and firewall settings.")
        elif "rate_limit" in str(e).lower():
            print("\n⚠️  Rate limit exceeded.")
            print("   Please wait a moment and try again.")
        
        return False
    
    # Test embeddings
    print("\nTesting embeddings...")
    try:
        response = await client.embeddings.create(
            model=settings.openai_embedding_model,
            input="Test embedding",
            dimensions=settings.openai_embedding_dimensions
        )
        
        print(f"✅ Embeddings successful!")
        print(f"   Embedding dimensions: {len(response.data[0].embedding)}")
        print(f"   Model used: {response.model}")
    except Exception as e:
        logger.error("embedding_failed", error=str(e), error_type=type(e).__name__)
        print(f"❌ Embedding failed: {type(e).__name__}: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ All OpenAI API tests passed successfully!")
    print("="*60)
    return True


async def main():
    """Main entry point."""
    print("="*60)
    print("Testing OpenAI API Connection")
    print("="*60)
    print()
    
    success = await test_openai_connection()
    
    if not success:
        print("\n" + "="*60)
        print("❌ OpenAI API connection test failed")
        print("="*60)
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
