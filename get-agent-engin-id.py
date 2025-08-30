# pip install -U google-cloud-aiplatform google-adk
import os, json
from google import genai
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
AGENT_ENGINE_ID = os.getenv("AGENT_ENGINE_ID")


# GenAI SDK로 Agent Engine 생성
client = genai.Client(vertexai=True)._api_client
# response = client.request(
#     http_method="POST",
#     path="reasoningEngines",
#     request_dict={
#         "displayName": "My Memory App",
#         "description": "ADK + Memory Bank test",
#     },
# )
#
# 응답 처리
# response_data = json.loads(response.body)
# print(response_data)


def extract_engine_id(name: str) -> str:
    """
    name이 엔진이든 오퍼레이션이든 상관없이
    reasoningEngines/<ENGINE_ID> 바로 뒤의 ID만 추출
    """
    parts = name.split("/")
    if "reasoningEngines" in parts:
        idx = parts.index("reasoningEngines")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    raise ValueError(f"engine_id를 찾을 수 없음: {name}")


def get_or_create_engine(display_name: str, description: str = ""):
    # 1) 기존 Agent Engine 목록 조회
    lst_response = client.request(
        http_method="GET", path="reasoningEngines", request_dict={}
    )
    lst = json.loads(lst_response.body)

    # 2) 동일한 displayName 찾기
    if isinstance(lst, dict) and "reasoningEngines" in lst:
        for item in lst.get("reasoningEngines", []):
            if item.get("displayName") == display_name:
                name = item["name"]
                engine_id = name.split("/")[-1]
                print("GET engine_id=", engine_id)
                return name, engine_id

    # 3) 없으면 새로 생성
    response = client.request(
        http_method="POST",
        path="reasoningEngines",
        request_dict={"displayName": display_name, "description": description},
    )

    response_data = json.loads(response.body)
    print("POST response:", response_data)

    # 응답에서 name 추출 → 마지막 토큰이 engine_id
    # e.g. projects/.../locations/.../reasoningEngines/1234567890
    name = response_data["name"]
    engine_id = extract_engine_id(name)
    print("CREATED engine_id=", engine_id)
    return name, engine_id


def main():
    name, engine_id = get_or_create_engine("My Memory App", "ADK + Memory Bank test")
    print("name, engine_id=", name, engine_id)


if __name__ == "__main__":
    main()
