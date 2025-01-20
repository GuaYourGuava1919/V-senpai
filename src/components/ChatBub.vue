<template>
    <div>
      <div class="chat-bub" v-if="status === 'bot'" style="justify-content: flex-start;">
        <div class="bot_content" v-html="parsedMarkdown"></div>
        <!-- 時間戳 -->
        <div class="time">
          2021-10-10 10:10:10
        </div>
      </div>
      <div class="chat-bub" v-else style="justify-content: flex-end;">
        <!-- 時間戳 -->
        <div class="time">
          2021-10-10 10:10:10
        </div>
        <div class="user_content">
          <p>{{ msg }}</p>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, watch, onMounted } from 'vue';
  // 使用命名匯出引入 Marked.js
  import { marked } from 'marked';
  
  // 使用 defineProps 定義 props
  const props = defineProps({
    status: {
      type: String,
      required: true
    },
    msg: {
      type: String,
      required: true
    }
  });
  
  // 存放轉換後的 HTML
  const parsedMarkdown = ref('');
  
  // 當 msg 改變時，重新解析 Markdown
  watch(() => props.msg, (newMsg) => {
    // 確保 msg 不為空或 null，再解析
    if (newMsg) {
      parsedMarkdown.value = marked(newMsg);
    } else {
      parsedMarkdown.value = ''; // 若 msg 為空，顯示空字串
    }
  });
  
  // 在組件掛載後解析初始的 Markdown
  onMounted(() => {
    if (props.msg) {
      parsedMarkdown.value = marked(props.msg);
    } else {
      parsedMarkdown.value = ''; // 若 msg 為空，顯示空字串
    }
  });
  </script>
  
  <style lang="scss" scoped>
  .chat-bub {
    display: flex;
    margin-top: 10px;
    align-items: end;
    .bot {
      justify-content: flex-start;
    }
    .bot_content {
      background-color: #6C63FF;
      color: white;
      padding: 40px;
      border-radius: 10px;
      min-width: 500px;
      overflow-x: auto;
    }
    .user_content {
      background-color: #d5d5d5;
      color: black;
      padding: 10px;
      border-radius: 10px;
    }
    .time {
      margin: 5px;
      font-size: 12px;
      color: #999;
    }
  }
  </style>
  