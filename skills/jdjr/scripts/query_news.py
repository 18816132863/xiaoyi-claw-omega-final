#!/usr/bin/env python3
"""
京东金融资讯查询脚本

功能：
- 查询任意关键字相关的资讯新闻

用法：
    python3 query_news.py 黄金
    python3 query_news.py 特朗普 10
    python3 query_news.py A股 5
"""
import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime


# 京东金融 API 基础地址
BASE_URL = "https://ms.jr.jd.com/gw2/generic/ugActs/h5/m"


def query_news(keyword: str, size: int = 5) -> dict:
    """查询资讯"""
    payload = {
        "query": keyword,
        "size": size
    }
    
    req = urllib.request.Request(
        f"{BASE_URL}/queryInformation",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    
    if not result.get("success"):
        return {
            "success": False,
            "error": result.get("resultMsg", "查询失败"),
        }
    
    data = result.get("resultData", {}).get("data", {})
    information_list = data.get("informationList", [])
    
    # 解析资讯列表
    news_items = []
    for item in information_list:
        timestamp = int(item.get("timeStamp", 0))
        dt = datetime.fromtimestamp(timestamp / 1000)
        
        news_items.append({
            "time": dt.strftime("%Y-%m-%d %H:%M"),
            "title": item.get("title", "").strip(),
            "content": item.get("content", "").strip(),
            "url": item.get("subUrl", ""),
        })
    
    return {
        "success": True,
        "data": {
            "keyword": keyword,
            "count": len(news_items),
            "news": news_items,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="查询京东金融资讯")
    parser.add_argument("keyword", help="查询关键字")
    parser.add_argument("size", nargs="?", type=int, default=10, help="查询条数（默认10条）")
    args = parser.parse_args()
    
    try:
        result = query_news(args.keyword, args.size)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except urllib.error.HTTPError as exc:
        print(json.dumps({"success": False, "error": f"HTTP {exc.code}"}, ensure_ascii=False))
        return 1
    except urllib.error.URLError as exc:
        print(json.dumps({"success": False, "error": f"网络请求失败: {exc.reason}"}, ensure_ascii=False))
        return 1
    except Exception as exc:
        print(json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
