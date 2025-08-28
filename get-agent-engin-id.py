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
    # response = client.request(
    #     http_method="POST",
    #     path="reasoningEngines",
    #     request_dict={"displayName": display_name, "description": description},
    # )

    # response_data = json.loads(response.body)
    # print(response_data)
    # ... 처리 로직
    # return name, engine_id
    return "test", AGENT_ENGINE_ID


def main():
    name, engine_id = get_or_create_engine("My Memory App", "ADK + Memory Bank test")
    print("name, engine_id=", name, engine_id)


if __name__ == "__main__":
    main()
