# VedaAI - AI Assessment Creator

## Live Demo: [Streamlit Cloud URL]

## Setup:
1. Fork this repo
2. Go to streamlit.io/cloud
3. Connect GitHub repo
4. Add `ANTHROPIC_API_KEY` in secrets
5. Deploy!

## Features:
- Single-page AI Assessment Generator
- Customizable Grade, Subjects, Topics, and Difficulty levels
- Real-time generation with Claude (claude-sonnet-4-20250514)
- Clean exam paper layout with dynamic difficulty badges
- Automatic PDF formatting and export using ReportLab
- Fully mobile responsive design
- Support for reference material uploads (TXT/PDF)

## Tech Stack: 
- Streamlit
- Python
- Anthropic Claude
- ReportLab
- PyPDF2

## Deployment Instructions

Step by step:
1. Go to share.streamlit.io
2. Sign in with GitHub (Himanivashisht03)
3. Click "New app"
4. Select repo: Himanivashisht03/vedaai
5. Branch: main
6. Main file: app.py
7. Click "Advanced settings" → add secret: ANTHROPIC_API_KEY = "sk-ant-..."
8. Click Deploy!
