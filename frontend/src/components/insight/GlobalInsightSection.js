import React from 'react';
import { Card } from 'antd';
import { BulbOutlined } from '@ant-design/icons';
import CommonInsightPanel from './CommonInsightPanel';

/**
 * 全局洞察总结组件
 */
const GlobalInsightSection = ({ reportData }) => {
  return (
    <Card 
      title={<><BulbOutlined /> 全局洞察总结</>} 
      className="card-container"
      headStyle={{ backgroundColor: '#000000', color: 'white' }}
    >      
      <CommonInsightPanel
        title="综合洞察分析"
        content={reportData.overall_insight || "暂无总体洞察数据"}
        type="success"
        icon={<BulbOutlined />}
      />
    </Card>
  );
};

export default GlobalInsightSection;
