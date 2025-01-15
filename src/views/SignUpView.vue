<script setup>

import { ref } from 'vue'
import { ElForm, ElFormItem, ElInput, ElSelect,ElCard } from 'element-plus'

const form = ref({
    name: '',
    class: ''   
})



</script>

<template>
    <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
        <el-card style="max-width: 480px; background-color: #6C63FF;" shadow="always">

            <el-form :model="form" label-width="auto" style="margin: 20px;">
                <el-form-item style="display: flex;">
                    <h1 style="color: #fff;">Sign Up</h1>
                    <el-input v-model="form.email" />
                </el-form-item>
                <el-form-item label="姓名">
                    <el-input v-model="form.name" />
                </el-form-item>
                <el-form-item label="Activity name">
                    <el-input v-model="form.name" />
                </el-form-item>
                <el-form-item label="Activity zone">
                <el-select
                    v-model="form.class"
                    placeholder="Activity zone"
                    clearable
                >
                    <el-option label="Zone one" value="shanghai" />
                    <el-option label="Zone two" value="beijing" />
                </el-select>
                </el-form-item>
            </el-form>
        </el-card>
    </div>
</template>

<style lang="scss" scoped>


</style>