from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Mini TP1 - MLOps II", version="1.0.0")
MODEL_VERSION = "v1.0.0"


class InputFeatures(BaseModel):
    feature_1: float = Field(..., ge=0)
    feature_2: float = Field(..., ge=0)
    feature_3: float = Field(..., ge=0)


class PredictionResponse(BaseModel):
    prediction: float
    model_version: str


def model_predict(features: InputFeatures) -> float:
    return float(1.5 * features.feature_1 + 2.0 * features.feature_2 - 0.5 * features.feature_3 + 10)


@app.get("/health")
def health():
    return {"status": "ok", "model_version": MODEL_VERSION}


@app.post("/v1/predict", response_model=PredictionResponse)
def predict(features: InputFeatures):
    return {"prediction": model_predict(features), "model_version": MODEL_VERSION}
