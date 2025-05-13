import React, { createContext, useState, useEffect, useContext } from 'react';

// 定义可用的报告主题
export const REPORT_THEMES = {
  // 暗黑绿主题（原默认主题）
  DARK_GREEN: 'dark_green',
  // 浅色蓝主题（新增）
  LIGHT_BLUE: 'light_blue',
};

// 主题配置对象 - 按组件形式抽象整个色彩和样式体系
export const themeConfigs = {
  // 暗黑绿主题（原默认主题）
  [REPORT_THEMES.DARK_GREEN]: {
    name: '暗黑绿',
    
    // 基础色彩系统
    colors: {
      primary: '#8AE65C',         // 主色
      secondary: '#FF9F45',       // 次要色
      success: '#52C41A',         // 成功色
      warning: '#FAAD14',         // 警告色
      error: '#FF3D3D',           // 错误色
      info: '#36CFC9',            // 信息色
      accent: '#9254DE',          // 强调色
    },
    
    // 整体容器样式
    container: {
      bgColor: '#121212',         // 整体背景色
      textColor: 'rgba(255, 255, 255, 0.85)', // 主要文字颜色
      textSecondaryColor: 'rgba(255, 255, 255, 0.65)', // 次要文字颜色
      borderColor: 'rgba(138, 230, 92, 0.2)', // 边框颜色
      dividerColor: 'rgba(255, 255, 255, 0.12)', // 分割线颜色
    },
    
    // 卡片和面板样式
    card: {
      bgColor: '#1E1E1E',         // 卡片背景色
      headerBgColor: '#262626',   // 卡片头部背景色
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3), 0 2px 6px rgba(138, 230, 92, 0.15)', // 卡片阴影
      borderRadius: '8px',        // 卡片圆角
      borderColor: 'rgba(138, 230, 92, 0.2)', // 卡片边框颜色
    },
    
    // 统计卡片样式
    statCard: {
      gradients: [
        'linear-gradient(135deg, #8AE65C 0%, #52C41A 100%)', // 绿色渐变
        'linear-gradient(135deg, #FF9F45 0%, #FAAD14 100%)', // 橙色渐变
        'linear-gradient(135deg, #9254DE 0%, #722ED1 100%)', // 紫色渐变
        'linear-gradient(135deg, #36CFC9 0%, #13C2C2 100%)'  // 青色渐变
      ],
      titleColor: 'rgba(255, 255, 255, 0.85)', // 标题颜色
      valueColor: '#FFFFFF',      // 数值颜色
      iconColor: 'rgba(255, 255, 255, 0.85)', // 图标颜色
    },
    
    // 用户画像样式
    userProfile: {
      bgColor: '#1E1E1E',         // 背景色
      headerColor: '#8AE65C',     // 标题颜色
      textColor: 'rgba(255, 255, 255, 0.85)', // 文字颜色
      borderColor: 'rgba(138, 230, 92, 0.2)', // 边框颜色
      tagBgColor: 'rgba(138, 230, 92, 0.1)',  // 标签背景色
      tagTextColor: '#8AE65C',    // 标签文字颜色
    },
    
    // 产品分析样式
    productAnalysis: {
      bgColor: '#1E1E1E',         // 背景色
      headerColor: '#8AE65C',     // 标题颜色
      textColor: 'rgba(255, 255, 255, 0.85)', // 文字颜色
      positiveColor: '#52C41A',   // 正面评价颜色
      negativeColor: '#FF3D3D',   // 负面评价颜色
      neutralColor: '#BFBFBF',    // 中性评价颜色
      barBgColor: 'rgba(255, 255, 255, 0.08)', // 进度条背景色
    },
    
    // 四象限样式
    quadrantChart: {
      bgColor: 'rgba(25, 25, 25, 0.8)', // 背景色
      borderColor: 'rgba(48, 48, 48, 0.6)', // 边框颜色
      axisColor: 'rgba(255, 255, 255, 0.3)', // 坐标轴颜色
      labelColor: 'rgba(255, 255, 255, 0.7)', // 标签颜色
      centerPointColor: '#FF4D4F', // 中心点颜色
      quadrants: {
        q1: { // 优势话题：右上
          bgColor: 'rgba(82, 196, 26, 0.10)', // 背景色
          labelColor: '#52C41A',  // 标签颜色
        },
        q2: { // 需改进话题：右下
          bgColor: 'rgba(242, 45, 52, 0.10)', // 背景色
          labelColor: '#FAAD14',  // 标签颜色
        },
        q3: { // 潜力话题：左上
          bgColor: 'rgba(24, 144, 255, 0.10)', // 背景色
          labelColor: '#1890FF',  // 标签颜色
        },
        q4: { // 次要话题：左下
          bgColor: 'rgba(220, 220, 220, 0.30)', // 背景色
          labelColor: '#D9D9D9',  // 标签颜色
        },
      },
      dataPointBorder: 'rgba(255, 255, 255, 0.3)', // 数据点边框颜色
    },
    
    // 洞察样式
    insight: {
      panelBgColor: 'rgba(138, 230, 92, 0.12)', // 面板背景色
      borderColor: 'rgba(138, 230, 92, 0.2)', // 边框颜色
      highlightColor: '#8AE65C',  // 高亮颜色
      textColor: 'rgba(255, 255, 255, 0.85)', // 文字颜色
      secondaryTextColor: 'rgba(255, 255, 255, 0.65)', // 次要文字颜色
      iconColor: '#8AE65C',       // 图标颜色
    },
    
    // 表格样式
    table: {
      headerBgColor: '#262626',   // 表头背景色
      headerTextColor: 'rgba(255, 255, 255, 0.85)', // 表头文字颜色
      rowBgColor: '#1E1E1E',      // 行背景色
      rowAltBgColor: '#252525',   // 交替行背景色
      rowHoverBgColor: '#303030', // 行悬停背景色
      borderColor: 'rgba(255, 255, 255, 0.12)', // 边框颜色
      textColor: 'rgba(255, 255, 255, 0.85)', // 文字颜色
    },
    
    // 图表样式
    chart: {
      bgColor: 'transparent',     // 背景色
      textColor: 'rgba(255, 255, 255, 0.85)', // 文字颜色
      gridColor: 'rgba(255, 255, 255, 0.1)', // 网格线颜色
      colors: ['#8AE65C', '#FF9F45', '#36CFC9', '#FF3D3D', '#9254DE', '#FAAD14'], // 图表颜色
    },
    
    // 表单样式
    form: {
      inputBgColor: '#141414',    // 输入框背景色
      inputBorderColor: '#434343', // 输入框边框颜色
      inputTextColor: 'rgba(255, 255, 255, 0.85)', // 输入框文字颜色
      labelColor: 'rgba(255, 255, 255, 0.85)', // 标签颜色
      placeholderColor: 'rgba(255, 255, 255, 0.3)', // 占位符颜色
    },
    
    // 按钮样式
    button: {
      primaryBgColor: '#8AE65C',  // 主要按钮背景色
      primaryTextColor: '#141414', // 主要按钮文字颜色
      defaultBgColor: 'transparent', // 默认按钮背景色
      defaultTextColor: 'rgba(255, 255, 255, 0.85)', // 默认按钮文字颜色
      defaultBorderColor: '#434343', // 默认按钮边框颜色
      dangerBgColor: '#FF3D3D',   // 危险按钮背景色
      dangerTextColor: '#FFFFFF', // 危险按钮文字颜色
    },
    
    // 其他效果
    effects: {
      gradient: 'linear-gradient(90deg, #8AE65C, #FF9F45, #FFFFFF, #FF3D3D)', // 渐变效果
      textShadow: '0 0 10px rgba(138, 230, 92, 0.3)', // 文字阴影
    }
  },
  
  // 浅色蓝主题 - 更清爽易读的设计
  [REPORT_THEMES.LIGHT_BLUE]: {
    name: '浅色蓝',
    
    // 基础色彩系统 - 减少饱和度，使用更柔和的色调
    colors: {
      primary: '#1890FF',         // 保持主蓝色
      secondary: '#73D3FF',       // 更浅的蓝色作为次要色
      success: '#52C41A',         // 保持成功色但降低使用频率
      warning: '#FAAD14',         // 保持警告色但降低使用频率
      error: '#F5222D',           // 保持错误色但降低使用频率
      info: '#1890FF',            // 与主色保持一致
      accent: '#4D7CFE',          // 更协调的蓝色强调色
    },
    
    // 整体容器样式 - 更清爽的背景和边框
    container: {
      bgColor: '#FFFFFF',         // 纯白背景
      textColor: 'rgba(0, 0, 0, 0.75)', // 稍微柔和的主文字颜色
      textSecondaryColor: 'rgba(0, 0, 0, 0.55)', // 柔和的次要文字颜色
      borderColor: 'rgba(24, 144, 255, 0.15)', // 更淡的边框颜色
      dividerColor: '#F5F9FC',    // 带蓝色调的分割线颜色
    },
    
    // 卡片和面板样式 - 更清爽的设计
    card: {
      bgColor: '#FFFFFF',         // 纯白背景
      headerBgColor: '#F0F7FF',   // 带淡蓝色的头部背景
      boxShadow: '0 1px 4px rgba(24, 144, 255, 0.05)', // 更柔和的阴影
      borderRadius: '8px',        // 保持圆角
      borderColor: '#E6F0FF',     // 带蓝色调的边框
    },
    
    // 统计卡片样式 - 使用更柔和的蓝色系渐变
    statCard: {
      gradients: [
        'linear-gradient(135deg, #1890FF 0%, #73D3FF 100%)', // 蓝色渐变
        'linear-gradient(135deg, #4D7CFE 0%, #73D3FF 100%)', // 另一种蓝色渐变
        'linear-gradient(135deg, #0050B3 0%, #1890FF 100%)', // 深蓝到蓝渐变
        'linear-gradient(135deg, #40A9FF 0%, #BAE7FF 100%)'  // 浅蓝渐变
      ],
      titleColor: '#FFFFFF',      // 白色标题
      valueColor: '#FFFFFF',      // 白色数值
      iconColor: 'rgba(255, 255, 255, 0.9)', // 图标颜色
    },
    
    // 用户画像样式 - 更清爽的蓝白配色
    userProfile: {
      bgColor: '#FFFFFF',         // 背景色
      headerColor: '#1890FF',     // 标题颜色
      textColor: 'rgba(0, 0, 0, 0.75)', // 文字颜色
      borderColor: '#E6F0FF',     // 边框颜色
      tagBgColor: 'rgba(24, 144, 255, 0.08)', // 更淡的标签背景色
      tagTextColor: '#1890FF',    // 标签文字颜色
    },
    
    // 产品分析样式 - 更协调的色彩
    productAnalysis: {
      bgColor: '#FFFFFF',         // 背景色
      headerColor: '#1890FF',     // 标题颜色
      textColor: 'rgba(0, 0, 0, 0.75)', // 文字颜色
      positiveColor: '#52C41A',   // 正面评价颜色
      negativeColor: '#F5222D',   // 负面评价颜色
      neutralColor: '#8C8C8C',    // 中性评价颜色
      barBgColor: '#F0F7FF',      // 进度条背景色改为淡蓝色
    },
    
    // 四象限样式 - 保持清爽易读的设计
    quadrantChart: {
      bgColor: '#FFFFFF',         // 背景色
      borderColor: '#E6F0FF',     // 边框颜色改为淡蓝色
      axisColor: 'rgba(24, 144, 255, 0.15)', // 坐标轴颜色改为淡蓝色
      labelColor: 'rgba(0, 0, 0, 0.65)', // 标签颜色
      centerPointColor: '#1890FF', // 中心点颜色改为主蓝色
      quadrants: {
        q1: { // 优势话题：右上
          bgColor: 'rgba(82, 196, 26, 0.08)', // 背景色
          labelColor: '#52C41A',  // 标签颜色
        },
        q2: { // 需改进话题：右下
          bgColor: 'rgba(245, 34, 45, 0.08)', // 背景色
          labelColor: '#F5222D',  // 标签颜色
        },
        q3: { // 潜力话题：左上
          bgColor: 'rgba(24, 144, 255, 0.08)', // 背景色
          labelColor: '#1890FF',  // 标签颜色
        },
        q4: { // 次要话题：左下
          bgColor: 'rgba(140, 140, 140, 0.08)', // 背景色
          labelColor: '#8C8C8C',  // 标签颜色
        },
      },
      dataPointBorder: 'rgba(24, 144, 255, 0.2)', // 数据点边框颜色改为淡蓝色
    },
    
    // 洞察样式 - 更清爽的蓝白配色
    insight: {
      panelBgColor: 'rgba(24, 144, 255, 0.03)', // 更淡的面板背景色
      borderColor: 'rgba(24, 144, 255, 0.15)', // 更淡的边框颜色
      highlightColor: '#1890FF',  // 高亮颜色
      textColor: 'rgba(0, 0, 0, 0.75)', // 文字颜色
      secondaryTextColor: 'rgba(0, 0, 0, 0.55)', // 次要文字颜色
      iconColor: '#1890FF',       // 图标颜色
    },
    
    // 表格样式 - 更清爽易读
    table: {
      headerBgColor: '#F0F7FF',   // 淡蓝色表头
      headerTextColor: 'rgba(0, 0, 0, 0.75)', // 表头文字颜色
      rowBgColor: '#FFFFFF',      // 白色行背景
      rowAltBgColor: '#F8FBFF',   // 极淡蓝色交替行背景
      rowHoverBgColor: '#E6F7FF', // 淡蓝色悬停背景
      borderColor: '#E6F0FF',     // 淡蓝色边框
      textColor: 'rgba(0, 0, 0, 0.75)', // 文字颜色
    },
    
    // 图表样式 - 蓝色系列配色
    chart: {
      bgColor: 'transparent',     // 透明背景
      textColor: 'rgba(0, 0, 0, 0.75)', // 文字颜色
      gridColor: 'rgba(24, 144, 255, 0.1)', // 蓝色网格线
      colors: ['#1890FF', '#40A9FF', '#69C0FF', '#91D5FF', '#BAE7FF', '#E6F7FF'], // 蓝色系列
    },
    
    // 表单样式 - 更协调的蓝白配色
    form: {
      inputBgColor: '#FFFFFF',    // 输入框背景色
      inputBorderColor: '#D9E8FF', // 输入框边框颜色改为淡蓝色
      inputTextColor: 'rgba(0, 0, 0, 0.75)', // 输入框文字颜色
      labelColor: 'rgba(0, 0, 0, 0.75)', // 标签颜色
      placeholderColor: 'rgba(0, 0, 0, 0.3)', // 占位符颜色
    },
    
    // 按钮样式 - 清爽的蓝白配色
    button: {
      primaryBgColor: '#1890FF',  // 主要按钮背景色
      primaryTextColor: '#FFFFFF', // 主要按钮文字颜色
      defaultBgColor: '#FFFFFF',  // 默认按钮背景色
      defaultTextColor: 'rgba(0, 0, 0, 0.65)', // 默认按钮文字颜色
      defaultBorderColor: '#D9D9D9', // 默认按钮边框颜色
      dangerBgColor: '#FF4D4F',   // 危险按钮背景色
      dangerTextColor: '#FFFFFF', // 危险按钮文字颜色
    },
    
    // 其他效果
    effects: {
      gradient: 'linear-gradient(90deg, #1890FF, #36CFC9, #722ED1, #F5222D)', // 渐变效果
      textShadow: 'none',         // 文字阴影
    }
  },
};

