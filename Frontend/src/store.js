import { reactive } from 'vue';

export const store = reactive({
    file : null,
    fileInput : null,

    pageNo: 1,

    cur_file_id : localStorage.getItem("current_file") || null,
    cur_file_name : localStorage.getItem("current_file_name") || null,
    cur_file_size : localStorage.getItem("current_file_size") || null,

    uploadError : '',
    csvErrorMessage : '',
    tableHeaders : [],
    tableData : [],

    setCurFile(cur_file_id, cur_file_name, cur_file_size) {
        this.cur_file_id = cur_file_id;
        this.cur_file_name = cur_file_name;
        this.cur_file_size = cur_file_size;

        localStorage.setItem("current_file", cur_file_id);
        localStorage.setItem("current_file_name", cur_file_name);
        localStorage.setItem("current_file_size", cur_file_size);
    },  

    resetlocalStorage() {
        localStorage.removeItem("current_file");
        localStorage.removeItem("current_file_name");
        localStorage.removeItem("current_file_size");
        this.cur_file_id = null;
        this.cur_file_name = null;
        this.cur_file_size = null;
    },

    removeFile(){
        store.file = null;
    }
    
});