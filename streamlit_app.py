"""
Streamlit wrapper for FastAPI backend.
This file is required for Streamlit Cloud deployment.

NOTE: Streamlit Cloud doesn't support running a separate uvicorn server.
Instead, we call the FastAPI functions directly through Python.
"""
import streamlit as st
import sys
import os
import json

# Add the backend directory to Python path so we can import the app module
backend_path = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_path)
sys.path.insert(0, os.path.dirname(__file__))

# Import the FastAPI app and services
from app.main import app
from app.config import get_settings
from app.models.request import EvaluationRequest
from app.orchestrator import run_evaluation


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="AI Output Evaluation API",
        page_icon="🔍",
        layout="wide",
    )

    st.title("🔍 AI Output Evaluation API")
    st.markdown("---")

    # Display status
    col1, col2, col3 = st.columns(3)

    settings = get_settings()

    with col1:
        st.metric("Status", "Ready", "✅")

    with col2:
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

    # Interactive Demo
    st.header("🧪 Try It Now (Direct Function Call)")
    
    with st.expander("Click to test evaluation"):
        user_query = st.text_input(
            "User Query",
            value="Should we invest in renewable energy?"
        )
        
        ai_response = st.text_area(
            "AI Response",
            value="Renewable energy is the future. Solar panels have 90% efficiency and wind power is growing rapidly.",
            height=100
        )
        
        if st.button("Run Evaluation", type="primary"):
            with st.spinner("Evaluating..."):
                try:
                    # Create request object
                    request = EvaluationRequest(
                        user_query=user_query,
                        ai_response=ai_response,
                        criteria=[
                            "claim_verification",
                            "source_transparency",
                            "logic_reasoning",
                            "missing_factors",
                            "improve_answer_quality"
                        ],
                        claim_verification_enabled=False,
                        source_preferences={
                            "memory": False,
                            "user_context": True,
                            "web": True,
                            "research": True,
                            "company": True,
                            "internal": False
                        },
                        regenerate=False,
                        answer_quality_intent={
                            "user_intent": "Investment decision",
                            "expertise_level": "intermediate",
                            "user_goal": "Data-driven recommendation",
                            "constraints_or_expectations": "Include sources",
                            "good_answer_looks_like": "Clear pros and cons"
                        }
                    )
                    
                    # Run evaluation directly (no HTTP needed!)
                    import asyncio
                    result = asyncio.run(run_evaluation(request))
                    
                    st.success("✅ Evaluation complete!")
                    
                    # Display results
                    st.json(result.model_dump())
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.exception(e)

    st.markdown("---")

    # Example usage for external API calls
    st.header("💡 Using the API Externally")
    
    st.info("""
    **Important:** Streamlit Cloud is designed for Streamlit apps, not as a REST API server.
    
    To use the evaluation API externally, you have two options:
    
    **Option 1: Deploy FastAPI Separately**
    - Use Railway, Render, or AWS/GCP/Azure
    - Deploy the `backend/` directory as a standalone FastAPI app
    - Use Dockerfile or `uvicorn app.main:app`
    
    **Option 2: Use Streamlit for Demo Only**
    - Use this Streamlit app for demonstrations
    - Call functions directly (as shown above)
    - Not suitable for production API usage
    
    **Recommended for Production:**
    Deploy the backend as a standalone FastAPI service on Railway/Render/AWS.
    """)

    st.markdown("---")

    # Configuration info
    st.header("⚙️ Configuration")
    
    st.info("""
    **Current Settings:**
    """)
    
    st.code(f"""
MOCK_MODE = {settings.mock_mode}
LLM_PROVIDER = {settings.llm_provider}
LLM_MODEL_ANALYSIS = {settings.llm_model_analysis}
LLM_MODEL_EVAL = {settings.llm_model_eval}
LLM_MODEL_REGEN = {settings.llm_model_regen}
MAX_CLAIMS = {settings.max_claims}
MAX_RESPONSE_CHARS = {settings.max_response_chars}
    """, language="bash")
    
    st.warning("""
    **For Production API Usage:**
    
    Deploy the backend separately using:
    - Railway (railway.app)
    - Render (render.com)
    - AWS/GCP/Azure
    
    With environment variables:
    ```bash
    MOCK_MODE=false
    GROQ_API_KEY=gsk_your_api_key_here
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
