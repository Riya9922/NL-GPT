"""
Quick start script to test Streamlit deployment locally.
Run: streamlit run streamlit_app.py
"""
import subprocess
import sys

print("=" * 60)
print("🚀 AI Output Evaluation Tool - Streamlit Local Test")
print("=" * 60)
print()
print("Starting Streamlit app...")
print()
print("Main file: streamlit_app.py")
print()
print("The app will be available at:")
print("  http://localhost:8501")
print()
print("Press Ctrl+C to stop")
print("=" * 60)
print()

# Run Streamlit
subprocess.run([
    sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
    "--server.headless", "true",
    "--server.port", "8501"
])
