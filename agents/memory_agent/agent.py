import sys
import os
from google.adk.agents import Agent
from google.adk.tools import load_memory  # Tool to query memory
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from typing import Optional
from google.genai import types
from google.adk.planners import BuiltInPlanner

# uv run adk web agents 로 실행했을 때, shared를 찾지 못하는 문제 해결위해 추가. (uv run main.py 실행했을 때는 path지정 안해도 shared 잘 찾음)
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from shared.constants import MODEL_GEMINI_2_0_FLASH

# adk web agents 실행시 LLM 호출을 위해 adk runtime이 알아서 .env 파일에 GOOGLE_API_KEY 추가함.


def my_before_model_logic(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    model_call_count = callback_context.state.get("user:model_call_count", 0)
    callback_context.state["user:model_call_count"] = model_call_count + 1
    callback_context.state["model_call_count"] = model_call_count + 1
    print(f"user:Model call count: {model_call_count}")
    return None


def get_memory_service(invocation_ctx):
    """
    다양한 경로로 메모리 서비스에 접근을 시도하는 함수
    """
    memory_service = None

    # 방법 1: invocation_context에서 직접 접근
    if hasattr(invocation_ctx, "memory_service"):
        memory_service = invocation_ctx.memory_service
        print("✅ invocation_context.memory_service로 접근 성공")
        return memory_service

    # 방법 2: runner를 통한 접근
    if hasattr(invocation_ctx, "runner") and hasattr(
        invocation_ctx.runner, "memory_service"
    ):
        memory_service = invocation_ctx.runner.memory_service
        print("✅ runner.memory_service로 접근 성공")
        return memory_service

    # 방법 3: adk web 환경에서의 특별한 접근 방법
    if hasattr(invocation_ctx, "app_context") and hasattr(
        invocation_ctx.app_context, "memory_service"
    ):
        memory_service = invocation_ctx.app_context.memory_service
        print("✅ app_context.memory_service로 접근 성공")
        return memory_service

    # 방법 4: global context 확인
    if hasattr(invocation_ctx, "services") and hasattr(
        invocation_ctx.services, "memory_service"
    ):
        memory_service = invocation_ctx.services.memory_service
        print("✅ services.memory_service로 접근 성공")
        return memory_service

    # 메모리 서비스를 찾지 못한 경우
    print("⚠️ 모든 경로에서 memory_service를 찾을 수 없습니다.")
    print(
        f"🔍 InvocationContext 상세 속성: {[attr for attr in dir(invocation_ctx) if not attr.startswith('__')]}"
    )
    return None


async def save_memory(callback_context: CallbackContext, llm_response: LlmResponse):
    """
    메모리 저장 콜백 함수
    ADK web 환경에서 메모리 서비스에 접근하여 세션을 저장합니다.
    """
    print(f"💾 메모리 저장 콜백 호출됨. load_memory")

    try:
        # 세션 정보 가져오기
        session = callback_context._invocation_context.session
        print(f"📝 세션 정보: user_id={session.user_id if session else 'None'}")

        if not session:
            raise Exception("세션이 None입니다. 메모리 저장 실패.")
        # 콜백 컨텍스트의 모든 속성 탐색
        invocation_ctx = callback_context._invocation_context
        # print(
        #     f"🔍 InvocationContext 속성들: {[attr for attr in dir(invocation_ctx) if not attr.startswith('_')]}"
        # )

        # 메모리 서비스 가져오기
        memory_service = get_memory_service(invocation_ctx)

        # 메모리 서비스가 있으면 세션 저장
        if memory_service:
            print(f"🔧 Memory service 타입: {type(memory_service)}")
            await memory_service.add_session_to_memory(session)
            print("✅ 세션이 메모리에 성공적으로 저장되었습니다.")
        else:
            raise Exception("memory_service이 None입니다. 메모리 저장 실패.")

    except Exception as e:
        print(f"❌ 메모리 저장 중 오류: {e}")
        import traceback

        traceback.print_exc()

    return None


# @title Define the Memory Agent
# Use one of the model constants defined earlier

memory_agent = Agent(
    name="memory_agent_v1",
    model="gemini-2.5-flash",
    description="Helpful assistant that can answer questions and use memory.",
    instruction="When user asks about previous conversations, you will answer from memory context. "
    "Use the load_memory or preload_memory tool to search for relevant information from past conversations."
    "**'load_memory 또는 preload_memory로 불러온 기억이 영어일지라도 한국어로 재서술하여 사용해!'**"
    "모든 답변은 한글로 해줘.",
    tools=[PreloadMemoryTool()],
    # tools=[PreloadMemoryTool()],
    before_model_callback=my_before_model_logic,
    # 메모리 저장 옵션:
    # 1. 콜백으로 자동 저장하려면 아래 주석 해제
    after_model_callback=save_memory,
    # 2. 수동 저장은 Runner 수준에서 처리 (현재 main.py 방식)
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            thinking_budget=0,
            include_thoughts=False,
        )
    ),
)

print(f"Agent '{memory_agent.name}' created using model '{memory_agent.model}'.")

root_agent = memory_agent
