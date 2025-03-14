<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router';
import { getAuth, signInWithEmailAndPassword } from "firebase/auth";
import { ElForm, ElFormItem, ElInput, ElSelect,ElCard,ElMessage } from 'element-plus'
        
const form = ref({
    email: '',
    pwd: ''
})

const auth = getAuth()
const router = useRouter()

import { storeToRefs } from "pinia";
import { useAuthStore } from '@/stores/auth';
const authStore = useAuthStore()

const { getUser } = storeToRefs(authStore)

const handleSignIn = () => {
    signInWithEmailAndPassword(auth, form.value.email, form.value.pwd)
        .then(async (userCredential) => {
            // 登入成功，取得使用者的 ID Token
            const user = userCredential.user;
            const idToken = await user.getIdToken();

            console.log("Login success");

            // 儲存 Token 或進一步操作
            localStorage.setItem('token', idToken);
            localStorage.setItem('uid', user.uid);

            // 導向首頁或其他頁面
            router.push('/');
        })
        .catch((error) => {
            // 錯誤處理
            console.error(error.message);
            ElMessage.error("登入失敗：" + error.message);
        });
};
        
</script>

<template>
    <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
        <el-card style="max-width: 550px; background-color: #AA60C8;" shadow="always">

            <el-form :model="form" label-width="auto" style="margin: 20px;">
                <el-form-item label="電子郵件" required>
                    <el-input v-model="form.email" />
                </el-form-item>

                <el-form-item label="密碼"  required> 
                    <el-input v-model="form.pwd" type="password"/>
                </el-form-item>
            </el-form>

            <div class="" style="display: flex; justify-content: center; align-items: center; flex-direction: column;">

                <div class="" style="display: flex; justify-content: center;" @click="handleSignIn">
                    <el-button round style="background-color: #FFA726; color: white;">登入</el-button>
                </div>

                <!-- 沒有帳號就註冊 -->
                <div style="display: flex; justify-content: center; align-items: center; margin-top: 10px;">
                    <p>還沒有帳號？</p>
                    <router-link to="/register">註冊</router-link>
                </div>

            </div>
            

        </el-card>
    </div>
</template>


<style lang="scss">

.el-form-item__label {
    color: #fff;
}

</style>