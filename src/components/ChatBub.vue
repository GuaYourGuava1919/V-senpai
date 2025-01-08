<template>
    <div>
        <div class="chat-bub" v-if="status === 'bot'" style=" justify-content: flex-start;">
            <div class="bot_content">
                <p>Hi, how can I help you?</p>
            </div>
            <!-- 時間戳 -->
            <div class="time">
                2021-10-10 10:10:10
            </div>
        </div>
        <div class="chat-bub" v-else style=" justify-content: flex-end;">
            <!-- 時間戳 -->
            <div class="time">
                2021-10-10 10:10:10
            </div>
            <div class="user_content">
                <p>Hi, I have a question.</p>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { defineProps } from 'vue';
    // 接收 status 作為 prop
    defineProps({
        status: {
            type: String,
            required: true
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
            padding: 10px;
            border-radius: 10px;
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