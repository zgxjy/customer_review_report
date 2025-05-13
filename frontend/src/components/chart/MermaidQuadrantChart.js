import React, { useRef, useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { useReportTheme } from '../../context/ReportThemeContext';
import './QuadrantChart.css'; 

/**
 * 纯HTML/CSS实现的四象限图表组件
 */
const QuadrantChart = ({ id, data, width = '100%', height = '500px', centerX, centerY }) => {
  // 使用主题上下文
  const { themeConfig } = useReportTheme();
  // console.log('QuadrantChart 接收到的 data:', data);
  const containerRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  // 计算平均线、标准差或使用提供的中心点
  const calculateStatistics = (data) => {
    // 如果提供了自定义中心点，则使用自定义值
    if (centerX !== undefined && centerY !== undefined) {
      // 计算X和Y的标准差
      let sumXSquaredDiff = 0;
      let sumYSquaredDiff = 0;
      
      if (Array.isArray(data) && data.length > 0) {
        data.forEach(item => {
          sumXSquaredDiff += Math.pow(item.x - centerX, 2);
          sumYSquaredDiff += Math.pow(item.y - centerY, 2);
        });
        
        const stdX = Math.sqrt(sumXSquaredDiff / data.length);
        const stdY = Math.sqrt(sumYSquaredDiff / data.length);
        
        return { avgX: centerX, avgY: centerY, stdX, stdY };
      }
      
      return { avgX: centerX, avgY: centerY, stdX: 10, stdY: 10 }; // 默认标准差
    }
    
    // 否则计算平均值和标准差
    if (!Array.isArray(data) || data.length === 0) {
      return { avgX: 50, avgY: 50, stdX: 10, stdY: 10 };
    }
    
    const avgX = data.reduce((sum, item) => sum + item.x, 0) / data.length;
    const avgY = data.reduce((sum, item) => sum + item.y, 0) / data.length;
    
    // 计算标准差
    let sumXSquaredDiff = 0;
    let sumYSquaredDiff = 0;
    
    data.forEach(item => {
      sumXSquaredDiff += Math.pow(item.x - avgX, 2);
      sumYSquaredDiff += Math.pow(item.y - avgY, 2);
    });
    
    const stdX = Math.sqrt(sumXSquaredDiff / data.length);
    const stdY = Math.sqrt(sumYSquaredDiff / data.length);
    
    return { avgX, avgY, stdX, stdY };
  };

  // 根据象限返回不同颜色
  // 象限颜色定义，从主题中获取颜色
  const QUADRANT_COLORS = {
    1: themeConfig.quadrantChart.quadrants.q1.labelColor, // 优势话题 - 绿色
    2: themeConfig.quadrantChart.quadrants.q2.labelColor, // 需改进话题 - 红色
    3: themeConfig.quadrantChart.quadrants.q3.labelColor, // 潜力话题 - 蓝色
    4: themeConfig.quadrantChart.quadrants.q4.labelColor  // 次要话题 - 灰色
  };

  const getQuadrantColor = (quadrant) => {
    return QUADRANT_COLORS[quadrant] || '#000000';
  };

  // 确定数据点在哪个象限
  const determineQuadrant = (x, y, avgX, avgY) => {
    if (x >= avgX && y >= avgY) return 1; // 右上 - 优势话题
    if (x >= avgX && y < avgY) return 2;  // 右下 - 需改进话题
    if (x < avgX && y >= avgY) return 3;  // 左上 - 潜力话题
    return 4;  // 左下 - 次要话题
  };

  // 转换数据点到图表坐标
  const pointToPosition = (point, avgX, avgY, stdX, stdY, width, height) => {
    // 原始数据点
    const x = point.x;
    const y = point.y;
    
    // 计算相对位置（减去内边距）
    const padding = 50; // 为轴标签和标题预留空间
    const chartWidth = width - (padding * 2);
    const chartHeight = height - (padding * 2);
    
    // 图表的中心像素坐标
    const xCenter = padding + (chartWidth / 2);
    const yCenter = height - padding - (chartHeight / 2);
    
    // 基于均值和标准差计算缩放范围
    // 使用均值 +/- 3*标准差作为缩放范围，覆盖约99.7%的数据
    const xRescaleMin = avgX - 3 * stdX;
    const xRescaleMax = avgX + 3 * stdX;
    const yRescaleMin = avgY - 3 * stdY;
    const yRescaleMax = avgY + 3 * stdY;
    
    // 根据新的范围进行数据标准化，将数据缩放到[0,1]区间
    // 并在图表坐标系中将其映射到[-0.5,0.5]区间，以中心点为原点
    let xNormalized = 0, yNormalized = 0;
    
    // 如果范围有效（避免除以零）
    if (xRescaleMax > xRescaleMin) {
      xNormalized = (x - xRescaleMin) / (xRescaleMax - xRescaleMin);
      xNormalized = Math.max(0, Math.min(1, xNormalized)); // 限制在[0,1]范围
      xNormalized = xNormalized * 2 - 1; // 映射到[-1,1]区间
    }
    
    if (yRescaleMax > yRescaleMin) {
      yNormalized = (y - yRescaleMin) / (yRescaleMax - yRescaleMin);
      yNormalized = Math.max(0, Math.min(1, yNormalized)); // 限制在[0,1]范围
      yNormalized = yNormalized * 2 - 1; // 映射到[-1,1]区间
    }
    
    // 计算像素坐标，将标准化后的数据映射到图表坐标系
    const xPos = xCenter + (xNormalized * 0.8) * (chartWidth / 2); // 缩小卖0.8避免越界
    const yPos = yCenter - (yNormalized * 0.8) * (chartHeight / 2); // 翻转Y轴，因为CSS中y轴向下
    
    return { xPos, yPos, quadrant: determineQuadrant(x, y, avgX, avgY) };
  };

  useEffect(() => {
    if (containerRef.current) {
      // 获取容器的实际尺寸
      const { offsetWidth, offsetHeight } = containerRef.current;
      setDimensions({ width: offsetWidth, height: offsetHeight });
    }
  }, []);

  useEffect(() => {
    if (!containerRef.current || !data || dimensions.width === 0) return;
    
    try {
      // 计算平均值和标准差
      const { avgX, avgY, stdX, stdY } = calculateStatistics(data);
      
      // 找出最大值，用于缩放 (保留原来的代码兼容性)
      // eslint-disable-next-line no-unused-vars
      const maxX = Math.max(...data.map(p => p.x), avgX * 1.2);
      // eslint-disable-next-line no-unused-vars
      const maxY = Math.max(...data.map(p => p.y), avgY * 1.2);
      
      // 清空容器
      const container = containerRef.current;
      container.innerHTML = '';
      
      // 创建四象限图
      const chart = document.createElement('div');
      chart.className = 'quadrant-chart';
      chart.style.width = `${dimensions.width}px`;
      chart.style.height = `${dimensions.height}px`;
      container.appendChild(chart);
      
      // 定义内边距
      const padding = 50; // 为轴标签和标题预留空间

      // 声明chartWidth、chartHeight、xCenter、yCenter变量
      // 这些变量后续绘制象限背景、坐标轴等都需要用到
      const chartWidth = dimensions.width - (padding * 2);
      const chartHeight = dimensions.height - (padding * 2);
      const xCenter = padding + (chartWidth / 2);
      const yCenter = dimensions.height - padding - (chartHeight / 2);

      // 左上（潜力话题）
      const q3Bg = document.createElement('div');
      q3Bg.className = 'quadrant-bg-q3';
      q3Bg.style.position = 'absolute';
      q3Bg.style.left = `${padding}px`;
      q3Bg.style.top = `${padding}px`;
      q3Bg.style.width = `${chartWidth/2}px`;
      q3Bg.style.height = `${chartHeight/2}px`;
      chart.appendChild(q3Bg);
      // 右上（优势话题）
      const q1Bg = document.createElement('div');
      q1Bg.className = 'quadrant-bg-q1';
      q1Bg.style.position = 'absolute';
      q1Bg.style.left = `${xCenter}px`;
      q1Bg.style.top = `${padding}px`;
      q1Bg.style.width = `${chartWidth/2}px`;
      q1Bg.style.height = `${chartHeight/2}px`;
      chart.appendChild(q1Bg);
      // 左下（次要话题）
      const q4Bg = document.createElement('div');
      q4Bg.className = 'quadrant-bg-q4';
      q4Bg.style.position = 'absolute';
      q4Bg.style.left = `${padding}px`;
      q4Bg.style.top = `${yCenter}px`;
      q4Bg.style.width = `${chartWidth/2}px`;
      q4Bg.style.height = `${chartHeight/2}px`;
      chart.appendChild(q4Bg);
      // 右下（需改进话题）
      const q2Bg = document.createElement('div');
      q2Bg.className = 'quadrant-bg-q2';
      q2Bg.style.position = 'absolute';
      q2Bg.style.left = `${xCenter}px`;
      q2Bg.style.top = `${yCenter}px`;
      q2Bg.style.width = `${chartWidth/2}px`;
      q2Bg.style.height = `${chartHeight/2}px`;
      chart.appendChild(q2Bg);

      // 变量声明移动至函数顶部，避免后续重复声明报错
      
      // 添加标题
      const title = document.createElement('div');
      title.className = 'chart-title';
      title.textContent = '产品话题四象限分析';
      chart.appendChild(title);
      
      // 添加坐标轴
      const xAxis = document.createElement('div');
      xAxis.className = 'x-axis';
      const yAxis = document.createElement('div');
      yAxis.className = 'y-axis';
      chart.appendChild(xAxis);
      chart.appendChild(yAxis);
      
      // 使用前面已经定义的图表尺寸和中心位置变量
      // 不需要重复声明 chartWidth、chartHeight、xCenter、yCenter
      
      // 添加坐标轴标签
      const xLabel = document.createElement('div');
      xLabel.className = 'x-label';
      xLabel.textContent = '提及率(%)';
      const yLabel = document.createElement('div');
      yLabel.className = 'y-label';
      yLabel.textContent = '满意度(%)';
      chart.appendChild(xLabel);
      chart.appendChild(yLabel);
      
      // 添加象限标签 - 将标签放在每个象限的中心位置
      const q1Label = document.createElement('div');
      q1Label.className = 'quadrant-label q1';
      q1Label.textContent = '优势话题';
      q1Label.style.top = `${padding + 20}px`;
      q1Label.style.left = `${xCenter + (chartWidth/2) - 70}px`;
      
      const q2Label = document.createElement('div');
      q2Label.className = 'quadrant-label q2';
      q2Label.textContent = '需改进话题';
      q2Label.style.top = `${height - padding - 30}px`;
      q2Label.style.left = `${xCenter + (chartWidth/2) - 70}px`;
      
      const q3Label = document.createElement('div');
      q3Label.className = 'quadrant-label q3';
      q3Label.textContent = '潜力话题';
      q3Label.style.top = `${padding + 20}px`;
      q3Label.style.left = `${padding + 20}px`;
      
      const q4Label = document.createElement('div');
      q4Label.className = 'quadrant-label q4';
      q4Label.textContent = '次要话题';
      q4Label.style.top = `${height - padding - 30}px`;
      q4Label.style.left = `${padding + 20}px`;
      chart.appendChild(q1Label);
      chart.appendChild(q2Label);
      chart.appendChild(q3Label);
      chart.appendChild(q4Label);
      
      // 添加平均线 (将平均线放在图表正中间)
      
      const xLine = document.createElement('div');
      xLine.className = 'avg-line x-line';
      xLine.style.top = `${yCenter}px`;
      
      const yLine = document.createElement('div');
      yLine.className = 'avg-line y-line';
      yLine.style.left = `${xCenter}px`;
      
      // 添加中心点标记
      const centerPoint = document.createElement('div');
      centerPoint.className = 'center-point';
      centerPoint.style.left = `${xCenter}px`;
      centerPoint.style.top = `${yCenter}px`;
      
      // 添加中心点标签
      const centerLabel = document.createElement('div');
      centerLabel.className = 'center-label';
      centerLabel.textContent = '中心点';
      centerPoint.appendChild(centerLabel);
      
      chart.appendChild(xLine);
      chart.appendChild(yLine);
      chart.appendChild(centerPoint);
      
      // 添加数据点
      data.forEach(point => {
        const { xPos, yPos, quadrant } = pointToPosition(
          point, avgX, avgY, stdX, stdY, dimensions.width, dimensions.height
        );
        
        // 创建数据点元素
        const pointElement = document.createElement('div');
        pointElement.className = 'data-point';
        pointElement.style.left = `${xPos}px`;
        pointElement.style.top = `${yPos}px`;
        pointElement.style.backgroundColor = getQuadrantColor(quadrant);
        
        // 添加数据点标签
        const pointLabel = document.createElement('div');
        pointLabel.className = 'point-label';
        pointLabel.textContent = point.name;
        pointElement.appendChild(pointLabel);
        
        // 添加工具提示
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = `${point.name}: 提及率 ${point.x.toFixed(1)}%, 满意度 ${point.y.toFixed(1)}%`;
        pointElement.appendChild(tooltip);
        
        chart.appendChild(pointElement);
      });
      
    } catch (error) {
      console.error("四象限图渲染错误:", error);
      containerRef.current.innerHTML = `<div class="chart-error">四象限图渲染失败: ${error.message}</div>`;
    }
  }, [data, dimensions, calculateStatistics, getQuadrantColor, height, pointToPosition]);

  // 为了预览和调试，定义一个内部的padding常量
  // eslint-disable-next-line no-unused-vars
  const padding = 50;

  return (
    <div
      ref={containerRef}
      id={`${id}-container`}
      className="quadrant-chart-container"
      style={{ width, height, position: 'relative' }}
    />
  );
};

QuadrantChart.propTypes = {
  id: PropTypes.string,
  data: PropTypes.array.isRequired,
  width: PropTypes.string,
  height: PropTypes.string,
  centerX: PropTypes.number, // 自定义X轴中心点（提几率均值）
  centerY: PropTypes.number  // 自定义Y轴中心点（好评率均值）
};

export default QuadrantChart;
