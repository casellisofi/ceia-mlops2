"""Mini TP2 - GraphQL + comparación con REST.

Este archivo resuelve la actividad del Mini-TP 2:
1) define un esquema GraphQL con el tipo Model y sus métricas;
2) expone la API en /graphql;
3) compara la misma lectura contra un endpoint REST y reporta llamadas y bytes.
"""

import json
from typing import Optional

import strawberry
from fastapi import FastAPI
from fastapi.testclient import TestClient
from strawberry.fastapi import GraphQLRouter

MI_MODELO = {
    "name": "churn_model",
    "version": 1,
    "metrics": {
        "auc": 0.92,
        "accuracy": 0.88,
        "f1": 0.90,
    },
    "experiment": "exp-2026-09-24",
    "dataset": "customer_churn_v2",
}


@strawberry.type
class Metrics:
    auc: float
    accuracy: float
    f1: float


@strawberry.type
class Model:
    name: str
    version: int

    @strawberry.field
    def metrics(self) -> Metrics:
        m = MI_MODELO["metrics"]
        return Metrics(auc=m["auc"], accuracy=m["accuracy"], f1=m["f1"])


@strawberry.type
class Query:
    @strawberry.field
    def model(self) -> Model:
        return Model(name=MI_MODELO["name"], version=MI_MODELO["version"])


schema = strawberry.Schema(query=Query)
app = FastAPI(title="Mini-TP 2 - metadatos por GraphQL")
app.include_router(GraphQLRouter(schema), prefix="/graphql")


@app.get("/rest/model")
def rest_model() -> dict:
    """Endpoint REST que devuelve la misma información con más campos extras."""
    payload = {
        "name": MI_MODELO["name"],
        "version": MI_MODELO["version"],
        "metrics": MI_MODELO["metrics"],
        "experiment": MI_MODELO["experiment"],
        "dataset": MI_MODELO["dataset"],
    }
    return payload


def compare_rest_vs_graphql() -> None:
    client = TestClient(app)

    graphql_query = "{ model { name version metrics { auc accuracy f1 } } }"
    graphql_response = client.post("/graphql", json={"query": graphql_query})

    rest_response = client.get("/rest/model")

    graphql_request_bytes = len(json.dumps({"query": graphql_query}).encode("utf-8"))
    graphql_response_bytes = len(json.dumps(graphql_response.json()).encode("utf-8"))
    rest_response_bytes = len(json.dumps(rest_response.json()).encode("utf-8"))

    print("=== GraphQL ===")
    print(graphql_response.status_code)
    print(graphql_response.json())
    print(f"Paquetes/llamadas: 1 consulta GraphQL")
    print(f"Tamaño estimado de request+response: {graphql_request_bytes + graphql_response_bytes} bytes")

    print("\n=== REST ===")
    print(rest_response.status_code)
    print(rest_response.json())
    print(f"Paquetes/llamadas: 1 llamada REST")
    print(f"Tamaño estimado de response: {rest_response_bytes} bytes")

    print("\nConclusión:")
    print(
        "GraphQL pide exactamente el subconjunto necesario y devuelve un payload plano, "
        "mientras que REST suele devolver más metadata o campos extras en la misma lectura. "
        "Esto reduce el over-fetching y hace la API más flexible para dashboard y clientes." 
    )


if __name__ == "__main__":
    compare_rest_vs_graphql()
