import React, { useState, useEffect, useRef } from 'react';
import { 
  Card, Row, Col, Typography, Spin, message, Alert, Breadcrumb, Divider, Tag, Button, Tooltip
} from 'antd';
import { 
  BulbOutlined, HomeOutlined, BarChartOutlined, AppstoreOutlined,
  UserOutlined, FullscreenOutlined, FullscreenExitOutlined
} from '@ant-design/icons';
import { useParams, useNavigate } from 'react-router-dom';
import { dataResultApi } from '../api';
import './InsightReport.css';

// 导入组件
import OverviewSection from '../components/insight/OverviewSection';
import UserProfileSection from '../components/insight/UserProfileSection';
import ProductAnalysisSection from '../components/insight/ProductAnalysisSection';
import GlobalInsightSection from '../components/insight/GlobalInsightSection';
import ThemeSelector from '../components/ThemeSelector';

const { Title } = Typography;

// 数据洞察报告组件
const InsightReport = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [reportData, setReportData] = useState(null);
  const [fullscreenMode, setFullscreenMode] = useState(false);
  const [screenshotMode, setScreenshotMode] = useState(false);

  const reportRef = useRef(null);

  // 获取报告数据
  const fetchReportData = async () => {
    try {
      setLoading(true);
      const data = await dataResultApi.getDataResultById(id);
      setReportData(data);
    } catch (error) {
      message.error('获取报告数据失败');
      console.error('获取报告数据失败:', error);
    } finally {
      setLoading(false);
    }
  };
  


  // 初始加载
  useEffect(() => {
    if (id) {
      fetchReportData();
    }
  }, [id]);
  
  // 切换全屏模式
  const toggleFullscreen = () => {
    const newFullscreenMode = !fullscreenMode;
    setFullscreenMode(newFullscreenMode);
    
    // 如果是在切换到全屏模式，滚动到顶部
    if (newFullscreenMode) {
      window.scrollTo(0, 0);
      
      // 添加全屏样式到body
      document.body.classList.add('app-fullscreen-mode');
      
      // 隐藏应用的导航栏
      const appHeader = document.querySelector('.ant-layout-header');
      const appSider = document.querySelector('.ant-layout-sider');
      
      if (appHeader) appHeader.style.display = 'none';
      if (appSider) appSider.style.display = 'none';
    } else {
      // 移除全屏样式
      document.body.classList.remove('app-fullscreen-mode');
      
      // 显示应用的导航栏
      const appHeader = document.querySelector('.ant-layout-header');
      const appSider = document.querySelector('.ant-layout-sider');
      
      if (appHeader) appHeader.style.display = '';
      if (appSider) appSider.style.display = '';
    }
  };

  // 如果加载中，显示loading
  if (loading) {
    return (
      <div className="loading-container">
        <Spin size="large" tip="加载报告数据中..." />
      </div>
    );
  }

  // 如果没有数据，显示提示
  if (!reportData) {
    return (
      <div className="no-data-container">
        <Alert 
          message="数据不存在" 
          description="未找到报告数据，请返回列表重新选择。" 
          type="warning" 
          showIcon 
        />
      </div>
    );
  }

  return (
    <div className={`report-container ${fullscreenMode ? 'fullscreen-mode' : ''}`}>
      {/* 操作区 */}
      {!fullscreenMode && (
        <div className="report-actions-container">
          <div className="dashboard-header">
            <Breadcrumb className="dashboard-breadcrumb">
              <Breadcrumb.Item href="#" onClick={() => navigate('/')}>
                <HomeOutlined /> 首页
              </Breadcrumb.Item>
              <Breadcrumb.Item>
                <BarChartOutlined /> 数据洞察报告
              </Breadcrumb.Item>
            </Breadcrumb>
            
            <div className="dashboard-actions">
              <ThemeSelector placement="bottomLeft" />
              <Divider type="vertical" style={{ margin: '0 12px' }} />
              <Tooltip title="切换全屏模式">
                <Button 
                  type="primary" 
                  icon={<FullscreenOutlined />} 
                  onClick={toggleFullscreen}
                  className="fullscreen-btn"
                >
                  全屏模式
                </Button>
              </Tooltip>
            </div>
          </div>
        </div>
      )}
      
      {/* 看板区 */}
      <div className="insight-dashboard" ref={reportRef}>
        {fullscreenMode && !screenshotMode && (
          <div className="fullscreen-exit-container">
            <ThemeSelector placement="bottomLeft" />
            <Divider type="vertical" style={{ margin: '0 12px' }} />
            <Button 
              type="primary" 
              icon={<FullscreenExitOutlined />} 
              onClick={toggleFullscreen}
              className="exit-fullscreen-btn"
              style={{ marginRight: '10px' }}
            >
              退出全屏
            </Button>
            <Button
              type="primary"
              onClick={() => setScreenshotMode(true)}
              className="screenshot-btn"
            >
              截图模式
            </Button>
          </div>
        )}
        
        {screenshotMode && (
          <div 
            className="screenshot-overlay"
            onClick={() => setScreenshotMode(false)}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              zIndex: 9998,
              cursor: 'pointer'
            }}
          />
        )}

      
      {/* 报告标题区 */}
      <div className="report-header">
        <Title level={1}>电商点评数据洞察报告</Title>
        <div className="report-info">
          <Tag className="report-tag">报告代号: {reportData.project_code}</Tag>
          {/*先注释掉解决方案和模型*/}
          {/* <Tag className="report-tag">解决方案: {reportData.solution}</Tag>
          <Tag className="report-tag">模型: {reportData.model}</Tag> */}
          <Tag className="report-tag">处理时间: {reportData.process_time}</Tag>
        </div>
      </div>
      
      {/* 总体概览部分 */}
      <OverviewSection reportData={reportData} />
      
      {/* 用户画像分析 */}
      <UserProfileSection reportData={reportData} />
      {/* 产品分析 */}
      <ProductAnalysisSection reportData={reportData} />
      
      {/* 全局洞察总结 */}
      <GlobalInsightSection reportData={reportData} />
      </div>
    </div>
  );
};

export default InsightReport;
