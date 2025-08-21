# @title 필요한 라이브러리를 불러옵니다.
import os
import asyncio
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types  # For creating message Content/Parts

import warnings
import logging


MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash-exp"


def setup():
    print("Hello from adk-memory-example!")
    # Ignore all warnings
    warnings.filterwarnings("ignore")
    logging.basicConfig(level=logging.ERROR)

    print("Libraries imported.")

    # Gemini API Key (Get from Google AI Studio: https://aistudio.google.com/app/apikey)
    os.environ["GOOGLE_API_KEY"] = (
        "AIzaSyBSOoOw8UCwuF3IGRT-8tMZHzX1QIp1ce8"  # <--- 교체
    )

    # --- 키 확인 (선택적인 확인) ---
    print("API Keys Set:")
    print(
        f"Google API Key set: {'Yes' if os.environ.get('GOOGLE_API_KEY') and os.environ['GOOGLE_API_KEY'] != 'YOUR_GOOGLE_API_KEY' else 'No (REPLACE PLACEHOLDER!)'}"
    )

    # API 키를 직접 사용하도록 ADK 설정 (Vertex AI을 사용하지 않도록 설정)
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

    print("\nEnvironment configured.")


# @title Define the get_weather Tool
def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    print(f"--- Tool: get_weather called for city: {city} ---")  # Log tool execution
    city_normalized = city.lower().replace(" ", "")  # Basic normalization

    # Mock weather data
    mock_weather_db = {
        "newyork": {
            "status": "success",
            "report": "The weather in New York is sunny with a temperature of 25°C.",
        },
        "london": {
            "status": "success",
            "report": "It's cloudy in London with a temperature of 15°C.",
        },
        "tokyo": {
            "status": "success",
            "report": "Tokyo is experiencing light rain and a temperature of 18°C.",
        },
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {
            "status": "error",
            "error_message": f"Sorry, I don't have weather information for '{city}'.",
        }


from google.genai import types  # 메시지 Content/Parts를 생성하기 위함


async def call_agent_async(query: str, runner, user_id, session_id):
    """에이전트에 쿼리를 보내고, 최종 응답을 출력합니다."""
    print(f"\n>>> User Query: {query}")

    # 사용자 메시지를 ADK 형식으로 준비합니다.
    content = types.Content(role="user", parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."  # Default

    # 핵심 컨셉: run_async는 에이전트의 로직을 실행하고 Event들을 생성합니다.
    # 최종 답변을 찾기 위해 이벤트들을 반복(iterate)합니다.
    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            # 아래 줄의 주석을 해제하면 실행 중 발생하는 *모든* 이벤트를 확인할 수 있습니다.
            # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

            # 핵심 컨셉: is_final_response()는 해당 턴의 마지막 메시지임을 나타냅니다.
            if event.is_final_response():
                if event.content and event.content.parts:
                    # 처음 부분에 텍스트 응답이 있다고 가정합니다.
                    final_response_text = event.content.parts[0].text
                elif (
                    event.actions and event.actions.escalate
                ):  # 잠재적인 오류나 에스컬레이션 상황을 처리합니다.
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                # 필요하다면 여기에서 추가적인 확인을 수행하세요 (예: 특정 오류 코드 등).
                break  # 최종 응답을 찾으면 이벤트 처리를 중단합니다.
    except Exception as e:
        print(f"ERROR in runner.run_async: {e}")
        final_response_text = f"Error occurred: {e}"

    print(f"<<< Agent Response: {final_response_text}")


async def main():
    setup()

    # Example tool usage (optional test)
    print(get_weather("New York"))
    print(get_weather("Paris"))

    # @title Weather Agent 정의하기
    # 앞서서 정의한 모델 상수 중 하나를 사용하세요.
    AGENT_MODEL = MODEL_GEMINI_2_0_FLASH  # Gemini로 시작

    weather_agent = Agent(
        name="weather_agent_v1",
        model=AGENT_MODEL,  # Gemini인 경우 문자열, LiteLLM인 경우 객체
        description="Provides weather information for specific cities.",
        instruction="You are a helpful weather assistant. "
        "When the user asks for the weather in a specific city, "
        "use the 'get_weather' tool to find the information. "
        "If the tool returns an error, inform the user politely. "
        "If the tool is successful, present the weather report clearly.",
        tools=[get_weather],  # 함수를 직접 전달
    )

    print(f"Agent '{weather_agent.name}' created using model '{AGENT_MODEL}'.")

    # @title Session Service와 Runner 설정

    # --- Session 관리 ---
    # 핵심 컨셉: SessionService는 대화 히스토리와 상태를 저장합니다.
    # 이 튜토리얼에서 사용하는 InMemorySessionService는 심플하고, 반영구적인 저장소입니다.
    session_service = InMemorySessionService()

    # 상호작용 컨텍스트를 식별하기 위한 상수를 정의합니다.
    APP_NAME = "weather_tutorial_app"
    USER_ID = "user_1"

    # --- Runner ---
    # 핵심 컨셉: Runner는 에이전트 실행 루프를 조율합니다.
    # 먼저 Runner를 생성합니다
    runner = Runner(
        agent=weather_agent,  # 우리가 실행하려는 에이전트
        app_name=APP_NAME,  # 실행을 우리 앱과 연관시킵니다.
        session_service=session_service,  # 우리의 Session 관리자를 사용합니다.
    )
    print(f"Runner created for agent '{runner.agent.name}'.")

    # Runner 생성 후에 세션을 생성 - 이것이 더 안전할 수 있습니다
    import time

    SESSION_ID = f"session_{int(time.time())}"

    print(f"Creating session with ID: {SESSION_ID}")

    # 대화가 발생할 특정한 Session 생성
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    print(
        f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'"
    )

    # @title 첫 대화 실행

    # 상호작용 헬퍼를 기다리기 위해 async 함수가 필요합니다.
    async def run_conversation():
        await call_agent_async(
            "What is the weather like in London?",
            runner=runner,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )

        # await call_agent_async(
        #     "How about Paris?", runner=runner, user_id=USER_ID, session_id=SESSION_ID
        # )  # 도구의 오류 메시지를 기대

        # await call_agent_async(
        #     "Tell me the weather in New York",
        #     runner=runner,
        #     user_id=USER_ID,
        #     session_id=SESSION_ID,
        # )

    # Colab이나 Jupyter와 같은 async 컨텍스트에서 `await`를 사용하여 대화를 실행합니다.
    await run_conversation()


if __name__ == "__main__":
    asyncio.run(main())
