#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本

提供便捷的测试运行接口，支持：
- 运行所有测试
- 运行特定类型的测试
- 生成测试报告
- 代码覆盖率分析
- 性能测试

Usage:
    python run_all_tests.py                    # 运行所有测试
    python run_all_tests.py --unit             # 只运行单元测试
    python run_all_tests.py --integration      # 只运行集成测试
    python run_all_tests.py --performance      # 只运行性能测试
    python run_all_tests.py --coverage         # 运行测试并生成覆盖率报告
    python run_all_tests.py --report           # 生成详细的HTML报告

Author: AeroLOPA Crawler Team
Version: 1.0.0
Date: 2024
"""

import os
import sys
import argparse
import subprocess
import time
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.project_root = project_root
        self.test_dir = self.project_root / 'tests'
        self.reports_dir = self.project_root / 'reports'
        self.coverage_dir = self.project_root / 'htmlcov'
        
        # 确保报告目录存在
        self.reports_dir.mkdir(exist_ok=True)
        self.coverage_dir.mkdir(exist_ok=True)
    
    def check_dependencies(self):
        """检查测试依赖"""
        print("检查测试依赖...")
        
        required_packages = [
            ('pytest', 'pytest'),
            ('pytest-cov', 'pytest_cov'),
            ('pytest-html', 'pytest_html'),
            ('coverage', 'coverage'),
            ('requests', 'requests'),
            ('beautifulsoup4', 'bs4')
        ]
        
        missing_packages = []
        
        for package_name, import_name in required_packages:
            try:
                __import__(import_name)
            except ImportError:
                missing_packages.append(package_name)
        
        if missing_packages:
            print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
            print("请运行: pip install -r requirements.txt")
            return False
        
        print("✅ 所有依赖包已安装")
        return True
    
    def run_unit_tests(self, coverage=False, verbose=True):
        """运行单元测试"""
        print("\n" + "="*50)
        print("运行单元测试")
        print("="*50)
        
        cmd = ['python', '-m', 'pytest', 'tests/', '-m', 'unit']
        
        if coverage:
            cmd.extend(['--cov=.', '--cov-report=html', '--cov-report=term'])
        
        if verbose:
            cmd.append('-v')
        
        cmd.extend([
            '--html=reports/unit_tests.html',
            '--self-contained-html'
        ])
        
        return self._run_command(cmd)
    
    def run_integration_tests(self, verbose=True):
        """运行集成测试"""
        print("\n" + "="*50)
        print("运行集成测试")
        print("="*50)
        
        # 检查API服务器是否运行
        if not self._check_api_server():
            print("⚠️  API服务器未运行，尝试启动...")
            if not self._start_api_server():
                print("❌ 无法启动API服务器，跳过集成测试")
                return False
        
        cmd = ['python', '-m', 'pytest', 'tests/', '-m', 'integration']
        
        if verbose:
            cmd.append('-v')
        
        cmd.extend([
            '--html=reports/integration_tests.html',
            '--self-contained-html'
        ])
        
        return self._run_command(cmd)
    
    def run_performance_tests(self, verbose=True):
        """运行性能测试"""
        print("\n" + "="*50)
        print("运行性能测试")
        print("="*50)
        
        # 检查API服务器是否运行
        if not self._check_api_server():
            print("⚠️  API服务器未运行，尝试启动...")
            if not self._start_api_server():
                print("❌ 无法启动API服务器，跳过性能测试")
                return False
        
        cmd = ['python', '-m', 'pytest', 'tests/', '-m', 'performance']
        
        if verbose:
            cmd.append('-v')
        
        cmd.extend([
            '--html=reports/performance_tests.html',
            '--self-contained-html',
            '--durations=0'  # 显示所有测试的执行时间
        ])
        
        return self._run_command(cmd)
    
    def run_all_tests(self, coverage=True, verbose=True):
        """运行所有测试"""
        print("\n" + "="*60)
        print("运行完整测试套件")
        print("="*60)
        
        start_time = time.time()
        
        cmd = ['pytest', 'tests/']
        
        if coverage:
            cmd.extend([
                '--cov=.',
                '--cov-report=html:htmlcov',
                '--cov-report=term-missing',
                '--cov-report=xml:coverage.xml'
            ])
        
        if verbose:
            cmd.append('-v')
        
        cmd.extend([
            '--html=reports/all_tests.html',
            '--self-contained-html',
            '--durations=10',
            '--tb=short'
        ])
        
        success = self._run_command(cmd)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n测试完成，总耗时: {duration:.2f}秒")
        
        if coverage and success:
            self._show_coverage_summary()
        
        return success
    
    def run_smoke_tests(self):
        """运行冒烟测试（快速验证）"""
        print("\n" + "="*50)
        print("运行冒烟测试")
        print("="*50)
        
        cmd = [
            'pytest', 'tests/',
            '-m', 'smoke',
            '-v',
            '--tb=line',
            '--durations=5'
        ]
        
        return self._run_command(cmd)
    
    def generate_coverage_report(self):
        """生成覆盖率报告"""
        print("\n" + "="*50)
        print("生成覆盖率报告")
        print("="*50)
        
        # 运行覆盖率测试
        cmd = [
            'pytest', 'tests/',
            '--cov=.',
            '--cov-report=html:htmlcov',
            '--cov-report=term-missing',
            '--cov-report=xml:coverage.xml',
            '--cov-report=json:coverage.json',
            '-q'  # 安静模式
        ]
        
        success = self._run_command(cmd)
        
        if success:
            print(f"\n✅ 覆盖率报告已生成:")
            print(f"   HTML报告: {self.coverage_dir / 'index.html'}")
            print(f"   XML报告:  {self.project_root / 'coverage.xml'}")
            print(f"   JSON报告: {self.project_root / 'coverage.json'}")
        
        return success
    
    def clean_test_artifacts(self):
        """清理测试产生的文件"""
        print("清理测试文件...")
        
        patterns_to_clean = [
            '**/__pycache__',
            '**/*.pyc',
            '**/*.pyo',
            '.coverage*',
            '.pytest_cache',
            'htmlcov',
            'reports/*.html',
            'coverage.xml',
            'coverage.json'
        ]
        
        import shutil
        from glob import glob
        
        for pattern in patterns_to_clean:
            for path in glob(str(self.project_root / pattern), recursive=True):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    print(f"已删除: {path}")
                except Exception as e:
                    print(f"删除失败 {path}: {e}")
        
        print("✅ 清理完成")
    
    def _check_api_server(self):
        """检查API服务器是否运行"""
        try:
            import requests
            response = requests.get('http://localhost:5000/health', timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def _start_api_server(self):
        """启动API服务器"""
        try:
            # 这里可以添加启动API服务器的逻辑
            print("请手动启动API服务器: python app.py")
            return False
        except Exception:
            return False
    
    def _run_command(self, cmd):
        """运行命令"""
        try:
            print(f"执行命令: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=False,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"❌ 命令执行失败: {e}")
            return False
    
    def _show_coverage_summary(self):
        """显示覆盖率摘要"""
        coverage_file = self.project_root / 'coverage.json'
        if coverage_file.exists():
            try:
                import json
                with open(coverage_file, 'r', encoding='utf-8') as f:
                    coverage_data = json.load(f)
                
                total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
                print(f"\n📊 代码覆盖率: {total_coverage:.1f}%")
                
                if total_coverage >= 80:
                    print("✅ 覆盖率良好")
                elif total_coverage >= 60:
                    print("⚠️  覆盖率一般，建议提高")
                else:
                    print("❌ 覆盖率较低，需要改进")
                    
            except Exception as e:
                print(f"无法读取覆盖率数据: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='AeroLOPA Crawler 测试运行器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_all_tests.py                    # 运行所有测试
  python run_all_tests.py --unit             # 只运行单元测试
  python run_all_tests.py --integration      # 只运行集成测试
  python run_all_tests.py --performance      # 只运行性能测试
  python run_all_tests.py --coverage         # 生成覆盖率报告
  python run_all_tests.py --smoke            # 运行冒烟测试
  python run_all_tests.py --clean            # 清理测试文件
        """
    )
    
    parser.add_argument('--unit', action='store_true', help='运行单元测试')
    parser.add_argument('--integration', action='store_true', help='运行集成测试')
    parser.add_argument('--performance', action='store_true', help='运行性能测试')
    parser.add_argument('--coverage', action='store_true', help='生成覆盖率报告')
    parser.add_argument('--smoke', action='store_true', help='运行冒烟测试')
    parser.add_argument('--clean', action='store_true', help='清理测试文件')
    parser.add_argument('--no-coverage', action='store_true', help='不生成覆盖率报告')
    parser.add_argument('--quiet', '-q', action='store_true', help='安静模式')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # 清理模式
    if args.clean:
        runner.clean_test_artifacts()
        return 0
    
    # 检查依赖
    if not runner.check_dependencies():
        return 1
    
    verbose = not args.quiet
    success = True
    
    print(f"\n🚀 AeroLOPA Crawler 测试开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 根据参数运行相应的测试
    if args.unit:
        success = runner.run_unit_tests(coverage=not args.no_coverage, verbose=verbose)
    elif args.integration:
        success = runner.run_integration_tests(verbose=verbose)
    elif args.performance:
        success = runner.run_performance_tests(verbose=verbose)
    elif args.coverage:
        success = runner.generate_coverage_report()
    elif args.smoke:
        success = runner.run_smoke_tests()
    else:
        # 默认运行所有测试
        success = runner.run_all_tests(coverage=not args.no_coverage, verbose=verbose)
    
    # 输出结果
    if success:
        print("\n🎉 所有测试通过！")
        print(f"📁 测试报告位置: {runner.reports_dir}")
        if not args.no_coverage:
            print(f"📊 覆盖率报告: {runner.coverage_dir / 'index.html'}")
    else:
        print("\n❌ 测试失败，请检查错误信息")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())