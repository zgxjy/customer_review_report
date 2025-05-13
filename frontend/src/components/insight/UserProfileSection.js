import React from 'react';
import { Card, Row, Col, Tag, Progress, Empty } from 'antd';
import { 
  UserOutlined, TeamOutlined, 
  EnvironmentOutlined, ShoppingOutlined, SmileOutlined,
  FallOutlined, AreaChartOutlined
} from '@ant-design/icons';
import { useReportTheme } from '../../context/ReportThemeContext';
import CommonInsightPanel from './CommonInsightPanel';

/**
 * 用户画像分析组件
 */
const UserProfileSection = ({ reportData }) => {
  // 使用主题上下文
  const { themeConfig } = useReportTheme();
  // 获取topN数量
  const topN = reportData.top_topics_count || 5;
  
  // Helper function to get stroke color based on type
  const getStrokeColor = (type) => {
    switch (type) {
      case 'thrill': return themeConfig.productAnalysis.positiveColor; // Green for thrill
      case 'pain': return themeConfig.productAnalysis.negativeColor;   // Red for pain
      case 'itch': return themeConfig.colors.info;   // Blue for itch
      default: return themeConfig.colors.primary;     // Default color
    }
  };
  
  // 数据处理函数 - 性别分布
  const formatGenderData = (data) => {
    if (!data || !data.user_profile || !data.user_profile.profiles || !data.user_profile.profiles.new_gender) return [];
    return data.user_profile.profiles.new_gender.map(item => ({
      name: item.value,
      value: parseInt(item.count, 10) || 0
    }));
  };
  
  // 数据处理函数 - 职业分布
  const formatOccupationData = (data) => {
    if (!data || !data.user_profile || !data.user_profile.profiles || !data.user_profile.profiles.new_occupation) return [];
    return data.user_profile.profiles.new_occupation.map(item => ({
      name: item.value,
      value: parseInt(item.count, 10) || 0
    }));
  };
  
  // 数据处理函数 - 消费场景
  const formatSceneData = (data) => {
    if (!data || !data.user_profile || !data.user_profile.profiles || !data.user_profile.profiles.new_consumption_scene) return [];
    return data.user_profile.profiles.new_consumption_scene.map(item => ({
      name: item.value,
      value: parseInt(item.count, 10) || 0
    }));
  };
  
  // 数据处理函数 - 消费频率
  const formatFrequencyData = (data) => {
    if (!data || !data.user_profile || !data.user_profile.profiles || !data.user_profile.profiles.new_consumption_frequency) return [];
    return data.user_profile.profiles.new_consumption_frequency.map(item => ({
      name: item.value,
      value: parseInt(item.count, 10) || 0
    }));
  };
  
  // 数据处理函数 - 消费爽点
  const formatThrillPointData = (data) => {
    if (!data || !data.user_profile || !data.user_profile.profiles || !data.user_profile.profiles.new_consumption_thrill_point) return [];
    return data.user_profile.profiles.new_consumption_thrill_point.map(item => ({
      name: item.value,
      value: parseInt(item.count, 10) || 0,
      summary: item.summary
    })).sort((a, b) => b.value - a.value).slice(0, topN);
  };
  
  // 数据处理函数 - 消费痛点
  const formatPainPointData = (data) => {
    if (!data || !data.user_profile || !data.user_profile.profiles || !data.user_profile.profiles.new_consumption_pain_point) return [];
    return data.user_profile.profiles.new_consumption_pain_point.map(item => ({
      name: item.value,
      value: parseInt(item.count, 10) || 0,
      summary: item.summary
    })).sort((a, b) => b.value - a.value).slice(0, topN);
  };
  
  // 数据处理函数 - 消费痒点
  const formatItchPointData = (data) => {
    if (!data || !data.user_profile || !data.user_profile.profiles || !data.user_profile.profiles.new_consumption_itch_point) return [];
    return data.user_profile.profiles.new_consumption_itch_point.map(item => ({
      name: item.value,
      value: parseInt(item.count, 10) || 0,
      summary: item.summary
    })).sort((a, b) => b.value - a.value).slice(0, topN);
  };
  

  
  return (
    <Card 
      title={<><UserOutlined /> 用户画像分析</>} 
      className="card-container"
      headStyle={{ backgroundColor: '#141414', color: 'rgba(255, 255, 255, 0.85)' }}
    >
      {/* AI洞察板块 */}
      <CommonInsightPanel
        title="用户画像洞察"
        content={reportData.user_profile_insight}
        type="success"
        icon={<UserOutlined />}
      />
      
      {/* 用户分布统计卡片式展示 */}
      <Row gutter={[24, 24]} className="user-attribute-section">
        {/* 性别分布 */}
        <Col xs={24} sm={12} md={6}>
          <Card className="attribute-card" bordered={false} style={{ backgroundColor: '#1E1E1E', border: '1px solid rgba(138, 230, 92, 0.2)', color: '#FFFFFF' }}>
            <h3 className="attribute-title" style={{ color: '#8AE65C', borderBottom: '1px solid rgba(138, 230, 92, 0.3)' }}><UserOutlined /> 性别分布</h3>
            <div className="bar-chart-container">
              {formatGenderData(reportData).sort((a, b) => b.value - a.value).map((item, index) => {
                // 计算百分比
                const total = formatGenderData(reportData).reduce((sum, i) => sum + i.value, 0) || 1;
                const percent = ((item.value / total) * 100).toFixed(1);
                return (
                  <div key={index} className="data-item">
                    <div className="data-label">
                      <Tag color="#1890ff" className="label-tag">{item.name}</Tag>
                      <span className="item-percent">{percent}%</span>
                    </div>
                    <Progress 
                      percent={parseFloat(percent)} 
                      strokeColor={{
                        '0%': '#1890ff',
                        '100%': '#69c0ff',
                      }}
                      strokeWidth={8}
                      format={() => `${item.value}人`}
                    />
                  </div>
                );
              })}
            </div>
          </Card>
        </Col>
        
        {/* 职业分布 */}
        <Col xs={24} sm={12} md={6}>
          <Card className="attribute-card" bordered={false} style={{ backgroundColor: '#1E1E1E', border: '1px solid rgba(138, 230, 92, 0.2)', color: '#FFFFFF' }}>
            <h3 className="attribute-title" style={{ color: '#8AE65C', borderBottom: '1px solid rgba(138, 230, 92, 0.3)' }}><TeamOutlined /> 职业分布</h3>
            <div className="bar-chart-container">
              {formatOccupationData(reportData).sort((a, b) => b.value - a.value).slice(0, 5).map((item, index) => {
                // 计算百分比
                const total = formatOccupationData(reportData).reduce((sum, i) => sum + i.value, 0) || 1;
                const percent = ((item.value / total) * 100).toFixed(1);
                const colors = ['#722ed1', '#7046e0', '#6d62ee', '#6b7bfc', '#688ffc'];
                return (
                  <div key={index} className="data-item">
                    <div className="data-label">
                      <Tag color={colors[index % colors.length]} className="label-tag">{item.name}</Tag>
                      <span className="item-percent">{percent}%</span>
                    </div>
                    <Progress 
                      percent={parseFloat(percent)} 
                      strokeColor={{
                        '0%': colors[index % colors.length],
                        '100%': '#d3adf7',
                      }}
                      strokeWidth={8}
                      format={() => `${item.value}人`}
                    />
                  </div>
                );
              })}
            </div>
          </Card>
        </Col>

          {/* 消费场景 */}
        <Col xs={24} sm={12} md={6}>
          <Card className="attribute-card" bordered={false} style={{ backgroundColor: '#1E1E1E', border: '1px solid rgba(138, 230, 92, 0.2)', color: '#FFFFFF' }}>
            <h3 className="attribute-title" style={{ color: '#8AE65C', borderBottom: '1px solid rgba(138, 230, 92, 0.3)' }}><EnvironmentOutlined /> 消费场景</h3>
            <div className="bar-chart-container">
              {formatSceneData(reportData).sort((a, b) => b.value - a.value).slice(0, 5).map((item, index) => {
                // 计算百分比
                const total = formatSceneData(reportData).reduce((sum, i) => sum + i.value, 0) || 1;
                const percent = ((item.value / total) * 100).toFixed(1);
                return (
                  <div key={index} className="data-item">
                    <div className="data-label">
                      <Tag color="#52c41a" className="label-tag">{item.name}</Tag>
                      <span className="item-percent">{percent}%</span>
                    </div>
                    <Progress 
                      percent={parseFloat(percent)} 
                      strokeColor={{
                        '0%': '#52c41a',
                        '100%': '#95de64',
                      }}
                      strokeWidth={8}
                      format={() => `${item.value}人`}
                    />
                  </div>
                );
              })}
            </div>
          </Card>
        </Col>
        
        {/* 消费频率 */}
        <Col xs={24} sm={12} md={6}>
          <Card className="attribute-card" bordered={false} style={{ backgroundColor: '#1E1E1E', border: '1px solid rgba(138, 230, 92, 0.2)', color: '#FFFFFF' }}>
            <h3 className="attribute-title" style={{ color: '#8AE65C', borderBottom: '1px solid rgba(138, 230, 92, 0.3)' }}><ShoppingOutlined /> 消费频率</h3>
            <div className="bar-chart-container">
              {formatFrequencyData(reportData).sort((a, b) => b.value - a.value).map((item, index) => {
                // 计算百分比
                const total = formatFrequencyData(reportData).reduce((sum, i) => sum + i.value, 0) || 1;
                const percent = ((item.value / total) * 100).toFixed(1);
                const colors = ['#fa8c16', '#faad14', '#ffc53d', '#ffec3d'];
                return (
                  <div key={index} className="data-item">
                    <div className="data-label">
                      <Tag color={colors[index % colors.length]} className="label-tag">{item.name}</Tag>
                      <span className="item-percent">{percent}%</span>
                    </div>
                    <Progress 
                      percent={parseFloat(percent)} 
                      strokeColor={{
                        '0%': colors[index % colors.length],
                        '100%': '#ffd591',
                      }}
                      strokeWidth={8}
                      format={() => `${item.value}人`}
                    />
                  </div>
                );
              })}
            </div>
          </Card>
        </Col>

      </Row>
      
      {/* 消费爽点 */}
      <div className="summary-chart-section">
        <h3 style={{ color: '#FFFFFF' }}><SmileOutlined style={{ color: '#52c41a' }} /> 消费爽点TOP{topN}分析</h3>
        {formatThrillPointData(reportData).length === 0 ? (
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无数据" />
        ) : (
          formatThrillPointData(reportData).map((item, index) => (
            <div key={index} className="insight-list-item">
              {/* 第一部分：排名标签 */}
              <div className="rank-container">
                <Tag className={`ranking-tag ranking-tag-thrill`}>{index + 1}</Tag>
              </div>
              
              {/* 第二部分：要点名称和条形图（上下排列） */}
              <div className="name-progress-container">
                <div className="item-name-container">
                  <span className="item-name">{item.name}</span>
                </div>
                <div className="progress-count-container">
                  <Progress
                    percent={(item.value / Math.max(...formatThrillPointData(reportData).map(i => i.value)) * 100) || 0}
                    strokeColor={getStrokeColor('thrill')}
                    showInfo={false}
                    className="short-progress-bar"
                  />
                  <span className="item-count">{item.value}次</span>
                </div>
              </div>
              
              {/* 第三部分：摘要 */}
              {item.summary && (
                <div className="summary-container">
                  <div className={`item-summary item-summary-thrill`}>
                    {item.summary}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
      
      {/* 消费痛点 */}
      <div className="summary-chart-section">
        <h3 style={{ color: '#FFFFFF' }}><FallOutlined style={{ color: '#f5222d' }} /> 消费者痛点TOP{topN}分析</h3>
        {formatPainPointData(reportData).length === 0 ? (
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无数据" />
        ) : (
          formatPainPointData(reportData).map((item, index) => (
            <div key={index} className="insight-list-item">
              {/* 第一部分：排名标签 */}
              <div className="rank-container">
                <Tag className={`ranking-tag ranking-tag-pain`}>{index + 1}</Tag>
              </div>
              
              {/* 第二部分：要点名称和条形图（上下排列） */}
              <div className="name-progress-container">
                <div className="item-name-container">
                  <span className="item-name">{item.name}</span>
                </div>
                <div className="progress-count-container">
                  <Progress
                    percent={(item.value / Math.max(...formatPainPointData(reportData).map(i => i.value)) * 100) || 0}
                    strokeColor={getStrokeColor('pain')}
                    showInfo={false}
                    className="short-progress-bar"
                  />
                  <span className="item-count">{item.value}次</span>
                </div>
              </div>
              
              {/* 第三部分：摘要 */}
              {item.summary && (
                <div className="summary-container">
                  <div className={`item-summary item-summary-pain`}>
                    {item.summary}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
      
      {/* 消费痒点 */}
      <div className="summary-chart-section">
        <h3 style={{ color: '#FFFFFF' }}><AreaChartOutlined style={{ color: '#1890ff' }} /> 消费者痒点TOP{topN}分析</h3>
        {formatItchPointData(reportData).length === 0 ? (
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无数据" />
        ) : (
          formatItchPointData(reportData).map((item, index) => (
            <div key={index} className="insight-list-item">
              {/* 第一部分：排名标签 */}
              <div className="rank-container">
                <Tag className={`ranking-tag ranking-tag-itch`}>{index + 1}</Tag>
              </div>
              
              {/* 第二部分：要点名称和条形图（上下排列） */}
              <div className="name-progress-container">
                <div className="item-name-container">
                  <span className="item-name">{item.name}</span>
                </div>
                <div className="progress-count-container">
                  <Progress
                    percent={(item.value / Math.max(...formatItchPointData(reportData).map(i => i.value)) * 100) || 0}
                    strokeColor={getStrokeColor('itch')}
                    showInfo={false}
                    className="short-progress-bar"
                  />
                  <span className="item-count">{item.value}次</span>
                </div>
              </div>
              
              {/* 第三部分：摘要 */}
              {item.summary && (
                <div className="summary-container">
                  <div className={`item-summary item-summary-itch`}>
                    {item.summary}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </Card>
  );
};

export default UserProfileSection;
