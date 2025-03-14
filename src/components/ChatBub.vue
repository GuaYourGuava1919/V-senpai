<template>
  <div class="chat-bub-container">
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
          <div class="scores-list">
            分數：
            <span>{{ chat.scores }}</span>
          </div>
        </div>
        <div class="time">
          <button class="dialog-btn" @click="dialogVisible = true">
            原文
          </button>
          {{ formattedTime }}
        </div>
        <el-dialog
          v-model="dialogVisible"
          title="原文"
          width="500"
        >
          <span>{{chat.originalText}}</span>
        </el-dialog>
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
const dialogVisible = ref(false);


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
.chat-bub-container{
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow-y: auto;
  gap: 10px;
.chat-bub {
  display: flex;
  margin-top: 10px;
  
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
    width: 500px;
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
    .scores-list{
      margin-top: 20px;
      font-size: 18px;
      color: #AA60C8;
      font-weight: 600;
      span{
        color: #D84040;
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
  
  .dialog-btn {
    background-color: #AA60C8;
    color: #fff;
    border: none;
    padding: 5px 10px;
    border-radius: 5px;
    cursor: pointer;
    margin-right: 10px;
  }
  }
}
</style>
