<template>
  <div class="chat-bub-container">
    <!-- 使用者訊息 -->
    <div class="chat-bub" v-if="props.chat.question" style="justify-content: flex-end; align-items: end;">
      <div class="time">{{ formattedTime }}</div>
      <div class="user_content">
        <p>{{ chat.question }}</p>
      </div>
    </div>

    <!-- Bot 訊息 -->
    <div class="chat-bub" v-if="props.chat.response" style="justify-content: flex-start; align-items: start;">
      <div class="chat-bub-avatar"></div>
      
      <!-- 包裝泡泡 + 時間按鈕 -->
      <div style="display: flex; align-items: end;">
        
        <!-- Bot 回應內容泡泡 -->
        <div class="bot_content">
          <div class="markdown-content" v-html="parsedMarkdown"></div>
          <button class="dialog-btn" @click="dialogVisible = true">顯示原文</button>
          <el-divider />
          <div class="respondent-list">
            內容來自於學長姐：
            <span v-if="chat.respondents && chat.respondents.length > 0">
              {{ chat.respondents.join(', ') }}
            </span>
            <span v-else>未知</span>
          </div>
          <div class="scores-list">
            <div v-if="typeof chat.avg === 'number'" class="score-block">
              <span class="score-label">相似度：</span>
              <span :class="getScoreClass(chat.avg)">
                {{ chat.avg.toFixed(2) }}
              </span>
              <div class="score-bar">
                <div
                  class="score-fill"
                  :class="getScoreClass(chat.avg)"
                  :style="{ width: (chat.avg * 100) + '%' }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 原文與時間：移出泡泡 -->
        <div class="meta-info-row">
          <button class="" @click="feedbackVisible = true">回饋</button>
          <div class="time">{{ formattedTime }}</div>
        </div>

        <!-- Dialog -->
        <el-dialog v-model="dialogVisible" title="原文" width="500">
          <span>{{ chat.original }}</span>
        </el-dialog>

        <!-- Dialog -->
        <el-dialog v-model="feedbackVisible" title="回饋" width="500">
          <p>您對這次的回覆滿意嗎？</p>

          <div class="feedback-buttons">
            <button :class="{'selected': feedbackType === 'like'}" @click="feedbackType = 'like'">👍 滿意</button>
            <button :class="{'selected': feedbackType === 'dislike'}" @click="feedbackType = 'dislike'">👎 不滿意</button>
          </div>

          <div class="feedback-textarea">
            <el-input
              v-model="feedbackText"
              type="textarea"
              :rows="4"
              placeholder="若有任何建議，也歡迎補充說明 :)"
            ></el-input>
          </div>

          <template #footer>
            <div class="dialog-footer">
              <el-button @click="feedbackVisible = false">取消</el-button>
              <el-button type="primary" @click="submitFeedback">送出</el-button>
            </div>
          </template>
        </el-dialog>


      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { db } from '../config/firebase'; // Adjust the import based on your project structure
import { collection, addDoc } from 'firebase/firestore';

const props = defineProps({
  chat: Object,
});

const formattedTime = ref('');
const parsedMarkdown = ref('');
const dialogVisible = ref(false);
const feedbackVisible = ref(false);

const feedbackType = ref(null); // 'like' or 'dislike'
const feedbackText = ref("");

const submitFeedback = async () => {

  const userId = localStorage.getItem('uid') || 'defaultUserId'; // Replace with actual user ID retrieval logic
  const messageId = props.chat?.id

  if (!props.chat?.id) {
    // ElMessage.error("找不到訊息 ID，無法儲存回饋！");
    // console.log("找不到訊息 ID，無法儲存回饋！");
    return;
  }

  const feedbackData = {
    type: feedbackType.value,
    comment: feedbackText.value,
    timestamp: new Date()
  };

  try {
    const feedbackRef = collection(
      db,
      'users',
      userId,
      'conversations',
      'chat01',
      'messages',
      messageId,
      'feedback'
    );
    await addDoc(feedbackRef, feedbackData);

    // ElMessage.success("感謝您的回饋！");
    feedbackVisible.value = false;
    feedbackType.value = null;
    feedbackText.value = "";
  } catch (err) {
    // console.error("回饋儲存失敗：", err);
    // console.log(userId, messageId);
  }
};



const timestampToTime = (timestamp) => {
  if (!timestamp || typeof timestamp !== 'object' || !('seconds' in timestamp)) return 'Invalid Time';
  const timeMs = timestamp.seconds * 1000 + Math.round(timestamp.nanoseconds / 1e6);
  return new Date(timeMs).toLocaleString('zh-TW', { hour12: false });
};

const getScoreClass = (score) => {
  if (score < 0.6) return 'score-low';
  if (score < 0.8) return 'score-mid';
  return 'score-high';
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
.chat-bub-container {
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow-y: auto;
  gap: 10px;

  .chat-bub {
    display: flex;
    margin-top: 10px;

  .meta-info-row {
      display: flex;
      align-items: center;
      margin-top: 6px;
      margin-left: 10px;
      button{
        background-color: #9FB3DF;
        color: #fff;
        border: none;
        padding: 5px 10px;
        border-radius: 5px;
        cursor: pointer;
        margin-right: 10px;
      }
      .time {
        font-size: 12px;
        color: #999;
      }
    }


    .bot_content {
      background-color: #F5EEDC;
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
          margin: 40px 0;
          border: none;
          height: 1.5px;
          background: #444545;
        }
      }

      .respondent-list {
        margin-top: 20px;
        font-size: 18px;
        color: #9FB3DF;

        span {
          color: #336D82;
        }
      }

      .scores-list {
        margin-top: 20px;
        font-size: 18px;
        color: #9FB3DF;
        font-weight: 600;

        span {
          color: #E16A54;
        }
      }

      .el-divider--horizontal {
        border-top: 1px solid #9FB3DF;
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
      background-color: #9FB3DF;
      color: #fff;
      border: none;
      padding: 5px 10px;
      border-radius: 5px;
      cursor: pointer;
      margin-top: 10px;
    }

  }
}

/* 新增的進度條與顏色樣式 */
.score-block {
  margin-top: 8px;
  font-size: 16px;
  font-weight: 500;
}

.score-label {
  margin-right: 6px;
  color: #9FB3DF;
}

.score-low {
  color: #e74c3c;
}

.score-mid {
  color: #f39c12;
}

.score-high {
  color: #27ae60;
}

.score-bar {
  background-color: #f5f5f5;
  height: 8px;
  border-radius: 4px;
  margin-top: 6px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.score-fill.score-low {
  background-color: #e74c3c;
}

.score-fill.score-mid {
  background-color: #f39c12;
}

.score-fill.score-high {
  background-color: #27ae60;
}

.feedback-buttons {
  display: flex;
  gap: 12px;
  margin-top: 10px;
  margin-bottom: 16px;

  button {
    padding: 8px 16px;
    border: 1px solid #ccc;
    background-color: #f9f9f9;
    border-radius: 6px;
    cursor: pointer;
    font-size: 16px;

    &.selected {
      background-color: #9fb3df;
      color: white;
    }
  }
}

.feedback-textarea {
  margin-bottom: 16px;
}


</style>
