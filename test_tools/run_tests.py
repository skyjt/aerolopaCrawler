#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AeroLOPA API 测试运行器

统一的测试运行脚本，支持运行不同类型的测试

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

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.test_dir)
        
    def check_dependencies(self):
        """检查测试依赖"""
        print("检查测试依赖...")
        
        required_packages = ['requests', 'flask', 'beautifulsoup4']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✓ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"✗ {package} (缺失)")
        
        if missing_packages:
            print(f"\n缺少以下依赖包: {', '.join(missing_packages)}")
            print("请运行: pip install -r requirements.txt")
            return False
        
        print("所有依赖检查通过\n")
        return True
    
    def check_api_server(self, timeout=5):
        """检查API服务器状态"""
        try:
            import requests
            response = requests.get('http://localhost:5000/health', timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    def start_api_server(self):
        """启动API服务器"""
        print("启动API服务器...")
        
        app_path = os.path.join(self.project_root, 'app.py')
        if not os.path.exists(app_path):
            print(f"错误: 找不到 app.py 文件: {app_path}")
            return None
        
        try:
            # 启动Flask应用
            process = subprocess.Popen(
                [sys.executable, app_path],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 等待服务器启动
            print("等待服务器启动...", end="")
            for i in range(30):  # 最多等待30秒
                if self.check_api_server():
                    print(" 完成")
                    return process
                time.sleep(1)
                print(".", end="", flush=True)
            
            print(" 超时")
            process.terminate()
            return None
            
        except Exception as e:
            print(f"启动服务器失败: {e}")
            return None
    
    def run_unit_tests(self, verbose=True):
        """运行单元测试"""
        print("运行单元测试...")
        print("="*50)
        
        test_file = os.path.join(self.test_dir, 'test_api.py')
        
        try:
            cmd = [sys.executable, test_file]
            if verbose:
                cmd.append('-v')
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            print(result.stdout)
            if result.stderr:
                print("错误输出:")
                print(result.stderr)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"运行单元测试失败: {e}")
            return False
    
    def run_performance_tests(self):
        """运行性能测试"""
        print("运行性能测试...")
        print("="*50)
        
        # 检查API服务器
        if not self.check_api_server():
            print("API服务器未运行，尝试启动...")
            server_process = self.start_api_server()
            if not server_process:
                print("无法启动API服务器，跳过性能测试")
                return False
        else:
            server_process = None
        
        try:
            test_file = os.path.join(self.test_dir, 'test_performance.py')
            
            result = subprocess.run(
                [sys.executable, test_file],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            print(result.stdout)
            if result.stderr:
                print("错误输出:")
                print(result.stderr)
            
            success = result.returncode == 0
            
        except Exception as e:
            print(f"运行性能测试失败: {e}")
            success = False
        
        finally:
            # 清理服务器进程
            if server_process:
                print("\n关闭API服务器...")
                server_process.terminate()
                server_process.wait()
        
        return success
    
    def run_integration_tests(self):
        """运行集成测试"""
        print("运行集成测试...")
        print("="*50)
        
        # 检查API服务器
        if not self.check_api_server():
            print("API服务器未运行，尝试启动...")
            server_process = self.start_api_server()
            if not server_process:
                print("无法启动API服务器，跳过集成测试")
                return False
        else:
            server_process = None
        
        try:
            # 运行集成测试（使用unittest发现机制）
            result = subprocess.run(
                [sys.executable, '-m', 'unittest', 'test_tools.test_api.TestAPIIntegration', '-v'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            print(result.stdout)
            if result.stderr:
                print("错误输出:")
                print(result.stderr)
            
            success = result.returncode == 0
            
        except Exception as e:
            print(f"运行集成测试失败: {e}")
            success = False
        
        finally:
            # 清理服务器进程
            if server_process:
                print("\n关闭API服务器...")
                server_process.terminate()
                server_process.wait()
        
        return success
    
    def run_all_tests(self, include_performance=False):
        """运行所有测试"""
        print(f"开始完整测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        results = {}
        
        # 1. 检查依赖
        if not self.check_dependencies():
            return False
        
        # 2. 运行单元测试
        print("\n1. 单元测试")
        results['unit'] = self.run_unit_tests()
        
        # 3. 运行集成测试
        print("\n2. 集成测试")
        results['integration'] = self.run_integration_tests()
        
        # 4. 运行性能测试（可选）
        if include_performance:
            print("\n3. 性能测试")
            results['performance'] = self.run_performance_tests()
        
        # 输出测试摘要
        print("\n" + "="*60)
        print("测试摘要")
        print("="*60)
        
        all_passed = True
        for test_type, passed in results.items():
            status = "通过" if passed else "失败"
            print(f"{test_type.capitalize():12} 测试: {status}")
            if not passed:
                all_passed = False
        
        print(f"\n总体结果: {'所有测试通过' if all_passed else '存在测试失败'}")
        print(f"测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return all_passed
    
    def generate_test_report(self):
        """生成测试报告"""
        print("生成测试报告...")
        
        report_file = os.path.join(self.test_dir, 'test_report.md')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# AeroLOPA API 测试报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 测试环境\n\n")
            f.write(f"- Python版本: {sys.version}\n")
            f.write(f"- 操作系统: {os.name}\n")
            f.write(f"- 测试目录: {self.test_dir}\n\n")
            
            f.write("## 测试用例\n\n")
            f.write("### 单元测试\n")
            f.write("- API参数验证测试\n")
            f.write("- API端点功能测试\n")
            f.write("- 错误处理测试\n\n")
            
            f.write("### 集成测试\n")
            f.write("- 完整API工作流程测试\n")
            f.write("- 端到端功能测试\n\n")
            
            f.write("### 性能测试\n")
            f.write("- 并发请求测试\n")
            f.write("- 负载测试\n")
            f.write("- 压力测试\n\n")
            
            f.write("## 运行方式\n\n")
            f.write("```bash\n")
            f.write("# 运行所有测试\n")
            f.write("python test_tools/run_tests.py --all\n\n")
            f.write("# 仅运行单元测试\n")
            f.write("python test_tools/run_tests.py --unit\n\n")
            f.write("# 运行性能测试\n")
            f.write("python test_tools/run_tests.py --performance\n")
            f.write("```\n\n")
        
        print(f"测试报告已生成: {report_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AeroLOPA API 测试运行器')
    parser.add_argument('--unit', action='store_true', help='仅运行单元测试')
    parser.add_argument('--integration', action='store_true', help='仅运行集成测试')
    parser.add_argument('--performance', action='store_true', help='仅运行性能测试')
    parser.add_argument('--all', action='store_true', help='运行所有测试')
    parser.add_argument('--with-performance', action='store_true', help='在完整测试中包含性能测试')
    parser.add_argument('--report', action='store_true', help='生成测试报告')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # 生成测试报告
    if args.report:
        runner.generate_test_report()
        return
    
    success = True
    
    # 根据参数运行相应测试
    if args.unit:
        success = runner.run_unit_tests(args.verbose)
    elif args.integration:
        success = runner.run_integration_tests()
    elif args.performance:
        success = runner.run_performance_tests()
    elif args.all:
        success = runner.run_all_tests(args.with_performance)
    else:
        # 默认运行单元测试和集成测试
        print("运行默认测试套件 (单元测试 + 集成测试)")
        success = runner.run_all_tests(False)
    
    # 退出码
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()