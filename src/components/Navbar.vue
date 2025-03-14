<script setup>
import { ref } from 'vue'
import { onMounted } from 'vue'
import {
  Menu as IconMenu,
  Setting,
} from '@element-plus/icons-vue'


import { storeToRefs } from "pinia";
import { useAuthStore } from '@/stores/auth';
import { getAuth} from "firebase/auth";
import { useRouter } from 'vue-router'


const auth = getAuth()
const router = useRouter()
const authStore = useAuthStore()
const {user} = storeToRefs(authStore)

const userName = ref('載入中...');
const userPhoto = ref("https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png");

onMounted(async () => {
  const uid = localStorage.getItem('uid')
  await authStore.fetchUser(uid);
  userName.value = user.value.name
  userPhoto.value = user.value.photoURL || "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
  
});
  
        
//登出
const handleClick = () => {
    auth.signOut().then(() => {
      auth.onAuthStateChanged(() => {
          localStorage.removeItem('token')
          router.push('/login')
        })
    }).catch((error) => {
      console.log(error)
    });
}    
</script>

<!-- 畫面 -->
<template>
    <div>
        <el-menu
        active-text-color="#FFA726"
        background-color="#AA60C8"
        class="el-menu-vertical-demo"
        text-color="#fff"
      >
        <!-- 1 -->
        <el-sub-menu index="1">
          <template #title>
            <el-icon>
              <svg xmlns="http://www.w3.org/2000/svg" id="Layer_1" data-name="Layer 1" viewBox="0 0 24 24" width="512" height="512"><path d="m21,23c0,.553-.448,1-1,1s-1-.447-1-1c0-2.206-1.794-4-4-4h-6c-2.206,0-4,1.794-4,4,0,.553-.448,1-1,1s-1-.447-1-1c0-3.309,2.691-6,6-6h6c3.309,0,6,2.691,6,6Zm1-15.5v2c0,.827-.673,1.5-1.5,1.5h-.5c0,2.206-1.794,4-4,4h-8c-2.206,0-4-1.794-4-4h-.5c-.827,0-1.5-.673-1.5-1.5v-2c0-.827.673-1.5,1.5-1.5h.5c0-2.206,1.794-4,4-4h3v-1c0-.553.448-1,1-1s1,.447,1,1v1h3c2.206,0,4,1.794,4,4h.5c.827,0,1.5.673,1.5,1.5Zm-4-1.5c0-1.103-.897-2-2-2h-8c-1.103,0-2,.897-2,2v5c0,1.103.897,2,2,2h8c1.103,0,2-.897,2-2v-5Zm-8.5,1c-.828,0-1.5.672-1.5,1.5s.672,1.5,1.5,1.5,1.5-.672,1.5-1.5-.672-1.5-1.5-1.5Zm5,0c-.828,0-1.5.672-1.5,1.5s.672,1.5,1.5,1.5,1.5-.672,1.5-1.5-.672-1.5-1.5-1.5Z"/></svg>
              <!-- <img src="/logo.png" alt="" width=""> -->
            </el-icon>
            <span>歷代學長姐</span>
          </template>
          <el-menu-item index="1-1">不分年度</el-menu-item>
          <el-menu-item index="1-1">2024年</el-menu-item>
          <el-menu-item index="1-2">2023年</el-menu-item>
        </el-sub-menu>
        <!-- 2 -->
        <el-menu-item index="2">
          <el-icon><svg xmlns="http://www.w3.org/2000/svg" id="Layer_1" data-name="Layer 1" viewBox="0 0 24 24">
          <path d="m8.5,9.5c0,.551.128,1.073.356,1.537-.49.628-.795,1.407-.836,2.256-.941-.988-1.52-2.324-1.52-3.792,0-3.411,3.122-6.107,6.659-5.381,2.082.428,3.769,2.105,4.213,4.184.134.628.159,1.243.091,1.831-.058.498-.495.866-.997.866h-.045c-.592,0-1.008-.527-.943-1.115.044-.395.021-.81-.08-1.233-.298-1.253-1.32-2.268-2.575-2.557-2.286-.525-4.324,1.207-4.324,3.405Zm-3.89-1.295c.274-1.593,1.053-3.045,2.261-4.178,1.529-1.433,3.531-2.141,5.63-2.011,3.953.256,7.044,3.719,6.998,7.865-.019,1.736-1.473,3.118-3.208,3.118h-2.406c-.244-.829-1.002-1.439-1.91-1.439-1.105,0-2,.895-2,2s.895,2,2,2c.538,0,1.025-.215,1.384-.561h2.932c2.819,0,5.168-2.245,5.208-5.063C21.573,4.715,17.651.345,12.63.021c-2.664-.173-5.191.732-7.126,2.548-1.499,1.405-2.496,3.265-2.855,5.266-.109.608.372,1.166.989,1.166.472,0,.893-.329.972-.795Zm7.39,8.795c-3.695,0-6.892,2.292-7.955,5.702-.165.527.13,1.088.657,1.253.526.159,1.087-.131,1.252-.657.351-1.127,1.052-2.089,1.952-2.825l1.401,2.101c.355.532,1.136.532,1.491,0l1.254-1.882,1.254,1.882c.355.532,1.136.532,1.491,0l1.363-2.044c.867.729,1.542,1.67,1.884,2.768.134.428.528.702.955.702.099,0,.198-.015.298-.045.527-.165.821-.726.657-1.253-1.063-3.41-4.26-5.702-7.955-5.702Z"/>
        </svg></el-icon>
          <span>助教即時連線</span>
        </el-menu-item>
        <!-- 3 -->
        <el-menu-item index="3">
          <el-icon><setting /></el-icon>
          <span>設定</span>
        </el-menu-item>

        <!-- 個人設置 -->
        <div class="avatar-nav">
          <el-dropdown>
            <div class="container">
              <span class="el-dropdown-link">
                <el-avatar
                  :src="userPhoto"
                />
                <div class="">
                  {{ userName }}
                </div>
              </span> 
            </div>
                
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>個人設定</el-dropdown-item>
                <el-dropdown-item>錯誤回報</el-dropdown-item>
                <el-dropdown-item divided @click="handleClick">登出</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-menu> 
    </div>
</template>


<style lang="scss" scoped>
.el-menu-vertical-demo {
  height: 100vh;
}


.avatar-nav {
  position: absolute;
  bottom: 0 ;
  left: 0;
  width: 100%;
  padding: 20px;
  // background-color: blue;
  color: #fff;
  text-align: center;
  outline: none;
  display: flex;
  justify-content: center;
  align-items: center;
  .el-dropdown {
    color: #fff;
    font-size: 18px;
    .container {
      cursor: pointer;
      outline: none;
      .el-dropdown-link {
        display: flex;
        flex-direction: row;
        justify-content: space-around;
        align-items: center;
        cursor: pointer;
        outline: none;
        .el-avatar {
          margin-right: 20px;
        }
    }
  }
  }
}

</style>