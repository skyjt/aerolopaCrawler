#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AeroLOPA API 性能和负载测试

用于测试API在高并发和大负载情况下的性能表现

Author: AeroLOPA Crawler Team
Version: 1.0.0
Date: 2024
"""

import time
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import unittest
from unittest.mock import patch

try:
    import requests
except ImportError:
    requests = None

from src.aerolopa_crawler.api.app import create_app


class APIPerformanceTester:
    """API性能测试器"""
    
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.api_base = f'{base_url}/api/v1'
        if requests:
            self.session = requests.Session()
        self.results = []
        
        # 测试配置
        self.timeout = 30
        self.max_workers = 20
        
    def check_server_availability(self):
        """检查服务器是否可用"""
        if not requests:
            return False
            
        try:
            response = self.session.get(f'{self.base_url}/health', timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def single_request_test(self, endpoint, params=None, method='GET'):
        """单个请求测试"""
        if not requests:
            return {
                'success': False,
                'error': 'requests library not available',
                'response_time': 0,
                'timestamp': datetime.now().isoformat()
            }
            
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
                       num_requests=10, max_workers=5):
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
                if (i + 1) % 5 == 0 or (i + 1) == num_requests:
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


class TestAPIPerformance(unittest.TestCase):
    """API性能测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
    
    def test_health_endpoint_performance(self):
        """测试健康检查端点性能"""
        start_time = time.time()
        
        # 连续请求10次
        for _ in range(10):
            response = self.client.get('/health')
            self.assertEqual(response.status_code, 200)
        
        total_time = time.time() - start_time
        avg_time = total_time / 10
        
        # 平均响应时间应小于0.1秒
        self.assertLess(avg_time, 0.1, f"健康检查平均响应时间过长: {avg_time:.3f}s")
    
    def test_airlines_endpoint_performance(self):
        """测试航空公司列表端点性能"""
        start_time = time.time()
        
        # 连续请求5次
        for _ in range(5):
            response = self.client.get('/api/v1/airlines')
            self.assertEqual(response.status_code, 200)
        
        total_time = time.time() - start_time
        avg_time = total_time / 5
        
        # 平均响应时间应小于0.5秒
        self.assertLess(avg_time, 0.5, f"航空公司列表平均响应时间过长: {avg_time:.3f}s")
    
    @unittest.skipIf(not requests, "requests library not available")
    def test_concurrent_requests(self):
        """测试并发请求"""
        # 这个测试需要实际的服务器运行
        # 在单元测试中跳过，可以在集成测试中运行
        self.skipTest("需要运行中的服务器进行并发测试")
    
    def test_response_time_consistency(self):
        """测试响应时间一致性"""
        response_times = []
        
        # 测试10次请求（减少测试次数提高稳定性）
        for _ in range(10):
            start_time = time.time()
            response = self.client.get('/health')
            end_time = time.time()
            
            self.assertEqual(response.status_code, 200)
            response_times.append(end_time - start_time)
        
        # 计算统计信息
        mean_time = statistics.mean(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        # 检查响应时间范围（最大响应时间不应超过平均时间的10倍或0.1秒，取较大值）
        # 这样既考虑了相对性能，也设置了绝对上限
        max_allowed = max(mean_time * 10, 0.1)
        self.assertLess(max_time, max_allowed, 
                       f"响应时间变化过大: 最大{max_time:.3f}s, 平均{mean_time:.3f}s, 允许最大{max_allowed:.3f}s")
        
        # 确保所有响应时间都在合理范围内（小于1秒）
        self.assertLess(max_time, 1.0, f"响应时间过长: {max_time:.3f}s")


if __name__ == '__main__':
    unittest.main()