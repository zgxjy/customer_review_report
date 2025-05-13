import React, { useState, useEffect } from 'react';
import { 
  Layout, Menu, Button, Dropdown, Avatar, Badge, Space, Divider,
  Input, Tooltip, Drawer, theme
} from 'antd';
import { 
  DashboardOutlined, UserOutlined, SettingOutlined, 
  BellOutlined, SearchOutlined, MenuOutlined, LogoutOutlined,
  ThunderboltOutlined, BarChartOutlined
} from '@ant-design/icons';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import './App.css';

import Dashboard from './pages/Dashboard';
import InsightReport from './pages/InsightReport';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import { ReportThemeProvider } from './context/ReportThemeContext';

const { Header, Content, Footer, Sider } = Layout;
const { Search } = Input;

const AppContent = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileDrawerVisible, setMobileDrawerVisible] = useState(false);
  const [currentMenuItem, setCurrentMenuItem] = useState('dashboard');
  const { isDarkMode } = useTheme();
  
  // 切换菜单项
  const handleMenuClick = (e) => {
    setCurrentMenuItem(e.key);
  };
  
  // 移动端抽屉关闭
  const closeDrawer = () => {
    setMobileDrawerVisible(false);
  };
  
  // 用户菜单项
  const userMenuItems = [
    {
      key: 'profile',
      label: '个人中心',
      icon: <UserOutlined />
    },
    {
      key: 'settings',
      label: '账户设置',
      icon: <SettingOutlined />
    },
    {
      type: 'divider'
    },
    {
      key: 'logout',
      label: '退出登录',
      icon: <LogoutOutlined />
    }
  ];
  
  // 侧边栏菜单项
  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: '数据概览'
    },
    {
      key: 'insight',
      icon: <BarChartOutlined />,
      label: '数据洞察'
    }
  ];
  
  return (
    <Layout className="app-layout">
      {/* 侧边导航栏 - 桌面端 */}
      <Sider
        className="app-sider"
        trigger={null}
        collapsible
        collapsed={collapsed}
        breakpoint="lg"
        onBreakpoint={(broken) => {
          if (broken) {
            setCollapsed(true);
          }
        }}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
          zIndex: 10
        }}
      >
        <div className="logo-container">
          <div className="sidebar-logo">
            {collapsed ? (
              <ThunderboltOutlined className="logo-icon" />
            ) : (
              <>
                <ThunderboltOutlined className="logo-icon" />
                <span className="logo-text">电商点评分析</span>
              </>
            )}
          </div>
          <Button 
            type="text"
            icon={collapsed ? <MenuOutlined /> : <MenuOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            className="collapse-button"
          />
        </div>
        <Menu
          theme="dark"
          mode="inline"
          defaultSelectedKeys={['dashboard']}
          selectedKeys={[currentMenuItem]}
          items={menuItems}
          onClick={handleMenuClick}
          className="sidebar-menu"
        />
      </Sider>

      {/* 移动端抽屉菜单 */}
      <Drawer
        title="电商点评分析"
        placement="left"
        onClose={closeDrawer}
        open={mobileDrawerVisible}
        className="mobile-drawer"
      >
        <Menu
          mode="inline"
          defaultSelectedKeys={['dashboard']}
          selectedKeys={[currentMenuItem]}
          items={menuItems}
          onClick={(e) => {
            handleMenuClick(e);
            closeDrawer();
          }}
        />
      </Drawer>

      <Layout className="site-layout" style={{ marginLeft: collapsed ? 80 : 200 }}>
        {/* 顶部导航栏 */}
        <Header className="app-header">
          <div className="header-left">
            <Button 
              type="text"
              icon={<MenuOutlined />}
              onClick={() => setMobileDrawerVisible(true)}
              className="mobile-menu-button"
            />
            <div className="breadcrumb-title">
              {currentMenuItem === 'dashboard' && '数据概览'}
            </div>
          </div>
          
          <div className="header-right">
            <Search 
              placeholder="搜索..."
              allowClear
              className="header-search"
              prefix={<SearchOutlined />}
            />
            <Divider type="vertical" className="header-divider" />
            <Tooltip title="通知中心">
              <Badge count={5} size="small">
                <Button type="text" icon={<BellOutlined />} className="header-icon-button" />
              </Badge>
            </Tooltip>
            <Dropdown 
              menu={{ items: userMenuItems }} 
              trigger={['click']} 
              placement="bottomRight"
            >
              <div className="user-profile">
                <Avatar size="small" icon={<UserOutlined />} />
                <span className="username">管理员</span>
              </div>
            </Dropdown>
          </div>
        </Header>
        
        {/* 主要内容区域 */}
        <Content className="app-content">
          <div className="app-main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/insight/:id" element={<InsightReport />} />
            </Routes>
          </div>
        </Content>
        
        {/* 页脚区域 */}
        <Footer className="app-footer">
          电商点评分析 ©{new Date().getFullYear()} 版权所有
        </Footer>
      </Layout>
    </Layout>
  );
}

const App = () => {
  return (
    <ThemeProvider>
      <ReportThemeProvider>
        <Router>
          <AppContent />
        </Router>
      </ReportThemeProvider>
    </ThemeProvider>
  );
};

export default App;
