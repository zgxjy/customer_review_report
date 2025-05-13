import React from 'react';
import { BulbOutlined, AppstoreOutlined, UserOutlined, ShoppingOutlined } from '@ant-design/icons';
import './InsightPanel.css';

/**
 * 通用洞察面板组件
 * @param {Object} props 组件属性
 * @param {string} props.title 洞察标题
 * @param {string|React.ReactNode} props.content 洞察内容
 * @param {string} props.type 洞察类型，可选值：'success'(绿色), 'info'(蓝色), 'warning'(黄色), 'error'(红色), 'default'(灰色)
 * @param {React.ReactNode} props.icon 自定义图标
 * @param {Object} props.style 自定义样式
 * @param {string} props.className 自定义类名
 */
const CommonInsightPanel = ({ 
  title, 
  content, 
  type = 'success', 
  icon, 
  style = {}, 
  className = ''
}) => {
  // 根据类型确定颜色
  const getTypeColor = () => {
    switch(type) {
      case 'success': return '#52c41a'; // 绿色
      case 'info': return '#1890ff';    // 蓝色
      case 'warning': return '#faad14'; // 黄色
      case 'error': return '#f5222d';   // 红色
      default: return '#8c8c8c';        // 灰色
    }
  };
  
  const color = getTypeColor();
  
  // 根据类型确定图标
  const getIcon = () => {
    if (icon) return icon;
    
    switch(type) {
      case 'info': return <AppstoreOutlined style={{ color }} />;
      case 'warning': return <ShoppingOutlined style={{ color }} />;
      case 'error': return <UserOutlined style={{ color }} />;
      default: return <BulbOutlined style={{ color }} />;
    }
  };
  
  return (
    <div 
      className={`common-insight-panel ${type} ${className}`}
      style={style}
    >
      <div className="common-insight-title">
        <span className="icon">{getIcon()}</span>
        <span>{title}</span>
      </div>
      <div className="common-insight-content">
        {content}
      </div>
    </div>
  );
};

export default CommonInsightPanel;
