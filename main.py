import os
from time import sleep, time

import mss
from PIL import Image
import torch

from connection import connect
from mute import mute_laptop
from sync import sync_tv_and_laptop
from embedding import load_model, embed, compute_similarity
from vllm_client import detect_cricket

x0, y0 = (120, 140)
w, h = (175, 175)

x0_replay, y0_replay = (75, 150)
w_replay, h_replay = (200, 100)

def extract_logo(image: Image.Image, x0, y0, w, h) -> Image.Image:
    """
    Extract the BCCI logo from the given image.
    """
    # Coordinate of top-left corner and size of the logo
    image = image.crop((x0, y0, x0 + w, y0 + h))  # Example crop box
    return image

def get_replay_logo_embeddings(model) -> torch.Tensor:
    """
    Extract the replay logo from the given image and compute its embedding.
    """
    # Load all images in imgs/sbi/cropped/ and compute their embeddings
    cropped_folder = "./imgs/sbi/cropped/"
    sbi_embeddings = []
    for filename in os.listdir(cropped_folder):
        img_path = os.path.join(cropped_folder, filename)
        img = Image.open(img_path).convert("RGB")
        emb = embed(img, model)
        sbi_embeddings.append(emb)
    
    return torch.vstack(sbi_embeddings)

if __name__ == "__main__":
    # Connect to LG TV
    tv_media, tv_app = connect()

    model = load_model()
    logo_img = Image.open("./imgs/icc-t20-logo.png").convert("RGB")
    logo_emb = embed(logo_img, model)
    replay_logo_embs = get_replay_logo_embeddings(model)

    last_sync_time = 0  # Track last sync time
    ad_seconds = 0
    mute = False
    while True:

        # Take screenshot
        with mss.mss() as sct:
            screenshot = sct.grab(sct.monitors[1])  # Monitor 1 = primary screen
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

        # Extract mainCCI logo (if needed)
        extracted_logo_img = extract_logo(img, x0, y0, w, h)

        # Check logo similarity
        extracted_logo_emb = embed(extracted_logo_img, model)
        similarity = compute_similarity(extracted_logo_emb, logo_emb).item()

        print(f"Logo Similarity: {similarity:.4f}")

        if similarity < 0.6:

            # Extract replay logo and compute similarity with known replay logos
            extracted_replay_logo = extract_logo(img, x0_replay, y0_replay, w_replay, h_replay)
            extracted_replay_logo.save(f"./imgs/replay_logo_img.png")  # Save for verification

            extracted_replay_logo_emb = embed(extracted_replay_logo, model)
            replay_logo_similarity = compute_similarity(extracted_replay_logo_emb, replay_logo_embs).max().item()
            print(f"Replay Logo Similarity: {replay_logo_similarity:.4f}")

            if replay_logo_similarity < 0.0:
                mute = True
            elif replay_logo_similarity > 0.6:
                mute = False
            else:
                vllm_response = detect_cricket(img)
                print(f"VLLM: {vllm_response}")
                mute = False if vllm_response.lower() == 'yes' else True
        else:
            mute = False
            
        if mute: 
            ad_seconds += 1
            if ad_seconds >= 10:
                print("Syncing TV and Laptop...")
                sync_tv_and_laptop(tv_media)
                ad_seconds = 0
        else:
            ad_seconds = 0

        print(f"Mute: {mute}")
        if tv_app.get_current() == 'hotstar':
            tv_media.mute(mute)
        mute_laptop(mute)

        sleep(1)  # Wait before taking another screenshot

