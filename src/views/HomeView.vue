<script setup>

import Navbar from '../components/Navbar.vue'
import ChatWindows from '../components/ChatWindows.vue'
import { db } from '../config/firebase'
import { collection ,addDoc } from 'firebase/firestore'

//輸入框
import { ref } from 'vue'
import { ElButton, ElInput } from 'element-plus'
const text = ref('')


// create a connection to websocket server
// ws:// 表示建立的是 WebSocket 的通訊協定

// WebSocket Echo Server 運行一個免費的非常簡單的端點伺服器，支援 websockets 和伺服器傳送事件 (SSE)，因此您可以輕鬆測試您的 websockets 和 SSE 用戶端。
// wss://echo.websocket.org/
// const ws = new WebSocket('ws://localhost:5000/echo');

// when the connection is opened
// ws.addEventListener('open', () => {
//   console.log('connected');
//   // presence.textContent = '🟢';
//   setTimeout(() => {
//     ws.send('ha你爸');
//   }, 1000);
//   ws.send("ha你媽");
// });

// every time socket receives a message
// ws.addEventListener('message', (event) => {
//   const data = event.data;
//   // allChat = data.msg;
//   // render();
//   console.log("data:",data);
// });

// when the connection is closed
// ws.addEventListener('close', () => {
//   console.log('disconnected');
//   // presence.textContent = '🔴';
// });



const saveMessageToFirebase = async (message) => {
  try {
    const docRef = await addDoc(collection(db, 'messages'), {
      message: message,
      timestamp: new Date()
    });
    console.log('Document written with ID:', docRef.id);
  } catch (error) {
    console.error('Error adding document:', error);
  }
};

const handleClick = () => {
  console.log('click', text.value);
  // 儲存到 Firebase
  // saveMessageToFirebase(text.value);
  // 傳送請求到 /chat API
  fetch('http://127.0.0.1:5000/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message: text.value }), // 使用 JSON.stringify 格式化資料
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const contentType = response.headers.get('Content-Type');
      if (contentType?.includes('application/json')) {
        return response.json(); // 解析 JSON 回應
      }
      return response.text(); // 如果不是 JSON 回應
    })
    .then((data) => {
      console.log('Response from /chat:', data || 'No response body');
    })
    .catch((error) => {
      console.error('Error:', error);
    });

  text.value = '';
};


</script>

<template>
  <div class="app-container">
    <el-col :span="4">
      <Navbar />
    </el-col>
    <el-col :span="20">
      <div class="" >
        <el-row style="display: flex; justify-content: center; align-items: center;">
          <div class="" style="height: calc(100vh*0.85) ; width: 80%; padding: 30px;">
            <!-- <h1>hello</h1> -->
            <ChatWindows />
          </div>
        </el-row>
        <el-row style="display: flex; justify-content: center; align-items: center; background-color: #f0f0f0;">
          <div class="" style="height: calc(100vh*0.1) ; width: 80%; padding: 30px; text-align: center;">
          <el-input
            v-model="text"
            style="width: 80%; margin-left: 20px; "
            maxlength="100"
            placeholder="輸入問題"
            show-word-limit
            type="text"
            @keyup.enter="handleClick"
          />
          <el-button
            style="margin-left: 20px;"
            color="#6C63FF"
            @click="handleClick">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="15"><path d="M498.1 5.6c10.1 7 15.4 19.1 13.5 31.2l-64 416c-1.5 9.7-7.4 18.2-16 23s-18.9 5.4-28 1.6L284 427.7l-68.5 74.1c-8.9 9.7-22.9 12.9-35.2 8.1S160 493.2 160 480l0-83.6c0-4 1.5-7.8 4.2-10.8L331.8 202.8c5.8-6.3 5.6-16-.4-22s-15.7-6.4-22-.7L106 360.8 17.7 316.6C7.1 311.3 .3 300.7 0 288.9s5.9-22.8 16.1-28.7l448-256c10.7-6.1 23.9-5.5 34 1.4z" fill="white"/></svg>
          </el-button>
          </div>
          <!-- <el-button type="primary" loading>Loading</el-button> -->
        </el-row>
      </div>
    </el-col>  
  </div>
</template>

<style lang="scss">
  $color-primary: #6C63FF;

  *{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  .app-container {
    display: flex;
    height: 100vh;
  }

</style>
