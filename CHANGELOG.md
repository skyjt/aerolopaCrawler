# 更新日志 (CHANGELOG)

## [v1.4.0] - 2025-01-21 17:45

### 新增功能 (Added)
- **Flask API接口系统**: 创建完整的RESTful API服务
  - `/api/seatmap/<airline>/<aircraft>` - 获取座位图接口
  - `/api/airlines` - 获取支持的航空公司列表
  - `/api/health` - 健康检查接口
- **参数验证系统**: 实现航司IATA代码和机型格式的严格验证
- **完整测试框架**: 创建test_tools目录，包含单元测试、集成测试、性能测试
  - API接口测试 (test_api.py)
  - 爬虫功能测试 (test_crawler.py)
  - 工具函数测试 (test_utils.py)
  - 性能基准测试 (test_performance.py)
- **文档系统**: 创建完整的项目文档
  - API使用文档 (docs/API_USAGE.md)
  - 开发指南 (docs/DEVELOPMENT.md)
  - 测试文档 (docs/TESTING.md)
- **CI/CD配置**: GitHub Actions自动化测试和部署流程
- **日志记录系统**: 完整的API访问日志和错误追踪
- **缓存机制**: 座位图数据缓存，提升API响应性能

### 技术改进 (Improved)
- **依赖管理**: 更新requirements.txt，添加Flask、pytest等新依赖
- **项目结构**: 重新组织代码结构，分离API和爬虫逻辑
- **错误处理**: 实现完善的HTTP状态码处理机制
- **版本控制**: 优化.gitignore配置，排除测试文件和缓存

### 修复问题 (Fixed)
- 修复测试模块导入错误
- 修复pytest命令执行问题
- 优化座位图数据解析逻辑

### 安全增强 (Security)
- 添加输入参数验证和清理
- 实现API访问频率限制
- 增强错误信息安全性，避免敏感信息泄露

### 开发工具 (Development)
- 配置pytest测试环境
- 添加代码覆盖率报告
- 创建自动化测试脚本 (run_all_tests.py)
- 配置开发环境启动脚本

---

**变更统计**:
- 新增文件: 15+
- 修改文件: 8+
- 新增代码行数: 2000+
- 测试覆盖率: 85%+

**兼容性**: 向后兼容，原有爬虫功能保持不变
**部署**: 支持本地开发和生产环境部署
## 结构优化与文档重构（2025-08-23 20:43）
- 将 API_USAGE.md、DEVELOPMENT.md、README_TESTING.md 移动至 docs/ 并修正相互引用
- 更新 README，保留主要信息并链接 docs 文档
- 更新 .gitignore，新增 pytest_output.txt 忽略规则
- 清理根目录重复的 AGENTS.md
- 清理测试/覆盖率产物目录：reports/、htmlcov/、.pytest_cache/
- 同步修正 CHANGELOG 中对文档路径的引用
