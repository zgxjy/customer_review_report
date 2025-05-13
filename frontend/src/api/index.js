import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    console.error('请求错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('响应错误:', error);
    return Promise.reject(error);
  }
);

// 数据结果相关API
export const dataResultApi = {
  // 获取数据结果列表
  getDataResults: (params) => {
    return api.get('/data_result', { params });
  },
  
  // 获取单个数据结果详情
  getDataResultById: (id) => {
    return api.get(`/data_result/${id}`);
  },
  
  // 获取项目代码列表
  getProjectCodes: () => {
    return api.get('/data_result/project_codes');
  },
  
  // 获取解决方案列表
  getSolutions: () => {
    return api.get('/data_result/solutions');
  },
  
  // 获取模型列表
  getModels: () => {
    return api.get('/data_result/models');
  }
};

export default api;
