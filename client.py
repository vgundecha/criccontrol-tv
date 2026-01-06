#!/usr/bin/env python3
"""
Cricket Detection Client
Send an image to the inference server and get prediction.
"""

import base64
import os

import requests

# Configuration
SERVER_URL = "http://localhost:8000"
IMAGE_PATH = "imgs/positive/Screenshot_5-1-2026_135246.jpeg"
TIMEOUT = 60


def encode_image_to_base64(image_path: str) -> str:
    """Read and encode an image file to base64."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_image_mime_type(image_path: str) -> str:
    """Get MIME type based on file extension."""
    ext = os.path.splitext(image_path)[1].lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    return mime_types.get(ext, "image/jpeg")


def get_served_model_name(server_url: str) -> str:
    """Query the server to get the served model name."""
    try:
        response = requests.get(f"{server_url.rstrip('/')}/v1/models", timeout=10)
        response.raise_for_status()
        models = response.json()
        if models.get("data"):
            return models["data"][0]["id"]
    except Exception:
        pass
    return "llava-hf/llava-1.5-13b-hf"  # fallback


def detect_cricket(image_path: str, server_url: str, timeout: int = 60) -> str:
    """
    Send an image to the inference server and detect if it's a cricket match.
    
    Returns:
        The model's response (Yes/No)
    """
    model_name = get_served_model_name(server_url)
    
    # Encode image to base64
    image_b64 = encode_image_to_base64(image_path)
    mime_type = get_image_mime_type(image_path)
    
    # Prepare the request
    prompt = "Is this image from a cricket match? Answer only with 'Yes' or 'No'."
    
    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_b64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "max_tokens": 10,
        "temperature": 0,
    }
    
    # Send request to the server
    endpoint = f"{server_url.rstrip('/')}/v1/chat/completions"
    
    try:
        response = requests.post(endpoint, json=payload, timeout=timeout)
        response.raise_for_status()
        
        result = response.json()
        answer = result["choices"][0]["message"]["content"].strip()
        return answer
        
    except requests.exceptions.ConnectionError:
        return f"ERROR: Cannot connect to server at {server_url}"
    except requests.exceptions.Timeout:
        return "ERROR: Request timed out"
    except requests.exceptions.RequestException as e:
        return f"ERROR: {str(e)}"


if __name__ == "__main__":
    print(f"Sending image to {SERVER_URL}...")
    answer = detect_cricket(IMAGE_PATH, SERVER_URL, TIMEOUT)
    print(f"Result: {answer}")
