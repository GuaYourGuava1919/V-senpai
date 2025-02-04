<template>
    <div class="chat-windows">
        <!-- 遍歷 -->
        <ChatBub v-for="chat in chats" :status="chat.role" :key="chat.id" :msg="chat.message" :time="chat.timestamp"/>

    </div>
</template>

<script setup>
import ChatBub from './ChatBub.vue';
import { db } from '../config/firebase';
import { onMounted, ref, watch, nextTick, onBeforeUnmount } from 'vue';
import { collection, query, orderBy, onSnapshot } from 'firebase/firestore';

const chats = ref([]);
const chatWindow = ref(null);


// 取得使用者 ID
const uid = localStorage.getItem('uid');


// 監聽 Firebase 數據變更
const getChatHistory = () => {
    const q = query(collection(db, `users/${uid}/messages`), orderBy("timestamp"));

    onSnapshot(q, (snapshot) => {
        chats.value = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
    });
};

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
    // background-color: aqua;
    width: 100%;
}


</style>