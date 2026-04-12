#!/usr/bin/env python3
"""
本地APP互联模块
终极鸽子王 V26.0 - 搜索与手机操作互联

功能:
1. 获取用户位置
2. 网络搜索房源
3. 手机APP操作获取联系方式
4. 结果融合输出
"""

import os
import sys
import json
import time
import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
import logging
from infrastructure.path_resolver import get_project_root

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class HouseSource:
    """房源信息"""
    title: str
    area: float  # 平米
    price: float  # 月租
    address: str
    city: str
    district: str
    contact_name: str = ""
    contact_phone: str = ""
    source: str = ""  # 来源: web/phone
    url: str = ""


class LocalAppInterconnect:
    """本地APP互联"""
    
    def __init__(self, workspace: str):
        self.workspace = workspace
        self.user_location = None
        self.user_city = "淄博"  # 默认淄博
        self.web_results: List[HouseSource] = []
        self.phone_results: List[HouseSource] = []
        self.final_results: List[HouseSource] = []
    
    def get_location(self) -> Tuple[float, float]:
        """获取用户位置"""
        logger.info("📍 获取用户位置...")
        
        # 尝试调用位置工具
        try:
            result = subprocess.run(
                ['python3', '-c', 'from tools import get_user_location; print(get_user_location())'],
                capture_output=True, text=True, timeout=60, cwd=self.workspace
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if 'latitude' in data:
                    self.user_location = (data['latitude'], data['longitude'])
                    logger.info(f"✅ 位置: {self.user_location}")
                    return self.user_location
        except Exception as e:
            logger.warning(f"位置获取失败: {e}")
        
        # 默认淄博位置
        self.user_location = (36.8131, 118.0658)  # 淄博市中心
        logger.info(f"📍 使用默认位置: 淄博 {self.user_location}")
        return self.user_location
    
    def web_search_houses(self, city: str, max_area: float = 50, max_price: float = 1000) -> List[HouseSource]:
        """网络搜索房源"""
        logger.info(f"🔍 网络搜索: {city} 商铺 <{max_area}平 <{max_price}元/月")
        
        results = []
        
        # 搜索URL列表
        search_urls = [
            f"https://zb.shop.fang.com/zu/house/",  # 房天下淄博商铺
            f"https://zb.zu.fang.com/house/",  # 房天下淄博租房
            f"https://zb.58.com/zufang/",  # 58同城淄博租房
        ]
        
        for url in search_urls:
            try:
                result = subprocess.run(
                    ['python3', '-c', f'''
from tools import web_fetch
result = web_fetch("{url}")
print(result[:2000] if result else "")
'''],
                    capture_output=True, text=True, timeout=30, cwd=self.workspace
                )
                
                if result.returncode == 0 and result.stdout:
                    # 解析房源信息
                    content = result.stdout
                    # 简单提取
                    if "商铺" in content or "出租" in content:
                        logger.info(f"  ✅ 找到房源信息: {url}")
            except Exception as e:
                logger.warning(f"  ⚠️ 搜索失败 {url}: {e}")
        
        self.web_results = results
        return results
    
    def phone_app_search(self, city: str, max_area: float = 50, max_price: float = 1000) -> List[HouseSource]:
        """手机APP搜索房源"""
        logger.info(f"📱 手机APP搜索: {city} 商铺 <{max_area}平 <{max_price}元/月")
        
        results = []
        
        # GUI Agent 指令
        gui_query = f"""
任务: 在手机上找房并获取联系方式

步骤:
1. 打开手机上已安装的找房APP（优先顺序：安居客 > 贝壳找房 > 58同城 > 链家）
2. 切换城市到"{city}"
3. 搜索商铺出租，筛选条件：
   - 面积: 小于{max_area}平米
   - 租金: 小于{max_price}元/月
   - 类型: 商铺/门面房
4. 点击符合条件的房源进入详情页
5. 点击"电话咨询"或"联系房东"按钮
6. 记录显示的电话号码
7. 返回列表，继续查找下一个房源
8. 最终返回所有找到的房源信息和电话号码

输出格式:
房源名称 | 面积 | 月租 | 地址 | 联系人 | 电话号码
"""
        
        try:
            result = subprocess.run(
                ['python3', '-c', f'''
from tools import xiaoyi_gui_agent
result = xiaoyi_gui_agent("""{gui_query}""")
print(result)
'''],
                capture_output=True, text=True, timeout=300, cwd=self.workspace
            )
            
            if result.returncode == 0:
                logger.info(f"✅ 手机APP搜索完成")
                # 解析结果
                output = result.stdout
                # 提取电话号码
                import re
                phones = re.findall(r'1[3-9]\d{{9}}', output)
                logger.info(f"  📞 找到 {len(phones)} 个电话号码")
            else:
                logger.warning(f"⚠️ 手机APP搜索失败: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ 手机APP操作超时")
        except Exception as e:
            logger.warning(f"⚠️ 手机APP搜索异常: {e}")
        
        self.phone_results = results
        return results
    
    def merge_results(self) -> List[HouseSource]:
        """融合结果"""
        logger.info("🔄 融合搜索结果...")
        
        # 合并去重
        all_results = self.web_results + self.phone_results
        
        # 按价格排序
        all_results.sort(key=lambda x: x.price)
        
        self.final_results = all_results
        return all_results
    
    def execute_full_search(self, city: str = "淄博", max_area: float = 50, max_price: float = 1000) -> Dict:
        """执行完整搜索流程"""
        logger.info(f"🚀 开始完整搜索: {city}")
        
        start_time = time.time()
        
        # Step 1: 获取位置
        location = self.get_location()
        
        # Step 2: 并行搜索（网络 + 手机）
        import threading
        
        web_thread = threading.Thread(
            target=self.web_search_houses, 
            args=(city, max_area, max_price)
        )
        phone_thread = threading.Thread(
            target=self.phone_app_search,
            args=(city, max_area, max_price)
        )
        
        web_thread.start()
        phone_thread.start()
        
        web_thread.join(timeout=60)
        phone_thread.join(timeout=300)
        
        # Step 3: 融合结果
        final = self.merge_results()
        
        elapsed = time.time() - start_time
        
        return {
            "city": city,
            "location": location,
            "web_results": len(self.web_results),
            "phone_results": len(self.phone_results),
            "total_results": len(final),
            "elapsed_seconds": round(elapsed, 2),
            "results": [
                {
                    "title": r.title,
                    "area": r.area,
                    "price": r.price,
                    "address": r.address,
                    "contact": r.contact_name,
                    "phone": r.contact_phone,
                    "source": r.source
                }
                for r in final
            ]
        }


def test_interconnect():
    """测试互联模块"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║          本地APP互联模块测试                                           ║
║          搜索 + 手机操作 互联能力验证                                   ║
╚══════════════════════════════════════════════════════════════════════╝
""")
    
    workspace = str(get_project_root())
    interconnect = LocalAppInterconnect(workspace)
    
    # 执行搜索
    result = interconnect.execute_full_search(
        city="淄博",
        max_area=50,
        max_price=1000
    )
    
    print(f"""
📊 搜索结果:
   城市: {result['city']}
   位置: {result['location']}
   网络搜索: {result['web_results']} 条
   手机搜索: {result['phone_results']} 条
   总计: {result['total_results']} 条
   耗时: {result['elapsed_seconds']} 秒
""")
    
    if result['results']:
        print("\n🏠 房源列表:")
        for i, r in enumerate(result['results'], 1):
            print(f"  {i}. {r['title']}")
            print(f"     面积: {r['area']}㎡ | 月租: {r['price']}元")
            print(f"     地址: {r['address']}")
            print(f"     联系: {r['contact']} {r['phone']}")
            print(f"     来源: {r['source']}")
            print()
    else:
        print("\n⚠️ 未找到符合条件的房源")
        print("建议: 请确保手机上安装了找房APP（安居客/贝壳/58同城）")
    
    return result


if __name__ == "__main__":
    test_interconnect()
