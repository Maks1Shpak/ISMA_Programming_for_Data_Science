#!/usr/bin/env bash
# Simple helper to run the Streamlit app from the repository root
cd "$(dirname "$0")"
streamlit run streamlit_service_app.py
