#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AeroLOPA API 性能和负载测试

用于测试API在高并发和大负载情况下的性能表现

Author: AeroLOPA Crawler Team
Version: 1.0.0
Date: 2024
"""

import os
import sys
import time
import json
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import requests
except ImportError:
    print("请安装 requests 库: pip install requests")
    sys.exit(1)


class APIPerformanceTester:
    """API性能测试器"""
    
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.api_base = f'{base_url}/api/v1'
        self.session = requests.Session()
        self.results = []
        
        # 测试配置
        self.timeout = 30
        self.max_workers = 20
        
    def check_server_availability(self):
        """检查服务器是否可用"""
        try:
            response = self.session.get(f'{self.base_url}/health', timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def single_request_test(self, endpoint, params=None, method='GET'):
        """单个请求测试"""
        start_time = time.time()
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(f'{self.api_base}{endpoint}', 
                                          params=params, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = self.session.post(f'{self.api_base}{endpoint}', 
                                           json=params, timeout=self.timeout)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                'success': True,
                'status_code': response.status_code,
                'response_time': response_time,
                'response_size': len(response.content),
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            end_time = time.time()
            return {
                'success': False,
                'error': str(e),
                'response_time': end_time - start_time,
                'timestamp': datetime.now().isoformat()
            }
    
    def concurrent_test(self, endpoint, params=None, method='GET', 
                       num_requests=100, max_workers=10):
        """并发测试"""
        print(f"开始并发测试: {num_requests} 个请求，{max_workers} 个并发线程")
        print(f"测试端点: {method} {endpoint}")
        
        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            futures = []
            for i in range(num_requests):
                future = executor.submit(self.single_request_test, endpoint, params, method)
                futures.append(future)
            
            # 收集结果
            for i, future in enumerate(as_completed(futures)):
                result = future.result()
                results.append(result)
                
                # 显示进度
                if (i + 1) % 10 == 0 or (i + 1) == num_requests:
                    print(f"完成: {i + 1}/{num_requests}")
        
        total_time = time.time() - start_time
        
        # 分析结果
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        
        if successful_requests:
            response_times = [r['response_time'] for r in successful_requests]
            status_codes = [r['status_code'] for r in successful_requests]
            
            analysis = {
                'total_requests': num_requests,
                'successful_requests': len(successful_requests),
                'failed_requests': len(failed_requests),
                'success_rate': len(successful_requests) / num_requests * 100,
                'total_time': total_time,
                'requests_per_second': num_requests / total_time,
                'response_time_stats': {
                    'min': min(response_times),
                    'max': max(response_times),
                    'mean': statistics.mean(response_times),
                    'median': statistics.median(response_times),
                    'p95': self._percentile(response_times, 95),
                    'p99': self._percentile(response_times, 99)
                },
                'status_code_distribution': self._count_status_codes(status_codes)
            }
        else:
            analysis = {
                'total_requests': num_requests,
                'successful_requests': 0,
                'failed_requests': len(failed_requests),
                'success_rate': 0,
                'total_time': total_time,
                'requests_per_second': 0,
                'errors': [r['error'] for r in failed_requests[:5]]  # 显示前5个错误
            }
        
        return analysis
    
    def load_test(self, endpoint, params=None, method='GET', 
                  duration_seconds=60, concurrent_users=10):
        """负载测试"""
        print(f"开始负载测试: 持续 {duration_seconds} 秒，{concurrent_users} 个并发用户")
        print(f"测试端点: {method} {endpoint}")
        
        results = []
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        def worker():
            """工作线程"""
            worker_results = []
            while time.time() < end_time:
                result = self.single_request_test(endpoint, params, method)
                worker_results.append(result)
                time.sleep(0.1)  # 短暂休息避免过度负载
            return worker_results
        
        # 启动并发用户
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(worker) for _ in range(concurrent_users)]
            
            # 收集所有结果
            for future in as_completed(futures):
                worker_results = future.result()
                results.extend(worker_results)
        
        actual_duration = time.time() - start_time
        
        # 分析结果
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        
        if successful_requests:
            response_times = [r['response_time'] for r in successful_requests]
            
            analysis = {
                'duration': actual_duration,
                'total_requests': len(results),
                'successful_requests': len(successful_requests),
                'failed_requests': len(failed_requests),
                'success_rate': len(successful_requests) / len(results) * 100,
                'requests_per_second': len(results) / actual_duration,
                'successful_rps': len(successful_requests) / actual_duration,
                'response_time_stats': {
                    'min': min(response_times),
                    'max': max(response_times),
                    'mean': statistics.mean(response_times),
                    'median': statistics.median(response_times),
                    'p95': self._percentile(response_times, 95),
                    'p99': self._percentile(response_times, 99)
                }
            }
        else:
            analysis = {
                'duration': actual_duration,
                'total_requests': len(results),
                'successful_requests': 0,
                'failed_requests': len(failed_requests),
                'success_rate': 0,
                'requests_per_second': len(results) / actual_duration,
                'successful_rps': 0
            }
        
        return analysis
    
    def stress_test(self, endpoint, params=None, method='GET'):
        """压力测试 - 逐步增加负载"""
        print(f"开始压力测试: 逐步增加并发数")
        print(f"测试端点: {method} {endpoint}")
        
        stress_results = []
        concurrent_levels = [1, 5, 10, 20, 50, 100]
        
        for concurrent in concurrent_levels:
            print(f"\n测试并发级别: {concurrent}")
            
            # 每个级别测试50个请求
            result = self.concurrent_test(endpoint, params, method, 
                                        num_requests=50, max_workers=concurrent)
            
            result['concurrent_level'] = concurrent
            stress_results.append(result)
            
            # 如果成功率低于80%，停止测试
            if result['success_rate'] < 80:
                print(f"成功率降至 {result['success_rate']:.1f}%，停止压力测试")
                break
            
            # 短暂休息
            time.sleep(2)
        
        return stress_results
    
    def _percentile(self, data, percentile):
        """计算百分位数"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _count_status_codes(self, status_codes):
        """统计状态码分布"""
        distribution = {}
        for code in status_codes:
            distribution[code] = distribution.get(code, 0) + 1
        return distribution
    
    def print_analysis(self, analysis, title="测试结果"):
        """打印分析结果"""
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}")
        
        if isinstance(analysis, list):  # 压力测试结果
            for result in analysis:
                concurrent = result['concurrent_level']
                success_rate = result['success_rate']
                rps = result['requests_per_second']
                
                if 'response_time_stats' in result:
                    avg_time = result['response_time_stats']['mean']
                    p95_time = result['response_time_stats']['p95']
                    print(f"并发 {concurrent:3d}: 成功率 {success_rate:5.1f}%, "
                          f"RPS {rps:6.1f}, 平均响应 {avg_time*1000:6.1f}ms, "
                          f"P95 {p95_time*1000:6.1f}ms")
                else:
                    print(f"并发 {concurrent:3d}: 成功率 {success_rate:5.1f}%, RPS {rps:6.1f}")
        
        else:  # 单个测试结果
            print(f"总请求数: {analysis['total_requests']}")
            print(f"成功请求: {analysis['successful_requests']}")
            print(f"失败请求: {analysis['failed_requests']}")
            print(f"成功率: {analysis['success_rate']:.2f}%")
            
            if 'total_time' in analysis:
                print(f"总耗时: {analysis['total_time']:.2f} 秒")
            if 'duration' in analysis:
                print(f"测试时长: {analysis['duration']:.2f} 秒")
            
            print(f"请求速率: {analysis['requests_per_second']:.2f} RPS")
            
            if 'successful_rps' in analysis:
                print(f"成功请求速率: {analysis['successful_rps']:.2f} RPS")
            
            if 'response_time_stats' in analysis:
                stats = analysis['response_time_stats']
                print(f"\n响应时间统计 (毫秒):")
                print(f"  最小值: {stats['min']*1000:.1f}")
                print(f"  最大值: {stats['max']*1000:.1f}")
                print(f"  平均值: {stats['mean']*1000:.1f}")
                print(f"  中位数: {stats['median']*1000:.1f}")
                print(f"  P95: {stats['p95']*1000:.1f}")
                print(f"  P99: {stats['p99']*1000:.1f}")
            
            if 'status_code_distribution' in analysis:
                print(f"\n状态码分布:")
                for code, count in analysis['status_code_distribution'].items():
                    print(f"  {code}: {count}")
            
            if 'errors' in analysis and analysis['errors']:
                print(f"\n错误示例:")
                for error in analysis['errors'][:3]:
                    print(f"  - {error}")


