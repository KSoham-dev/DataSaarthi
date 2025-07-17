<template>
    <div class="container mt-5">
        <h1 class="display-5 text-center mb-4">Upload Your Data</h1>
        <div class="card p-4" :class="{'pt-0': tableData.length > 0}" style="max-width: 600px; margin-left: auto; margin-right:auto;">
            <!-- Drop Area -->
            <div
            class="drop-area p-5 text-center border rounded-3"
            :class="{ 'border-primary bg-light': isDragging, 'border-danger': uploadError }"
            @dragover.prevent="handleDragOver"
            @dragleave.prevent="handleDragLeave"
            @drop.prevent="handleDrop"
            @click="openFileDialog"
            v-if="!cur_file_id"
            >
            <input
                type="file"
                @change="handleFileSelect"
                ref="fileInput"
                class="d-none"
                accept=".csv"
            />
            <div class="upload-icon mb-3">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" class="bi bi-cloud-arrow-up text-muted" viewBox="0 0 16 16">
                <path fill-rule="evenodd" d="M7.646 5.146a.5.5 0 0 1 .708 0l2 2a.5.5 0 0 1-.708.708L8.5 6.707V10.5a.5.5 0 0 1-1 0V6.707L6.354 7.854a.5.5 0 1 1-.708-.708z"/>
                <path d="M4.406 3.342A5.53 5.53 0 0 1 8 2c2.69 0 4.923 2 5.166 4.579C14.758 6.804 16 8.137 16 9.773 16 11.569 14.502 13 12.687 13H3.781C1.708 13 0 11.366 0 9.318c0-1.763 1.266-3.223 2.942-3.593.143-.863.698-1.723 1.464-2.383zm.653.757c-.757.653-1.153 1.44-1.153 2.056v.448l-.445.049C2.064 6.805 1 7.952 1 9.318 1 10.785 2.23 12 3.781 12h8.906C13.98 12 15 10.988 15 9.773c0-1.216-1.02-2.228-2.313-2.228h-.5v-.5C12.188 4.825 10.328 3 8 3a4.53 4.53 0 0 0-2.941 1.1z"/>
                </svg>
            </div>
            <p class="text-muted mb-0">
                Drag & drop a CSV file, or
                <span class="fw-bold text-primary">browse</span>
            </p>
            </div>

            <!-- Error Message Display -->
            <div v-if="uploadError" class="alert alert-danger mt-3" role="alert">
            {{ uploadError }}
            </div>

            <!-- File Info and Upload Actions -->
            <div v-if="file" class="mt-4">
            <ul class="list-group">
                <li class="list-group-item d-flex justify-content-between align-items-center">
                <div class="file-info text-truncate me-3">
                    <span class="file-name">{{ file.name }}</span>
                    <span class="d-block text-muted small">{{ formatFileSize(file.size) }}</span>
                </div>
                <button @click="removeFile" type="button" class="btn-close" aria-label="Remove"></button>
                </li>
            </ul>
            <div class="d-grid mt-3">
                <button @click="uploadFile" class="btn btn-primary" :disabled="isUploading">
                    <span v-if="isUploading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    {{ isUploading ? ' Uploading...' : 'Upload File' }}
                </button>
            </div>
            </div>

            <div v-if="cur_file_id" :class="{ 'mt-4': tableData.length === 0 }">
            <div class="d-grid mt-3 my-3">
                <span @click="uploadFile" class="fw-bold">
                    Uploaded Files: 
                </span>
            </div>
            <ul class="list-group">
                <li class="list-group-item d-flex justify-content-between align-items-center">
                <div class="file-info text-truncate me-3">
                    <span class="file-name">{{cur_file_name}}</span>
                    <span class="d-block text-muted small">{{cur_file_size}}</span>
                </div>
                <button @click="deleteFile" type="button" class="btn-close" aria-label="Remove"></button>
                </li>
            </ul>
            </div>
        </div>

        <div class="datadisplay mt-5">
            <div class="card p-4 pt-0 pe-0 mb-5" style="max-width: 600px; max-height: 600px; margin-left: auto; margin-right:auto; overflow: auto;">
                <div class="title mb-3 pt-3" style="position: sticky; top: 0; background-color: white;">
                    <h5 class="card-title display-6 fs-4">Data Preview (100 rows)</h5>
                </div>
                <table class="table table-striped">
                    <thead style="position: sticky; top: 0; background-color: white;">
                        <tr>
                            <th v-for="header in tableHeaders" :key="header">{{ header }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(row, index) in tableData.slice(0,100)" :key="index">
                            <td v-for="header in tableHeaders" :key="header">{{ row[header] }}</td>
                        </tr>
                    </tbody>
                </table>
                <span v-if="tableData.length === 0" class="text-center w-100" style="color: red;">
                            Upload a CSV file to see the data preview.
                </span>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Papa from 'papaparse';

let allowedMimeTypes = [
  'text/csv',
];
let allowedExtensions = ['.csv'];

let file = ref(null);
let fileInput = ref(null);
let isDragging = ref(false);
let isUploading = ref(false);
let cur_file_id = localStorage.getItem("current_file");
let cur_file_name = localStorage.getItem("current_file_name");
let cur_file_size = localStorage.getItem("current_file_size");
let uploadError = ref('');
let csvErrorMessage = ref('');
let tableHeaders = ref([]);
let tableData = ref([]);

onMounted(() => {
  if (cur_file_id) {
    console.log("Current file ID:", cur_file_id);
    fetch(`http://127.0.0.1:8000/get_file/${cur_file_id}`)
      .then(resp => resp.json())
      .then(data => {
        console.log("Fetched file data:", data);
        tableHeaders.value = data.columns || [];
        tableData.value = data.sample_data || [];
        console.log("Table Headers:", tableHeaders.value);
        console.log("Table Data:", tableData.value);
      })
      .catch(error => {
        console.error("Error fetching file data:", error);
      });
  }
});

let openFileDialog = () => {
  if(fileInput.value) {
    fileInput.value.value = '';
  }
  fileInput.value.click();
};

let handleFileSelect = (event) => {
  let selectedFile = event.target.files[0];
  addFile(selectedFile);
};

let handleDrop = (event) => {
  isDragging.value = false;
  let droppedFile = event.dataTransfer.files[0];
  addFile(droppedFile);
};

let addFile = (newFile) => {
  uploadError.value = '';
  if (!newFile) {
    return;
  }

  let fileExtension = '.' + newFile.name.split('.').pop().toLowerCase();
  let isValidMime = allowedMimeTypes.includes(newFile.type);
  let isValidExt = allowedExtensions.includes(fileExtension);

  if (isValidMime || isValidExt) {
    file.value = newFile;
  } else {
    file.value = null;
    uploadError.value = `Invalid file type. Only ${allowedExtensions.join(', ')} are allowed.`;
  }
};

let deleteFile = () => {
    fetch(`http://127.0.0.1:8000/remove_file/${cur_file_id}`,{
        method: "DELETE"
    }).then(resp => {
        if (!resp.ok){
            throw new Error(resp.statusText);
        } else {
            console.log("File deleted successfully");
            localStorage.removeItem("current_file");
            localStorage.removeItem("current_file_name");
            localStorage.removeItem("current_file_size");
            window.location.reload();
        }
    }).catch(error => {
        console.error("Error deleting file:", error);
    });
};

const csvParser = (file) => {
  return new Promise((resolve, reject) => {
    if (!file) {
      return reject(new Error("No file provided to parser."));
    }
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const csvData = event.target.result;
        Papa.parse(csvData, {
          header: true,
          skipEmptyLines: true,
          complete: (results) => {
            if (results.errors.length > 0) {
              reject(new Error(results.errors[0].message));
            } else if (results.data.length > 0 && results.meta.fields) {
              resolve({
                headers: results.meta.fields,
                data: results.data
              });
            } else {
              reject(new Error("CSV file is empty or has an invalid format."));
            }
          },
        });
      } catch (error) {
        reject(error);
      }
    };
    reader.onerror = (event) => {
      reject(new Error("Failed to read the file."));
    };
    reader.readAsText(file);
  });
};


