
import os
import uuid

def save_uploaded_file(uploaded_file):
    upload_dir = "input_videos"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{uuid.uuid4().hex}.mp4")
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    return file_path
