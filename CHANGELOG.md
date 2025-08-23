# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2024-12-21 15:30

### Added
- 建立了标准的Python项目目录结构
- 新增了模块化的API服务架构
- 添加了完整的测试套件覆盖
- 新增了配置管理模块统一配置处理
- 添加了航空公司管理模块
- 实现了HTTP客户端模块用于网络请求
- 新增了数据解析器和存储模块
- 添加了请求限流和规范化处理模块

### Changed
- **重大重构**: 将单体应用拆分为模块化架构
- 统一了配置管理，合并了根目录和包内的config.py文件
- 重构了爬虫实现，统一了AerolopaCrawler和Crawler类
- 模块化了API服务，将大文件拆分为功能模块：
  - `api/app.py` - 应用工厂和配置
  - `api/routes.py` - 路由定义
  - `api/validators.py` - 请求验证
  - `api/utils.py` - 工具函数
  - `api/decorators.py` - 装饰器
  - `api/exceptions.py` - 异常处理
- 优化了airlines_config管理，移入包内并标准化
- 更新了所有模块导入关系，确保依赖清晰
- 修复了测试文件中的导入问题和测试逻辑

### Removed
- 移除了根目录下冗余的config.py和airlines_config.py文件
- 清理了重复的爬虫实现代码
- 移除了test_tools目录中的过时测试文件

### Fixed
- 修复了CLI测试中的HttpClient导入问题
- 解决了模块间循环依赖问题
- 修复了配置文件路径引用错误
- 确保了所有测试用例正常通过

### Technical Details
- 项目结构现在遵循标准Python包布局
- 所有功能模块职责单一，代码可读性和可维护性显著提升
- 模块间依赖关系清晰合理
- 测试覆盖率达到29%，所有核心功能均有测试保障
- API服务支持健康检查、统计信息和航空公司数据查询

### Migration Notes
- 如果您之前直接导入根目录的config或airlines_config，请更新为从`aerolopa_crawler.config`和`aerolopa_crawler.airlines`导入
- CLI接口保持不变，但内部实现已完全重构
- API端点保持向后兼容