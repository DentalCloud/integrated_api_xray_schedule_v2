from utils import get_model
from PIL import Image
from torchvision import transforms
import torch

def classify_image(image_path):
    model = get_model()

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])

    image = Image.open(image_path).convert("RGB")
    input_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(input_tensor)
        predicted = torch.argmax(outputs, dim=1).item()

    labels = ["xray", "intraoral", "others"]
    return labels[predicted]
