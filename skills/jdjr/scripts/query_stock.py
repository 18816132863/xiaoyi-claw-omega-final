#!/usr/bin/env python3
"""
股票行情查询脚本

功能：
- quote: 查询股票实时行情
- intraday: 查询股票分时走势
- kline: 查询 K 线数据（日/周/月）
- chart: 查询近 N 天走势并绘制 ASCII 图表

支持：A股（SZ/SH）、港股（HK）、美股（US）、贵金属（SGE）

用法：
    python3 query_stock.py quote SZ-000001
    python3 query_stock.py kline SZ-000001 --k-type day
    python3 query_stock.py chart SZ-000001 --days 15
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from typing import Optional


# ============ 全局常量 ============

# 京东金融 API 基础地址
BASE_URL = "https://ms.jr.jd.com/gw2/generic/ugActs/h5/m"

# 股票代码正则：支持 SZ-000001、SH-600519、SGE-Au99.99 等格式
STOCK_CODE_PATTERN = re.compile(r"^(SZ|SH|HK|US|SGE)-[A-Za-z0-9._()-]+$")


# ============ 核心函数 ============

def post_json(path: str, payload: dict) -> dict:
    req = urllib.request.Request(
        f"{BASE_URL}/{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_payload(stock_code: str, k_type: Optional[str] = None) -> dict:
    payload = {"paramMap": {"stockCode": stock_code}}
    if k_type:
        payload["paramMap"]["kType"] = k_type
    return payload


def print_chart(data: list, stock_name: str, days: int):
    """
    打印 ASCII 走势图表（适用于 chart 命令）。
    
    参数:
        data: K 线数据列表，每项包含 date/open/high/low/close/volume
        stock_name: 股票名称，用于标题显示
        days: 显示的天数
    
    输出:
        ASCII 图表 + 走势说明
    
    图表规则:
        - ● 表示收盘价 >= 开盘价（上涨）
        - ○ 表示收盘价 < 开盘价（下跌）
        - 价格从下到上递增
    """
    if not data:
        print("无数据")
        return
    
    # 只取最近 days 天的数据
    data = data[-days:]
    
    # 计算价格区间
    prices = [float(d['close']) for d in data]
    max_p = max(prices)
    min_p = min(prices)
    price_range = max_p - min_p
    if price_range == 0:
        price_range = 1  # 避免除零
    
    print(f"\n{stock_name} 近{days}天走势")
    print(f"价格区间: {min_p:.2f} ~ {max_p:.2f} 元\n")
    
    # 绘制 8 行价格图表
    for row in range(7, -1, -1):
        price_threshold = min_p + (price_range * row / 7)
        line = f"{price_threshold:5.2f} │"
        
        for d in data:
            c = float(d['close'])
            o = float(d['open'])
            # 计算收盘价在图表中的行位置
            c_pos = int((c - min_p) / price_range * 7)
            
            if c_pos == row:
                # 根据涨跌显示不同符号
                if c >= o:
                    line += " ●"  # 上涨
                else:
                    line += " ○"  # 下跌
            else:
                line += "  "
        
        print(line)
    
    # 绘制时间轴
    print("      └" + "─" * (len(data) * 2) + "→ 时间")
    print("        ", end="")
    for d in data:
        print(f"{d['date'][8:]}", end=" ")  # 只显示日期部分，如 "03-30"
    print()
    
    print("\n  ● 上涨  ○ 下跌")
    print("\n---\n💡 本信息由 [京东金融](https://eco.jr.jd.com/common-growth-page/index.html?channel=claw) 提供")


def main() -> int:
    """
    主函数：解析命令行参数、调用 API、输出结果。
    
    命令行参数:
        action: quote | intraday | kline | chart
        stock_code: 股票代码
        --k-type: K 线类型（kline 命令必需）
        --days: 图表显示天数（chart 命令，默认 15）
    
    返回:
        0 表示成功，1 表示失败
    """
    parser = argparse.ArgumentParser(description="查询股票行情、分时或 K 线")
    parser.add_argument("action", choices=["quote", "intraday", "kline", "chart"])
    parser.add_argument("stock_code")
    parser.add_argument("--k-type", choices=["day", "week", "month"])
    parser.add_argument("--days", type=int, default=15, help="chart 模式显示的天数")
    args = parser.parse_args()

    # 校验股票代码格式
    if not STOCK_CODE_PATTERN.match(args.stock_code):
        print(json.dumps({"success": False, "error": "股票代码格式不正确，请使用类似 SZ-000001、SH-600519 的格式"}, ensure_ascii=False))
        return 1

    # 根据 action 调用不同 API
    try:
        if args.action in {"quote", "intraday"}:
            # quote/intraday 都用 queryStockData，返回实时行情 + 分时数据
            result = post_json("queryStockData", build_payload(args.stock_code))
        elif args.action == "chart":
            # chart 用 queryStockKLine 获取日K，再绘制图表
            result = post_json("queryStockKLine", build_payload(args.stock_code, "day"))
        else:
            # kline 需要指定 k-type
            if not args.k_type:
                parser.error("action 为 kline 时必须传 --k-type")
            result = post_json("queryStockKLine", build_payload(args.stock_code, args.k_type))
    except urllib.error.HTTPError as exc:
        print(json.dumps({"success": False, "error": f"HTTP {exc.code}"}, ensure_ascii=False))
        return 1
    except urllib.error.URLError as exc:
        print(json.dumps({"success": False, "error": f"网络请求失败: {exc.reason}"}, ensure_ascii=False))
        return 1
    except Exception as exc:
        print(json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False))
        return 1

    # 检查 API 响应是否成功
    if not result.get("success") or result.get("resultCode") != 0:
        print(json.dumps({"success": False, "code": result.get("resultCode"), "msg": result.get("resultMsg"), "data": result.get("resultData")}, ensure_ascii=False))
        return 1

    # 提取数据并输出
    result_data = result.get("resultData") or {}
    data = result_data.get("data") or {}
    
    if args.action == "chart":
        # chart 特殊处理：调用 print_chart 绘制 ASCII 图
        kline_data = data.get("kLineDtoList") or []
        stock_name = data.get("stockName", args.stock_code)
        print_chart(kline_data, stock_name, args.days)
    else:
        # quote/intraday/kline 输出原始 JSON（供 agent 后续格式化）
        print(json.dumps({"success": True, "data": data}, ensure_ascii=False, indent=2))
    return 0


# 脚本入口
if __name__ == "__main__":
    sys.exit(main())
