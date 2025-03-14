<template>
  <div>
    <!-- {{ isLoading }} -->
    <!-- 使用者訊息 -->
    <div class="chat-bub" v-if="props.chat.question" style="justify-content: flex-end; align-items: end;">
      <div class="time">{{ formattedTime }}</div>
      <div class="user_content">
        <p>{{ chat.question }}</p>
      </div>
    </div>
    <!-- Bot 訊息 -->
    <div class="chat-bub" 
         v-if="props.chat.response" 
         style="justify-content: flex-start; align-items: start;">
      <div class="chat-bub-avatar" >
        <img src="/logo.png" alt="" height="40" width="40"/>
      </div>
      <div class="" style="display: flex; align-items: end;">
          <div class="bot_content">
          <div class="markdown-content" v-html="parsedMarkdown"></div>
          <el-divider />
          <div class="respondent-list">
            內容來自於學長姐：
            <span v-if="chat.respondents && chat.respondents.length > 0">
              {{ chat.respondents.join(', ') }}
            </span>
            <span v-else>未知</span>
          </div>
        </div>
        <div class="time">{{ formattedTime }}</div>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, watch, onMounted } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';



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
  parsedMarkdown.value = props.chat.response
    ? DOMPurify.sanitize(marked(props.chat.response)) 
    : '';
});

watch(() => props.chat.response, (newResponse) => {
  parsedMarkdown.value = newResponse 
    ? DOMPurify.sanitize(marked(newResponse)) 
    : '';
});

</script>

<style lang="scss">

.chat-bub {
  display: flex;
  margin-top: 10px;
  // align-items: start;
  
  .chat-bub-avatar {
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: #fff;
    border-radius: 50%;
    margin-right: 10px;
    padding: 10px;
  }
  
  .bot_content {
    background-color: #F8F3D9;
    color: #444545;
    padding: 40px;
    border-radius: 30px;
    max-width: 55%;
    overflow-x: auto;
    .markdown-content {
        font-family: "LXGW WenKai TC", serif !important;
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
      color: #AA60C8;
      font-weight: 600;
      span{
        color: #FFA725;
      }
    }
    .el-divider--horizontal{
      border-top: 1px solid #AA60C8;
    }
  }

  .user_content {
    background-color: #F8F3D9;
    color: #444545;
    padding: 15px;
    border-radius: 30px;
    max-width: 40%;
  }
  
  .time {
    margin: 5px;
    font-size: 12px;
    color: #999;
  }
 
}
</style>
