# AeroLOPA Crawler 测试文档

本文档详细介绍了 AeroLOPA Crawler 项目的测试系统，包括测试结构、运行方法、最佳实践等。

## 📋 目录

- [测试概述](#测试概述)
- [测试结构](#测试结构)
- [快速开始](#快速开始)
- [测试类型](#测试类型)
- [运行测试](#运行测试)
- [测试配置](#测试配置)
- [代码覆盖率](#代码覆盖率)
- [持续集成](#持续集成)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)

## 🎯 测试概述

本项目采用全面的测试策略，确保 API 接口的稳定性和可靠性：

- **单元测试**: 测试独立的函数和类
- **集成测试**: 测试组件间的交互
- **API 测试**: 测试 HTTP 接口
- **性能测试**: 测试系统性能和负载能力
- **爬虫测试**: 测试网页抓取功能

## 📁 测试结构

```
tests/
├── __init__.py              # 测试包初始化
├── conftest.py              # pytest 配置和 fixtures
├── test_api.py              # API 接口测试
├── test_crawler_unit.py     # 爬虫单元测试
├── test_cli_smoke.py        # CLI 冒烟测试
├── test_normalizers.py      # 数据标准化测试
├── test_throttle.py         # 限流测试
└── test_performance.py      # 性能测试
```

### 配置文件

```
├── pytest.ini              # pytest 配置
├── .coveragerc             # 覆盖率配置

└── .github/workflows/tests.yml  # CI/CD 配置
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装所有依赖（包括测试依赖）
pip install -r requirements.txt
```

### 2. 运行所有测试

```bash
# 使用 pytest 运行测试
pytest tests/
```

### 3. 查看测试报告

测试完成后，可以在以下位置查看报告：
- HTML 报告: `reports/all_tests.html`
- 覆盖率报告: `htmlcov/index.html`

## 🧪 测试类型

### 单元测试 (Unit Tests)

测试独立的函数和类，不依赖外部服务。

```bash
# 运行单元测试
pytest tests/ -m unit
```

**覆盖范围:**
- 参数验证函数
- 数据处理函数
- 配置管理
- 工具函数

### 集成测试 (Integration Tests)

测试组件间的交互，需要 API 服务器运行。

```bash
# 先启动 API 服务器
python app.py

# 在另一个终端运行集成测试
pytest tests/ -m integration
```

**覆盖范围:**
- API 端点交互
- 数据库操作
- 外部服务调用

### API 测试

测试 HTTP 接口的功能和错误处理。

```bash
# 运行 API 测试
pytest tests/test_api.py -v
```

**测试端点:**
- `GET /` - 根路径
- `GET /health` - 健康检查
- `GET /api/v1/airlines` - 航空公司列表
- `GET /api/v1/seatmap` - 座位图查询
- `POST /api/v1/seatmap` - 座位图提交

### 性能测试 (Performance Tests)

测试系统在负载下的表现。

```bash
# 运行性能测试
pytest tests/ -m performance

# 或直接运行性能测试脚本
python tests/test_performance.py
```

**测试指标:**
- 响应时间
- 吞吐量 (RPS)
- 并发处理能力
- 错误率

### 爬虫测试 (Crawler Tests)

测试网页抓取和数据解析功能。

```bash
# 运行爬虫测试
pytest tests/test_crawler_unit.py -v
```

**覆盖范围:**
- 网页抓取
- HTML 解析
- 图片下载
- 重试机制

## 🏃‍♂️ 运行测试

### 使用 pytest 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定类型的测试
pytest tests/ -m unit           # 单元测试
pytest tests/ -m integration    # 集成测试
pytest tests/ -m performance    # 性能测试

# 生成覆盖率报告
pytest tests/ --cov=. --cov-report=html

# 运行冒烟测试（快速验证）
pytest tests/ -m smoke
```

### 使用 pytest 直接运行

```bash
# 运行所有测试
pytest tests/

# 运行特定文件
pytest tests/test_api.py

# 运行特定测试函数
pytest tests/test_api.py::TestAPIEndpoints::test_health_check

# 使用标记运行测试
pytest tests/ -m "unit and not slow"

# 并行运行测试
pytest tests/ -n auto

# 详细输出
pytest tests/ -v

# 显示最慢的10个测试
pytest tests/ --durations=10
```

### 测试标记 (Markers)

项目定义了以下测试标记：

- `unit`: 单元测试
- `integration`: 集成测试
- `performance`: 性能测试
- `slow`: 运行时间较长的测试
- `api`: API 接口测试
- `crawler`: 爬虫功能测试
- `smoke`: 冒烟测试

```bash
# 运行快速测试（排除慢测试）
pytest tests/ -m "not slow"

# 运行 API 相关测试
pytest tests/ -m api

# 组合标记
pytest tests/ -m "unit or integration"
```

## ⚙️ 测试配置

### pytest.ini

主要配置项：

```ini
[tool:pytest]
testpaths = tests
addopts = -v --tb=short --strict-markers
markers =
    unit: 单元测试
    integration: 集成测试
    performance: 性能测试
```

### test_config.py

测试配置和数据：

```python
# API 服务器配置
TEST_CONFIG = {
    'api_server': {
        'host': 'localhost',
        'port': 5000,
        'timeout': 30
    }
}

# 测试数据
TEST_DATA = {
    'airlines': ['CA', 'MU', 'CZ'],
    'aircraft_types': ['737', '320', '777']
}
```

## 📊 代码覆盖率

### 生成覆盖率报告

```bash
# 运行测试并生成覆盖率报告
pytest tests/ --cov=. --cov-report=html

# 或使用主脚本
pytest tests/ --cov=. --cov-report=html
```

### 查看覆盖率报告

- **HTML 报告**: 打开 `htmlcov/index.html`
- **终端报告**: 运行测试时直接显示
- **XML 报告**: `coverage.xml` (用于 CI/CD)

### 覆盖率目标

- **总体覆盖率**: ≥ 80%
- **核心模块**: ≥ 90%
- **API 接口**: ≥ 95%

### 排除文件

在 `.coveragerc` 中配置了排除规则：

```ini
[run]
omit = 
    */tests/*
    */venv/*
    setup.py
```

## 🔄 持续集成

### GitHub Actions

项目配置了 GitHub Actions 工作流 (`.github/workflows/tests.yml`)：

**触发条件:**
- 推送到 `main` 或 `develop` 分支
- 创建 Pull Request
- 每日定时运行

**测试矩阵:**
- Python 版本: 3.8, 3.9, 3.10, 3.11
- 操作系统: Ubuntu Latest

**测试步骤:**
1. 代码检出
2. Python 环境设置
3. 依赖安装
4. 代码质量检查 (flake8)
5. 单元测试
6. 集成测试
7. 覆盖率报告
8. 性能测试 (仅主分支)
9. 安全扫描

### 本地 CI 模拟

```bash
# 模拟 CI 环境运行测试
export FLASK_ENV=testing
export PYTHONPATH=.

# 运行完整测试套件
pytest tests/ --cov=. --cov-report=html
```

## 💡 最佳实践

### 编写测试

1. **测试命名**: 使用描述性的测试名称
   ```python
   def test_validate_iata_code_with_valid_input(self):
       # 测试有效的 IATA 代码验证
   ```

2. **测试结构**: 使用 AAA 模式 (Arrange, Act, Assert)
   ```python
   def test_api_endpoint(self):
       # Arrange - 准备测试数据
       data = {'airline': 'CA', 'aircraft': '737'}
       
       # Act - 执行操作
       response = self.client.get('/api/v1/seatmap', params=data)
       
       # Assert - 验证结果
       self.assertEqual(response.status_code, 200)
   ```

3. **使用 fixtures**: 复用测试设置
   ```python
   @pytest.fixture
   def api_client():
       return TestClient(app)
   ```

4. **模拟外部依赖**: 使用 mock 隔离测试
   ```python
   @patch('requests.get')
   def test_external_api_call(self, mock_get):
       mock_get.return_value.status_code = 200
   ```

### 测试数据管理

1. **使用工厂模式**: 生成测试数据
2. **数据隔离**: 每个测试使用独立的数据
3. **清理资源**: 测试后清理临时文件和数据

### 性能测试

1. **设置合理的阈值**: 基于实际需求设定性能指标
2. **环境一致性**: 在相同环境下进行性能测试
3. **监控趋势**: 跟踪性能变化趋势

## 🔧 故障排除

### 常见问题

#### 1. 测试依赖缺失

**错误**: `ModuleNotFoundError: No module named 'pytest'`

**解决**:
```bash
pip install -r requirements.txt
```

#### 2. API 服务器未启动

**错误**: `ConnectionError: Failed to establish a new connection`

**解决**:
```bash
# 启动 API 服务器
python app.py
```

#### 3. 端口被占用

**错误**: `OSError: [Errno 48] Address already in use`

**解决**:
```bash
# 查找占用端口的进程
lsof -i :5000

# 终止进程
kill -9 <PID>
```

#### 4. 权限问题

**错误**: `PermissionError: [Errno 13] Permission denied`

**解决**:
```bash
# 检查文件权限
ls -la tests/

# 修改权限
# 确保测试文件有执行权限
chmod +x tests/*.py
```

#### 5. 覆盖率报告生成失败

**错误**: `CoverageException: No data to report`

**解决**:
```bash
# 清理旧的覆盖率数据
rm -f .coverage*

# 重新运行测试
pytest tests/ --cov=.
```

### 调试技巧

1. **使用 pdb 调试**:
   ```python
   import pdb; pdb.set_trace()
   ```

2. **增加日志输出**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **运行单个测试**:
   ```bash
   pytest tests/test_api.py::test_specific_function -v -s
   ```

4. **查看详细错误信息**:
   ```bash
   pytest tests/ --tb=long
   ```

### 获取帮助

- 查看测试配置: `pytest --help`
- 查看可用标记: `pytest --markers`
- 查看 fixtures: `pytest --fixtures`

## 📈 测试指标

### 质量指标

- **测试覆盖率**: 当前覆盖率状态
- **测试通过率**: 测试成功的百分比
- **测试执行时间**: 测试套件运行时间

### 性能指标

- **响应时间**: API 接口响应时间
- **吞吐量**: 每秒处理请求数
- **并发能力**: 同时处理的请求数
- **错误率**: 请求失败的百分比

### 监控和报告

测试结果会自动生成以下报告：

1. **HTML 测试报告**: `reports/all_tests.html`
2. **覆盖率报告**: `htmlcov/index.html`
3. **性能测试报告**: `reports/performance_tests.html`
4. **CI/CD 报告**: GitHub Actions 中查看

---

## 📞 联系方式

如果在使用测试系统时遇到问题，请：

1. 查看本文档的故障排除部分
2. 检查 GitHub Issues
3. 联系开发团队

---

**最后更新**: 2024年
**文档版本**: 1.0.0