let removeFile = () => {
  file.value = null;
};

let handleDragOver = () => {
  isDragging.value = true;
};

let handleDragLeave = () => {
  isDragging.value = false;
};

let formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  let k = 1024;
  let sizes = ['Bytes', 'KB', 'MB', 'GB'];
  let i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

let uploadFile = () => {
  if (isUploading.value || !file.value) return;
  isUploading.value = true;

  console.log(`Uploading file: ${file.value.name}`);
  const formData = new FormData();
  formData.append('file', file.value);
  fetch("http://127.0.0.1:8000/uploadfile", {
    method: "POST",
    body: formData,
  }).then(resp => {
    if (resp.ok){
        return resp.json();
    } else{
        isUploading.value = false;
        throw new Error(resp.statusText);
    }
  }).then(async data =>{
    localStorage.setItem("current_file", data.file_id);
    localStorage.setItem("current_file_name", file.value.name);
    localStorage.setItem("current_file_size", formatFileSize(file.value.size));
    
    cur_file_id = localStorage.getItem("current_file");
    cur_file_name = localStorage.getItem("current_file_name");
    cur_file_size = localStorage.getItem("current_file_size");
    try{
        const csvData = await csvParser(file.value);
        tableHeaders.value = csvData.headers;
        tableData.value = csvData.data;
        console.log("CSV Data Parsed Successfully:", csvData);
    } catch (error) {
        console.error("Error parsing CSV file:", error);
        csvErrorMessage.value = "Error parsing CSV file. Please check the file format.";
        uploadError.value = csvErrorMessage.value;
        file = ref(null);
        return;
    }

    file = ref(null);
    console.log(tableHeaders.value, tableData.value);
  }).catch(error => {
        console.log(error);
        file = ref(null);
        uploadError.value = "Error Uploading File. Please Try Again"
  }).finally(() => {
    isUploading.value = false;
  })
 
}
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
