/**
 * 数据结果相关类型定义
 */

// 数据结果类型
export interface DataResult {
  _id: string;
  data_id: string;
  project_code: string;
  solution: string;
  model: string;
  process_time: string;
  total_review: number;
  product_topics?: {
    total_stats?: {
      total_count?: number;
    };
  };
  all_stages_total_tokens?: number;
  top_topics_count?: number;
}

// 筛选选项类型
export interface FilterOptions {
  projectCodes: string[];
  solutions: string[];
  models: string[];
}

// 筛选条件类型
export interface Filters {
  project_code?: string;
  solution?: string;
  model?: string;
  date_from?: string;
  date_to?: string;
  [key: string]: string | undefined; // 索引签名，允许任意字符串键
}

// 分页类型
export interface Pagination {
  current: number;
  pageSize: number;
  total: number;
}

// API响应类型
export interface ApiResponse<T = any> {
  data: T;
  total?: number;
  success: boolean;
  message?: string;
}

// 数据结果查询参数类型
export interface DataResultParams {
  skip?: number;
  limit?: number;
  project_code?: string;
  solution?: string;
  model?: string;
  date_from?: string;
  date_to?: string;
  [key: string]: any; // 索引签名，允许任意字符串键
}
