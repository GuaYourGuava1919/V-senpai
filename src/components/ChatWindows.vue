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
//components
import ChatBub from './ChatBub.vue';
//firebase
import { db } from '../config/firebase';
import { collection, query, orderBy, onSnapshot } from 'firebase/firestore';
//pinia
import { storeToRefs } from "pinia";
import { useCountStore } from '@/stores/counter';
import { ref, onMounted, nextTick, onUnmounted } from 'vue';

const chats = ref([]);
const chatWindowRef = ref(null);
const uid = localStorage.getItem('uid');

const countStore = useCountStore();
const { isLoading } = storeToRefs(countStore);

let unsubscribe; // 儲存解除監聽函式

const scrollToBottom = () => {
    nextTick(() => {
        if (chatWindowRef.value) {
            chatWindowRef.value.scrollTo({
                top: chatWindowRef.value.scrollHeight,
                behavior: 'smooth'
            });
        }
    });
};

const getChatHistory = () => {
    if (!uid) {
        console.warn('尚未登入，無法取得聊天紀錄');
        return;
    }

    const q = query(collection(db, `users/${uid}/conversations/chat01/messages`), orderBy("timestamp"));
    unsubscribe = onSnapshot(q, (snapshot) => {
        chats.value = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        scrollToBottom();
    });
};

onMounted(getChatHistory);

onUnmounted(() => {
    if (unsubscribe) unsubscribe();
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
    // background-color: #F8F3D9;
}

.chat-windows {
    display: flex;
    flex-direction: column;
    padding: 20px;
    height: 100%;
    overflow-y: auto;
    //隱藏滾動條
    &::-webkit-scrollbar {
        display: none;
    }
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
