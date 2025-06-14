import tensorflow_hub as hub
import tensorflow as tf

# Load FILM model from TF Hub
model = hub.load("https://tfhub.dev/google/film/1")

# Save to a directory using SavedModel format
tf.saved_model.save(model, "local_film_model")
