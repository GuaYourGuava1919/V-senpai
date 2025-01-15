<script>
// import { RouterView, RouterLink } from 'vue-router'

export default {
//   components: { RouterView, RouterLink },
    data() {
        return {
        email: '',
        password: ''
        }
    }
}

</script>

<template>
    <div>
        <h1>Sign In </h1>
        <form>
            <div>
                <label for="email">Email</label>
                <input type="email" id="email" v-model="email" />
            </div>
            <div>
                <label for="password">Password</label>
                <input type="password" id="password" v-model="password" />
            </div>
            <button type="submit">Sign In</button>
        </form>
    </div>
</template>

<style lang="scss" scoped>

</style>