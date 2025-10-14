import torch
import torch.nn as nn
from torchvision import transforms, models
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
import io
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    # ou especifique o IP do Expo Go, se quiser restringir
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- Configurações do modelo ---
MODEL_PATH = "tl_validacao_mobilenet.pth"  # caminho do seu .pth
DEVICE = torch.device("cpu")  # Render ou servidores sem GPU, use CPU

# --- Função para carregar checkpoint ---


def load_model(path):
    checkpoint = torch.load(path, map_location=DEVICE)

    # Exemplo usando MobileNet (ajuste se seu modelo for outro)
    modelo = models.mobilenet_v2(weights=None)  # sem pesos pré-treinados
    modelo.classifier[1] = nn.Linear(
        modelo.last_channel, len(checkpoint["classes"]))
    modelo.load_state_dict(checkpoint["model_state_dict"])
    modelo.to(DEVICE)
    modelo.eval()  # importante: modo avaliação
    return modelo, checkpoint["classes"], checkpoint["mean"], checkpoint["std"], checkpoint["input_size"]


modelo, classes, media, desvio, input_size = load_model(MODEL_PATH)

# --- Transformações da imagem (igual ao treinamento) ---


def preprocess_image(image_bytes):
    transform = transforms.Compose([
        transforms.Resize((input_size, input_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=media, std=desvio)
    ])
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return transform(image).unsqueeze(0)  # adiciona batch dimension


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Ler a imagem
    contents = await file.read()

    # Pré-processar
    tensor = preprocess_image(contents).to(DEVICE)

    # Predição
    with torch.no_grad():
        outputs = modelo(tensor)
        probs = torch.softmax(outputs, dim=1)
        conf, pred_idx = torch.max(probs, dim=1)

    classe_predita = classes[pred_idx.item()]
    confianca = conf.item()  # já em float

    # Log no servidor
    print(
        f"Arquivo: {file.filename}, Classe: {classe_predita}, Confiança: {confianca:.4f}")

    # Retornar JSON para o app
    return JSONResponse(content={
        "classe_predita": classe_predita,
        "confianca": confianca
    })


@app.get("/ping")
async def ping():
    return {"message": "pong"}
