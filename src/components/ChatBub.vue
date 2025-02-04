<template>
  <div>
    <div class="chat-bub" v-if="status === 'bot'" style="justify-content: flex-start;">
      <div class="bot_content" v-html="parsedMarkdown"></div>
      <!-- 時間戳 -->
      <div class="time">{{ formattedTime }}</div>
    </div>
    <div class="chat-bub" v-else style="justify-content: flex-end;">
      <div class="time">{{ formattedTime }}</div>
      <div class="user_content">
        <p>{{ msg }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { marked } from 'marked';

// 接收 props
const props = defineProps({
  status: { type: String, required: true },
  msg: { type: String, required: true },
  time: { type: Object, required: false } // Firestore Timestamp 應該是 Object
});

// 轉換時間
const formattedTime = ref('');

// 解析 Markdown
const parsedMarkdown = ref('');

// 轉換 Firestore Timestamp
const timestampToTime = (timestamp) => {
  if (!timestamp || typeof timestamp !== 'object' || !('seconds' in timestamp)) return 'Invalid Time';

  const timeMs = timestamp.seconds * 1000 + Math.round(timestamp.nanoseconds / 1e6);
  return new Date(timeMs).toLocaleString('zh-TW', { hour12: false });
};

// 在組件掛載後轉換時間
onMounted(() => {
  formattedTime.value = timestampToTime(props.time); // 修正 this.time.value 錯誤
  parsedMarkdown.value = props.msg ? marked(props.msg) : '';
});

// 監聽 props.time 變化，確保時間顯示更新
watch(() => props.time, (newTime) => {
  formattedTime.value = timestampToTime(newTime);
});
</script>

<style lang="scss" scoped>
.chat-bub {
  display: flex;
  margin-top: 10px;
  align-items: end;
  .bot_content {
    background-color: #d5d5d5;
    color: #444545;
    padding: 40px;
    border-radius: 10px;
    max-width: 55%;
    overflow-x: auto;
  }
  .user_content {
    background-color: #d5d5d5;
    color: #444545;
    padding: 10px;
    border-radius: 10px;
    max-width: 30%;
  }
  .time {
    margin: 5px;
    font-size: 12px;
    color: #999;
  }
}
</style>
