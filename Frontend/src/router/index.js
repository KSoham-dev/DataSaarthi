import { createRouter, createWebHistory } from 'vue-router'
import DataUpload from '../views/Data_Upload.vue'
import Export from '../views/Export.vue'
import FeatureEngg from '../views/Feature_Engg.vue'
import EDA from '../views/EDA.vue'
import Model from '../views/Model_Training.vue'
import ModelEvaluation from '../views/Model_Eval.vue'
import ModelPredictions from '../views/Model_Preds.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Data Upload',
      component: DataUpload,
    },
    {
      path: '/EDA',
      name: 'EDA',
      component: EDA,
    },
    {
        path: '/FeatureEngg',
        name: 'Feature Engineering',
        component: FeatureEngg,
    },
    {
        path: '/Export',
        name: 'Export',
        component: Export,
    },
    {
        path: '/Training',
        name: 'Model Training',
        component: Model,
    },
    {
        path: '/Evaluation',
        name: 'Model Evaluation',
        component: ModelEvaluation,
    },
    {
        path: '/Predictions',
        name: 'Model Predictions',
        component: ModelPredictions,
    }

  ],
})

export default router
