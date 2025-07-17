# DataSaarthi: Your End-to-End Machine Learning Companion

A modern, web-based platform designed to streamline the entire machine learning workflow, from data ingestion to model deployment.

## About The Project

DataSaarthi is an integrated environment that empowers data scientists and ML enthusiasts to manage the complete machine learning lifecycle through an intuitive web interface. Built with a powerful backend and a responsive frontend, it eliminates the need to switch between multiple tools for data analysis, preprocessing, training, and validation.

## Key Features

DataSaarthi offers a comprehensive suite of tools covering every stage of the ML pipeline:

*   **Data Upload:** Seamlessly upload your datasets (CSV format) directly through the browser.
*   **Exploratory Data Analysis (EDA):** Instantly generate descriptive statistics, visualize data distributions, and understand key characteristics of your dataset.
*   **Feature Engineering:** Preprocess your data with essential techniques like handling missing values, encoding categorical variables, and scaling numerical features.
*   **Model Training:** Train various classification and regression models from the Scikit-learn library on your prepared data with just a few clicks.
*   **Model Validation:** Evaluate model performance using standard metrics (e.g., Accuracy, F1-Score, R², MSE) and visualize results with tools like confusion matrices.
*   **Model Export:** Once satisfied with a model, export it as a standard `.pkl` file, ready for deployment in production environments.

## Tech Stack

This project is built using a modern, decoupled architecture with a focus on performance and user experience.

*   **Frontend:**
    *   **Vue.js 3:** A progressive JavaScript framework for building the user interface.
    *   **Bootstrap 5:** For responsive design and pre-built UI components.
    *   **PapaParse:** For fast, in-browser CSV file parsing.

*   **Backend:**
    *   **FastAPI:** A high-performance Python web framework for building the API.
    *   **Uvicorn:** An ASGI server to run the FastAPI application.
    *   **Pydantic:** For robust data validation and settings management.

*   **Machine Learning & Data Processing:**
    *   **Scikit-learn:** The core library for all machine learning models and preprocessing tasks.
    *   **Pandas:** For efficient data manipulation and analysis on the backend.
    *   **NumPy:** For fundamental numerical computations.

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

Ensure you have Node.js, npm, and Anaconda/Miniconda installed on your system.

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/DataSaarthi.git
    cd DataSaarthi
    ```

2.  **Setup the Backend (FastAPI):**
    ```sh
    # Navigate to the backend directory
    cd backend

    # Create and activate a new conda environment (e.g., named 'datasaarthi_env')
    conda create --name datasaarthi_env
    conda activate datasaarthi_env

    # Install Python dependencies
    pip install -r requirements.txt
    ```

3.  **Setup the Frontend (Vue.js):**
    ```sh
    # Navigate to the frontend directory from the root
    cd frontend

    # Install NPM packages
    npm install
    ```

### Running the Application

1.  **Start the FastAPI Backend:**
    From the `backend` directory (with your conda environment activated), run:
    ```sh
    uvicorn main:app --reload
    ```
    The backend will be running at `http://127.0.0.1:8000`.

2.  **Start the Vue.js Frontend:**
    In a separate terminal, from the `frontend` directory, run:
    ```sh
    npm run dev
    ```
    The frontend will be available at `http://localhost:5173`.

## Typical Workflow

A user journey through DataSaarthi typically follows these steps:

1.  **Upload Data:** Begin by dragging and dropping or browsing for a CSV file on the main upload page.
2.  **Analyze (EDA):** Once the data is uploaded, navigate to the EDA section to view statistics, column types, and visualizations to understand the data's structure.
3.  **Engineer Features:** Select features and a target variable. Apply preprocessing steps like imputation or scaling.
4.  **Train Model:** Choose a machine learning algorithm (e.g., Logistic Regression, Random Forest), set its parameters, and click "Train."
5.  **Validate Results:** Review the model's performance metrics and visualizations to determine its effectiveness.
6.  **Export:** If the model meets your criteria, export it as a `.pkl` file for future use.