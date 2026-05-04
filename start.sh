#!/bin/bash
echo "🌿 Starting MindfulYogi Content Tool..."
ollama serve &
sleep 3
streamlit run app.py &
sleep 3
ngrok http 8502
