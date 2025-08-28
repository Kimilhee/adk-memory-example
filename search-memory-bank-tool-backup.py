import vertexai
import os
import asyncio
from dotenv import load_dotenv
from google.adk.memory import VertexAiMemoryBankService

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


async def search_memory():
    """VertexAIMemoryBankService를 사용하여 사용자의 기억을 검색합니다."""
    try:
        # VertexAIMemoryBankService 초기화
        memory_service = VertexAiMemoryBankService(agent_engine_id=AGENT_ENGINE_ID)
        print(f"메모리 서비스가 성공적으로 초기화되었습니다.")

        # 검색 파라미터 설정
        user_id = "user"
        search_query = "나는 어디에 살아요?"  # 원래 검색어로 복원
        app_name = "memory_agent"  # 메모리 리스트에서 확인된 실제 app_name 사용

        print(f"\n🔍 검색 정보:")
        print(f"  User ID: {user_id}")
        print(f"  검색어: {search_query}")
        print(f"  Agent Engine ID: {AGENT_ENGINE_ID}")
        print(f"  App Name: {app_name}")

        # 메모리 검색 실행
        print(f"\n검색 중...")
        search_results = await memory_service.search_memory(
            query=search_query, user_id=user_id, app_name=app_name
        )

        # 검색 결과 출력
        if hasattr(search_results, "memories") and search_results.memories:
            memories = search_results.memories
            print(f"\n✅ 검색된 기억 ({len(memories)}개):")
            print("=" * 60)

            for i, memory in enumerate(memories, 1):
                print(f"\n📋 기억 {i}:")

                # 메모리의 내용 출력
                if hasattr(memory, "content") and memory.content:
                    # content.parts[0].text에서 실제 텍스트 추출
                    if hasattr(memory.content, "parts") and memory.content.parts:
                        text_content = memory.content.parts[0].text
                        print(f"  대화 내용: {text_content}")
                    else:
                        print(f"  Content: {memory.content}")
                elif hasattr(memory, "fact") and memory.fact:
                    print(f"  사실: {memory.fact}")
                else:
                    print(f"  내용: {memory}")

                # 추가 정보 출력
                if hasattr(memory, "author") and memory.author:
                    print(f"  작성자: {memory.author}")
                if hasattr(memory, "timestamp") and memory.timestamp:
                    print(f"  시간: {memory.timestamp}")
                if hasattr(memory, "score"):
                    print(f"  유사도 점수: {memory.score}")

                print("-" * 40)
        else:
            print(f"\n❌ '{search_query}'에 대한 검색 결과가 없습니다.")
            print("💡 다음과 같은 이유일 수 있습니다:")
            print("  - 해당 사용자에게 관련 정보가 저장되어 있지 않음")
            print("  - 검색어와 일치하는 내용이 없음")
            print("  - 메모리가 아직 생성되지 않음")
            print(f"  - 사용자 '{user_id}'가 존재하지 않음")

    except Exception as e:
        print(f"❌ 메모리 검색 중 오류가 발생했습니다: {e}")
        import traceback

        traceback.print_exc()


# 메인 실행 함수
async def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🧠 Memory Bank 검색 도구")
    print("=" * 60)

    await search_memory()

    print("\n" + "=" * 60)
    print("🔍 검색 완료!")
    print("\n💡 참고사항:")
    print("- search_memory()는 사용자가 입력한 대화 내용에서 검색합니다")
    print("- list_memories()는 시스템이 추출한 사실(Facts)을 보여줍니다")
    print("- 두 기능은 서로 다른 데이터를 대상으로 합니다")
    print("\n⚠️ 검색 알고리즘의 특성:")
    print("- 항상 고정된 개수(보통 3개)의 결과를 반환합니다")
    print("- 관련성이 낮은 결과도 포함될 수 있습니다")
    print("- 한국어 자연어 검색보다는 키워드 검색이 더 정확합니다")
    print("- 예: '나는 어디에 살아요?' 대신 'Incheon', 'live' 등으로 검색")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"실행 중 오류가 발생했습니다: {e}")
        import traceback

        traceback.print_exc()
