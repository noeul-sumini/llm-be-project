from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def test_ping():
    response = client.get("/v1/common/ping")
    assert response.status_code == 200
    assert response.json()["status_msg"] == "pong"


def test_upload():
    api_path = "/v1/qa/upload"
    file_name = "test.pdf"
    file_path = os.path.join(BASE_DIR, file_name)
    
    

    with open(file_path, "rb") as file:
        files = {"files": (file.name, file, "text/plain")}
        data = {"collection_name" : "test"}
        response = client.post(url = api_path, files=files, data=data)
    assert response.status_code == 200
    assert response.json()['status_msg'] == "File Upload Success"
    assert response.json()['filenames'] == [file_path]
    


def test_query():

    api_path = "/v1/qa/query"
    data = {
            "user_id" : "0",
            "collection_name": "test",
            "query": "토큰이 중복 발급되었을 경우 어떻게 되나요?",
            "query_params": {
                "num_retrieval_docs": 3,
                "score_threshold": 0.3,
                "dense_retriever_weight": 0.5
            }
    }
    response = client.post(url = api_path, json = data)
    assert response.status_code == 200
    assert 'text/event-stream' in response.headers['Content-Type'].split(";")
    
