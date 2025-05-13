import React from 'react';
import { Alert } from 'antd';
import { BulbOutlined, LightbulbOutlined } from '@ant-design/icons';
import { useReportTheme } from '../../context/ReportThemeContext';
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
const InsightPanel = ({ 
  title, 
  content, 
  type = 'success', 
  icon, 
  style = {}, 
  className = '',
  bordered = true
}) => {
  // 使用主题上下文
  const { themeConfig } = useReportTheme();
  // 根据类型确定颜色，使用主题变量
  const getTypeColor = () => {
    switch(type) {
      case 'success': return themeConfig.colors.success; // 绿色
      case 'info': return themeConfig.colors.info;      // 蓝色
      case 'warning': return themeConfig.colors.warning; // 黄色
      case 'error': return themeConfig.colors.error;    // 红色
      default: return 'rgba(140, 140, 140, 1)';         // 灰色
    }
  };
  
  const color = getTypeColor();
  
  // 根据类型确定图标
  const getIcon = () => {
    if (icon) return icon;
    
    return <BulbOutlined style={{ fontSize: '24px', color: color }} />;
  };
  
  // 根据类型确定背景色和边框色，使用主题变量
  const getBgAndBorder = () => {
    const alpha = '0.12';
    const borderAlpha = '0.3';
    
    // 从主题中获取颜色
    const successColor = themeConfig.colors.success;
    const infoColor = themeConfig.colors.info;
    const warningColor = themeConfig.colors.warning;
    const errorColor = themeConfig.colors.error;
    
    // 提取RGB值，用于创建rgba
    const extractRGB = (hexColor) => {
      // 如果已经是rgba格式，直接返回
      if (hexColor.startsWith('rgba')) return hexColor.replace(/[^\d,]/g, '').split(',').slice(0, 3).join(', ');
      
      // 处理十六进制颜色
      const hex = hexColor.replace('#', '');
      if (hex.length === 3) {
        return `${parseInt(hex[0] + hex[0], 16)}, ${parseInt(hex[1] + hex[1], 16)}, ${parseInt(hex[2] + hex[2], 16)}`;
      }
      return `${parseInt(hex.substr(0, 2), 16)}, ${parseInt(hex.substr(2, 2), 16)}, ${parseInt(hex.substr(4, 2), 16)}`;
    };
    
    switch(type) {
      case 'success':
        return {
          backgroundColor: `rgba(${extractRGB(successColor)}, ${alpha})`,
          border: bordered ? `1px solid rgba(${extractRGB(successColor)}, ${borderAlpha})` : 'none'
        };
      case 'info':
        return {
          backgroundColor: `rgba(${extractRGB(infoColor)}, ${alpha})`,
          border: bordered ? `1px solid rgba(${extractRGB(infoColor)}, ${borderAlpha})` : 'none'
        };
      case 'warning':
        return {
          backgroundColor: `rgba(${extractRGB(warningColor)}, ${alpha})`,
          border: bordered ? `1px solid rgba(${extractRGB(warningColor)}, ${borderAlpha})` : 'none'
        };
      case 'error':
        return {
          backgroundColor: `rgba(${extractRGB(errorColor)}, ${alpha})`,
          border: bordered ? `1px solid rgba(${extractRGB(errorColor)}, ${borderAlpha})` : 'none'
        };
      default:
        return {
          backgroundColor: `rgba(140, 140, 140, ${alpha})`,
          border: bordered ? `1px solid rgba(140, 140, 140, ${borderAlpha})` : 'none'
        };
    }
  };
  
  const bgAndBorder = getBgAndBorder();
  
  return (
    <Alert
      message={<span className="insight-panel-title" style={{ color }}>{title}</span>}
      description={
        <div className="insight-panel-content">
          {content}
        </div>
      }
      type="info"
      showIcon
      icon={getIcon()}
      className={`insight-panel ${className}`}
      style={{
        ...bgAndBorder,
        marginBottom: '24px',
        color: themeConfig.container.textColor, // 使用主题文字颜色
        ...style
      }}
    />
  );
};

export default InsightPanel;
