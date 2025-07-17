<script setup>
import { RouterLink, RouterView } from 'vue-router'
import BSNavbar from './components/BSNavbar.vue';
</script>

<template>
  <div class="d-flex">
    <BSNavbar />
    <main class="main-content flex-grow-1">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>

</style>
