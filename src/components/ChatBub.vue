<template>
  <div>
    <!-- {{ isLoading }} -->
    <!-- Bot 訊息 -->
    <div class="chat-bub" 
         v-if="props.chat.role === 'bot' && !(isLoading && isLastMessage)" 
         style="justify-content: flex-start;">
      <div class="bot_content">
        <div class="markdown-content" v-html="parsedMarkdown"></div>
        <el-divider />
        <div class="respondent-list">
          內容來自於學長姐：
          <span v-if="chat.respondent && chat.respondent.length > 0">
            {{ chat.respondent.join(', ') }}
          </span>
          <span v-else>未知</span>
        </div>
      </div>
      <div class="time">{{ formattedTime }}</div>
    </div>

    <!-- 使用者訊息 -->
    <div class="chat-bub" v-if="props.chat.role === 'user'" style="justify-content: flex-end;">
      <div class="time">{{ formattedTime }}</div>
      <div class="user_content">
        <p>{{ chat.message }}</p>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, watch, onMounted, defineEmits } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

// import { storeToRefs } from "pinia";
// import { useCountStore } from '@/stores/counter';


const props = defineProps({
  chat: Object,
});


const formattedTime = ref('');
const parsedMarkdown = ref('');


const timestampToTime = (timestamp) => {
  if (!timestamp || typeof timestamp !== 'object' || !('seconds' in timestamp)) return 'Invalid Time';
  const timeMs = timestamp.seconds * 1000 + Math.round(timestamp.nanoseconds / 1e6);
  return new Date(timeMs).toLocaleString('zh-TW', { hour12: false });
};

onMounted(() => {
  formattedTime.value = timestampToTime(props.chat.timestamp);
  parsedMarkdown.value = props.chat.message 
    ? DOMPurify.sanitize(marked(props.chat.message)) 
    : '';
});

watch(() => props.chat.message, (newMessage) => {
  parsedMarkdown.value = newMessage 
    ? DOMPurify.sanitize(marked(newMessage)) 
    : '';
});


</script>



<style lang="scss">

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
    .markdown-content {
        font-family: Arial, sans-serif;
        line-height: 2;
        color: #333;
        hr {
          margin: 40px 0 ;
          border: none ;
          height: 1.5px ;
          background: #444545 ;
        }
    }
    .respondent-list{
      margin-top: 20px;
      font-size: 18px;
      color: #6C63FF;
      font-weight: 600;
      span{
        color: #FFA726;
      }
    }
    .el-divider--horizontal{
      border-top: 1px solid #6C63FF;
    }
  }
  
  .respondent {
    font-size: 14px;
    color: #666;
    margin-top: 5px;
  }

  .user_content {
    background-color: #d5d5d5;
    color: #444545;
    padding: 10px;
    border-radius: 10px;
    max-width: 40%;
  }
  
  .time {
    margin: 5px;
    font-size: 12px;
    color: #999;
  }
 
}
</style>
