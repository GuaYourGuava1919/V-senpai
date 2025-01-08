<template>
    <div>
        <ChatBub status="bot"/>
        <ChatBub status="user"/>

    </div>
</template>

<script setup>
import { ref } from 'vue';
import ChatBub from './ChatBub.vue';

// 定義 status 狀態
const status = ref('bot');


</script>

<style lang="scss" scoped>

</style>