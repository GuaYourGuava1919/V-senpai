<template>
  <div>
    <RouterView />
  </div>
</template>

<script>
import { RouterLink, RouterView } from 'vue-router'

export default {
  components: { RouterLink, RouterView },
}

</script>

<style lang="scss">
:root {
  --el-color-primary: #6C63FF;  /* 主色 */
  --el-color-warning: #FFA726;  /* 副色 */

  // background-color: #d5d5d5;
}


</style>
