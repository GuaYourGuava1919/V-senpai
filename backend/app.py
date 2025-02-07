from flask import Flask, request, jsonify, redirect, render_template
from flask_sockets import Sockets

from flask_cors import CORS
# from openai_client import get_openai_response
from groq_client import get_groq_response
# from pinecone import Pinecone, ServerlessSpec

app = Flask(__name__, template_folder='static')
CORS(app)  # 啟用 CORS


# pc = Pinecone(api_key="pcsk_VPkZN_FYg8jEj3q9F8MNzqQzBXXGhrtzRPzhY4C8A4W4mPBHCrX8eUQ8QMPTD3FZCtGFe")


@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/api/')
def index():
    return 'Hello Flask API!'

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # 解析 JSON 請求
        user_input = request.json.get("message", "")
        if not user_input:
            return jsonify({"error": "Message cannot be empty"}), 400
        # 呼叫 OpenAI 客戶端並獲取回應
        reply = get_groq_response(user_input)
        # reply = get_openai_response(user_input)
        # reply = user_input
        return jsonify({"reply": reply}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
    
