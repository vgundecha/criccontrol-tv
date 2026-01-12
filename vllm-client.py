#!/usr/bin/env python3
"""
Cricket Detection Client
Send an image to the inference server and get prediction.
"""

import base64
import os
import io

import requests
from PIL import Image

# Configuration
SERVER_URL = ""
MODEL_NAME = "llava-hf/llava-1.5-13b-hf" 
TIMEOUT = 60

# def encode_image_to_base64(image_path: str, max_size: tuple = (600, 400), quality: int = 85) -> str:
#     """Read, resize, compress, and encode an image to base64."""
#     img = Image.open(image_path)
#     img.thumbnail(max_size, Image.Resampling.LANCZOS)  # Maintains aspect ratio
    
#     buffer = io.BytesIO()
#     img.save(buffer, format='JPEG', quality=quality, optimize=True)
#     return base64.b64encode(buffer.getvalue()).decode("utf-8")

def encode_image_to_base64(image, quality: int = 85) -> str:
    """Read and encode an image to base64."""

    buffer = io.BytesIO()   
    image.save(buffer, format='JPEG', quality=quality, optimize=True)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


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


def detect_cricket(image_path: str, timeout: int = 60) -> str:
    """
    Send an image to the inference server and detect if it's a cricket match.
    
    Returns:
        The model's response (Yes/No)
    """
    # model_name = get_served_model_name(server_url)
    
    # Encode image to base64
    image_b64 = encode_image_to_base64(image_path)
    
    # Prepare the request
    prompt = "Is this image from a cricket match? Answer only with 'Yes' or 'No'."
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{"image/jpeg"};base64,{image_b64}"
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
    endpoint = f"{SERVER_URL.rstrip('/')}/v1/chat/completions"
    
    try:
        response = requests.post(endpoint, json=payload, timeout=timeout)
        response.raise_for_status()
        
        result = response.json()
        answer = result["choices"][0]["message"]["content"].strip()
        return answer
        
    except requests.exceptions.ConnectionError:
        return f"ERROR: Cannot connect to server at {SERVER_URL}"
    except requests.exceptions.Timeout:
        return "ERROR: Request timed out"
    except requests.exceptions.RequestException as e:
        return f"ERROR: {str(e)}"


if __name__ == "__main__":
    print(f"Sending image to {SERVER_URL}...")
    image_path = "imgs/positive/Screenshot_5-1-2026_13550_www.hotstar.com.jpeg"
    answer = detect_cricket(image_path, TIMEOUT)
    print(f"Result: {answer}")
