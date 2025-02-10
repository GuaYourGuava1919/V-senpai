<script setup>

import Navbar from '../components/Navbar.vue'
import ChatWindows from '../components/ChatWindows.vue'
import { db } from '../config/firebase'
import { collection ,addDoc } from 'firebase/firestore'


import { storeToRefs } from "pinia";
import { useCountStore } from '@/stores/counter';


//輸入框
import { onMounted, ref } from 'vue'
import { ElButton, ElInput, roleTypes } from 'element-plus'
const text = ref('')

const uid = localStorage.getItem('uid')

//讀取Action
const countStore = useCountStore()
const { isLoading } = storeToRefs(countStore)


const saveMessageToFirebase = async (message,role,respondent) => {
  try {
       //儲存路徑/users/{uid}/messages/
      const docRef = await addDoc(collection(db, `users/${uid}/messages`), {
        message,
        timestamp: new Date(),
        role: role,
        respondent,
      });
    console.log('Document written with ID:', docRef.id);
  } catch (error) {
    console.error('Error adding document:', error);
  }
};

const handleClick = async () => {
  if (text.value) {

    countStore.setLoading(true);

    console.log('click', text.value);

    await saveMessageToFirebase(text.value, "user", null);

    try {

      // const response = await fetch('/api/chat', {
      const response = await fetch('http://127.0.0.1:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: text.value }), // 使用 JSON.stringify 格式化資料
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const contentType = response.headers.get('Content-Type');
      let data;
      if (contentType?.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      console.log('機器人的回應', data.reply || 'No response body');

      let uniqueNames = [];
      if (Array.isArray(data.reply) && data.reply.length > 1 && Array.isArray(data.reply[1])) {
        const allNames = data.reply[1].flatMap(entry =>
          entry.replace("姓名：", "").split("、").map(name => 
            name.replace(/[^\w\u4e00-\u9fa5]/g, '') // 只保留中文、英文、数字
          )
        );
        uniqueNames = [...new Set(allNames)];
      }

      // 儲存機器人回應到 Firebase
      if (Array.isArray(data.reply) && data.reply.length > 0) {
        await saveMessageToFirebase(data.reply[0], "bot", uniqueNames.length > 0 ? uniqueNames : null);
        console.log("成功儲存 bot 訊息", data.reply[0]);
      }

    } catch (error) {
      console.error('Error:', error);
    }

    text.value = '';
    countStore.setLoading(false);
    
  }else{
    console.log('請輸入問題')
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
          <div class="" style="height: calc(100vh*0.1) ; width: 80%; text-align: center; display: flex; justify-content: space-around; align-items: center;">
            <el-input
              v-model="text"
              style="width: 80%;"
              size="large"
              maxlength="100"
              placeholder="輸入問題"
              show-word-limit
              type="text"
              @keyup.enter="handleClick"
              
            />
            <el-button
              color="#6C63FF"
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
  .slogan{
    font-size: 10px;
    font-weight: 600;
    color: $color-primary;
  }

</style>
