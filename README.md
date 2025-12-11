# 🌦️ SanchAI Weather Agent (Full-Stack LLM Application)

A minimal and simple full-stack web application designed to demonstrate the use of a **Langchain Agent** powered by **Openrouter** and a custom **Weather Tool** to answer user queries.

This project fulfills the technical assessment requirements from SanchAI Analytics.

---

## ✨ Features

This application implements the following core features:

1.  **Full-Stack Architecture:** Separate **React** frontend and **FastAPI** backend.
2.  **LLM-Powered Weather:** Users can ask for the weather of any city.
3.  **Agent Tooling:** The backend uses a **Langchain Agent** that is instructed to use a custom `get_current_weather` tool to fetch real-time data.
4.  **Openrouter Integration:** The Langchain Agent uses an **Openrouter** endpoint for LLM inference and function calling.
5.  **Action Flow:** User query is sent from the frontend to the backend's `/chat` endpoint, which invokes the Langchain Agent, and the LLM's final response is returned and displayed in the frontend chat window.

---

## 💻 Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | **React** (Vite) | User interface for chat and interaction. |
| **Backend** | **FastAPI** (Python) | High-performance API server with a single `/chat` endpoint. |
| **LLM Orchestration** | **Langchain** | Framework for building the intelligent agent and integrating the tool. |
| **Model Provider** | **Openrouter** | Used as the OpenAI-compatible endpoint to access models like `openai/gpt-4o-mini`. |
| **Tooling** | **OpenWeatherMap** (API) | External service used by the LLM tool to get weather data. |

---

## ⚙️ Setup and Installation

Follow these steps to get the project running locally.

### 1. Prerequisites

You need the following installed on your system:

* **Python** (3.8+)
* **Node.js** (18+) & **npm**
* **Git**

### 2. API Key Configuration

The application requires two main API keys.

1.  **Openrouter API Key:** Get your key from the Openrouter platform.
2.  **Weather API Key:** Get a free API key from a service like **OpenWeatherMap**.

Create a file named **`.env`** in the root directory (`sanchai-weather-app/`) and add your keys:

```bash
# Openrouter API Configuration
OPENAI_API_KEY="sk-your-openrouter-key-here"
OPENAI_API_BASE="[https://openrouter.ai/api/v1](https://openrouter.ai/api/v1)"
OPENROUTER_MODEL="openai/gpt-4o-mini" 

# Weather API Configuration (e.g., OpenWeatherMap)
WEATHER_API_KEY="your-openweathermap-key-here"
