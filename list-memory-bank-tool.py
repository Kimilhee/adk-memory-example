import vertexai
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
AGENT_ENGINE_ID = os.getenv("AGENT_ENGINE_ID")

# Vertex AI 클라이언트 초기화
client = vertexai.Client(project=PROJECT_ID, location=LOCATION)

# Agent Engine 인스턴스 이름 구성
agent_engine_name = (
    f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{AGENT_ENGINE_ID}"
)

print(f"'{AGENT_ENGINE_ID}' Agent Engine에서 'user'의 기억을 조회합니다.")

# Agent Engine의 메모리 조회
try:
    memories = client.agent_engines.list_memories(name=agent_engine_name)
except Exception as e:
    print(f"❌ 메모리 조회 실패: {e}")
    memories = []

# 조회된 기억 출력
memory_found = False
try:
    for memory in memories:
        memory_found = True
        print("------------------------------------")
        print(f"Memory Name: {getattr(memory, 'name', 'N/A')}")

        # 메모리 내용 출력
        if hasattr(memory, "fact") and memory.fact:
            print(f"Fact: {memory.fact}")

        if hasattr(memory, "scope") and memory.scope:
            print(f"Scope: {memory.scope}")

        if hasattr(memory, "create_time") and memory.create_time:
            print(f"Create Time: {memory.create_time}")

except Exception as e:
    print(f"❌ 메모리 순회 중 오류: {e}")

if not memory_found:
    print("해당 사용자에 대해 저장된 기억이 없습니다.")
