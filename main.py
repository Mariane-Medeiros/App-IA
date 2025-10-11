from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

app = FastAPI()


@app.post("/predict")
async def test_receive_image(file: UploadFile = File(...)):
    # Imprimir informações da imagem recebida no terminal
    print(f"Recebi o arquivo: {file.filename}")
    print(f"Tipo do arquivo: {file.content_type}")
    contents = await file.read()
    print(f"Tamanho do arquivo recebido: {len(contents)} bytes")

    # Retornar resposta simples para o app mobile
    return JSONResponse(content={"mensagem": f"Recebi o arquivo {file.filename} com sucesso!"})
