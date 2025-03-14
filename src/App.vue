<template>
  <div class="lxgw-wenkai-tc">
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
@import "@/assets/fonts.css";

// :root {
//   --el-color-primary: #AA60C8;  /* 主色 */
//   --el-color-warning: #FFA726;  /* 副色 */

//   // background-color: #d5d5d5;
// }


</style>
