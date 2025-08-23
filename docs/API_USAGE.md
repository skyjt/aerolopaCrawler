# AeroLOPA API 使用说明

## 快速开始

### 1. 启动服务

```bash
# 安装依赖
pip install -r requirements.txt

# 启动 API 服务
python app.py
```

服务启动后，访问 `http://localhost:5000` 查看服务信息。

### 2. 基础使用示例

#### Python 示例

```python
import requests
import json

# API 基础 URL
BASE_URL = "http://localhost:5000"

def check_service_status():
    """检查服务状态"""
    response = requests.get(f"{BASE_URL}/health")
    return response.json()

def get_airlines():
    """获取支持的航空公司列表"""
    response = requests.get(f"{BASE_URL}/api/v1/airlines")
    return response.json()

def get_seatmap(airline, aircraft):
    """获取座位图数据"""
    params = {
        'airline': airline,
        'aircraft': aircraft,
        'limit': 10
    }
    response = requests.get(f"{BASE_URL}/api/v1/seatmap", params=params)
    return response.json()

def download_image(iata_code, filename, save_path=None):
    """下载座位图图片"""
    url = f"{BASE_URL}/api/v1/image/{iata_code}/{filename}"
    params = {
        'quality': 85,
        'width': 1200,
        'height': 800
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        if save_path:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"图片已保存到: {save_path}")
        return response.content
    else:
        print(f"下载失败: {response.status_code}")
        return None

# 使用示例
if __name__ == "__main__":
    # 1. 检查服务状态
    print("=== 检查服务状态 ===")
    status = check_service_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))
    
    # 2. 获取航空公司列表
    print("\n=== 获取航空公司列表 ===")
    airlines = get_airlines()
    print(f"支持的航空公司数量: {airlines['data']['total_count']}")
    for airline in airlines['data']['airlines'][:5]:  # 显示前5个
        print(f"- {airline['iata_code']}: {airline['chinese_name']}")
    
    # 3. 获取座位图数据
    print("\n=== 获取座位图数据 ===")
    seatmap = get_seatmap('CA', 'A320')
    if seatmap['success']:
        images = seatmap['data']['seatmap']['images']
        print(f"找到 {len(images)} 张座位图")
        
        # 4. 下载第一张图片
        if images:
            first_image = images[0]
            print(f"\n=== 下载图片: {first_image['filename']} ===")
            download_image('CA', first_image['filename'], f"./downloaded_{first_image['filename']}")
    else:
        print(f"获取座位图失败: {seatmap['error']['message']}")
```

#### JavaScript/Node.js 示例

