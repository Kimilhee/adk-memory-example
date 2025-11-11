"""
# AI Lamp POC Agent Engine 생성

# 환경 설정.
# gcloud config list 명령으로 아래와 같이 원하는 account와 project가 설정 되어 있어야 함!
account = software@knowre.com
project = ai-lamp-poc-dev

# 설정되어 있지 않으면 아래 명령어를 순서대로 실행하면 됨.
# 로그인 & ADC 설정(표준 모드에서 권장) - 아래 둘다 브라우저 띄워주는데 해당 계정에서 승인하면 됨.
gcloud auth login
gcloud auth application-default login

# 보유 프로젝트 나열(IDs 컬럼 확인)
gcloud projects list

gcloud config list

# 기본 프로젝트로 설정
gcloud config set project <YOUR_PROJECT_ID>
gcloud config list

# 추가로 set-quota-project 도 설정함.
gcloud auth application-default set-quota-project <YOUR_PROJECT_ID>

# 그리고 원하는 세팅한 프로젝트를 환경변수에 직접 설정해줘야 함.
os.environ["GOOGLE_CLOUD_PROJECT"] = "ai-lamp-poc-dev"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

"""

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
def create_agent_engine(display_name: str, description: str = ""):
    client = genai.Client(vertexai=True)._api_client
    response = client.request(
        http_method="POST",
        path="reasoningEngines",
        request_dict={"displayName": display_name, "description": description},
    )
    # 응답 처리
    response_data = json.loads(response.body)
    print(response_data)

    name = response_data.get("name", "")
    # name 형식: 'projects/.../locations/.../reasoningEngines/{engine_id}/operations/{operation_id}'
    if "/reasoningEngines/" in name and "/operations/" in name:
        # operations 부분 제거하여 reasoning engine의 full name 생성
        full_name = name.split("/operations/")[0]
        engine_id = full_name.split("/")[-1]
        print("CREATED engine_id=", engine_id)
        print("full_name=", full_name)


def main():
    create_agent_engine(
        "ai-lamp-poc-agent-engine-dev", "AI Lamp POC Agent Engine for Dev."
    )


if __name__ == "__main__":
    main()
