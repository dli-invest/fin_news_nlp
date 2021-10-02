# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from starlette.testclient import TestClient
from app.api import app


def test_docs_redirect():
    client = TestClient(app)
    response = client.get("/")
    assert response.history[0].status_code == 307
    assert response.status_code == 200
    assert response.url == "http://testserver/docs"


def test_api():
    client = TestClient(app)

    text = """But Google is starting from behind. The company made a late push
    into hardware, and Apple's Siri, available on iPhones, and Amazon's Alexa
    software, which runs on its Echo and Dot devices, have clear leads in
    consumer adoption."""

    request_data = {
        "values": [{"recordId": "a1", "data": {"text": text, "language": "en"}}]
    }

    response = client.post("/entities", json=request_data)
    assert response.status_code == 200

    first_record = response.json()["values"][0]
    assert first_record["recordId"] == "a1"
    assert first_record["errors"] == None
    assert first_record["warnings"] == None
    # convert to flat list now
    entities = first_record["data"]["entities"]
    entities = [er_entity.get("name", None) for er_entity in entities]
    # strip special characters and trim
    clean_entities = [er.replace("\n", "").strip() for er in entities]
    clean_entities.sort()
    assert clean_entities == [
        "Alexa",
        "Amazon",
        "Apple",
        "Echo",
        "iPhones"
    ]
