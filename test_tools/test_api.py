#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AeroLOPA API 测试用例

包含完整的单元测试和集成测试，用于验证API接口的功能和稳定性

Author: AeroLOPA Crawler Team
Version: 1.0.0
Date: 2024
"""

import os
import sys
import json
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from app import app, validate_iata_code, validate_aircraft_model, standardize_aircraft_model
from config import DATA_DIR, LOGS_DIR
from airlines_config import AIRLINES


class TestAPIValidation(unittest.TestCase):
    """API参数验证测试"""
    
    def test_validate_iata_code(self):
        """测试IATA代码验证"""
        # 有效的IATA代码
        valid_codes = ['CA', 'CZ', 'MU', '3U', 'AA', 'UA', 'DL']
        for code in valid_codes:
            self.assertTrue(validate_iata_code(code), f"IATA代码 {code} 应该有效")
        
        # 无效的IATA代码
        invalid_codes = ['', None, 'A', 'ABCD', '123', 'a1', 'CA1']
        for code in invalid_codes:
            self.assertFalse(validate_iata_code(code), f"IATA代码 {code} 应该无效")
    
    def test_validate_aircraft_model(self):
        """测试机型验证"""
        # 有效的机型
        valid_models = ['A320', 'B737', 'A380', 'B777-300ER', 'A350-900', 'CRJ900']
        for model in valid_models:
            self.assertTrue(validate_aircraft_model(model), f"机型 {model} 应该有效")
        
        # 无效的机型
        invalid_models = ['', None, 'A', 'A' * 25, '!@#$%', '中文机型']
        for model in invalid_models:
            self.assertFalse(validate_aircraft_model(model), f"机型 {model} 应该无效")
    
    def test_standardize_aircraft_model(self):
        """测试机型标准化"""
        test_cases = [
            ('boeing 737', 'B 737'),
            ('airbus a320', 'A A320'),
            ('B-737', 'B737'),
            ('A-320', 'A320'),
            ('  a350  900  ', 'A350 900')
        ]
        
        for input_model, expected in test_cases:
            result = standardize_aircraft_model(input_model)
            self.assertEqual(result, expected, f"机型 {input_model} 标准化结果应为 {expected}，实际为 {result}")


class TestAPIEndpoints(unittest.TestCase):
    """API端点测试"""
    
    def setUp(self):
        """测试前准备"""
        self.app = app.test_client()
        self.app.testing = True
        
        # 创建临时测试目录
        self.test_data_dir = tempfile.mkdtemp()
        self.test_logs_dir = tempfile.mkdtemp()
        
        # 模拟数据目录
        app.config['TESTING'] = True
    
    def tearDown(self):
        """测试后清理"""
        # 清理临时目录
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)
        if os.path.exists(self.test_logs_dir):
            shutil.rmtree(self.test_logs_dir)
    
    def test_index_endpoint(self):
        """测试根路径接口"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('service', data)
        self.assertIn('version', data)
        self.assertIn('endpoints', data)
        self.assertEqual(data['service'], 'AeroLOPA 航空座位图 API')
    
    def test_health_check(self):
        """测试健康检查接口"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertIn('version', data)
    
    def test_get_airlines(self):
        """测试获取航空公司列表接口"""
        response = self.app.get('/api/v1/airlines')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('airlines', data['data'])
        self.assertIn('supported_codes', data['data'])
        self.assertGreater(data['data']['total_count'], 0)
    
    def test_get_airline_info_valid(self):
        """测试获取有效航空公司信息"""
        # 使用已知存在的航空公司代码
        test_iata = 'CA'  # 中国国际航空
        response = self.app.get(f'/api/v1/airlines/{test_iata}')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertEqual(data['data']['iata_code'], test_iata)
        self.assertIn('chinese_name', data['data'])
        self.assertIn('english_name', data['data'])
    
    def test_get_airline_info_invalid(self):
        """测试获取无效航空公司信息"""
        # 使用无效的IATA代码
        invalid_codes = ['XX', 'INVALID', '123']
        
        for code in invalid_codes:
            response = self.app.get(f'/api/v1/airlines/{code}')
            self.assertIn(response.status_code, [400, 404])
            
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertIn('error', data)
    
    def test_seatmap_missing_params(self):
        """测试座位图接口缺少参数"""
        # 缺少airline参数
        response = self.app.get('/api/v1/seatmap?aircraft=A320')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['code'], 'MISSING_AIRLINE')
        
        # 缺少aircraft参数
        response = self.app.get('/api/v1/seatmap?airline=CA')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['code'], 'MISSING_AIRCRAFT')
    
    def test_seatmap_invalid_params(self):
        """测试座位图接口无效参数"""
        # 无效的IATA代码
        response = self.app.get('/api/v1/seatmap?airline=INVALID&aircraft=A320')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['code'], 'INVALID_IATA_CODE')
        
        # 无效的机型
        response = self.app.get('/api/v1/seatmap?airline=CA&aircraft=!@#$')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['code'], 'INVALID_AIRCRAFT_MODEL')
    
    @patch('app.crawler.crawl_airline_seatmaps')
    def test_seatmap_valid_params(self, mock_crawl):
        """测试座位图接口有效参数"""
        # 模拟爬虫返回数据
        mock_crawl.return_value = {
            'images': [
                {
                    'filename': 'CA_A320_seatmap.jpg',
                    'file_path': '/test/path/CA_A320_seatmap.jpg',
                    'url': '/api/v1/image/CA/CA_A320_seatmap.jpg',
                    'size': 1024000,
                    'modified_time': datetime.now().isoformat(),
                    'source_url': 'https://example.com/image.jpg'
                }
            ]
        }
        
        response = self.app.get('/api/v1/seatmap?airline=CA&aircraft=A320')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('data', data)
        self.assertIn('airline', data['data'])
        self.assertIn('aircraft', data['data'])
        self.assertIn('seatmap', data['data'])
        
        # 验证航空公司信息
        airline_data = data['data']['airline']
        self.assertEqual(airline_data['iata_code'], 'CA')
        
        # 验证机型信息
        aircraft_data = data['data']['aircraft']
        self.assertEqual(aircraft_data['original_model'], 'A320')
        
        # 验证座位图数据
        seatmap_data = data['data']['seatmap']
        self.assertIn('images', seatmap_data)
        self.assertIn('metadata', seatmap_data)
    
    def test_seatmap_post_method(self):
        """测试座位图接口POST方法"""
        post_data = {
            'airline': 'CA',
            'aircraft': 'A320',
            'format': 'json',
            'force_refresh': False
        }
        
        response = self.app.post('/api/v1/seatmap', 
                               data=json.dumps(post_data),
                               content_type='application/json')
        
        # 应该返回200或者相关的错误状态码
        self.assertIn(response.status_code, [200, 404, 500])
        
        data = json.loads(response.data)
        self.assertIn('success', data)
    
    def test_api_docs(self):
        """测试API文档接口"""
        response = self.app.get('/docs')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('title', data)
        self.assertIn('version', data)
        self.assertIn('endpoints', data)
        self.assertIn('error_codes', data)
    
    def test_404_error_handler(self):
        """测试404错误处理"""
        response = self.app.get('/nonexistent-endpoint')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertEqual(data['error']['code'], 'NOT_FOUND')
        self.assertIn('timestamp', data)


class TestAPIIntegration(unittest.TestCase):
    """API集成测试"""
    
    def setUp(self):
        """集成测试前准备"""
        self.base_url = 'http://localhost:5000'
        self.api_base = f'{self.base_url}/api/v1'
    
    def test_api_workflow(self):
        """测试完整的API工作流程"""
        # 注意：这个测试需要API服务器运行
        # 在实际测试中，可以使用测试服务器或模拟请求
        
        try:
            # 1. 检查服务健康状态
            health_response = requests.get(f'{self.base_url}/health', timeout=5)
            if health_response.status_code != 200:
                self.skipTest("API服务器未运行，跳过集成测试")
            
            # 2. 获取航空公司列表
            airlines_response = requests.get(f'{self.api_base}/airlines', timeout=10)
            self.assertEqual(airlines_response.status_code, 200)
            
            airlines_data = airlines_response.json()
            self.assertTrue(airlines_data['success'])
            
            # 3. 获取特定航空公司信息
            if airlines_data['data']['supported_codes']:
                test_airline = airlines_data['data']['supported_codes'][0]
                airline_response = requests.get(f'{self.api_base}/airlines/{test_airline}', timeout=10)
                self.assertEqual(airline_response.status_code, 200)
                
                # 4. 尝试获取座位图
                seatmap_response = requests.get(
                    f'{self.api_base}/seatmap',
                    params={'airline': test_airline, 'aircraft': 'A320'},
                    timeout=30
                )
                # 座位图请求可能成功或失败（取决于数据可用性），但不应该是参数错误
                self.assertNotEqual(seatmap_response.status_code, 400)
        
        except requests.exceptions.RequestException:
            self.skipTest("无法连接到API服务器，跳过集成测试")


class TestAPIPerformance(unittest.TestCase):
    """API性能测试"""
    
    def setUp(self):
        """性能测试前准备"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_response_time(self):
        """测试响应时间"""
        import time
        
        # 测试健康检查响应时间
        start_time = time.time()
        response = self.app.get('/health')
        end_time = time.time()
        
        response_time = end_time - start_time
        self.assertLess(response_time, 1.0, "健康检查响应时间应小于1秒")
        self.assertEqual(response.status_code, 200)
        
        # 测试航空公司列表响应时间
        start_time = time.time()
        response = self.app.get('/api/v1/airlines')
        end_time = time.time()
        
        response_time = end_time - start_time
        self.assertLess(response_time, 2.0, "航空公司列表响应时间应小于2秒")
        self.assertEqual(response.status_code, 200)
    
    def test_concurrent_requests(self):
        """测试并发请求处理"""
        import threading
        import time
        
        results = []
        
        def make_request():
            start_time = time.time()
            response = self.app.get('/health')
            end_time = time.time()
            results.append({
                'status_code': response.status_code,
                'response_time': end_time - start_time
            })
        
        # 创建10个并发请求
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # 启动所有线程
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # 验证结果
        self.assertEqual(len(results), 10)
        for result in results:
            self.assertEqual(result['status_code'], 200)
            self.assertLess(result['response_time'], 2.0)
        
        # 总时间应该明显小于串行执行时间
        self.assertLess(total_time, 5.0, "并发请求总时间应小于5秒")


if __name__ == '__main__':
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试用例
    test_suite.addTest(unittest.makeSuite(TestAPIValidation))
    test_suite.addTest(unittest.makeSuite(TestAPIEndpoints))
    test_suite.addTest(unittest.makeSuite(TestAPIPerformance))
    
    # 可选：添加集成测试（需要服务器运行）
    # test_suite.addTest(unittest.makeSuite(TestAPIIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果摘要
    print(f"\n{'='*50}")
    print(f"测试摘要:")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print(f"\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError: ')[-1].split('\n')[0]}")
    
    if result.errors:
        print(f"\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('\n')[-2]}")
    
    print(f"{'='*50}")
    
    # 退出码
    sys.exit(0 if result.wasSuccessful() else 1)