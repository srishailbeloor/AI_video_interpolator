import os
import subprocess
import ffmpeg
from config import QUALITY_OPTIONS
import tensorflow as tf
import tensorflow_hub as hub
from PIL import Image
import numpy as np
import tensorflow as tf

# Load the locally saved FILM model
film_model = tf.saved_model.load("local_film_model")


def load_image_as_tensor(image_path):
    image = tf.io.read_file(image_path)
    image = tf.image.decode_png(image, channels=3)
    image = tf.image.convert_image_dtype(image, tf.float32)
    return tf.expand_dims(image, axis=0)  # Shape: [1, H, W, 3]

def save_tensor_as_image(tensor, output_path):
    tensor = tf.clip_by_value(tensor, 0.0, 1.0)
    image = tf.image.convert_image_dtype(tensor, dtype=tf.uint8)
    encoded = tf.io.encode_png(tf.squeeze(image))
    tf.io.write_file(output_path, encoded)

def extract_frames(video_path, frame_dir):
    os.makedirs(frame_dir, exist_ok=True)
    (
        ffmpeg
        .input(video_path)
        .output(f'{frame_dir}/frame_%04d.png', start_number=0)
        .run(overwrite_output=True)
    )


def interpolate_with_film(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    print("Using locally loaded FILM model...")

    frame_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.png')])
    idx = 0

    for i in range(len(frame_files) - 1):
        frame1_path = os.path.join(input_dir, frame_files[i])
        frame2_path = os.path.join(input_dir, frame_files[i + 1])

        frame1 = load_image_as_tensor(frame1_path)
        frame2 = load_image_as_tensor(frame2_path)

        # Save original frame
        save_tensor_as_image(frame1[0], os.path.join(output_dir, f"frame_{idx:04d}.png"))
        idx += 1

        # Interpolate
        output = film_model({
            'x0': frame1,
            'x1': frame2,
            'time': tf.constant([[0.5]], dtype=tf.float32)
        })
        interpolated = output['image']

        save_tensor_as_image(interpolated[0], os.path.join(output_dir, f"frame_{idx:04d}.png"))
        idx += 1

    # Save last frame
    frame2 = load_image_as_tensor(os.path.join(input_dir, frame_files[-1]))
    save_tensor_as_image(frame2[0], os.path.join(output_dir, f"frame_{idx:04d}.png"))



def assemble_video(frame_dir, output_path, fps, bitrate):
    (
        ffmpeg
        .input(f"{frame_dir}/frame_%04d.png", framerate=fps)
        .output(output_path, vcodec='libx264', pix_fmt='yuv420p', video_bitrate=bitrate)
        .run(overwrite_output=True)
    )


def process_video(input_path, fps, quality_label):
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    extracted = f"extracted_frames/{base_name}"
    interpolated = f"interpolated_frames/{base_name}"
    output_path = f"output_videos/slowmo_{fps}fps_{quality_label.lower()}.mp4"

    extract_frames(input_path, extracted)
    interpolate_with_film(extracted, interpolated)
    assemble_video(interpolated, output_path, fps, QUALITY_OPTIONS[quality_label])
    return output_path