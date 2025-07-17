<template>
  <div class="container mt-5">
        <h1 class="display-5 text-center mb-4">Exploratory Data Analysis</h1>
    </div>
<div v-if="store.cur_file_id" class="datadisplay mt-5">
    File Uploaded: {{ store.cur_file_name }}
    File Size: {{ store.cur_file_size }}
</div>
</template>

<script setup>
import { store } from '@/store.js';
</script>

<style>

</style>
