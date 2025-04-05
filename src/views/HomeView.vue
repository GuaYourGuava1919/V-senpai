<script setup>
// components
import Navbar from '../components/Navbar.vue'
import ChatWindows from '../components/ChatWindows.vue'

// firebase
import { db } from '../config/firebase';
import { collection, addDoc, doc, updateDoc, serverTimestamp } from "firebase/firestore";

// pinia
import { useCountStore } from '@/stores/counter';


//element-plus
import { onMounted, ref } from 'vue'
import { ElButton, ElInput, roleTypes } from 'element-plus'


const text = ref('') // 輸入框的值
const uid = localStorage.getItem('uid') // 使用者 ID
const countStore = useCountStore() //讀取Action


const saveMessageToFirebase = async (uid, message, sender, conversationId = null, respondents = [], originalText, scores,) => {
  try {
    if (!uid) {
      throw new Error("未提供 UID，無法儲存對話");
    }

    if (sender === "user") {
      //建立新的對話記錄 (使用 collection)
      const collectionRef = collection(db, `users/${uid}/conversations/chat02/messages`);
      //必須存下 addDoc 回傳值 (文件參考)
      const docRef = await addDoc(collectionRef, {
        question: message,
        response: "",
        respondents: [],
        timestamp: new Date(),
        original:'',
        avg: 0,
      });

      // console.log(`成功儲存使用者問題: ${message}`);

      // 這裡才有 id 可以回傳!
      return docRef.id;

    } 
    else if (sender === "bot" && conversationId) {
      //更新指定文件 (使用 doc)
      const docRef = doc(db, `users/${uid}/conversations/chat02/messages/${conversationId}`);
      await updateDoc(docRef, {
        response: message,
        respondents: respondents,
        original:originalText,
        avg: scores,
      });
      // console.log(`更新 conversation: ${conversationId}，添加機器人回應與 respondents: ${respondents}`);
    } 
    else {
      throw new Error("機器人回應缺少 conversationId，無法更新資料");
    }
  } catch (error) {
    console.error("儲存訊息時發生錯誤:", error);
  }
};

const handleClick = async () => {
  if (text.value) {
    countStore.setLoading(true);
    try {
      //先儲存使用者問題，並取得 conversationId
      const conversationId = await saveMessageToFirebase(uid, text.value, "user", null, [], "", 0);

      // 2. 發送請求到 Flask API
      // deploy開
      const response = await fetch('/api/chat', {
      // local開
      // const response = await fetch('http://127.0.0.1:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: text.value }),
      });

      const data = await response.json(); // 將回應轉換為 JSON 格式
      // console.log("完整的回傳資料：", data);
      // console.log('機器人的回應', data.reply || 'No response body');

      // 3. 儲存機器人回應到 Firebase，使用相同 conversationId
      if (Array.isArray(data.reply) && data.reply.length > 1 && typeof data.reply[1] === "object") {
        const message = data.reply[0];
        const info = data.reply[1];

        // 合併受訪者陣列
        const respondents = [...new Set(info.interviewee.flat())];

        await saveMessageToFirebase(
          uid,
          message,               // 機器人回答文字
          "bot",                 // sender
          conversationId || null,
          respondents,           // interviewee
          info.answer || "",     // 原始回覆內容（原始文字）
          info.score || 0        // 分數（平均或相似度）
        );

        // console.log("✅ 成功儲存機器人的回應", message);
      }


    } catch (error) {
      console.error('Error:', error);
    }

    text.value = '';
    countStore.setLoading(false);
  } else {
    // console.log('請輸入問題');
  }
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
          <div class="" style="height: calc(100vh*0.85); padding: 30px; width: 100%;">
            <!-- <h1>hello</h1> -->
            <ChatWindows />
          </div>
        </el-row>
        <el-row style="display: flex; justify-content: center; align-items: center; flex-direction: column;">
          <div class="" style=" height: calc(100vh*0.1) ; width: 100%; text-align: center; display: flex; justify-content: center; gap: 10px; align-items: center;">
            <el-input
              v-model="text"
              style="width: 80%; padding: 10px;"
              size="large"
              maxlength="200"
              placeholder="輸入問題"
              show-word-limit
              type="text"
              @keyup.enter="handleClick"
              
            />
            <el-button
              color="#9FB3DF"
              @click="handleClick">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="15"><path d="M498.1 5.6c10.1 7 15.4 19.1 13.5 31.2l-64 416c-1.5 9.7-7.4 18.2-16 23s-18.9 5.4-28 1.6L284 427.7l-68.5 74.1c-8.9 9.7-22.9 12.9-35.2 8.1S160 493.2 160 480l0-83.6c0-4 1.5-7.8 4.2-10.8L331.8 202.8c5.8-6.3 5.6-16-.4-22s-15.7-6.4-22-.7L106 360.8 17.7 316.6C7.1 311.3 .3 300.7 0 288.9s5.9-22.8 16.1-28.7l448-256c10.7-6.1 23.9-5.5 34 1.4z" fill="white"/></svg>
          </el-button>
          </div>
          <!-- <el-button type="primary" loading>Loading</el-button> -->
          <div class="slogan">如對V-senpai的回覆有疑慮。請找助教查核。</div>
        </el-row>
      </div>
    </el-col>  
  </div>
</template>

<style lang="scss">
  $color-primary: #9FB3DF;

  *{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  .app-container {
    display: flex;
    height: 100vh;
  }
  .slogan{
    font-size: 14px;
    font-weight: 600;
    color: $color-primary;
  }

</style>