```javascript
const axios = require('axios');
const fs = require('fs');

const BASE_URL = 'http://localhost:5000';

// 检查服务状态
async function checkServiceStatus() {
    try {
        const response = await axios.get(`${BASE_URL}/health`);
        return response.data;
    } catch (error) {
        console.error('服务状态检查失败:', error.message);
        return null;
    }
}

// 获取航空公司列表
async function getAirlines() {
    try {
        const response = await axios.get(`${BASE_URL}/api/v1/airlines`);
        return response.data;
    } catch (error) {
        console.error('获取航空公司列表失败:', error.message);
        return null;
    }
}

// 获取座位图数据
async function getSeatmap(airline, aircraft) {
    try {
        const response = await axios.get(`${BASE_URL}/api/v1/seatmap`, {
            params: {
                airline: airline,
                aircraft: aircraft,
                limit: 10
            }
        });
        return response.data;
    } catch (error) {
        console.error('获取座位图失败:', error.message);
        return null;
    }
}

// 下载图片
async function downloadImage(iataCode, filename, savePath) {
    try {
        const response = await axios.get(
            `${BASE_URL}/api/v1/image/${iataCode}/${filename}`,
            {
                params: {
                    quality: 85,
                    width: 1200,
                    height: 800
                },
                responseType: 'stream'
            }
        );
        
        if (savePath) {
            const writer = fs.createWriteStream(savePath);
            response.data.pipe(writer);
            
            return new Promise((resolve, reject) => {
                writer.on('finish', () => {
                    console.log(`图片已保存到: ${savePath}`);
                    resolve(true);
                });
                writer.on('error', reject);
            });
        }
        
        return response.data;
    } catch (error) {
        console.error('下载图片失败:', error.message);
        return null;
    }
}

// 使用示例
async function main() {
    console.log('=== 检查服务状态 ===');
    const status = await checkServiceStatus();
    if (status) {
        console.log(JSON.stringify(status, null, 2));
    }
    
    console.log('\n=== 获取航空公司列表 ===');
    const airlines = await getAirlines();
    if (airlines && airlines.success) {
        console.log(`支持的航空公司数量: ${airlines.data.total_count}`);
        airlines.data.airlines.slice(0, 5).forEach(airline => {
            console.log(`- ${airline.iata_code}: ${airline.chinese_name}`);
        });
    }
    
    console.log('\n=== 获取座位图数据 ===');
    const seatmap = await getSeatmap('CA', 'A320');
    if (seatmap && seatmap.success) {
        const images = seatmap.data.seatmap.images;
        console.log(`找到 ${images.length} 张座位图`);
        
        if (images.length > 0) {
            const firstImage = images[0];
            console.log(`\n=== 下载图片: ${firstImage.filename} ===`);
            await downloadImage('CA', firstImage.filename, `./downloaded_${firstImage.filename}`);
        }
    }
}

main().catch(console.error);
```

#### cURL 示例

```bash
#!/bin/bash

# 1. 检查服务状态
echo "=== 检查服务状态 ==="
curl -s http://localhost:5000/health | jq .

# 2. 获取航空公司列表
echo -e "\n=== 获取航空公司列表 ==="
curl -s http://localhost:5000/api/v1/airlines | jq '.data.airlines[:5]'

# 3. 获取座位图数据
echo -e "\n=== 获取座位图数据 ==="
curl -s "http://localhost:5000/api/v1/seatmap?airline=CA&aircraft=A320&limit=5" | jq .

# 4. 下载图片（需要先从座位图数据中获取文件名）
echo -e "\n=== 下载图片 ==="
curl -s "http://localhost:5000/api/v1/image/CA/CA_A320_001.jpg?quality=85&width=800" \
     -o "downloaded_image.jpg"
echo "图片已下载为 downloaded_image.jpg"

# 5. 获取 API 统计信息
echo -e "\n=== API 统计信息 ==="
curl -s http://localhost:5000/api/v1/stats | jq '.data.performance'

# 6. 获取实时性能指标
echo -e "\n=== 实时性能指标 ==="
curl -s http://localhost:5000/api/v1/metrics | jq .
```

## 高级用法

### 1. 批量下载座位图

```python
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def batch_download_seatmaps(airline, aircraft, save_dir="./downloads"):
    """批量下载指定航空公司和机型的所有座位图"""
    
    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)
    
    # 获取座位图列表
    response = requests.get(f"{BASE_URL}/api/v1/seatmap", {
        'airline': airline,
        'aircraft': aircraft
    })
    
    if not response.json()['success']:
        print(f"获取座位图列表失败: {response.json()['error']['message']}")
        return
    
    images = response.json()['data']['seatmap']['images']
    print(f"准备下载 {len(images)} 张图片...")
    
    def download_single_image(image_info):
        filename = image_info['filename']
        save_path = os.path.join(save_dir, filename)
        
        try:
            img_response = requests.get(
                f"{BASE_URL}/api/v1/image/{airline}/{filename}",
                params={'quality': 90, 'compress': True}
            )
            
            if img_response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(img_response.content)
                return f"✓ {filename}"
            else:
                return f"✗ {filename} (HTTP {img_response.status_code})"
        except Exception as e:
            return f"✗ {filename} (错误: {str(e)})"
    
    # 并发下载
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(download_single_image, img) for img in images]
        
        for future in as_completed(futures):
            result = future.result()
            print(result)
    
    print(f"\n下载完成！文件保存在: {save_dir}")

# 使用示例
batch_download_seatmaps('CA', 'A320', './CA_A320_seatmaps')
```

