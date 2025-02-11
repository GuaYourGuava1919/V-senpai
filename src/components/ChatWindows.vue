<template>
    <div class="chat-windows-container" v-loading="isLoading">
        <div class="chat-windows" ref="chatWindowRef">
            <!-- 無對話時顯示提示 -->
            <div class="chat_window_box" v-if="chats.length === 0">
                <el-card style="max-width: 480px; background-color: rgba(108, 99, 255, 0.4); padding: 20px; border-radius: 20px; color:rgba(108, 99, 255); font-size: 12px;">
                    <p>還沒有對話喔！趕快開始吧！</p>
                </el-card>
            </div>

            <!-- 聊天內容 -->
            <div class="chat-content">
                <ChatBub 
                    v-for="(chat, index) in chats" 
                    :key="chat.id" 
                    :chat="chat"
                />
            </div>
        </div>
    </div>
</template>



<script setup>
import ChatBub from './ChatBub.vue';
import { db } from '../config/firebase';
import { onMounted, ref, nextTick } from 'vue';
import { collection, query, orderBy, onSnapshot } from 'firebase/firestore';

import { storeToRefs } from "pinia";
import { useCountStore } from '@/stores/counter';

const chats = ref([]);
const chatWindowRef = ref(null); // 🔹 用來綁定 chat 視窗
const uid = localStorage.getItem('uid');

const countStore = useCountStore()
const { isLoading } = storeToRefs(countStore)


// 🔹 取得聊天紀錄並滾動到底部
const getChatHistory = () => {
    const q = query(collection(db, `users/${uid}/messages`), orderBy("timestamp"));
    onSnapshot(q, (snapshot) => {
        chats.value = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        
        // 🔹 等待 DOM 更新後滾動到底部
        nextTick(() => {
            if (chatWindowRef.value) {
                chatWindowRef.value.scrollTop = chatWindowRef.value.scrollHeight;
            }
        });
    });
};

// 🔹 在掛載時取得聊天記錄
onMounted(() => {
    getChatHistory();
});
</script>


<style lang="scss" scoped>
.chat-windows-container {
    position: relative; /* 🔹 讓 v-loading 正確顯示 */
    width: 100%;
    height: 100%;
    border-radius:20px ;
    border: 2px solid #ccc;
    padding: 20px;
}

.chat-windows {
    display: flex;
    flex-direction: column;
    padding: 20px;
    height: 100%;
    overflow-y: auto;
    border-radius: 20px;
    width: 100%;

    .chat-content {
    position: relative;
    min-height: 100px; /* 防止畫面塌陷 */
    }

    .chat_window_box {
        display: flex;
        justify-content: center;
        align-items: start;
    }
    
}


</style>
