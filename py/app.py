from flask import Flask, request, jsonify
from flask_sockets import Sockets

from py.openai_client import get_openai_response
from flask_cors import CORS
# from pinecone import Pinecone, ServerlessSpec

app = Flask(__name__)
CORS(app)  # 啟用 CORS


# pc = Pinecone(api_key="pcsk_VPkZN_FYg8jEj3q9F8MNzqQzBXXGhrtzRPzhY4C8A4W4mPBHCrX8eUQ8QMPTD3FZCtGFe")


@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # 解析 JSON 請求
        user_input = request.json.get("message", "")
        if not user_input:
            return jsonify({"error": "Message cannot be empty"}), 400
        # 呼叫 OpenAI 客戶端並獲取回應
        reply = get_openai_response(user_input)
        return jsonify({"reply": reply}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
    
