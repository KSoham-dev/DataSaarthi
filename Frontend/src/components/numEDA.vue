<template>
    <div class="container DescriptiveStatsDiv mt-5" v-if="descriptiveStats && store.cur_file_id">
        <div class="row m-2 mb-4">
            <h1 class="display-6 pe-2 fs-2">{{ Dtype }}</h1>
        </div>
        <div class="row">
            <div class="col-md-7">
                <div class="card p-4 pt-0 mb-5 display" :class="{ overflow: descriptiveStats && Object.keys(descriptiveStats).length > 5 }">
                    <div class="title mb-3 pt-3">
                        <h5 class="card-title display-6 fs-4 pb-4">Descriptive Statistics</h5>
                        <table class="table table-bordered table-striped">
                            <thead>
                                <tr>
                                    <th> Stats </th>
                                    <th v-for="vName in Object.keys(descriptiveStats)" :key="vName">{{ vName }}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="statName in Object.keys(Object.values(descriptiveStats)[0])" :key="statName">
                                    <td>{{ statName }}</td>
                                    <td v-for="variableName in Object.keys(descriptiveStats)" :key="variableName">{{
                                        toFixednew(descriptiveStats[variableName][statName]) }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <div class="col-md-5">
                <div class="card p-2 pt-0 mb-5 display">
                    <div class="title mb-3 pt-3">
                        <h5 class="card-title display-6 fs-4">Correlation Matrix</h5>
                        <img v-if="corr_mat_url" :src="corr_mat_url" alt="Correlation Matrix" width="101%" class="pt-2">
                        <span v-else class="text-center w-100" style="color: red;">
                            Correlation matrix not available.
                        </span>
                    </div>
                </div>
            </div>
        </div>
        <div class="row" v-if="box_plot_url && hist_url">
            <div class="col-md-6">
                <div class="card p-2 pt-0 mb-5 display">
                    <div class="title mb-3 pt-3">
                        <h5 class="card-title display-6 fs-4">Box Plots</h5>
                        <img v-if="box_plot_url" :src="box_plot_url" alt="Box Plots" width="101%" class="pt-2">
                        <span v-else class="text-center w-100" style="color: red;">
                            Box plots not available.
                        </span>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card p-2 pt-0 mb-5 display">
                    <div class="title mb-3 pt-3">
                        <h5 class="card-title display-6 fs-4">Histograms</h5>
                        <img v-if="hist_url" :src="hist_url" alt="Histograms" width="101%" class="pt-2" height="350px">
                        <span v-else class="text-center w-100" style="color: red;">
                            Histograms not available.
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { store } from '@/store.js';
import { onMounted, ref } from 'vue';

const props = defineProps({
    descriptiveStats: Object,
    corr_mat_url: String,
    box_plot_url: String,
    hist_url: String,
    Dtype: String,
});

const toFixednew = (value) => {
    const num = parseFloat(value);
    if (!isNaN(num)) {
        return num.toFixed(2);
    }
    return value;
};

</script>

<style scoped>
.display {
    max-width: 600px;
    max-height: 600px;
    margin-left: auto;
    margin-right: auto;
    min-height: 480px;
}

.overflow {
    overflow: auto;
}

@media screen and (max-width: 768px) {
    .display {
        max-width: 350px;
        overflow: auto;
    }

}
</style>