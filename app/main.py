import sys
import streamlit as st
import os
from processor import process_video
from utils import save_uploaded_file
from config import FPS_OPTIONS, QUALITY_OPTIONS

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

st.set_page_config(page_title="AI Video Frame Interpolation", layout="centered")
st.title("🎥 AI-Powered Video Frame Interpolation")

# Upload video
uploaded_file = st.file_uploader("📤 Upload your video (.mp4)", type=["mp4"])

# Select FPS
selected_fps = st.selectbox("🎞️ Select Output FPS", FPS_OPTIONS)

# Select Quality
selected_quality = st.selectbox("🔧 Select Output Quality", list(QUALITY_OPTIONS.keys()))

# Process button
if st.button("🚀 Generate Slow-Motion Video") and uploaded_file:
    with st.spinner("Processing video. This might take a few moments..."):
        input_path = save_uploaded_file(uploaded_file)
        output_path = process_video(input_path, selected_fps, selected_quality)

    st.success("✅ Processing complete!")
    st.video(output_path)
    st.download_button(
        label="⬇️ Download Slow-Motion Video",
        data=open(output_path, "rb"),
        file_name=os.path.basename(output_path),
        mime="video/mp4"
    )
