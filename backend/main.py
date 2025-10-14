from modelos import tl_AlexNet  # substitua pelo seu modelo
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import torch
from torchvision import transforms

# === Configurações ===
app = FastAPI()

# Permite que seu app mobile (React Native) acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # em produção, especifique apenas seu domínio/IP
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Carregar modelo PyTorch ===
checkpoint_path = "tl_validacao_mobilenet.pth"

checkpoint = torch.load(checkpoint_path, map_location="cpu")
# supondo que seu checkpoint contém o state_dict e classes
classes = checkpoint["classes"]
input_size = checkpoint["input_size"]

# Aqui você deve criar a arquitetura do modelo igual ao treinamento
# Exemplo: modelo = MinhaRede(...)
# Se tiver MobileNet, AlexNet, etc., importe e instancie a mesma classe
modelo = tl_AlexNet(num_classes=len(classes))
modelo.load_state_dict(checkpoint["model_state_dict"])
modelo.eval()

# === Transformações de imagem ===
preprocess = transforms.Compose([
    transforms.Resize((input_size, input_size)),
    transforms.ToTensor(),
    transforms.Normalize(mean=checkpoint["mean"], std=checkpoint["std"])
])

# === Endpoint de predição ===


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Abrir imagem
        image = Image.open(file.file).convert("RGB")
        image_tensor = preprocess(image).unsqueeze(
            0)  # adicionar batch dimension

        # Rodar modelo
        with torch.no_grad():
            output = modelo(image_tensor)
            probs = torch.softmax(output, dim=1)
            conf, pred = torch.max(probs, dim=1)

        return {
            "classe_predita": classes[pred.item()],
            "confianca": conf.item()
        }

    except Exception as e:
        return {"error": str(e)}
