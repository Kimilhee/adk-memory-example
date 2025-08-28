# @title Import necessary libraries
import os, json
import asyncio
from dotenv import load_dotenv

# from google.adk.models.lite_llm import LiteLlm  # For multi-model support
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types  # For creating message Content/Parts

from google.adk.sessions import DatabaseSessionService
from google.adk.memory import VertexAiMemoryBankService

from agents.memory_agent.agent import memory_agent

import warnings
import logging

# Ignore all warnings
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)

# Load environment variables from .env file (if present)
load_dotenv()

# @title Define Agent Interaction Function

from google import genai
import os

# os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE"
# os.environ["GOOGLE_API_KEY"] = "YOUR_EXPRESS_API_KEY"

api = genai.Client(vertexai=True)._api_client


def as_json(resp):
    print(f"as_json input type: {type(resp)}")
    print(f"as_json input: {resp}")

    if hasattr(resp, "json"):
        result = resp.json()
        print(f"Using .json() method, result: {result},{type(result)}")
        result = json.loads(result)
        print(f"@@@Using .json() method, result: {result},{type(result)}")
        # body 필드가 있으면 body 안의 JSON을 파싱
        if result["body"]:
            print(f"@@@body: {result["body"]}")
            try:
                body_data = json.loads(result["body"])
                print(f"Parsed body data: {body_data}")
                return body_data
            except json.JSONDecodeError as e:
                print(f"Failed to parse body JSON: {e}")
                return result
        return result
    elif hasattr(resp, "content"):
        result = json.loads(resp.content)
        print(f"Using .content, result: {result}")
        return result
    else:
        print(f"Response type: {type(resp)}")
        print(f"Response attributes: {dir(resp)}")
        raise ValueError("Response is not a valid JSON object")


def get_or_create_engine(display_name: str, description: str = ""):
    request_dict = {"displayName": display_name, "description": description}
    # 1) 목록 조회로 같은 displayName이 있는지 확인
    lst = as_json(
        api.request(http_method="GET", path="reasoningEngines", request_dict={})
    )

    # lst가 딕셔너리이고 reasoningEngines가 있는지 확인
    if isinstance(lst, dict) and "reasoningEngines" in lst:
        for item in lst.get("reasoningEngines", []):
            if item.get("displayName") == display_name:
                name = item["name"]
                rid = name.split("/")[-1]
                return name, rid
    else:
        print(f"Warning: No reasoningEngines found in response: {lst}")

    # 2) 없으면 생성
    resp = as_json(
        api.request(
            http_method="POST",
            path="reasoningEngines",
            request_dict=request_dict,
        )
    )

    # POST 응답은 operation이므로 operation ID를 추출
    if "name" in resp and "operations" in resp["name"]:
        operation_name = resp["name"]
        print(f"Created operation: {operation_name}")

        # operation이 완료될 때까지 기다리기
        # 여기서는 간단히 operation ID만 반환하거나,
        # 실제로는 operation 완료를 기다려야 함
        return operation_name, "operation_pending"

    # 예상치 못한 응답
    print(f"Unexpected POST response: {resp}")
    return None, None


