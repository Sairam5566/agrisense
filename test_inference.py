import requests
from inference_sdk import InferenceHTTPClient

# Replace with the local URL of your FastAPI app endpoint
url = "http://127.0.0.1:8000/api/disease/predict"

# Replace with the path to your test image
image_path = "uploads/test_image.jpg"

# Initialize the Roboflow client
print("🔧 Initializing Roboflow Inference Client...")
CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="lS5O4g1XRBHZmXad0Roj"
)

# Model ID for plant disease detection
MODEL_ID = "plant-disease-detection-v2-2nclk/1"

def predict_image(image_path):
    """Test the Roboflow inference API with a sample image"""
    try:
        result = CLIENT.infer(image_path, model_id=MODEL_ID)
        print("Roboflow Inference Result:")
        print(result)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    predict_image(image_path)
