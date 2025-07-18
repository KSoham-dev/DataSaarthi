<template>
    <div class="app-layout" >
        <div class="sidebar d-flex flex-column flex-shrink-0 p-3 text-white bg-dark">
            <router-link to="/"
                class="d-flex align-items-center mb-3 mb-md-0 me-md-auto text-white text-decoration-none">
                <!-- <img src="@/assets/logo.svg" alt="Logo" class="logo" width="50px"/> -->
                <ul class="nav nav-pills flex-column mb-auto">
                    <li class="nav-item">
                        <span class="fs-4">DataSaarthi</span>
                    </li>
                    <li class="nav-item">
                        <span class="fs-6 fw-light">Your Data Companion</span>
                    </li>
                </ul>
            </router-link>
            <hr>
            <ul class="nav nav-pills flex-column mb-auto gap-3">
                <li class="nav-item">
                    <router-link to="/" class="nav-link text-white" active-class="active">
                        <img src="@/assets/icons/upload.svg" alt="Home" width="20px" class="me-2">
                        Data Upload
                    </router-link>
                </li>
                <li>
                    <router-link to="/EDA" class="nav-link text-white" active-class="active" :class="{'disabled': store.cur_file_id == null}">
                        <img src="@/assets/icons/EDA.svg" alt="EDA" width="20px" class="me-2">
                        Exploratory Data Analysis
                    </router-link>
                </li>
                <li>
                    <router-link to="/FeatureEngg" class="nav-link text-white" active-class="active" :class="{'disabled': store.pageNo != 2}">
                        <img src="@/assets/icons/FE.svg" alt="Feature Engineering" width="20px" class="me-2">
                        Feature Engineering
                    </router-link>
                </li>
                <li>
                    <router-link to="/Training" class="nav-link text-white disabled" active-class="active">
                        <img src="@/assets/icons/training.svg" alt="Model Training" width="20px" class="me-2">
                        Model Training
                    </router-link>
                </li>
                <li>
                    <router-link to="/Evaluation" class="nav-link text-white disabled" active-class="active">
                        <img src="@/assets/icons/eval.svg" alt="Model Evaluation" width="20px" class="me-2">
                        Model Evaluation
                    </router-link>
                </li>
                <li>
                    <router-link to="/Predictions" class="nav-link text-white disabled" active-class="active">
                        <img src="@/assets/icons/predictions.svg" alt="Model Predictions" width="20px" class="me-2">
                        Model Predictions
                    </router-link>
                </li>
                <li>
                    <router-link to="/export" class="nav-link text-white disabled" active-class="active">
                        <img src="@/assets/icons/export.svg" alt="Export" width="20px" class="me-2">
                        Export
                    </router-link>
                </li>
            </ul>
        </div>
    </div>
</template>

<script setup>
import {store} from '@/store.js';
</script>

<style scoped>
.disabled {
    opacity: 0.5;
    pointer-events: none;
}
</style>