def main():
    """主函数"""
    print("AeroLOPA API 性能测试工具")
    print("="*50)
    
    # 初始化测试器
    tester = APIPerformanceTester()
    
    # 检查服务器可用性
    print("检查服务器可用性...")
    if not tester.check_server_availability():
        print("错误: 无法连接到API服务器 (http://localhost:5000)")
        print("请确保API服务器正在运行")
        return
    
    print("服务器可用，开始性能测试\n")
    
    # 测试用例
    test_cases = [
        {
            'name': '健康检查',
            'endpoint': '/health',
            'method': 'GET'
        },
        {
            'name': '航空公司列表',
            'endpoint': '/airlines',
            'method': 'GET'
        },
        {
            'name': '特定航空公司信息',
            'endpoint': '/airlines/CA',
            'method': 'GET'
        },
        {
            'name': '座位图查询',
            'endpoint': '/seatmap',
            'method': 'GET',
            'params': {'airline': 'CA', 'aircraft': 'A320'}
        }
    ]
    
    # 运行测试
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试 {test_case['name']}")
        print("-" * 40)
        
        # 并发测试
        print("\n并发测试 (100 请求, 10 并发):")
        concurrent_result = tester.concurrent_test(
            test_case['endpoint'],
            test_case.get('params'),
            test_case['method'],
            num_requests=100,
            max_workers=10
        )
        tester.print_analysis(concurrent_result, "并发测试结果")
        
        # 如果是轻量级端点，进行负载测试
        if test_case['name'] in ['健康检查', '航空公司列表']:
            print("\n负载测试 (30秒, 5并发):")
            load_result = tester.load_test(
                test_case['endpoint'],
                test_case.get('params'),
                test_case['method'],
                duration_seconds=30,
                concurrent_users=5
            )
            tester.print_analysis(load_result, "负载测试结果")
    
    # 压力测试（仅对健康检查端点）
    print("\n\n压力测试 - 健康检查端点")
    print("="*50)
    stress_results = tester.stress_test('/health')
    tester.print_analysis(stress_results, "压力测试结果")
    
    print("\n\n性能测试完成！")
    print("建议:")
    print("- 响应时间应保持在 1000ms 以下")
    print("- 成功率应保持在 99% 以上")
    print("- P95 响应时间应保持在 2000ms 以下")
    print("- 在正常负载下 RPS 应达到预期值")


if __name__ == '__main__':
    main()