#!/usr/bin/env python3
"""
Startup script for Janus Prop AI Backend

This script provides a simple way to start the backend server.
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"Starting Janus Prop AI Backend on {host}:{port}")
    print(f"Reload mode: {reload}")
    
    # Start the server
    uvicorn.run(
        "main:create_app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