### 2. 性能监控脚本

```python
import requests
import time
import json
from datetime import datetime

def monitor_api_performance(duration_minutes=10, interval_seconds=30):
    """监控 API 性能"""
    
    end_time = time.time() + (duration_minutes * 60)
    
    print(f"开始监控 API 性能，持续 {duration_minutes} 分钟...")
    print("时间\t\t\t请求总数\t成功率\t\t平均响应时间\tCPU使用率\t内存使用率")
    print("-" * 100)
    
    while time.time() < end_time:
        try:
            # 获取性能指标
            metrics_response = requests.get(f"{BASE_URL}/api/v1/metrics")
            system_response = requests.get(f"{BASE_URL}/api/v1/system")
            
            if metrics_response.status_code == 200 and system_response.status_code == 200:
                metrics = metrics_response.json()['data']
                system = system_response.json()['data']
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                total_requests = metrics['requests']['total']
                success_rate = f"{metrics['requests']['success_rate']:.1f}%"
                avg_response_time = f"{metrics['response_times']['average']:.3f}s"
                cpu_usage = f"{system['system']['cpu_percent']:.1f}%"
                memory_usage = f"{system['system']['memory_percent']:.1f}%"
                
                print(f"{timestamp}\t\t{total_requests}\t\t{success_rate}\t\t{avg_response_time}\t\t{cpu_usage}\t\t{memory_usage}")
            else:
                print(f"{datetime.now().strftime('%H:%M:%S')}\t\t监控数据获取失败")
                
        except Exception as e:
            print(f"{datetime.now().strftime('%H:%M:%S')}\t\t监控异常: {str(e)}")
        
        time.sleep(interval_seconds)
    
    print("\n监控结束")

# 使用示例
monitor_api_performance(duration_minutes=5, interval_seconds=10)
```

### 3. 错误处理和重试机制

```python
import requests
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1, backoff=2):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            
            while retries < max_retries:
                try:
                    result = func(*args, **kwargs)
                    if result is not None:
                        return result
                except Exception as e:
                    print(f"尝试 {retries + 1} 失败: {str(e)}")
                
                retries += 1
                if retries < max_retries:
                    print(f"等待 {current_delay} 秒后重试...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            print(f"所有重试都失败了，放弃操作")
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3, delay=2)
def robust_get_seatmap(airline, aircraft):
    """带重试机制的座位图获取"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/seatmap",
            params={'airline': airline, 'aircraft': aircraft},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                return data
            else:
                print(f"API 返回错误: {data['error']['message']}")
                return None
        elif response.status_code == 429:
            print("请求频率超限，等待更长时间...")
            time.sleep(60)  # 等待1分钟
            raise Exception("Rate limit exceeded")
        else:
            print(f"HTTP 错误: {response.status_code}")
            raise Exception(f"HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("请求超时")
        raise Exception("Request timeout")
    except requests.exceptions.ConnectionError:
        print("连接错误")
        raise Exception("Connection error")

# 使用示例
result = robust_get_seatmap('CA', 'A320')
if result:
    print(f"成功获取 {len(result['data']['seatmap']['images'])} 张座位图")
else:
    print("获取座位图失败")
```

### 4. 缓存管理

