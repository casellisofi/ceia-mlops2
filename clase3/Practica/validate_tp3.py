import subprocess
import sys
from concurrent import futures
from pathlib import Path

import grpc

BASE = Path(__file__).resolve().parent
PROJECT_ROOT = BASE.parents[1]
TP1_DIR = PROJECT_ROOT / "clase1" / "Practica"
sys.path.insert(0, str(TP1_DIR))

subprocess.run(
    [
        sys.executable,
        "-m",
        "grpc_tools.protoc",
        f"-I{BASE}",
        f"--python_out={BASE}",
        f"--grpc_python_out={BASE}",
        str(BASE / "scoring.proto"),
    ],
    check=True,
)

import scoring_pb2
import scoring_pb2_grpc
from api_ml_tp1 import InputFeatures, MODEL_VERSION, model_predict


class ScoringServicer(scoring_pb2_grpc.ScoringServicer):
    def Predict(self, request, context):
        features = InputFeatures(
            feature_1=request.feature_1,
            feature_2=request.feature_2,
            feature_3=request.feature_3,
        )
        prediction = model_predict(features)
        return scoring_pb2.Prediction(
            prediction=prediction,
            model_version=MODEL_VERSION,
        )

    def PredictStream(self, request, context):
        for item in request.items:
            features = InputFeatures(
                feature_1=item.feature_1,
                feature_2=item.feature_2,
                feature_3=item.feature_3,
            )
            prediction = model_predict(features)
            yield scoring_pb2.Prediction(
                prediction=prediction,
                model_version=MODEL_VERSION,
            )


server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
scoring_pb2_grpc.add_ScoringServicer_to_server(ScoringServicer(), server)
port = server.add_insecure_port("127.0.0.1:0")
server.start()

channel = grpc.insecure_channel(f"127.0.0.1:{port}")
stub = scoring_pb2_grpc.ScoringStub(channel)
request = scoring_pb2.Features(
    feature_1=0.2,
    feature_2=1.3,
    feature_3=0.7,
)
batch = scoring_pb2.FeatureBatch(
    items=[
        request,
        scoring_pb2.Features(feature_1=1.0, feature_2=0.0, feature_3=2.0),
        scoring_pb2.Features(feature_1=4.0, feature_2=2.0, feature_3=1.0),
    ]
)

try:
    response = stub.Predict(request, timeout=5)
    stream = list(stub.PredictStream(batch, timeout=5))
    assert response.prediction == 12.55
    assert [item.prediction for item in stream] == [12.55, 10.5, 19.5]
    print("unary:", response.prediction, response.model_version)
    print("stream:", [(item.prediction, item.model_version) for item in stream])
finally:
    channel.close()
    server.stop(0).wait()
