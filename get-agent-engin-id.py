# pip install -U google-cloud-aiplatform google-adk
import os, json
from google import genai

# from dotenv import load_dotenv

# load_dotenv()

# PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
# LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")

# 환경변수 직접 설정
os.environ["GOOGLE_CLOUD_PROJECT"] = "ai-lamp-poc-dev"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

# GenAI SDK로 Agent Engine 생성


def get_engine_id(display_name: str):
    # 기존 Agent Engine 목록 조회
    client = genai.Client(vertexai=True)._api_client
    lst_response = client.request(
        http_method="GET", path="reasoningEngines", request_dict={}
    )
    lst = json.loads(lst_response.body)

    # 동일한 displayName 찾기
    if isinstance(lst, dict) and "reasoningEngines" in lst:
        for item in lst.get("reasoningEngines", []):
            if item.get("displayName") == display_name:
                name = item["name"]
                engine_id = name.split("/")[-1]
                print("GET engine_id=", engine_id)
                return name, engine_id

    raise ValueError(f"Could not extract engine_id from '{display_name}'.")


def main():
    full_name, engine_id = get_engine_id("ai-lamp-poc-agent-engine-dev")
    print("full_name, engine_id=", full_name, engine_id)


if __name__ == "__main__":
    main()
