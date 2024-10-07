# Instagram API

This project provides a FastAPI-based REST API for interacting with Instagram data.

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file in the root directory and add your Instagram access token:
   ````
   INSTAGRAM_ACCESS_TOKEN=your_access_token_here
   THREAD_ACCESS_TOKEN=your_thread_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   ````
6. Run the server: `uvicorn app.main:app --reload`

## API Endpoints

- GET `/api/posts`: Fetch recent Instagram posts
- GET `/api/stats`: Get Instagram user statistics

For more details, visit the `/docs` endpoint after starting the server.