async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")

    # Prepare the user's message in ADK format
    content = types.Content(role="user", parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."  # Default

    # Key Concept: run_async executes the agent logic and yields Events.
    # We iterate through events to find the final answer.
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        # You can uncomment the line below to see *all* events during execution
        # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

        # Key Concept: is_final_response() marks the concluding message for the turn.
        if event.is_final_response():
            if event.content and event.content.parts:
                # Assuming text response in the first part
                final_response_text = event.content.parts[0].text
            elif (
                event.actions and event.actions.escalate
            ):  # Handle potential errors/escalations
                final_response_text = (
                    f"Agent escalated: {event.error_message or 'No specific message.'}"
                )
            # Add more checks here if needed (e.g., specific error codes)
            break  # Stop processing events once the final response is found

    print(f"<<< Agent Response: {final_response_text}")


async def main():
    # @title Setup Session Service and Runner

    # --- Session Management ---
    # Key Concept: SessionService stores conversation history & state.
    # InMemorySessionService is simple, non-persistent storage for this tutorial.
    # session_service = InMemorySessionService()
    db_url = "sqlite:///./my_agent_data.db"
    session_service = DatabaseSessionService(db_url=db_url)

    # Define constants for identifying the interaction context
    APP_NAME = "weather_tutorial_app"
    USER_ID = "user_1"
    # SESSION_ID = "session_001"  # Using a fixed ID for simplicity

    # Create the specific session where the conversation will happen
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
    SESSION_ID = session.id
    print(
        f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'"
    )
    # --- Runner ---
    # Key Concept: Runner orchestrates the agent execution loop.
    runner = Runner(
        agent=memory_agent,  # The agent we want to run
        app_name=APP_NAME,  # Associates runs with our app
        session_service=session_service,  # Uses our session manager
    )
    print(f"Runner created for agent '{runner.agent.name}'.")
    # @title Run the Initial Conversation

    # We need an async function to await our interaction helper
    async def run_conversation():
        await call_agent_async(
            # "What is the weather like in London?",
            "서울에서 부산까지의 거리는 대략 몇 km인가요?",
            runner=runner,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )

        # await call_agent_async(
        #     "How about Paris?", runner=runner, user_id=USER_ID, session_id=SESSION_ID
        # )  # Expecting the tool's error message

        # await call_agent_async(
        #     "Tell me the weather in New York",
        #     runner=runner,
        #     user_id=USER_ID,
        #     session_id=SESSION_ID,
        # )

    # Execute the conversation using await in an async context (like Colab/Jupyter)
    await run_conversation()


async def main_memory():
    db_url = "sqlite:///./my_agent_data.db"
    session_service = DatabaseSessionService(db_url=db_url)

    APP_NAME, APP_ID = get_or_create_engine("My Memory App", "ADK + Memory Bank test")
    print(f"APP_NAME, APP_ID: {APP_NAME}, {APP_ID}")
    USER_ID = "user_1"
    # SESSION_ID = "session_001"  # Using a fixed ID for simplicity

    # Define constants for identifying the interaction context
    # 메모리 서비스 생성 시 디버그 정보 추가
    print(f"🔧 Creating VertexAiMemoryBankService with agent_engine_id: {APP_ID}")
    memory_service = VertexAiMemoryBankService(agent_engine_id=APP_ID)
    print("✅ VertexAiMemoryBankService created successfully")

    # 메모리 서비스 직접 테스트
    try:
        print("🧪 Testing memory service directly...")
        # 빈 쿼리로 테스트
        test_result = await memory_service.search_memory("test query", USER_ID)
        print(f"🧪 Memory search test result: {test_result}")
    except Exception as e:
        print(f"❌ Memory service test failed: {e}")

    # 메모리 추가 후 확인
    # Generate a memory from that session so the Agent can remember relevant details about the user
    # Create the specific session where the conversation will happen
    session = await session_service.create_session(app_name=APP_ID, user_id=USER_ID)
    SESSION_ID = session.id
    print(
        f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'"
    )

    # --- Runner ---
    # Key Concept: Runner orchestrates the agent execution loop.
    runner = Runner(
        agent=memory_agent,  # The agent we want to run
        app_name=APP_ID,  # Associates runs with our app
        session_service=session_service,  # Uses our session manager
        memory_service=memory_service,
    )
    print(f"Runner created for agent '{runner.agent.name}'.")
    # @title Run the Initial Conversation

    # We need an async function to await our interaction helper
    async def run_conversation():
        await call_agent_async(
            # "What is the weather like in London?",
            "내 이름이 뭔지 아니?",
            runner=runner,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )

        await call_agent_async(
            # "What is the weather like in London?",
            "서울에서 부산까지의 거리는 대략 몇 km인가요?",
            runner=runner,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )

    # Execute the conversation using await in an async context (like Colab/Jupyter)
    await run_conversation()

    # 공식 문서 방식에 따라 get_session 호출 (키워드 인자 사용)
    try:
        print("🔍 첫 번째 세션을 메모리에 추가 중...")
        session1_comp = await session_service.get_session(
            app_name=APP_ID, session_id=SESSION_ID, user_id=USER_ID
        )
        print(f"세션 가져오기 성공: {type(session1_comp)}")
        await memory_service.add_session_to_memory(session=session1_comp)
        print("✅ 첫 번째 세션이 메모리에 성공적으로 추가되었습니다.")
    except Exception as e:
        print(f"❌ 첫 번째 세션 메모리 추가 실패: {e}")
        print(f"에러 타입: {type(e)}")
        # 에러가 발생해도 계속 진행

    # 메모리 인덱싱을 위한 대기 시간 추가
    import asyncio

    print("Waiting for memory indexing...")
    await asyncio.sleep(10)  # 10초로 늘림

    session2 = await session_service.create_session(app_name=APP_ID, user_id=USER_ID)
    SESSION_ID2 = session2.id

    async def run_conversation2():
        await call_agent_async(
            "지난 대화에서 내가 무엇을 물어봤는지 말해줘.",  # 더 명확한 질문
            runner=runner,
            user_id=USER_ID,
            session_id=SESSION_ID2,
        )

        await call_agent_async(
            # "What is the weather like in London?",
            "내 이름은 홍길동이야. 잘 기억해둬.",
            runner=runner,
            user_id=USER_ID,
            session_id=SESSION_ID2,
        )

    await run_conversation2()

    # 두 번째 세션도 동일한 방식으로 처리
    try:
        print("🔍 두 번째 세션을 메모리에 추가 중...")
        session2_comp = await session_service.get_session(
            app_name=APP_ID, session_id=SESSION_ID2, user_id=USER_ID
        )
        print(f"두 번째 세션 가져오기 성공: {type(session2_comp)}")
        await memory_service.add_session_to_memory(session=session2_comp)
        print("✅ 두 번째 세션이 메모리에 성공적으로 추가되었습니다.")
    except Exception as e:
        print(f"❌ 두 번째 세션 메모리 추가 실패: {e}")
        print(f"에러 타입: {type(e)}")


# --- OR ---

def get_engine_id():
    APP_NAME, APP_ID = get_or_create_engine("My Memory App", "ADK + Memory Bank test")
    print(f"APP_NAME, APP_ID: {APP_NAME}, {APP_ID}")

# Uncomment the following lines if running as a standard Python script (.py file):
# import asyncio
if __name__ == "__main__":
    try:
        # asyncio.run(main())
        # asyncio.run(main_memory())
        get_engine_id()
    except Exception as e:
        print(f"An error occurred: {e}")
