import React, { createContext, useEffect, useContext } from 'react';

// 创建主题上下文
const ThemeContext = createContext({
  isDarkMode: true,
  // 移除主题切换功能，但保留属性以避免破坏现有组件
  toggleTheme: () => {}
});

// 主题提供者组件
export const ThemeProvider = ({ children }) => {
  // 固定为深色模式
  const isDarkMode = true;

  // 空函数，保留API兼容性
  const toggleTheme = () => {
    console.log('主题切换功能已禁用，系统固定使用深色模式');
  };

  // 确保使用深色模式
  useEffect(() => {
    // 移除可能存在的light-mode类
    document.body.classList.remove('light-mode');
    
    // 保存到本地存储
    localStorage.setItem('theme', 'dark');
  }, []);

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// 自定义钩子，方便组件使用主题上下文
export const useTheme = () => useContext(ThemeContext);

export default ThemeContext;
