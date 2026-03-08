# disease_model.py
"""Plant disease detection module.

The demo implementation uses a pretrained torchvision model to produce a
vector of logits and then returns a placeholder label. In a real system you
would load a custom model trained on leaf images, map its outputs to
meaningful disease names, and perhaps highlight affected regions.
"""

import os
from PIL import Image

import torch
from torchvision import transforms, models

_MODEL = None
_TRANSFORM = None


def _initialize():
    global _MODEL, _TRANSFORM
    if _MODEL is None:
        # load a lightweight pretrained model; in practice replace with a
        # model trained on plant leaves
        _MODEL = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        _MODEL.eval()
        _TRANSFORM = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])


def predict_disease(image: Image.Image) -> dict:
    """Return a disease prediction and treatment suggestion for the provided leaf image.

    Args:
        image: PIL image of a plant leaf
    Returns:
        dict with 'disease' and 'treatment'
    """
    try:
        _initialize()
        img_tensor = _TRANSFORM(image).unsqueeze(0)
        with torch.no_grad():
            logits = _MODEL(img_tensor)
        # placeholder logic: simulate detection
        # In real app, use actual model predictions
        diseases = {
            0: {"disease": "Healthy", "treatment": "No treatment needed. Keep monitoring."},
            1: {"disease": "Leaf Blight", "treatment": "Apply copper-based fungicide. Remove affected leaves."},
            2: {"disease": "Powdery Mildew", "treatment": "Use sulfur-based fungicide. Improve air circulation."},
            3: {"disease": "Rust", "treatment": "Apply fungicide like triadimefon. Avoid overhead watering."},
        }
        # dummy prediction based on some logic, e.g., random or based on image features
        # For demo, use a simple hash of image size to pick
        pred_class = hash(image.size) % 4
        return diseases[pred_class]
    except Exception as e:
        return {"disease": f"Error during prediction: {e}", "treatment": "Please consult a local expert."}
