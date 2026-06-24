# Project Documentation: AI Assistant for RPG Game Masters

## 1. Project Overview
An intelligent assistant (co-pilot) designed to support Game Masters in worldbuilding, narrative creation, and campaign management. The AI does not replace the Game Master but accelerates the creation of complex content, allowing them to focus on improvisation and running the game.

## 2. Phase 1: The Minimum Viable Product (MVP) – Focus on D&D 5e
To start and validate the project with a clear focus, the first step will be the creation of a **Story and Adventure Generator for Dungeons & Dragons 5e**.

### The "Narrative Funnel"
To avoid linear or generic stories, AI-generated content should follow structured logical blocks:
* **The Plot Hook:** The reason why adventurers become involved in the quest (money, morality, duty, etc.).
* **The Antagonist and the Threat:** The driving force behind the conflict and the "Doom Clock" (what happens if the players fail).
* **Key Locations and NPCs:** Brief descriptions of environments and important characters containing crucial information.

### Three-Act Structure
The generated adventure will be presented to the Game Master in a clean and structured format:
* **Act 1: The Call** (Introduction of the problem and initial engagement).
* **Act 2: The Development** (Exploration, investigation, and minor combat encounters).
* **Act 3: The Climax** (Final confrontation and resolution).

## 3. Phase 2: Multi-System Expansion (D&D and Cyberpunk RED)
The natural evolution of the assistant is to make it system-agnostic, capable of switching seamlessly between high fantasy and a deadly dystopian future.

### Technical Strategies for Multi-System Management
* **Dynamic Prompt Routing:** The system injects different instructions depending on the Game Master's choice, changing the "tone of voice" (epic for D&D, cynical/neon for Cyberpunk).
* **Isolated Knowledge Bases (RAG):** Strict separation of rules. D&D will use SRD-based documents, while Cyberpunk will require accurate documentation of modern mechanics (Netrunning, scarcity economy, localized armor, etc.).
* **Structured Data Templates (JSON Schemas):** The AI will respond using data structures specific to each game. D&D will structure classic attributes and spells; Cyberpunk will structure Humanity points, Cyberware, and Lifepaths.

## 4. Architecture and Technology Stack
* **Programming Language:** Python 3.10+ (ideal for Artificial Intelligence integration).
* **Visual Interface (Frontend):** Streamlit (allows the creation of functional and attractive web interfaces using only Python code).
* **Brain (AI Engine):** Language Model APIs such as Google Gemini or OpenAI.
* **Data Structuring:** Python's native `json` library to ensure proper processing of AI responses.
* **Security and Environment Variables:** Libraries such as `python-dotenv` to keep API keys secure.

## 5. Development Guide (Step by Step)
1. **Environment Setup:**
   * Create a Git repository for version control.
   * Configure a virtual environment (`venv`).
   * Install dependencies via terminal: `pip install streamlit google-generativeai python-dotenv`.
2. **API Connection Test:** Create a basic script (`test_api.py`) to validate successful communication with the AI model.
3. **Prompt Engineering:** Write the master System Prompt that defines the assistant's personality.
4. **Frontend Development with Streamlit:** Develop the main screen (`app.py`), including text input fields (where the Game Master enters the core idea) and action buttons.
5. **Backend/Frontend Integration:** Connect the Game Master's text submission to the API call and format the generated story for display on screen.

## 6. Recommended Folder Structure
```text
rpg-ai-assistant/
│
├── .env                  # File containing secret API keys (never share publicly)
├── .gitignore            # Defines which files Git should ignore
├── README.md             # This project documentation
├── requirements.txt      # List of libraries for easy installation
├── app.py                # Main file that runs the Streamlit application
└── src/
    ├── __init__.py
    ├── ia_client.py      # Module for direct AI API requests
    └── prompts.py        # File containing System Prompts and JSON structures
```
