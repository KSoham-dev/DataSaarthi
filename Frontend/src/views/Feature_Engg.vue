<template>
  <div class="container mt-5">
        <div class="row">
            <div class="col-7 col-lg-12">
                <h1 class="display-5 text-center mb-4">Feature Engineering</h1>
            </div>
        </div>
        <div class="row m-4">
            <div class="col-12">
                <h1 class="display-6 fs-2"> A. Missing Value Imputation</h1>
            </div>
        </div>
    </div>
</template>

<script setup>
import { store } from '@/store.js';
import { onMounted } from 'vue';

onMounted(() => {
    if (store.cur_file_id) {
        fetchData();
        store.pageNo = 3; // Set page number for Feature Engineering
    }
});

const fetchData = () => {
    fetch(`http://localhost:8000/missingVals/${store.cur_file_id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Feature Engineering Data:', data);
            // Process the data as needed
        })
        .catch(error => {
            console.error('Error fetching Feature Engineering data:', error);
        });
}

</script>

<style>

</style>
