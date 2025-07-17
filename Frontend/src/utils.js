import Papa from 'papaparse';

export const csvParser = (file) => {
    return new Promise((resolve, reject) => {
        if (!file) {
            return reject(new Error("No file provided to parser."));
        }
        Papa.parse(file, {
            header: true, skipEmptyLines: true,
            complete: (results) => {
                if (results.errors.length) return reject(new Error(results.errors[0].message));
                if (results.data.length > 0 && results.meta.fields) {
                    resolve({ headers: results.meta.fields, data: results.data });
                } else {
                    reject(new Error("CSV file is empty or has an invalid format."));
                }
            },
            error: (error) => reject(new Error(`Parsing Error: ${error.message}`))
        });
    });
};

export const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};