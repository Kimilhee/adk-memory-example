import os
import asyncio
from google import adk
from google.adk.agents import Agent
from google.adk.tools import load_memory  # Tool to query memory
from google.adk.sessions import DatabaseSessionService
from google.adk.memory import VertexAiMemoryBankService
from google.adk.runners import Runner
from google.genai import types # For creating message Content/Parts
from dotenv import load_dotenv

import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

# Load environment variables from .env file (if present)
load_dotenv()


# --- Verify Keys (Optional Check) ---
print("API Keys Set:")
print(f"Google API Key set: {'Yes' if os.environ.get('GOOGLE_API_KEY') and os.environ['GOOGLE_API_KEY'] != 'INSERT API KEY HERE' else 'No (REPLACE PLACEHOLDER!)'}")

# Use an allowlisted model for EasyGCP, we will use gemini 2.0
MODEL_GEMINI_2_0_FLASH = "gemini-2.0-flash-001"

print("\nEnvironment configured.")


remember_agent = Agent(
    name="remember_agent",
    # model=MODEL_GEMINI_2_0_FLASH,
    model="gemini-2.5-flash",
    description="Remember user information and tell when user asks for that.",
    instruction="You are a helpful assistant. "
                "When the user tell you you try to remember and later you can recall this information when asked.",
    tools=[load_memory], # Pass the function directly
)

print(f"Agent '{remember_agent.name}' created using model '{MODEL_GEMINI_2_0_FLASH}'.")

from google import genai
import json

# Create Agent Engine with GenAI SDK

client = genai.Client(vertexai = True)._api_client
string_response = client.request(
        http_method='POST',
        path=f'reasoningEngines',
        request_dict={"displayName": "Express-Mode-Agent-Engine", "description": "Test Agent Engine demo"},
    ).body
response = json.loads(string_response)
print(response)

APP_NAME="/".join(response['name'].split("/")[:6])
APP_ID=APP_NAME.split('/')[-1]
# APP_NAME='projects/795334696302/locations/asia-southeast1/reasoningEngines/83668436827242496'
# APP_ID='1026402900621918208'

print('APP_NAME, APP_ID=', APP_NAME, APP_ID)

async def call_agent_async(query: str, runner, user_id, session_id):
  """Sends a query to the agent and prints the final response."""
  print(f"\n>>> User Query: {query}")

  # Prepare the user's message in ADK format
  content = types.Content(role='user', parts=[types.Part(text=query)])

  final_response_text = "Agent did not produce a final response." # Default

  # Key Concept: run_async executes the agent logic and yields Events.
  # We iterate through events to find the final answer.
  async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
      # You can uncomment the line below to see *all* events during execution
      print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

      # Key Concept: is_final_response() marks the concluding message for the turn.
      if event.is_final_response():
          if event.content and event.content.parts:
             # Assuming text response in the first part
             final_response_text = event.content.parts[0].text
          elif event.actions and event.actions.escalate: # Handle potential errors/escalations
             final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
          # Add more checks here if needed (e.g., specific error codes)
          break # Stop processing events once the final response is found

  print(f"<<< Agent Response: {final_response_text}")

async def main():
    # Create Vertex AI Session through ADK
    # session_service = VertexAiSessionService(agent_engine_id=APP_ID)
    print(f"start main Using App ID: {APP_ID}")
    db_url = "sqlite:///./my_agent_data.db"
    print(f"create session service. App ID: {APP_ID}")
    session_service = DatabaseSessionService(db_url=db_url)
    print(f"create memory service. App ID: {APP_ID}")
    memory_service = VertexAiMemoryBankService(agent_engine_id=APP_ID)
    print(f"@@@ memory service created..: {APP_ID}")

    USER_ID = "INSERT_USER_ID" #@param {type:"string"}
    session = await session_service.create_session(app_name=APP_ID, user_id=USER_ID)
    SESSION_ID = session.id
    print(f"Session created: App='{APP_ID}', User='{USER_ID}', Session='{SESSION_ID}'")
    
    # Connect with ADK. ADK will also use the easygcp key to generate content
    # --- Runner ---
    # Key Concept: Runner orchestrates the agent execution loop.
    runner = Runner(
        agent=remember_agent, # The agent we want to run
        app_name=APP_ID,   # Associates runs with our app
        session_service=session_service, # Uses vertex session service
        memory_service=memory_service # Uses vertex memory service
    )
    print(f"Runner created for agent '{runner.agent.name}'.")

    # await call_agent_async("내 이름이 뭐야?",
    #                                 runner=runner,
    #                                 user_id=USER_ID,
    #                                 session_id=SESSION_ID)
    await call_agent_async("내 이름은 홍길동이야.",
                                    runner=runner,
                                    user_id=USER_ID,
                                    session_id=SESSION_ID)
    await call_agent_async("나이는 18살이고, 취미는 등산이야.",
                                    runner=runner,
                                    user_id=USER_ID,
                                    session_id=SESSION_ID)
    
    session = await session_service.get_session(app_name=APP_ID, session_id=SESSION_ID, user_id = USER_ID)
    await memory_service.add_session_to_memory(session=session)
    
    print(f"Start creating session: App='{APP_ID}', User='{USER_ID}'")
    session = await session_service.create_session(app_name=APP_ID, user_id=USER_ID)
    SESSION_ID = session.id

    print(f"New Session created: App='{APP_ID}', User='{USER_ID}', Session='{SESSION_ID}'")

    await call_agent_async("내 이름과 취미를 말해봐?",
                                        runner=runner,
                                        user_id=USER_ID,
                                        session_id=SESSION_ID)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}")
