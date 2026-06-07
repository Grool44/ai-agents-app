"""
Entry point for Railway deployment.
Installs dependencies and runs the app.
"""
import subprocess
import sys
import os

# Install dependencies
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

# Change to backend directory
os.chdir(os.path.dirname(__file__))

# Import and run the app
from main import app
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)