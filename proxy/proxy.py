from flask import Flask, request, Response, jsonify
import requests
import json
import time

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


# -------------------------
# Models endpoint
# -------------------------
@app.route("/v1/models", methods=["GET"])
def models():
    return jsonify({
        "object": "list",
        "data": [{
            "id": "proxy",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "proxy"
        }]
    })


# -------------------------
# Streaming chat completion
# -------------------------
@app.route("/v1/chat/completions", methods=["POST"])
def chat():

    data = request.json
    messages = data.get("messages", [])

    prompt = messages[-1]["content"]

    print("Incoming Prompt:", prompt)

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    r = requests.post(OLLAMA_URL, json=payload)
    result = r.json()

    answer = result.get("response", "")

    print("Model Response:", answer)

    def generate():

        chunk = {
            "id": "chatcmpl-1",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": "proxy",
            "choices": [{
                "delta": {
                    "content": answer
                },
                "index": 0,
                "finish_reason": None
            }]
        }

        yield f"data: {json.dumps(chunk)}\n\n"

        end = {
            "id": "chatcmpl-1",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": "proxy",
            "choices": [{
                "delta": {},
                "index": 0,
                "finish_reason": "stop"
            }]
        }

        yield f"data: {json.dumps(end)}\n\n"
        yield "data: [DONE]\n\n"

    return Response(generate(), mimetype="text/event-stream")


# -------------------------
# Run server
# -------------------------
if __name__ == "__main__":
    print("Proxy running on http://localhost:4000")
    app.run(host="0.0.0.0", port=4000)
