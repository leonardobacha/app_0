from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np

router = APIRouter()

# Exemplo de modelo de entrada para predição
class RioFeatures(BaseModel):
    feature1: float
    feature2: float
    feature3: float
    # Adicione mais features conforme necessário

# Carregue o modelo RandomForest treinado (arquivo .pkl salvo previamente)
model = joblib.load("random_forest_model.pkl")

@router.post("/predict")
def predict(features: RioFeatures):
    try:
        # Converta os dados recebidos para o formato esperado pelo modelo
        input_data = np.array([[features.feature1, features.feature2, features.feature3]])
        prediction = model.predict(input_data)
        return {"prediction": float(prediction[0])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))