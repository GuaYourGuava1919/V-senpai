<template>
  <div>
    <!-- <nav>
      <router-link to="/">Home</router-link>
      <router-link to="/about">About</router-link>
      <router-link to="/signup">Sign Up</router-link>
    </nav> -->
    <RouterView />
  </div>
</template>

<script>
import { RouterLink, RouterView } from 'vue-router'

export default {
  components: { RouterLink, RouterView },
}
</script>

<style lang="scss" scoped>

</style>
