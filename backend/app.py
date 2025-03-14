from flask_cors import CORS
from flask import Flask, request, jsonify, redirect, render_template

from dotenv import load_dotenv
load_dotenv()

# deploy開
# from backend.llm_client import get_groq_response

#local開
from llm_client import get_groq_response



app = Flask(__name__, template_folder='dist', static_folder='dist')
CORS(app)  # 啟用 CORS


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
        return jsonify({"reply": reply}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


if __name__ == "__main__":
    app.run(debug=True)
    
