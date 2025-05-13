import React, { useState, useEffect } from 'react';
import { 
  Table, Card, Select, Space, Row, Col, Typography, Spin, message, Button, 
  Tag, Divider, Tooltip, Statistic, Avatar, Breadcrumb
} from 'antd';
import { 
  DatabaseOutlined, FilterOutlined, SyncOutlined, AppstoreOutlined,
  BarChartOutlined, TableOutlined, HomeOutlined, SearchOutlined,
  ExportOutlined, ReloadOutlined, LineChartOutlined, PieChartOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { dataResultApi } from '../api';
import './Dashboard.css';

const { Title } = Typography;
const { Option } = Select;

const Dashboard = () => {
  const navigate = useNavigate();
  // 状态管理
  const [loading, setLoading] = useState(false);
  const [dataList, setDataList] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });
  
  // 筛选条件
  const [filters, setFilters] = useState({
    project_code: undefined,
    solution: undefined,
    model: undefined,
  });
  
  // 筛选选项
  const [filterOptions, setFilterOptions] = useState({
    projectCodes: [],
    solutions: [],
    models: [],
  });

  // 获取筛选选项
  const fetchFilterOptions = async () => {
    try {
      const [projectCodes, solutions, models] = await Promise.all([
        dataResultApi.getProjectCodes(),
        dataResultApi.getSolutions(),
        dataResultApi.getModels(),
      ]);
      
      setFilterOptions({
        projectCodes,
        solutions,
        models,
      });
    } catch (error) {
      message.error('获取筛选选项失败');
      console.error('获取筛选选项失败:', error);
    }
  };

  // 获取数据列表
  const fetchDataList = async (params = {}) => {
    setLoading(true);
    try {
      const { current, pageSize } = pagination;
      const skip = (current - 1) * pageSize;
      
      // 构建查询参数
      const queryParams = {
        skip,
        limit: pageSize,
        ...filters,
        ...params,
      };
      
      // 移除未定义的参数
      Object.keys(queryParams).forEach(key => {
        if (queryParams[key] === undefined) {
          delete queryParams[key];
        }
      });
      
      const { total, data } = await dataResultApi.getDataResults(queryParams);
      
      setDataList(data);
      setPagination(prev => ({
        ...prev,
        total,
      }));
    } catch (error) {
      message.error('获取数据列表失败');
      console.error('获取数据列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 处理表格变化
  const handleTableChange = (pagination) => {
    setPagination(pagination);
  };

  // 处理筛选条件变化
  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value,
    }));
    
    // 重置分页
    setPagination(prev => ({
      ...prev,
      current: 1,
    }));
  };

  // 初始加载
  useEffect(() => {
    fetchFilterOptions();
  }, []);

  // 筛选条件或分页变化时重新加载数据
  useEffect(() => {
    fetchDataList();
  }, [filters, pagination.current, pagination.pageSize]);

  // 表格列定义
  const columns = [
    {
      title: '项目代码',
      dataIndex: 'project_code',
      key: 'project_code',
      width: 150,
      render: (text) => (
        <Tag color="blue">{text}</Tag>
      ),
      sorter: (a, b) => a.project_code.localeCompare(b.project_code),
    },
    {
      title: '解决方案',
      dataIndex: 'solution',
      key: 'solution',
      width: 150,
      render: (text) => (
        <Tag color="green">{text}</Tag>
      ),
      sorter: (a, b) => a.solution.localeCompare(b.solution),
    },
    {
      title: '模型',
      dataIndex: 'model',
      key: 'model',
      width: 150,
      render: (text) => (
        <Tag color="purple">{text}</Tag>
      ),
      sorter: (a, b) => a.model.localeCompare(b.model),
    },
    {
      title: '处理时间',
      dataIndex: 'process_time',
      key: 'process_time',
      width: 200,
      render: (text) => (
        <Tooltip title={text}>
          <span>{text}</span>
        </Tooltip>
      ),
      sorter: (a, b) => new Date(a.process_time) - new Date(b.process_time),
    },
    {
      title: '总评论数',
      dataIndex: 'total_review',
      key: 'total_review',
      width: 120,
      render: (value) => (
        <Statistic 
          value={value || 0} 
          valueStyle={{ fontSize: '14px', fontWeight: 'bold' }}
        />
      ),
      sorter: (a, b) => (a.total_review || 0) - (b.total_review || 0),
    },
    {
      title: '总话题数',
      dataIndex: 'product_topics',
      key: 'product_topics.total_stats.total_count',
      width: 120,
      render: (product_topics) => (
        <Statistic 
          value={product_topics?.total_stats?.total_count || 0} 
          valueStyle={{ fontSize: '14px', fontWeight: 'bold', color: '#1890ff' }}
        />
      ),
      sorter: (a, b) => (a.product_topics?.total_stats?.total_count || 0) - (b.product_topics?.total_stats?.total_count || 0),
    },
    {
      title: 'Token用量',
      dataIndex: 'all_stages_total_tokens',
      key: 'all_stages_total_tokens',
      width: 120,
      render: (all_stages_total_tokens) => (
        <Statistic 
          value={all_stages_total_tokens || 0} 
          valueStyle={{ fontSize: '14px', fontWeight: 'bold', color: '#722ed1' }}
        />
      ),
      sorter: (a, b) => (a.all_stages_total_tokens || 0) - (b.all_stages_total_tokens || 0),
    },
    {
      title: '摘要TopN',
      dataIndex: 'top_topics_count',
      key: 'top_topics_count',
      width: 120,
      render: (value) => (
        <Tag color="orange">{value || 0}</Tag>
      ),
      sorter: (a, b) => (a.top_topics_count || 0) - (b.top_topics_count || 0),
    },
    {
      title: '数据ID',
      dataIndex: 'data_id',
      key: 'data_id',
      width: 200,
      ellipsis: true,
      render: (text) => (
        <Tooltip title={text}>
          <span className="data-id">{text}</span>
        </Tooltip>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看数据洞察报告">
            <Button 
              type="primary" 
              size="small" 
              icon={<LineChartOutlined />}
              onClick={() => navigate(`/insight/${record._id}`)}
            >
              数据洞察
            </Button>
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div className="dashboard-container">
      {/* 页面头部区域 */}
      <div className="dashboard-header">
        <div className="header-left">
          <div className="header-description">
            查看和管理所有电商点评分析数据，包括项目代码、解决方案和模型等信息
          </div>
        </div>
        <div className="header-actions">
          <Button 
            type="primary" 
            icon={<ReloadOutlined />} 
            onClick={() => fetchDataList()}
          >
            刷新数据
          </Button>
          <Button icon={<ExportOutlined />}>
            导出数据
          </Button>
        </div>
      </div>
      
      {/* 统计卡片区域 */}
      <Row gutter={[16, 16]} className="stats-cards">
        <Col xs={24} sm={12} md={6}>
          <Card className="stat-card stat-card-1">
            <Statistic 
              title="总报告数量" 
              value={pagination.total || 0} 
              prefix={<DatabaseOutlined />} 
              suffix="个"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="stat-card stat-card-2">
            <Statistic 
              title="项目数量" 
              value={filterOptions.projectCodes.length || 0} 
              prefix={<AppstoreOutlined />} 
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="stat-card stat-card-3">
            <Statistic 
              title="解决方案" 
              value={filterOptions.solutions.length || 0} 
              prefix={<BarChartOutlined />} 
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="stat-card stat-card-4">
            <Statistic 
              title="模型数量" 
              value={filterOptions.models.length || 0} 
              prefix={<TableOutlined />} 
            />
          </Card>
        </Col>
      </Row>
      
      {/* 筛选区域 */}
      <Card 
        className="filter-card"
        title={<><FilterOutlined /> 筛选条件</>}
        extra={<Button type="link" onClick={() => setFilters({})}>重置筛选</Button>}
      >
        <Row gutter={[24, 16]}>
          <Col xs={24} sm={8}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Typography.Text strong>项目代码</Typography.Text>
              <Select
                placeholder="选择项目代码"
                style={{ width: '100%' }}
                allowClear
                suffixIcon={<SearchOutlined />}
                onChange={(value) => handleFilterChange('project_code', value)}
                showSearch
                optionFilterProp="children"
                value={filters.project_code}
                className="custom-select"
              >
                {filterOptions.projectCodes.map(code => (
                  <Option key={code} value={code}>{code}</Option>
                ))}
              </Select>
            </Space>
          </Col>
          <Col xs={24} sm={8}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Typography.Text strong>解决方案</Typography.Text>
              <Select
                placeholder="选择解决方案"
                style={{ width: '100%' }}
                allowClear
                suffixIcon={<SearchOutlined />}
                onChange={(value) => handleFilterChange('solution', value)}
                showSearch
                optionFilterProp="children"
                value={filters.solution}
                className="custom-select"
              >
                {filterOptions.solutions.map(solution => (
                  <Option key={solution} value={solution}>{solution}</Option>
                ))}
              </Select>
            </Space>
          </Col>
          <Col xs={24} sm={8}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Typography.Text strong>模型</Typography.Text>
              <Select
                placeholder="选择模型"
                style={{ width: '100%' }}
                allowClear
                suffixIcon={<SearchOutlined />}
                onChange={(value) => handleFilterChange('model', value)}
                showSearch
                optionFilterProp="children"
                value={filters.model}
                className="custom-select"
              >
                {filterOptions.models.map(model => (
                  <Option key={model} value={model}>{model}</Option>
                ))}
              </Select>
            </Space>
          </Col>
        </Row>
        <div className="active-filters">
          {Object.entries(filters).filter(([_, value]) => value !== undefined).length > 0 && (
            <>
              <Divider orientation="left">当前筛选</Divider>
              <Space wrap>
                {Object.entries(filters).map(([key, value]) => {
                  if (value === undefined) return null;
                  return (
                    <Tag 
                      key={key} 
                      closable 
                      color="blue" 
                      onClose={() => handleFilterChange(key, undefined)}
                    >
                      {key === 'project_code' ? '项目代码' : key === 'solution' ? '解决方案' : '模型'}: {value}
                    </Tag>
                  );
                })}
              </Space>
            </>
          )}
        </div>
      </Card>
      
      {/* 数据表格 */}
      <Card 
        className="data-table-card"
        title={
          <Space>
            <DatabaseOutlined /> 
            <span>数据列表</span>
            {loading && <SyncOutlined spin />}
          </Space>
        }
        extra={
          <Typography.Text type="secondary">
            最后更新时间: {new Date().toLocaleString()}
          </Typography.Text>
        }
      >
        <div className="table-container">
          <Spin spinning={loading} tip="加载中...">
            <Table
              rowKey="_id"
              columns={columns}
              dataSource={dataList}
              pagination={{
                ...pagination,
                showSizeChanger: true,
                showTotal: (total) => `共 ${total} 条数据`,
                showQuickJumper: true,
                className: "custom-pagination"
              }}
              onChange={handleTableChange}
              scroll={{ x: 'max-content' }}
              bordered
              rowClassName={(record, index) => index % 2 === 0 ? 'table-row-light' : 'table-row-dark'}
              className="custom-table"
            />
          </Spin>
        </div>
      </Card>
    </div>
  );
};

export default Dashboard;
