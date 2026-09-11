"""FinMitra server entry point."""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment configuration
load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print("=" * 60)
    print("  FINMITRA — Your Everyday Financial Companion")
    print("  Track: SDG 1 — No Poverty")
    print(f"  Web Interface:  http://localhost:{port}/")
    print(f"  Chat API:       http://localhost:{port}/chat")
    print(f"  Interactive API Docs: http://localhost:{port}/docs")
    print("=" * 60)
    
    uvicorn.run(
        "backend.app:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
