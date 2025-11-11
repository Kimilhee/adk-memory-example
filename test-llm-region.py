import google.generativeai as genai
import time
import os

# Google Cloud 프로젝트 ID와 API 키를 환경 변수 또는 직접 설정
# on-premise 서버에서는 환경 변수로 설정하는 것이 좋습니다.
# export GOOGLE_API_KEY="YOUR_API_KEY"
# export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
# GOOGLE_CLOUD_PROJECT = velvety - being - 469807 - q2
# GOOGLE_CLOUD_LOCATION = us - central1
# AGENT_ENGINE_ID = 3022341960477179904
# AGENT_MODEL = gemini - 2.0 - flash
# SESSION_DB_URL = "sqlite:///./my_agent_data.db"
# GOOGLE_CLOUD_PROJECT = dkailens
# GOOGLE_CLOUD_LOCATION = asia - northeast3

GOOGLE_API_KEY = "AIzaSyBSOoOw8UCwuF3IGRT-8tMZHzX1QIp1ce8"
GOOGLE_CLOUD_PROJECT = "velvety-being-469807-q2"

genai.configure(
    api_key=GOOGLE_API_KEY,
    transport="rest",  # Vertex AI를 위해 REST 전송 방식을 사용합니다.
)

PROJECT_ID = GOOGLE_CLOUD_PROJECT
test_count = 10
test_regions = {
    "asia-northeast3 (Seoul)": "asia-northeast3",
    "asia-northeast1 (Tokyo)": "asia-northeast1",
    "us-central1 (Iowa)": "us-central1",
}

model_name = "gemini-1.0-pro"
prompt = "한국의 수도는?"

print("--- Vertex AI 리전 벤치마킹 시작 ---")

for region_name, location in test_regions.items():
    print(f"\n[테스트 리전]: {region_name}")

    # Vertex AI 엔드포인트 설정
    genai.configure(
        api_key=os.environ.get("GOOGLE_API_KEY"),
        transport="rest",
        client_options={"api_endpoint": f"{location}-aiplatform.googleapis.com"},
    )

    # Vertex AI 모델 초기화
    try:
        model = genai.GenerativeModel(
            model_name=f"projects/{PROJECT_ID}/locations/{location}/models/{model_name}"
        )
    except Exception as e:
        print(f"  모델 초기화 실패: {e}")
        continue

    total_time = 0
    for i in range(test_count):
        start_time = time.time()
        try:
            response = model.generate_content(prompt)
            end_time = time.time()
            total_time += end_time - start_time
            print(f"  {i+1}/{test_count} - 응답 시간: {end_time - start_time:.4f}초")
        except Exception as e:
            print(f"  {i+1}/{test_count} - 요청 실패: {e}")

    if total_time > 0:
        average_time = total_time / test_count
        print(f"  평균 응답 시간: {average_time:.4f}초")

print("\n--- 벤치마킹 완료 ---")
