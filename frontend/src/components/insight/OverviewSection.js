import React from 'react';
import { Card, Row, Col } from 'antd';
import { 
  TeamOutlined, SoundOutlined,  UserOutlined, SmileOutlined, FrownOutlined
} from '@ant-design/icons';

/**
 * 总体概览组件 - 展示六个关键指标
 */
const OverviewSection = ({ reportData }) => {
  // 计算好评率和差评率的百分比
  const goodRate = ((reportData.product_topics?.total_stats?.good_rate || 0) * 100).toFixed(2);
  const badRate = ((reportData.product_topics?.total_stats?.neutral_bad_rate || 0) * 100).toFixed(2);
  
  // 数据处理
  
  return (
    <Card 
      title={<><SoundOutlined /> 总体概览</>} 
      className="card-container overview-section"
      headStyle={{ backgroundColor: '#141414', color: 'white' }}
    >
      <Row gutter={[24, 24]} className="overview-stats-row">
        {/* 总评论数 */}
        <Col xs={12} sm={12} md={6} lg={6} flex={1}>
          <div className="stat-card-transparent">
            <div className="stat-icon">
              <TeamOutlined style={{ color: '#52c41a' }} />
            </div>
            <div className="stat-content">
              <div className="stat-title">总评论数</div>
              <div className="stat-value" style={{ color: '#52c41a' }}>{reportData.total_review}</div>
            </div>
          </div>
        </Col>
        
        {/* 总话题数 */}
        <Col xs={12} sm={12} md={6} lg={6} flex={1}>
          <div className="stat-card-transparent">
            <div className="stat-icon">
              <SoundOutlined style={{ color: '#1890ff' }} />
            </div>
            <div className="stat-content">
              <div className="stat-title">总话题数</div>
              <div className="stat-value" style={{ color: '#1890ff' }}>{reportData.product_topics?.total_stats?.total_count || 0}</div>
            </div>
          </div>
        </Col>
        
        {/* 话题好评占比 */}
        <Col xs={12} sm={12} md={6} lg={6} flex={1}>
          <div className="stat-card-transparent">
            <div className="stat-icon">
              <span role="img" aria-label="thumbs-up" style={{ fontSize: '20px' }}>👍</span>
            </div>
            <div className="stat-content">
              <div className="stat-title">好评率</div>
              <div className="stat-value" style={{ color: '#52c41a' }}>
                {goodRate}%
              </div>
            </div>
          </div>
        </Col>
        
        {/* 话题差评占比 */}
        <Col xs={12} sm={12} md={6} lg={6} flex={1}>
          <div className="stat-card-transparent">
            <div className="stat-icon">
              <span role="img" aria-label="thumbs-down" style={{ fontSize: '20px' }}>👎</span>
            </div>
            <div className="stat-content">
              <div className="stat-title">差评率</div>
              <div className="stat-value" style={{ color: '#ff7a45' }}>
                {badRate}%
              </div>
            </div>
          </div>
        </Col>
      </Row>

    <Row gutter={[24, 24]} className="overview-stats-row">
           
        {/* 主要性别 */}
        <Col xs={12} sm={12} md={6} lg={6} flex={1}>
          <div className="stat-card-transparent">
            <div className="stat-icon">
              <UserOutlined style={{ color: '#52c41a' }} />
            </div>
            <div className="stat-content">
              <div className="stat-title">主要性别</div>
              <div className="stat-value" style={{ color: '#52c41a' }}>
                {reportData.user_profile?.top_profile?.new_gender?.value || '未知'}
              </div>
            </div>
          </div>
        </Col>

        {/* 主要用户 */}
        <Col xs={12} sm={12} md={6} lg={6} flex={1}>
          <div className="stat-card-transparent">
            <div className="stat-icon">
              <UserOutlined style={{ color: '#52c41a' }} />
            </div>
            <div className="stat-content">
              <div className="stat-title">主要用户</div>
              <div className="stat-value" style={{ color: '#52c41a' }}>
                {reportData.user_profile?.top_profile?.new_occupation?.value || '未知'}
              </div>
            </div>
          </div>
        </Col>
        
        {/* 主要爆点 */}
        <Col xs={12} sm={12} md={6} lg={6} flex={1}>
          <div className="stat-card-transparent">
            <div className="stat-icon">
              <SmileOutlined style={{ color: '#ff7a45' }} />
            </div>
            <div className="stat-content">
              <div className="stat-title">主要爆点</div>
              <div className="stat-value" style={{ color: '#ff7a45' }}>
                {reportData.user_profile?.top_profile?.new_consumption_thrill_point?.value || '未知'}
              </div>
            </div>
          </div>
        </Col>

        {/* 主要痛点 */}
        <Col xs={12} sm={12} md={6} lg={6} flex={1}>
          <div className="stat-card-transparent">
            <div className="stat-icon">
              <FrownOutlined style={{ color: '#ff7a45' }} />
            </div>
            <div className="stat-content">
              <div className="stat-title">主要痛点</div>
              <div className="stat-value" style={{ color: '#ff7a45' }}>
                {reportData.user_profile?.top_profile?.new_consumption_pain_point?.value || '未知'}
              </div>
            </div>
          </div>
        </Col>
    </Row>
    </Card>
  );
};

export default OverviewSection;
