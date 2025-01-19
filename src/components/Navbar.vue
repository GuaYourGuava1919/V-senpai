<template>
    <div>
      <!-- <el-col :span="4"> -->
        <el-menu
        active-text-color="#FFA726"
        background-color="#6C63FF"
        class="el-menu-vertical-demo"
        default-active="2"
        text-color="#fff"
      >
        <el-sub-menu index="1">
          <template #title>
            <el-icon><location /></el-icon>
            <span>歷代學長姐</span>
          </template>
          <el-menu-item-group title="Group One">
            <el-menu-item index="1-1">item one</el-menu-item>
            <el-menu-item index="1-2">item two</el-menu-item>
          </el-menu-item-group>
          <el-menu-item-group title="Group Two">
            <el-menu-item index="1-3">item three</el-menu-item>
          </el-menu-item-group>
          <el-sub-menu index="1-4">
            <template #title>item four</template>
            <el-menu-item index="1-4-1">item one</el-menu-item>
          </el-sub-menu>
        </el-sub-menu>
        <el-menu-item index="2">
          <el-icon><icon-menu /></el-icon>
          <span>Navigator Two</span>
        </el-menu-item>
        <el-menu-item index="3" disabled>
          <el-icon><document /></el-icon>
          <span>Navigator Three</span>
        </el-menu-item>
        <el-menu-item index="4">
          <el-icon><setting /></el-icon>
          <span>Navigator Four</span>
        </el-menu-item>
        <div class="avatar-nav" @click="handleClick">
          <div class="container">
            <el-avatar
              src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
            />
            <p>Admin</p>
          </div>
        </div>
      </el-menu> 
    <!-- </el-col> -->
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import {
  Document,
  Menu as IconMenu,
  Location,
  Setting,
} from '@element-plus/icons-vue'
import { getAuth } from 'firebase/auth';

const router = useRouter()
const auth = getAuth()

const handleClick = () => {
  auth.signOut().then(() => {
        auth.onAuthStateChanged(() => {
          localStorage.removeItem('token')
          router.push('/login')
        })
      })
}


</script>

<style lang="scss" scoped>
.el-menu-vertical-demo {
  height: 100vh;
}
.avatar-nav {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 20px;
  background-color: #6C63FF;
  color: #fff;
  // text-align: center;
  .container {
    display: flex;
    align-items: center;
    // justify-content: center;
    p {
      margin-left: 10px;
    }
  }
}

</style>