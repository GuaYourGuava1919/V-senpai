from flask import Flask, request, jsonify
from flask_sockets import Sockets
import datetime
import time
import random
from openai_client import get_openai_response
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # 啟用 CORS
# sockets = Sockets(app)


# @sockets.route('/echo')
# def echo_socket(ws):
#     while not ws.closed:

#         now = datetime.datetime.now().isoformat() + 'Z'
#         ws.send(now)  #发送数据
#         time.sleep(1)



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
    

# if __name__ == "__main__":
#     from gevent import pywsgi
#     from geventwebsocket.handler import WebSocketHandler
#     server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
#     print('server start')
#     server.serve_forever()