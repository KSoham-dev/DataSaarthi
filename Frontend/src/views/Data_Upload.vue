<template>
    <div class="container mt-5">
        <h1 class="display-5 text-center mb-4">Upload Your Data</h1>
        <div class="card p-4" :class="{ 'pt-0': store.tableData.length > 0 }"
            style="max-width: 600px; margin-left: auto; margin-right:auto;">
            <div class="drop-area p-5 text-center border rounded-3"
                :class="{ 'border-primary bg-light': isDragging, 'border-danger': store.uploadError }"
                @dragover.prevent="handleDragOver" @dragleave.prevent="handleDragLeave" @drop.prevent="handleDrop"
                @click="openFileDialog" v-if="!store.cur_file_id">
                <input type="file" @change="handleFileSelect" ref="fileInput" class="d-none" accept=".csv" />
                <div class="upload-icon mb-3">
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor"
                        class="bi bi-cloud-arrow-up text-muted" viewBox="0 0 16 16">
                        <path fill-rule="evenodd"
                            d="M7.646 5.146a.5.5 0 0 1 .708 0l2 2a.5.5 0 0 1-.708.708L8.5 6.707V10.5a.5.5 0 0 1-1 0V6.707L6.354 7.854a.5.5 0 1 1-.708-.708z" />
                        <path
                            d="M4.406 3.342A5.53 5.53 0 0 1 8 2c2.69 0 4.923 2 5.166 4.579C14.758 6.804 16 8.137 16 9.773 16 11.569 14.502 13 12.687 13H3.781C1.708 13 0 11.366 0 9.318c0-1.763 1.266-3.223 2.942-3.593.143-.863.698-1.723 1.464-2.383zm.653.757c-.757.653-1.153 1.44-1.153 2.056v.448l-.445.049C2.064 6.805 1 7.952 1 9.318 1 10.785 2.23 12 3.781 12h8.906C13.98 12 15 10.988 15 9.773c0-1.216-1.02-2.228-2.313-2.228h-.5v-.5C12.188 4.825 10.328 3 8 3a4.53 4.53 0 0 0-2.941 1.1z" />
                    </svg>
                </div>
                <p class="text-muted mb-0">
                    Drag & drop a CSV file, or
                    <span class="fw-bold text-primary">browse</span>
                </p>
            </div>

            <div v-if="store.uploadError" class="alert alert-danger mt-3" role="alert">
                {{ store.uploadError }}
            </div>

            <div v-if="store.file" class="mt-4">
                <ul class="list-group">
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <div class="file-info text-truncate me-3">
                            <span class="file-name">{{ store.file.name }}</span>
                            <span class="d-block text-muted small">{{ formatFileSize(store.file.size) }}</span>
                        </div>
                        <button @click="store.removeFile()" type="button" class="btn-close"
                            aria-label="Remove"></button>
                    </li>
                </ul>
                <div class="d-grid mt-3">
                    <button @click="uploadFile" class="btn btn-primary" :disabled="isUploading">
                        <span v-if="isUploading" class="spinner-border spinner-border-sm" role="status"
                            aria-hidden="true"></span>
                        {{ isUploading ? ' Uploading...' : 'Upload File' }}
                    </button>
                </div>
            </div>

            <div v-if="store.cur_file_id" :class="{ 'mt-4': store.tableData.length === 0 }">
                <div class="d-grid mt-3 my-3">
                    <span class="fw-bold">
                        Uploaded Files:
                    </span>
                </div>
                <ul class="list-group">
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <div class="file-info text-truncate me-3">
                            <span class="file-name">{{ store.cur_file_name }}</span>
                            <span class="d-block text-muted small">{{ store.cur_file_size }}</span>
                        </div>
                        <button @click="deleteFile" type="button" class="btn-close" aria-label="Remove"></button>
                    </li>
                </ul>
            </div>
        </div>

        <div class="datadisplay mt-5">
            <div class="card p-4 pt-0 pe-0 mb-5"
                style="max-width: 600px; max-height: 600px; margin-left: auto; margin-right:auto; overflow: auto;">
                <div class="title mb-3 pt-3" style="position: sticky; top: 0; background-color: white;">
                    <h5 class="card-title display-6 fs-4">Data Preview (100 rows)</h5>
                </div>
                <table class="table table-striped">
                    <thead style="position: sticky; top: 0; background-color: white;">
                        <tr>
                            <th v-for="header in store.tableHeaders" :key="header">{{ header }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(row, index) in store.tableData.slice(0, 100)" :key="index">
                            <td v-for="header in store.tableHeaders" :key="header">{{ row[header] }}</td>
                        </tr>
                    </tbody>
                </table>
                <span v-if="store.tableData.length === 0" class="text-center w-100" style="color: red;">
                    Upload a CSV file to see the data preview.
                </span>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { store } from '@/store.js';
import { csvParser, formatFileSize } from '@/utils.js';

const fileInput = ref(null);
const isDragging = ref(false);
const isUploading = ref(false);

onMounted(() => {
    if (store.cur_file_id) {
        fetch(`http://127.0.0.1:8000/get_file/${store.cur_file_id}`)
            .then(resp => {
                if (!resp.ok) throw new Error('Failed to fetch initial file data.');
                return resp.json();
            })
            .then(data => {
                store.tableHeaders = data.columns || [];
                store.tableData = data.sample_data || [];
            })
            .catch(error => {
                console.error("Error fetching file data:", error);
                store.uploadError = "Could not load data for the existing file.";
            });
    }
});

const openFileDialog = () => {
    if (fileInput.value) {
        fileInput.value.value = '';
        fileInput.value.click();
    }
};

const handleFileSelect = (event) => {
    const selectedFile = event.target.files[0];
    addFile(selectedFile);
};

const handleDrop = (event) => {
    isDragging.value = false;
    const droppedFile = event.dataTransfer.files[0];
    addFile(droppedFile);
};

const addFile = (newFile) => {
    store.uploadError = '';
    if (!newFile) return;

    if (newFile.type.includes('csv') || newFile.name.endsWith('.csv')) {
        store.file = newFile;
    } else {
        store.file = null;
        store.uploadError = 'Invalid file type. Only CSV files are allowed.';
    }
};

const deleteFile = async () => {
    if (!store.cur_file_id) return;
    try {
        const resp = await fetch(`http://127.0.0.1:8000/remove_file/${store.cur_file_id}`, { method: "DELETE" });
        if (!resp.ok) throw new Error(resp.statusText);

        store.setCurFile(null, null, null);
        store.tableData = [];
        store.tableHeaders = [];
        store.uploadError = '';
        store.file = null;
    } catch (error) {
        console.error("Error deleting file:", error);
        store.uploadError = "Could not delete the file.";
    }
};

const handleDragOver = () => isDragging.value = true;
const handleDragLeave = () => isDragging.value = false;

const uploadFile = async () => {
    if (isUploading.value || !store.file) return;
    isUploading.value = true;
    store.uploadError = '';

    const formData = new FormData();
    formData.append('file', store.file);

    try {
        const resp = await fetch("http://127.0.0.1:8000/uploadfile", { method: "POST", body: formData });
        if (!resp.ok) throw new Error(resp.statusText);

        const data = await resp.json();

        const fileToUpload = store.file;
        const formattedSize = formatFileSize(fileToUpload.size);

        store.setCurFile(data.file_id, fileToUpload.name, formattedSize);

        const csvData = await csvParser(fileToUpload);
        store.tableHeaders = csvData.headers;
        store.tableData = csvData.data;

        store.file = null;
    } catch (error) {
        console.error("Error during upload process:", error);
        store.uploadError = `Upload process failed: ${error.message}`;
        store.file = null;
    } finally {
        isUploading.value = false;
    }
};
</script>

<style scoped>
.drop-area {
    border-style: dashed !important;
    transition: background-color 0.2s ease, border-color 0.2s ease;
    cursor: pointer;
}

.file-name {
    font-size: 0.9rem;
    font-weight: 500;
}
</style>
