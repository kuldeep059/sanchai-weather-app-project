from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
from typing import List
from fastapi.middleware.cors import CORSMiddleware

# Langchain imports
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool

# Load environment variables from .env file
load_dotenv()

# --- 1. CONFIGURATION AND INITIALIZATION ---

# Initialize FastAPI app
app = FastAPI(title="SanchAI Weather Agent")

# Add CORS Middleware to allow the frontend to access the backend
origins = [
    "http://127.0.0.1:5173",  # Your React development server address
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],
)

# Environment Variables
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"


# --- 2. LANGCHAIN TOOL DEFINITION ---

@tool
def get_current_weather(city: str) -> str:
    """
    Returns the current weather in a given city. 
    The city must be a single string, e.g., 'Pune' or 'London'.
    """
    if not WEATHER_API_KEY:
        return "Weather API key is not configured."

    params = {
        'q': city,
        'appid': WEATHER_API_KEY,
        # 'units': 'metric' is good for Celsius, remove it if you prefer Fahrenheit/Kelvin
        'units': 'metric' 
    }
    
    try:
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()

        if data.get("cod") == "404":
             return f"Could not find weather data for {city}. Please check the city name."

        main = data.get("main", {})
        weather_desc = data.get("weather", [{}])[0].get("description", "N/A")
        
        # Extracting key weather details
        temperature = main.get("temp")
        feels_like = main.get("feels_like")
        humidity = main.get("humidity")

        return (
            f"The current weather in {city} is {weather_desc}. "
            f"The temperature is {temperature}°C and it feels like {feels_like}°C. "
            f"Humidity is {humidity}%."
        )

    except requests.exceptions.RequestException as e:
        return f"Error connecting to weather service: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


# --- 3. LANGCHAIN AGENT SETUP ---

# Define the tools the agent can use
tools: List[tool] = [get_current_weather]

# Initialize the LLM client (pointing to Openrouter)
llm = ChatOpenAI(
    model=OPENROUTER_MODEL,
    openai_api_base=OPENAI_API_BASE,
    openai_api_key=OPENAI_API_KEY,
    temperature=0
)

# Define the prompt for the agent
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system", 
            "You are a helpful and friendly weather assistant. Your only goal is to answer questions about the weather of a city. If the user asks for the weather, you MUST use the 'get_current_weather' tool to find the answer. If the question is not about the weather, respond politely that you can only provide weather information."
        ),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# Create the agent
agent = create_openai_tools_agent(llm, tools, prompt)

# Create the executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# --- 4. FASTAPI ENDPOINT ---

class ChatRequest(BaseModel):
    """Schema for the user's incoming message."""
    message: str

class ChatResponse(BaseModel):
    """Schema for the application's response."""
    response: str


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Receives a user message and uses the Langchain agent to generate a response.
    """
    user_input = request.message
    
    try:
        # Invoke the agent with the user's input
        result = await agent_executor.ainvoke({"input": user_input})
        
        # The agent's output is the final answer
        final_response = result.get("output", "Sorry, I couldn't process your request.")
        
        return ChatResponse(response=final_response)

    except Exception as e:
        print(f"Agent execution error: {e}")
        return ChatResponse(response=f"An error occurred while processing your request: {e}")


# --- 5. STATUS ENDPOINTS (from Step 3) ---

@app.get("/")
def read_root():
    return {"Hello": "Welcome to the Weather Agent Backend! Use the /chat endpoint."}

@app.get("/status")
def get_status():
    keys_loaded = {
        "openrouter": OPENAI_API_KEY is not None and OPENAI_API_BASE is not None,
        "weather": WEATHER_API_KEY is not None
    }
    return {"status": "Running", "keys_loaded": keys_loaded}