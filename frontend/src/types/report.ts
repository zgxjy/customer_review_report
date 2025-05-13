// 报告数据类型定义

// 总体统计数据
export interface TotalStats {
  total_count: number;
  good_rate: number;
  neutral_bad_rate: number;
}

// 话题数据
export interface Topic {
  name: string;
  count: number;
  good_count: number;
  bad_count: number;
  satisfaction_rate: number;
  mention_rate: number;
  summary?: string;
}

// 产品话题数据
export interface ProductTopics {
  total_stats: TotalStats;
  topics: Topic[];
}

// 用户属性数据项
export interface ProfileItem {
  value: string;
  count: number;
}

// 用户画像数据
export interface UserProfile {
  gender: ProfileItem[];
  occupation: ProfileItem[];
  consumption_scene: ProfileItem[];
  consumption_frequency: ProfileItem[];
  consumption_thrill_point: ProfileItem[];
  consumption_pain_point: ProfileItem[];
  consumption_itch_point: ProfileItem[];
  top_profile?: {
    new_gender?: ProfileItem;
    new_occupation?: ProfileItem;
    new_consumption_scene?: ProfileItem;
    new_consumption_frequency?: ProfileItem;
    new_consumption_thrill_point?: ProfileItem;
    new_consumption_pain_point?: ProfileItem;
    new_consumption_itch_point?: ProfileItem;
  };
}

// 四象限数据项
export interface QuadrantItem {
  name: string;
  x: number;  // 提及率
  y: number;  // 满意度
  count: number;
  quadrant: number;
  summary?: string;
}

// 报告数据
export interface ReportData {
  id: string;
  project_code: string;
  solution: string;
  model: string;
  process_time: string;
  total_review: number;
  top_topics_count: number;
  product_topics: ProductTopics;
  user_profile: UserProfile;
  topic_insight: string;
  user_profile_insight: string;
  overall_insight: string;
}
