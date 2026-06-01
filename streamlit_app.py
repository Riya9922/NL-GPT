"""
Streamlit wrapper for FastAPI backend.
This file is required for Streamlit Cloud deployment.
"""
import streamlit as st
import uvicorn
import threading
import time
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the FastAPI app
from app.main import app

# Store the server thread
server_thread = None
server = None


def start_server():
    """Start the FastAPI server in a separate thread."""
    global server
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8501,  # Streamlit's default port
        log_level="info",
        access_log=False,
    )
    server = uvicorn.Server(config)
    server.run()


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="AI Output Evaluation API",
        page_icon="🔍",
        layout="wide",
    )

    st.title("🔍 AI Output Evaluation API")
    st.markdown("---")

    # Start FastAPI server if not already running
    global server_thread, server
    if server_thread is None or not server_thread.is_alive():
        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        time.sleep(2)  # Wait for server to start
        st.success("✅ FastAPI server started!")

    # Display status
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Status", "Running", "✅")

    with col2:
        from app.config import get_settings
        settings = get_settings()
        mode = "Mock" if settings.mock_mode else "Live"
        st.metric("Mode", mode, "🔧" if settings.mock_mode else "🚀")

    with col3:
        st.metric("LLM Provider", settings.llm_provider.upper(), "🤖")

    st.markdown("---")

    # API Documentation
    st.header("📚 API Endpoints")
    
    st.subheader("Health Check")
    st.code("GET /health", language="bash")
    st.write("Returns API status and configuration.")

    st.subheader("Evaluate Response")
    st.code("POST /api/v1/evaluate", language="bash")
    st.write("Full pipeline: analyze → attribute → evaluate → regenerate")

    st.subheader("Analyze Only")
    st.code("POST /api/v1/analyze", language="bash")
    st.write("Phase 3: Extract claims and reasoning structure.")

    st.subheader("Attribute Only")
    st.code("POST /api/v1/attribute", language="bash")
    st.write("Phase 3.5: Build source attribution chains.")

    st.subheader("Upload File")
    st.code("POST /api/v1/uploads", language="bash")
    st.write("Upload user context files (PDF/text).")

    st.subheader("Fetch URL")
    st.code("POST /api/v1/context/fetch-url", language="bash")
    st.write("Fetch text content from a URL.")

    st.markdown("---")

    # Example usage
    st.header("💡 Example Usage")
    
    example_code = """
import requests

# Evaluate an AI response
response = requests.post(
    "http://localhost:8501/api/v1/evaluate",
    json={
        "user_query": "Should we invest in renewable energy?",
        "ai_response": "Renewable energy is the future. Solar panels have 90% efficiency.",
        "criteria": [
            "claim_verification",
            "source_transparency",
            "logic_reasoning",
            "missing_factors",
            "improve_answer_quality"
        ],
        "claim_verification_enabled": True,
        "source_preferences": {
            "memory": False,
            "user_context": True,
            "web": True,
            "research": True,
            "company": True,
            "internal": False
        },
        "regenerate": True,
        "answer_quality_intent": {
            "user_intent": "Investment decision for renewable energy",
            "expertise_level": "intermediate",
            "user_goal": "Data-driven investment recommendation",
            "constraints_or_expectations": "Include ROI projections and risk analysis",
            "good_answer_looks_like": "Executive summary with pros/cons and data sources"
        }
    }
)

print(response.json())
"""
    
    st.code(example_code, language="python")

    st.markdown("---")

    # Configuration info
    st.header("⚙️ Configuration")
    
    st.info("""
    **For Production Deployment:**
    
    1. Set `MOCK_MODE=false` in Streamlit secrets
    2. Add your `GROQ_API_KEY` to secrets
    3. Configure `CORS_ORIGINS` with your Vercel frontend URL
    4. Deploy frontend to Vercel with `VITE_API_BASE` pointing to this URL
    
    **Streamlit Secrets (secrets.toml):**
    ```toml
    MOCK_MODE = "false"
    GROQ_API_KEY = "gsk_your_api_key_here"
    LLM_PROVIDER = "groq"
    CORS_ORIGINS = "https://your-vercel-app.vercel.app"
    ```
    """)

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
            <p>AI Output Evaluation Tool • Phase 3-7 Implementation</p>
            <p>
                <a href='https://github.com/Riya9922/NL-GPT' target='_blank'>GitHub Repository</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
