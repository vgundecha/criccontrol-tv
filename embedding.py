
from PIL import Image

import torch
import torch.nn as nn
import torchvision.transforms as T
import torch.nn.functional as F
from torchvision.models import mobilenet_v3_small

def load_model():
    # -------- Model --------
    model = mobilenet_v3_small(weights="IMAGENET1K_V1")
    model.classifier = nn.Identity()  # remove classification head
    model.eval()
    return model

# -------- Preprocessing --------
transform = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize(
        mean=[0.485, 0.456, 0.406],
        std =[0.229, 0.224, 0.225]
    )
])

def embed(img, model):
    x = transform(img).unsqueeze(0)
    with torch.no_grad():
        emb = model(x)
    return F.normalize(emb, dim=1)

def compute_similarity(emb1, emb2):
    return F.cosine_similarity(emb1, emb2).item()
