import React from 'react';
import { Select, Tooltip, Space } from 'antd';
import { BgColorsOutlined } from '@ant-design/icons';
import { useReportTheme, REPORT_THEMES, themeConfigs } from '../context/ReportThemeContext';
import './ThemeSelector.css';

/**
 * 报告主题选择器组件
 * 允许用户切换报告的主题风格
 */
const ThemeSelector = ({ placement = 'bottomRight' }) => {
  const { currentTheme, changeTheme, themeOptions, themeConfig } = useReportTheme();

  // 处理主题变更
  const handleThemeChange = (value) => {
    changeTheme(value);
  };

  // 主题颜色预览
  const themeColorDot = (color) => (
    <span 
      className="theme-color-dot" 
      style={{ backgroundColor: color }}
    />
  );
  
  return (
    <div className="theme-selector-container">
      <Tooltip title="切换报告主题风格">
        <Space>
          <BgColorsOutlined className="theme-icon" style={{ color: themeConfig.highlightColor }} />
          <Select
            value={currentTheme}
            onChange={handleThemeChange}
            options={themeOptions.map(option => ({
              ...option,
              label: (
                <Space>
                  {themeColorDot(themeConfigs[option.value].colors.primary)}
                  {option.label}
                </Space>
              )
            }))}
            dropdownMatchSelectWidth={false}
            placement={placement}
            className="theme-select"
            popupClassName="theme-select-dropdown"
            bordered={false}
          />
        </Space>
      </Tooltip>
    </div>
  );
};

// 使用从 ReportThemeContext 导入的主题配置对象

export default ThemeSelector;
