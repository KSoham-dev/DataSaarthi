<template>
    <div class="container mt-5">
        <h1 class="display-5 text-center mb-4">Exploratory Data Analysis</h1>
        <div id="loading-overlay" class="loading-overlay" v-if="isLoading">
            <div class="overlay-content">
                <div class="spinner-border text-danger" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <h5 class="mt-2">Analyzing your data...</h5>
            </div>
        </div>
    </div>
        <numEDA v-if="!isLoading" :descriptiveStats="descriptiveStats" :corr_mat_url="corr_mat_url"
                :box_plot_url="box_plot_url" :hist_url="hist_url" :Dtype="'A. Numerical Data'"/>
        
        <numEDA v-if="!isLoading" :descriptiveStats="cat_summary" :corr_mat_url="count_plots_url"
                :Dtype="'B. Categorical Data'"/>
</template>

<script setup>
import { store } from '@/store.js';
import { onMounted, ref } from 'vue';
import numEDA from '@/components/numEDA.vue';

let descriptiveStats = ref(null);
let corr_mat_url = ref(null);
let box_plot_url = ref(null);
let hist_url = ref(null);
let isLoading = ref(true);
let cat_summary = ref(null);
let count_plots_url = ref(null);

onMounted(() => {
    if (store.cur_file_id) {
        getEDAResults();
        store.pageNo = 2;
    }
});

const getEDAResults = () => {
    fetch(`http://localhost:8000/EDA/${store.cur_file_id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            descriptiveStats.value = data.summary_statistics;
            corr_mat_url.value = data.corr_figure_url;
            box_plot_url.value = data.box_plot_url;
            hist_url.value = data.histogram_figure_url;
            cat_summary.value = data.cat_summary;
            count_plots_url.value = data.count_plots_url;
            store.uploadError = null; // Clear any previous errors
            console.log('EDA Results:', data);
        })
        .catch(error => {
            console.error('Error fetching EDA results:', error);
        }).finally(() => {
            isLoading.value = false;
        });
};

</script>


