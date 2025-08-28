import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

# .env 파일 로드
load_dotenv()


AGENT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "agents"
)  # agents 디렉토리 위치
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
SESSION_DB_URL = os.getenv("SESSION_DB_URL")
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
AGENT_ENGINE_ID = os.getenv("AGENT_ENGINE_ID")
MEMORY_SERVICE_URI = f"agentengine://projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ENGINE_ID}"

print(f"AGENT_DIR: {AGENT_DIR}")
print(f"SESSION_DB_URL: {SESSION_DB_URL}")

# Call the function to get the FastAPI app instance
# Ensure the agent directory name ('capital_agent') matches your agent folder
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_DB_URL,
    memory_service_uri=MEMORY_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=True,  # True주면 UI까지 제공, False는 단순 api만 제공
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
