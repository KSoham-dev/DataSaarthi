import { reactive } from 'vue';

export const store = reactive({
    file : null,
    fileInput : null,

    cur_file_id : localStorage.getItem("current_file"),
    cur_file_name : localStorage.getItem("current_file_name"),
    cur_file_size : localStorage.getItem("current_file_size"),

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
    }
});