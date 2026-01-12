from time import sleep

import mss
from PIL import Image
from IPython.display import display, clear_output

from client import detect_cricket
from connection import connect
from mute import mute_laptop, unmute_laptop
from embedding import load_model, embed, compute_similarity

def extract_bcci_logo(image: Image.Image) -> Image.Image:
    """
    Extract the BCCI logo from the given image.
    """
    # Coordinate of top-left corner and size of the logo
    x0, y0 = (60, 115)
    size = 90
    image = image.crop((x0, y0, x0 + size, y0 + size))  # Example crop box
    return image



tv = connect()

model = load_model()
ref_img = Image.open("./imgs/bcci-logo.png")
ref_emb = embed(ref_img, model)

while True:
    # Take screenshot
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])  # Monitor 1 = primary screen
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

    # Extract BCCI logo (if needed)
    logo_img = extract_bcci_logo(img)

    # Display images
    # print("Screenshot:")
    # display(img)
    # print("Extracted Logo:")
    # display(logo_img)

    # Check logo similarity
    logo_emb = embed(logo_img, model)
    similarity = compute_similarity(ref_emb, logo_emb)

    # Increase font size for better visibility
    print(f"Logo Similarity: {similarity:.4f}")

    if similarity < 0.7:
        tv.mute(True)
        mute_laptop()
        print(f"Mute: Yes")
    else:
        tv.mute(False)
        unmute_laptop()
        print(f"Mute: No")

    sleep(1)  # Wait before taking another screenshot

    # Clear display output
    clear_output(wait=True)

