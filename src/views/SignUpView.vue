<script setup>

import { ref } from 'vue'
import { db } from '../config/firebase'
import { doc, setDoc } from "firebase/firestore"; 
import { getAuth, createUserWithEmailAndPassword } from "firebase/auth";
import { ElForm, ElFormItem, ElInput, ElSelect,ElCard,ElMessage } from 'element-plus'

const form = ref({
    email: '',
    sid: '',
    name: '',
    class: '',
    pwd: ''
})

const auth = getAuth();

  //正規表達式
    const emailReg = /^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$/; 
    const sidReg = /^[0-9]{9}$/;
    const nameReg = /^[\u4e00-\u9fa5]{2,4}$/;

    const warningPop = (v) => {
    ElMessage({
        message: v,
        type: 'warning',
    })
    }

  // 驗證表單
    const validateForm = () => {
        if (!emailReg.test(form.value.email)) {
        warningPop('電子郵件格式錯誤或未填寫');
        console.log(form.value.email);
        return false;
        }
        if (!sidReg.test(form.value.sid)) {
        warningPop('學號格式錯誤或未填寫');
        // console.log("學號格式錯誤");
        return false;
        }
        if (!nameReg.test(form.value.name)) {
        warningPop('姓名格式錯誤或未填寫');
        // console.log("姓名格式錯誤");
        return false;
        }
        if (form.value.class === '') {
        warningPop('班級未選擇');
        // console.log("班級未選擇");
        return false;
        }
        if (form.value.pwd.length < 8) {
        warningPop('密碼長度不足');
        // console.log("密碼長度不足");
        return false;
        }
        return true;
    }

   

    const handleSignUp = () => {
        if (validateForm()) { 
            createUserWithEmailAndPassword(auth, form.value.email, form.value.pwd)
            .then(async (userCredential) => {
                // Signed up 
                const user = userCredential.user;
                // 註冊成功 跳轉至其他頁面
                console.log("註冊成功", user);
                // 新增資料到firestore
                // console.log(db);

                const docRef = await setDoc(doc(db, "users", form.value.sid), {
                    email: form.value.email,
                    // sid: form.value.sid,
                    name: form.value.name,
                    class: form.value.class,
                    // pwd: form.value.pwd
                });
                ElMessage({
                    message: "註冊成功",
                    type: 'success',
                })
        
            })
            .catch((error) => {
                ElMessage({
                    message: "註冊失敗",
                    type: 'error',
                })
                console.log("註冊失敗", error);
            });
                return;
        }
        else{
            console.log("表單驗證失敗",form.value);

        }


    }


</script>

<template>
    <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
        <el-card style="max-width: 550px; background-color: #6C63FF;" shadow="always">

            <el-form :model="form" label-width="auto" style="margin: 20px;">
                <el-form-item label="電子郵件" required>
                    <el-input v-model="form.email" />
                </el-form-item>
                <el-form-item label="學號" required>
                    <el-input v-model="form.sid" />
                </el-form-item>
                <el-form-item label="姓名" required> 
                    <el-input v-model="form.name" />
                </el-form-item>
                <el-form-item label="班級" required>
                <el-select
                    v-model="form.class"
                    placeholder="請選擇修課班級"
                    clearable
                >
                    <el-option label="二甲" value="二甲" />
                    <el-option label="二乙" value="二乙" />
                </el-select>
                </el-form-item>
                <el-form-item label="密碼"  required> 
                    <el-input v-model="form.pwd" type="password"/>
                </el-form-item>
            </el-form>

            <div class="" style="display: flex; justify-content: center;" @click="handleSignUp">
                <el-button round style="background-color: #FFA726; color: white;">註冊</el-button>
            </div>

        </el-card>
    </div>
</template>

<style lang="scss" >
.el-form-item__label {
    color: #fff;
}

</style>