// 创建报告主题上下文
const ReportThemeContext = createContext({
  currentTheme: REPORT_THEMES.DEFAULT,
  themeConfig: themeConfigs[REPORT_THEMES.DEFAULT],
  changeTheme: () => {},
  themeOptions: []
});

// 报告主题提供者组件
export const ReportThemeProvider = ({ children }) => {
  // 从本地存储中获取报告主题设置，默认为暗黑绿主题
  const [currentTheme, setCurrentTheme] = useState(() => {
    const savedTheme = localStorage.getItem('reportTheme');
    return savedTheme && Object.values(REPORT_THEMES).includes(savedTheme) 
      ? savedTheme 
      : REPORT_THEMES.DARK_GREEN;
  });

  // 获取当前主题配置
  const themeConfig = themeConfigs[currentTheme] || themeConfigs[REPORT_THEMES.DARK_GREEN];

  // 切换主题的函数
  const changeTheme = (theme) => {
    if (Object.values(REPORT_THEMES).includes(theme)) {
      setCurrentTheme(theme);
    }
  };

  // 生成主题选项
  const themeOptions = Object.values(REPORT_THEMES).map(themeKey => ({
    value: themeKey,
    label: themeConfigs[themeKey].name
  }));

  // 当主题变化时，更新CSS变量和本地存储
  useEffect(() => {
    // 基础色彩系统
    document.documentElement.style.setProperty('--primary-color', themeConfig.colors.primary);
    document.documentElement.style.setProperty('--secondary-color', themeConfig.colors.secondary);
    document.documentElement.style.setProperty('--success-color', themeConfig.colors.success);
    document.documentElement.style.setProperty('--warning-color', themeConfig.colors.warning);
    document.documentElement.style.setProperty('--error-color', themeConfig.colors.error);
    document.documentElement.style.setProperty('--info-color', themeConfig.colors.info);
    document.documentElement.style.setProperty('--accent-color', themeConfig.colors.accent);
    
    // 整体容器样式
    document.documentElement.style.setProperty('--bg-color', themeConfig.container.bgColor);
    document.documentElement.style.setProperty('--text-color', themeConfig.container.textColor);
    document.documentElement.style.setProperty('--text-color-secondary', themeConfig.container.textSecondaryColor);
    document.documentElement.style.setProperty('--border-color', themeConfig.container.borderColor);
    document.documentElement.style.setProperty('--divider-color', themeConfig.container.dividerColor);
    
    // 卡片和面板样式
    document.documentElement.style.setProperty('--card-bg', themeConfig.card.bgColor);
    document.documentElement.style.setProperty('--card-header-bg', themeConfig.card.headerBgColor);
    document.documentElement.style.setProperty('--box-shadow-base', themeConfig.card.boxShadow);
    document.documentElement.style.setProperty('--border-radius-base', themeConfig.card.borderRadius);
    document.documentElement.style.setProperty('--card-border-color', themeConfig.card.borderColor);
    
    // 统计卡片样式
    themeConfig.statCard.gradients.forEach((gradient, index) => {
      document.documentElement.style.setProperty(`--stat-card-gradient-${index + 1}`, gradient);
    });
    document.documentElement.style.setProperty('--stat-card-title-color', themeConfig.statCard.titleColor);
    document.documentElement.style.setProperty('--stat-card-value-color', themeConfig.statCard.valueColor);
    document.documentElement.style.setProperty('--stat-card-icon-color', themeConfig.statCard.iconColor);
    
    // 用户画像样式
    document.documentElement.style.setProperty('--user-profile-bg', themeConfig.userProfile.bgColor);
    document.documentElement.style.setProperty('--user-profile-header', themeConfig.userProfile.headerColor);
    document.documentElement.style.setProperty('--user-profile-text', themeConfig.userProfile.textColor);
    document.documentElement.style.setProperty('--user-profile-border', themeConfig.userProfile.borderColor);
    document.documentElement.style.setProperty('--user-profile-tag-bg', themeConfig.userProfile.tagBgColor);
    document.documentElement.style.setProperty('--user-profile-tag-text', themeConfig.userProfile.tagTextColor);
    
    // 产品分析样式
    document.documentElement.style.setProperty('--product-analysis-bg', themeConfig.productAnalysis.bgColor);
    document.documentElement.style.setProperty('--product-analysis-header', themeConfig.productAnalysis.headerColor);
    document.documentElement.style.setProperty('--product-analysis-text', themeConfig.productAnalysis.textColor);
    document.documentElement.style.setProperty('--product-positive-color', themeConfig.productAnalysis.positiveColor);
    document.documentElement.style.setProperty('--product-negative-color', themeConfig.productAnalysis.negativeColor);
    document.documentElement.style.setProperty('--product-neutral-color', themeConfig.productAnalysis.neutralColor);
    document.documentElement.style.setProperty('--product-bar-bg', themeConfig.productAnalysis.barBgColor);
    
    // 四象限样式
    document.documentElement.style.setProperty('--quadrant-bg', themeConfig.quadrantChart.bgColor);
    document.documentElement.style.setProperty('--quadrant-border', themeConfig.quadrantChart.borderColor);
    document.documentElement.style.setProperty('--quadrant-axis', themeConfig.quadrantChart.axisColor);
    document.documentElement.style.setProperty('--quadrant-label', themeConfig.quadrantChart.labelColor);
    document.documentElement.style.setProperty('--quadrant-center-point', themeConfig.quadrantChart.centerPointColor);
    
    // 四象限区域样式
    document.documentElement.style.setProperty('--quadrant-q1-bg', themeConfig.quadrantChart.quadrants.q1.bgColor);
    document.documentElement.style.setProperty('--quadrant-q1-label', themeConfig.quadrantChart.quadrants.q1.labelColor);
    document.documentElement.style.setProperty('--quadrant-q2-bg', themeConfig.quadrantChart.quadrants.q2.bgColor);
    document.documentElement.style.setProperty('--quadrant-q2-label', themeConfig.quadrantChart.quadrants.q2.labelColor);
    document.documentElement.style.setProperty('--quadrant-q3-bg', themeConfig.quadrantChart.quadrants.q3.bgColor);
    document.documentElement.style.setProperty('--quadrant-q3-label', themeConfig.quadrantChart.quadrants.q3.labelColor);
    document.documentElement.style.setProperty('--quadrant-q4-bg', themeConfig.quadrantChart.quadrants.q4.bgColor);
    document.documentElement.style.setProperty('--quadrant-q4-label', themeConfig.quadrantChart.quadrants.q4.labelColor);
    document.documentElement.style.setProperty('--quadrant-data-point-border', themeConfig.quadrantChart.dataPointBorder);
    
    // 洞察样式
    document.documentElement.style.setProperty('--insight-panel-bg', themeConfig.insight.panelBgColor);
    document.documentElement.style.setProperty('--insight-border-color', themeConfig.insight.borderColor);
    document.documentElement.style.setProperty('--insight-highlight-color', themeConfig.insight.highlightColor);
    document.documentElement.style.setProperty('--insight-text-color', themeConfig.insight.textColor);
    document.documentElement.style.setProperty('--insight-text-secondary', themeConfig.insight.secondaryTextColor);
    document.documentElement.style.setProperty('--insight-icon-color', themeConfig.insight.iconColor);
    
    // 表格样式
    document.documentElement.style.setProperty('--table-header-bg', themeConfig.table.headerBgColor);
    document.documentElement.style.setProperty('--table-header-text', themeConfig.table.headerTextColor);
    document.documentElement.style.setProperty('--table-row-bg', themeConfig.table.rowBgColor);
    document.documentElement.style.setProperty('--table-row-alt-bg', themeConfig.table.rowAltBgColor);
    document.documentElement.style.setProperty('--table-row-hover-bg', themeConfig.table.rowHoverBgColor);
    document.documentElement.style.setProperty('--table-border', themeConfig.table.borderColor);
    document.documentElement.style.setProperty('--table-text', themeConfig.table.textColor);
    
    // 图表样式
    document.documentElement.style.setProperty('--chart-bg', themeConfig.chart.bgColor);
    document.documentElement.style.setProperty('--chart-text', themeConfig.chart.textColor);
    document.documentElement.style.setProperty('--chart-grid-color', themeConfig.chart.gridColor);
    
    // 设置图表颜色
    themeConfig.chart.colors.forEach((color, index) => {
      document.documentElement.style.setProperty(`--chart-color-${index + 1}`, color);
    });
    
    // 表单样式
    document.documentElement.style.setProperty('--form-input-bg', themeConfig.form.inputBgColor);
    document.documentElement.style.setProperty('--form-input-border', themeConfig.form.inputBorderColor);
    document.documentElement.style.setProperty('--form-input-text', themeConfig.form.inputTextColor);
    document.documentElement.style.setProperty('--form-label', themeConfig.form.labelColor);
    document.documentElement.style.setProperty('--form-placeholder', themeConfig.form.placeholderColor);
    
    // 按钮样式
    document.documentElement.style.setProperty('--btn-primary-bg', themeConfig.button.primaryBgColor);
    document.documentElement.style.setProperty('--btn-primary-text', themeConfig.button.primaryTextColor);
    document.documentElement.style.setProperty('--btn-default-bg', themeConfig.button.defaultBgColor);
    document.documentElement.style.setProperty('--btn-default-text', themeConfig.button.defaultTextColor);
    document.documentElement.style.setProperty('--btn-default-border', themeConfig.button.defaultBorderColor);
    document.documentElement.style.setProperty('--btn-danger-bg', themeConfig.button.dangerBgColor);
    document.documentElement.style.setProperty('--btn-danger-text', themeConfig.button.dangerTextColor);
    
    // 其他效果
    document.documentElement.style.setProperty('--insight-gradient', themeConfig.effects.gradient);
    document.documentElement.style.setProperty('--insight-text-shadow', themeConfig.effects.textShadow);
    
    // 兼容旧版变量名称 - 为了确保现有组件不受影响
    document.documentElement.style.setProperty('--component-bg', themeConfig.card.bgColor);
    
    // 保存到本地存储
    localStorage.setItem('reportTheme', currentTheme);
  }, [currentTheme, themeConfig]);

  return (
    <ReportThemeContext.Provider value={{ currentTheme, themeConfig, changeTheme, themeOptions }}>
      {children}
    </ReportThemeContext.Provider>
  );
};

// 自定义钩子，方便组件使用报告主题上下文
export const useReportTheme = () => useContext(ReportThemeContext);

export default ReportThemeContext;
