<template>
    <div class="chat-windows">
        <!-- 遍歷 -->
        <ChatBub v-for="chat in chats" :status="chat.role" :key="chat.id" :msg="chat.message"/>

    </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { db } from '../config/firebase';
import ChatBub from './ChatBub.vue';
import { getDocs, collection } from 'firebase/firestore';

// 定義 status 狀態
const status = ref('');
// 定義 message 訊息
const msg = ref('');

// 取得使用者 ID
const uid = localStorage.getItem('uid');

const chats = ref([]);

//讀取聊天紀錄
const getChatHistory = async () => {
    const querySnapshot = await getDocs(collection(db, `users/${uid}/messages`));
    querySnapshot.forEach((doc) => {
        console.log(doc.id, doc.data());
        chats.value.push(doc.data());
    });
};


// 執行取得聊天紀錄
onMounted(() => {
    getChatHistory();
});


</script>

<style lang="scss" scoped>
.chat-windows {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 10px;
    height: 100%;
    overflow-y: auto;
}


</style>