import React from 'react';
import { Card, Row, Col, Alert, Divider, Tag, Progress, Empty} from 'antd';
import MermaidQuadrantChart from '../chart/MermaidQuadrantChart';
import { BarChartOutlined, BulbOutlined, CheckCircleOutlined, CloseCircleOutlined, DotChartOutlined, AppstoreOutlined, RiseOutlined, FallOutlined, AreaChartOutlined, ShoppingOutlined} from '@ant-design/icons';
import CommonInsightPanel from './CommonInsightPanel';
import './InsightPanel.css';

/**
 * 产品话题分析组件
 */
const ProductAnalysisSection = ({ reportData }) => {
  // 获取topN数量
  const topN = reportData.top_topics_count || 5;
  
  // 数据处理函数 - 话题好评数量
  const formatTopicGoodRateData = (data) => {
    const topicsObj = data?.product_topics?.topics || {};
    const topN = data?.top_topics_count || 5;
    
    // 将对象转换为数组，只选择有好评摘要的话题
    const topicsArray = Object.entries(topicsObj)
      .filter(([_, stats]) => stats.好评摘要) // 只选择有好评摘要的话题
      .map(([name, stats]) => ({
        name,
        value: stats.好评 || 0,  // 使用实际好评数而不是占比
        summary: stats.好评摘要
      }));
    
    // 按好评数量降序排序，取TopN
    return topicsArray
      .sort((a, b) => b.value - a.value)
      .slice(0, topN);
  };
  
  // 数据处理函数 - 话题差评数量
  const formatTopicBadRateData = (data) => {
    const topicsObj = data?.product_topics?.topics || {};
    const topN = data?.top_topics_count || 5;
    
    // 将对象转换为数组，只选择有中差评摘要的话题
    const topicsArray = Object.entries(topicsObj)
      .filter(([_, stats]) => stats.中差评摘要) // 只选择有中差评摘要的话题
      .map(([name, stats]) => ({
        name,
        value: (stats.差评 || 0) + (stats.中评 || 0),  // 使用实际差评数和中评数之和
        summary: stats.中差评摘要
      }));
    
    // 按差评数量降序排序，取TopN
    return topicsArray
      .sort((a, b) => b.value - a.value)
      .slice(0, topN);
  };
  
  // 数据处理函数 - 四象限数据
  const formatQuadrantData = (data) => {
    const topicsObj = data?.product_topics?.topics || {};
    const totalReview = data?.total_review || 1;
    
    // 获取后端计算的平均提及率和满意度
    const avgX = data?.product_topics?.total_stats?.avg_mention_rate * 100 || 0;
    const avgY = data?.product_topics?.total_stats?.avg_satisfaction_rate * 100 || 0;
    
    // 将对象转换为数组
    const topicsArray = Object.entries(topicsObj).map(([name, stats]) => ({
      name,
      x: (stats.提及率 || (stats.总数 / totalReview)) * 100, // 提及率
      y: (stats.好评占比 || (stats.好评 / (stats.总数 || 1))) * 100, // 满意度
      count: stats.总数 || 0,
      // 使用后端计算的象限信息
      quadrant: stats.quadrant || 0
    }));
  
    // 过滤掉总数过少的话题
    const filteredTopics = topicsArray
      .filter(item => item.count > 10 && item.quadrant > 0)
      .sort((a, b) => b.count - a.count)
      .slice(0, 15);
    
    // 添加平均值信息，不需要再次计算象限
    return filteredTopics.map(item => {
      return {
        ...item,
        avgX,
        avgY
      };
    });
  };
  
  // 生成四象限图总结
  const generateQuadrantSummary = (data) => {
    // 优先使用quadrant_insight作为四象限图分析的总结
    if (data?.quadrant_insight) {
      return data.quadrant_insight;
    }
    
    // 如果没有quadrant_insight，则使用topic_insight
    if (data?.topic_insight) {
      return data.topic_insight;
    }
    
    // 获取四象限数据
    const quadrantData = formatQuadrantData(data);
    const avgX = quadrantData[0]?.avgX.toFixed(1) || 0;
    const avgY = quadrantData[0]?.avgY.toFixed(1) || 0;
    
    // 生成不同象限的话题列表
    const q1 = quadrantData.filter(item => item.quadrant === 1).map(item => item.name).join('、');
    const q2 = quadrantData.filter(item => item.quadrant === 2).map(item => item.name).join('、');
    const q3 = quadrantData.filter(item => item.quadrant === 3).map(item => item.name).join('、');
    const q4 = quadrantData.filter(item => item.quadrant === 4).map(item => item.name).join('、');
    
    return `此四象限图展示了各话题的提及率与满意度关系，使用平均提及率(${avgX}%)和平均好评率(${avgY}%)划分象限。

• 右上象限(优势话题): ${q1 || '无'}
• 右下象限(需改进话题): ${q2 || '无'}
• 左上象限(潜力话题): ${q3 || '无'}
• 左下象限(次要话题): ${q4 || '无'}

建议重点关注需改进话题，并发挥优势话题的优势。`;
  };
  
  // 准备四象限数据
  const quadrantData = formatQuadrantData(reportData);
  
  return (
    <Card 
      title={<><AppstoreOutlined /> 产品分析</>} 
      className="card-container product-analysis-section"
      headStyle={{ backgroundColor: '#141414', color: 'rgba(255, 255, 255, 0.85)' }}
    >
      {/* AI洞察板块 */}
      <CommonInsightPanel
        title="产品洞察"
        content={reportData.topic_insight}
        type="warning"
        icon={<ShoppingOutlined />}
      />
      
      {/* 话题好评占比 */}
      <div className="summary-chart-section" style={{ backgroundColor: 'rgba(25, 25, 25, 0.8)', border: '1px solid rgba(138, 230, 92, 0.15)' }}>
        <h3 style={{ color: '#FFFFFF' }}><span role="img" aria-label="thumbs-up" style={{ marginRight: '8px', fontSize: '16px' }}>👍</span> 话题好评数量TOP{topN}分析</h3>
        {formatTopicGoodRateData(reportData).length === 0 ? (
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无数据" />
        ) : (
          formatTopicGoodRateData(reportData).map((item, index) => (
            <div key={index} className="insight-list-item">
              {/* 第一部分：排名标签 */}
              <div className="rank-container">
                <Tag className="ranking-tag" style={{ backgroundColor: '#52c41a' }}>{index + 1}</Tag>
              </div>
              
              {/* 第二部分：要点名称和条形图（上下排列） */}
              <div className="name-progress-container">
                <div className="item-name-container">
                  <span className="item-name">{item.name}</span>
                </div>
                <div className="progress-count-container">
                  <Progress
                    percent={(item.value / Math.max(...formatTopicGoodRateData(reportData).map(i => i.value)) * 100) || 0}
                    strokeColor="#52c41a"
                    showInfo={false}
                    className="short-progress-bar"
                  />
                  <span className="item-count">{item.value}次</span>
                </div>
              </div>
              
              {/* 第三部分：摘要 */}
              {item.summary && (
                <div className="summary-container">
                  <div className="item-summary" style={{ color: '#e0e0e0', backgroundColor: 'rgba(82, 196, 26, 0.1)', border: '1px solid rgba(82, 196, 26, 0.2)', padding: '8px', borderRadius: '4px', marginTop: '8px' }}>
                    {item.summary || "该话题在用户评价中表现良好，用户普遍认可。"}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
      
      {/* 话题差评占比 */}
      <div className="summary-chart-section" style={{ backgroundColor: 'rgba(25, 25, 25, 0.8)', border: '1px solid rgba(138, 230, 92, 0.15)' }}>
        <h3 style={{ color: '#FFFFFF' }}><span role="img" aria-label="thumbs-down" style={{ marginRight: '8px', fontSize: '16px' }}>👎</span> 话题差评数量TOP{topN}分析</h3>
        {formatTopicBadRateData(reportData).length === 0 ? (
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无数据" />
        ) : (
          formatTopicBadRateData(reportData).map((item, index) => (
            <div key={index} className="insight-list-item">
              {/* 第一部分：排名标签 */}
              <div className="rank-container">
                <Tag className="ranking-tag" style={{ backgroundColor: '#ff4d4f' }}>{index + 1}</Tag>
              </div>
              
              {/* 第二部分：要点名称和条形图（上下排列） */}
              <div className="name-progress-container">
                <div className="item-name-container">
                  <span className="item-name">{item.name}</span>
                </div>
                <div className="progress-count-container">
                  <Progress
                    percent={(item.value / Math.max(...formatTopicBadRateData(reportData).map(i => i.value)) * 100) || 0}
                    strokeColor="#ff4d4f"
                    showInfo={false}
                    className="short-progress-bar"
                  />
                  <span className="item-count">{item.value}次</span>
                </div>
              </div>
              
              {/* 第三部分：摘要 */}
              {item.summary && (
                <div className="summary-container">
                  <div className="item-summary" style={{ color: '#e0e0e0', backgroundColor: 'rgba(255, 77, 79, 0.1)', border: '1px solid rgba(255, 77, 79, 0.2)', padding: '8px', borderRadius: '4px', marginTop: '8px' }}>
                    {item.summary || "该话题在用户评价中有较多负面反馈，需要关注改进。"}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
      
      {/* 产品话题四象限分析 */}
      <div className="quadrant-analysis-section summary-chart-section" style={{ backgroundColor: 'rgba(25, 25, 25, 0.8)', border: '1px solid rgba(24, 144, 255, 0.15)' }}>
        <h3 style={{ color: '#FFFFFF' }}><DotChartOutlined style={{ marginRight: '8px', fontSize: '16px', color: '#1890ff' }} /> 产品话题满意度和提及率分析</h3>
        
        {/* 四象限分析总结 */}
        <CommonInsightPanel
          title="四象限洞察"
          content={generateQuadrantSummary(reportData)}
          type="info"
          icon={<AppstoreOutlined />}
        />
        
        {/* Mermaid四象限图表 - 使用自适应容器 */}
        <div style={{ 
          width: '100%', 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center',
          margin: '0 auto'
        }}>
          <div className="mermaid-quadrant-container" style={{ 
            width: '100%', 
            minWidth: '300px',
            maxWidth: '1200px',
            margin: '0 auto'
          }}>
            <MermaidQuadrantChart 
              id="product-topics-quadrant" 
              data={quadrantData} 
              height="500px"
              width="100%"
              centerX={quadrantData && quadrantData.length > 0 ? quadrantData[0].avgX : 50}
              centerY={quadrantData && quadrantData.length > 0 ? quadrantData[0].avgY : 50}
            />
          </div>
        </div>
        
        {/* 四象限卡片式展示 */}
        <Row gutter={[16, 16]}>
          {/* 右上象限：优势话题 */}
          <Col xs={24} md={12}>
            <Card 
              title={<><RiseOutlined /> 优势话题 <Tag color="#8AE65C">右上象限</Tag></>}
              className="quadrant-card advantage-card"
              bordered={false}
              headStyle={{ backgroundColor: '#000000', color: 'white' }}
              style={{ backgroundColor: '#1E1E1E', border: '1px solid rgba(138, 230, 92, 0.2)' }}
            >
              <div className="quadrant-description" style={{ backgroundColor: 'rgba(30, 30, 30, 0.7)', border: '1px solid rgba(138, 230, 92, 0.2)', color: '#FFFFFF' }}>
                <p>高提及率、高满意度，产品的优势领域，应继续发扬并强化。</p>
              </div>
              <div className="topic-list">
                {quadrantData
                  .filter(item => item.quadrant === 1)
                  .sort((a, b) => b.count - a.count)
                  .map((item, index) => (
                    <div key={index} className="topic-item advantage-item" title={`话题总数：${item.count}`}>
                      <div className="topic-header">
                        <span className="topic-name">{item.name}</span>
                        <div className="topic-metrics">
                          <Tag color="#52c41a">满意度: {item.y.toFixed(1)}%</Tag>
                          <Tag color="#52c41a">提及率: {item.x.toFixed(1)}%</Tag>
                        </div>
                      </div>
                      <Progress 
                        percent={item.x} 
                        size="small" 
                        status="success" 
                        strokeColor={{
                          '0%': '#52c41a',
                          '100%': '#95de64'
                        }}
                        format={() => `${item.count}`}
                      />
                    </div>
                  ))
                }
                {quadrantData.filter(item => item.quadrant === 1).length === 0 && 
                  <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无优势话题" />
                }
              </div>
            </Card>
          </Col>
          
          {/* 右下象限：需改进话题 */}
          <Col xs={24} md={12}>
            <Card 
              title={<><FallOutlined /> 需改进话题 <Tag color="#FF3D3D">右下象限</Tag></>}
              className="quadrant-card improvement-card"
              bordered={false}
              headStyle={{ backgroundColor: '#000000', color: 'white' }}
              style={{ backgroundColor: '#1E1E1E', border: '1px solid rgba(255, 61, 61, 0.2)' }}
            >
              <div className="quadrant-description" style={{ backgroundColor: 'rgba(30, 30, 30, 0.7)', border: '1px solid rgba(255, 61, 61, 0.2)', color: '#FFFFFF' }}>
                <p>高提及率、低满意度，产品严重不足需要优先解决。</p>
              </div>
              <div className="topic-list">
                {quadrantData
                  .filter(item => item.quadrant === 2)
                  .sort((a, b) => b.count - a.count)
                  .map((item, index) => (
                    <div key={index} className="topic-item improvement-item" title={`话题总数：${item.count}`}>
                      <div className="topic-header">
                        <span className="topic-name">{item.name}</span>
                        <div className="topic-metrics">
                          <Tag color="#f22d34">满意度: {item.y.toFixed(1)}%</Tag>
                          <Tag color="#f22d34">提及率: {item.x.toFixed(1)}%</Tag>
                        </div>
                      </div>
                      <Progress 
                        percent={item.x} 
                        size="small" 
                        status="exception" 
                        strokeColor={{
                          '0%': '#f22d34',
                          '100%': '#f22d34'
                        }}
                        format={() => `${item.count}`}
                      />
                    </div>
                  ))
                }
                {quadrantData.filter(item => item.quadrant === 2).length === 0 && 
                  <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无需改进话题" />
                }
              </div>
            </Card>
          </Col>
          
          {/* 左上象限：潜力话题 */}
          <Col xs={24} md={12}>
            <Card 
              title={<><AreaChartOutlined /> 潜力话题 <Tag color="#1677ff">左上象限</Tag></>}
              className="quadrant-card potential-card"
              bordered={false}
              headStyle={{ backgroundColor: '#000000', color: 'white' }}
              style={{ backgroundColor: '#1E1E1E', border: '1px solid rgba(24, 144, 255, 0.2)' }}
            >
              <div className="quadrant-description" style={{ backgroundColor: 'rgba(30, 30, 30, 0.7)', border: '1px solid rgba(24, 144, 255, 0.2)', color: '#FFFFFF' }}>
                <p>低提及率、高满意度，可加强营销和用户教育。</p>
              </div>
              <div className="topic-list">
                {quadrantData
                  .filter(item => item.quadrant === 3)
                  .sort((a, b) => b.count - a.count)
                  .map((item, index) => (
                    <div key={index} className="topic-item potential-item" title={`话题总数：${item.count}`}>
                      <div className="topic-header">
                        <span className="topic-name">{item.name}</span>
                        <div className="topic-metrics">
                          <Tag color="#1677ff">满意度: {item.y.toFixed(1)}%</Tag>
                          <Tag color="#1677ff">提及率: {item.x.toFixed(1)}%</Tag>
                        </div>
                      </div>
                      <Progress 
                        percent={item.x} 
                        size="small" 
                        status="active" 
                        strokeColor="#1677ff"
                        format={() => `${item.count}`}
                      />
                    </div>
                  ))
                }
                {quadrantData.filter(item => item.quadrant === 3).length === 0 && 
                  <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无潜力话题" />
                }
              </div>
            </Card>
          </Col>
          
          {/* 左下象限：次要话题 */}
          <Col xs={24} md={12}>
            <Card 
              title={<><AppstoreOutlined /> 次要话题 <Tag color="#8e959e">左下象限</Tag></>}
              className="quadrant-card minor-card"
              bordered={false}
              headStyle={{ backgroundColor: '#000000', color: 'white' }}
              style={{ backgroundColor: '#1E1E1E', border: '1px solid rgba(142, 149, 158, 0.2)' }}
            >
              <div className="quadrant-description" style={{ backgroundColor: 'rgba(30, 30, 30, 0.7)', border: '1px solid rgba(142, 149, 158, 0.2)', color: '#FFFFFF' }}>
                <p>低提及率、低满意度，当前影响较小，可暂时不优先。</p>
              </div>
              <div className="topic-list">
                {quadrantData
                  .filter(item => item.quadrant === 4)
                  .sort((a, b) => b.count - a.count)
                  .map((item, index) => (
                    <div key={index} className="topic-item minor-item" title={`话题总数：${item.count}`}>
                      <div className="topic-header">
                        <span className="topic-name">{item.name}</span>
                        <div className="topic-metrics">
                          <Tag color="#8e959e">满意度: {item.y.toFixed(1)}%</Tag>
                          <Tag color="#8e959e">提及率: {item.x.toFixed(1)}%</Tag>
                        </div>
                      </div>
                      <Progress 
                        percent={item.x} 
                        size="small" 
                        strokeColor="#8e959e"
                        format={() => `${item.count}`}
                      />
                    </div>
                  ))
                }
                {quadrantData.filter(item => item.quadrant === 4).length === 0 && 
                  <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无次要话题" />
                }
              </div>
            </Card>
          </Col>
        </Row>
      </div>
    </Card>
  );
};



export default ProductAnalysisSection;