```python
import requests

def clear_api_cache():
    """清理 API 缓存"""
    try:
        response = requests.post(f"{BASE_URL}/api/v1/cache/clear")
        if response.status_code == 200:
            result = response.json()
            print(f"缓存清理成功: {result['data']['message']}")
            return True
        else:
            print(f"缓存清理失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"缓存清理异常: {str(e)}")
        return False

def get_cache_stats():
    """获取缓存统计信息"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/stats")
        if response.status_code == 200:
            stats = response.json()['data']
            cache_info = {
                'image_cache_files': stats['cache']['image_cache_files'],
                'image_cache_size_mb': stats['cache']['image_cache_size_mb'],
                'flask_cache_timeout': stats['config']['cache_timeout']
            }
            return cache_info
        else:
            return None
    except Exception as e:
        print(f"获取缓存统计失败: {str(e)}")
        return None

# 使用示例
print("=== 缓存统计信息 ===")
cache_stats = get_cache_stats()
if cache_stats:
    print(f"图片缓存文件数: {cache_stats['image_cache_files']}")
    print(f"图片缓存大小: {cache_stats['image_cache_size_mb']:.2f} MB")
    print(f"Flask 缓存超时: {cache_stats['flask_cache_timeout']} 秒")

print("\n=== 清理缓存 ===")
if clear_api_cache():
    print("缓存清理完成")
else:
    print("缓存清理失败")
```

## 常见问题解决

### 1. 连接问题

```python
def test_connection():
    """测试 API 连接"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ API 服务正常")
            return True
        else:
            print(f"✗ API 服务异常: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到 API 服务，请检查服务是否启动")
        return False
    except requests.exceptions.Timeout:
        print("✗ 连接超时，请检查网络状况")
        return False
    except Exception as e:
        print(f"✗ 连接测试失败: {str(e)}")
        return False
```

### 2. 参数验证

```python
def validate_params(airline, aircraft):
    """验证请求参数"""
    errors = []
    
    # 验证航空公司代码
    if not airline or len(airline) != 2 or not airline.isalpha():
        errors.append("航空公司代码必须是2位字母")
    
    # 验证机型
    if not aircraft or len(aircraft) < 2:
        errors.append("机型名称不能为空且至少2个字符")
    
    return errors

# 使用示例
errors = validate_params('CA', 'A320')
if errors:
    print("参数验证失败:")
    for error in errors:
        print(f"- {error}")
else:
    print("参数验证通过")
```

### 3. 响应处理

```python
def handle_api_response(response):
    """统一处理 API 响应"""
    try:
        if response.status_code == 200:
            data = response.json()
            if data.get('success', False):
                return data['data'], None
            else:
                error_info = data.get('error', {})
                return None, f"API 错误: {error_info.get('message', '未知错误')}"
        elif response.status_code == 400:
            return None, "请求参数错误"
        elif response.status_code == 404:
            return None, "请求的资源不存在"
        elif response.status_code == 429:
            return None, "请求频率超限，请稍后重试"
        elif response.status_code == 500:
            return None, "服务器内部错误"
        else:
            return None, f"HTTP 错误: {response.status_code}"
    except ValueError:
        return None, "响应格式错误，无法解析 JSON"
    except Exception as e:
        return None, f"响应处理异常: {str(e)}"

# 使用示例
response = requests.get(f"{BASE_URL}/api/v1/airlines")
data, error = handle_api_response(response)

if error:
    print(f"请求失败: {error}")
else:
    print(f"请求成功，获取到 {len(data['airlines'])} 个航空公司")
```

## 最佳实践

### 1. 请求优化

- 使用连接池减少连接开销
- 设置合理的超时时间
- 实现请求重试机制
- 合理使用缓存

### 2. 错误处理

- 始终检查响应状态码
- 处理网络异常
- 记录错误日志
- 提供用户友好的错误信息

### 3. 性能优化

- 并发请求时控制并发数
- 使用适当的图片质量参数
- 监控 API 性能指标
- 定期清理缓存

### 4. 安全考虑

- 不要在客户端硬编码敏感信息
- 遵守 API 请求频率限制
- 验证下载的文件类型
- 使用 HTTPS（生产环境）

---

更多详细信息请参考 [README.md](../README.md) 和 [开发文档](DEVELOPMENT.md)。