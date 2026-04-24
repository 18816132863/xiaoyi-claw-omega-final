#!/usr/bin/env python3
"""
element.py - CDP元素操作脚本 (V3简化版)
支持: 查找元素、点击、输入文本、截图
"""

import argparse
import json
import sys
import time
import subprocess
from urllib.request import urlopen

def get_cdp_url(port=18800):
    """获取CDP WebSocket URL"""
    try:
        with urlopen(f"http://127.0.0.1:{port}/json") as resp:
            pages = json.loads(resp.read())
            for page in pages:
                if page.get("type") == "page":
                    return page.get("webSocketDebuggerUrl")
    except Exception as e:
        print(f"无法连接CDP: {e}", file=sys.stderr)
    return None

def cdp_command(ws_url, method, params=None):
    """发送CDP命令"""
    import websocket
    ws = websocket.create_connection(ws_url)
    cmd = {"id": 1, "method": method, "params": params or {}}
    ws.send(json.dumps(cmd))
    resp = ws.recv()
    ws.close()
    return json.loads(resp)

def find_elements(ws_url, keywords):
    """查找包含指定文本的元素"""
    result = cdp_command(ws_url, "Runtime.evaluate", {
        "expression": f"""
            Array.from(document.querySelectorAll('*'))
                .filter(el => el.textContent && ({' || '.join([f'el.textContent.includes("{k}")' for k in keywords])}))
                .map(el => {{
                    const rect = el.getBoundingClientRect();
                    return {{
                        tag: el.tagName,
                        text: el.textContent.trim().substring(0, 50),
                        x: Math.round(rect.x),
                        y: Math.round(rect.y),
                        width: Math.round(rect.width),
                        height: Math.round(rect.height)
                    }};
                }})
        """,
        "returnByValue": True
    })
    
    # CDP 返回结构: result.result.value
    inner_result = result.get("result", {}).get("result", {})
    elements = inner_result.get("value", []) if inner_result.get("type") == "object" else []
    if elements:
        print(f"找到 {len(elements)} 个匹配元素:")
        for i, el in enumerate(elements[:5]):
            print(f"  [{i+1}] {el.get('tag')}: '{el.get('text')}' at ({el.get('x', 0)}, {el.get('y', 0)})")
    else:
        print("未找到匹配元素")
    return elements

def click_at(ws_url, x, y):
    """在指定坐标点击"""
    import websocket
    ws = websocket.create_connection(ws_url)
    
    # 鼠标按下
    ws.send(json.dumps({
        "id": 1,
        "method": "Input.dispatchMouseEvent",
        "params": {"type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1}
    }))
    ws.recv()
    
    # 鼠标释放
    ws.send(json.dumps({
        "id": 2,
        "method": "Input.dispatchMouseEvent",
        "params": {"type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1}
    }))
    ws.recv()
    ws.close()
    
    print(f"点击坐标: ({x}, {y})")
    return True

def click_element_by_text(ws_url, text, use_js=False):
    """点击包含指定文本的元素
    
    Args:
        ws_url: CDP WebSocket URL
        text: 要点击的元素文本
        use_js: 是否使用JavaScript点击（绕过部分反爬检测）
    """
    if use_js:
        # 使用JavaScript点击（更可靠，绕过反爬）
        result = cdp_command(ws_url, "Runtime.evaluate", {
            "expression": f"""
                (function() {{
                    var keywords = ['{text}'];
                    var elements = document.querySelectorAll('a, button, div, span');
                    for (var i = 0; i < elements.length; i++) {{
                        var el = elements[i];
                        var elText = (el.innerText || el.textContent || '').trim();
                        for (var j = 0; j < keywords.length; j++) {{
                            if (elText === keywords[j] || elText.includes(keywords[j])) {{
                                var rect = el.getBoundingClientRect();
                                if (rect.width > 0 && rect.height > 0 && rect.top > 0 && rect.left > 0) {{
                                    el.click();
                                    return {{
                                        text: elText.substring(0, 50),
                                        x: Math.round(rect.left + rect.width/2),
                                        y: Math.round(rect.top + rect.height/2),
                                        clicked: true
                                    }};
                                }}
                            }}
                        }}
                    }}
                    return {{clicked: false, reason: 'element not found'}};
                }})()
            """,
            "returnByValue": True
        })
        
        inner_result = result.get("result", {}).get("result", {})
        value = inner_result.get("value") if inner_result.get("type") != "undefined" else None
        if value and value.get('clicked'):
            print(f"JS点击成功: '{value['text']}' at ({int(value['x'])}, {int(value['y'])})")
            return True
        else:
            print(f"JS点击失败: {value}")
            return False
    else:
        # 使用CDP鼠标事件点击
        result = cdp_command(ws_url, "Runtime.evaluate", {
            "expression": f"""
                (function() {{
                    const el = Array.from(document.querySelectorAll('*'))
                        .find(e => e.textContent && e.textContent.trim().includes('{text}'));
                    if (el) {{
                        const rect = el.getBoundingClientRect();
                        el.click();
                        return {{x: rect.left + rect.width/2, y: rect.top + rect.height/2}};
                    }}
                    return null;
                }})()
            """,
            "returnByValue": True
        })
        
        inner_result = result.get("result", {}).get("result", {})
        pos = inner_result.get("value") if inner_result.get("type") != "undefined" else None
        if pos:
            print(f"点击元素 '{text}' 在 ({int(pos['x'])}, {int(pos['y'])})")
            return True
        else:
            print(f"未找到元素 '{text}'")
            return False

def type_text(ws_url, text):
    """输入文本"""
    import websocket
    ws = websocket.create_connection(ws_url)
    
    for char in text:
        ws.send(json.dumps({
            "id": 1,
            "method": "Input.dispatchKeyEvent",
            "params": {"type": "char", "text": char}
        }))
        ws.recv()
        time.sleep(0.01)
    
    ws.close()
    print(f"输入文本: {text}")
    return True

def screenshot(ws_url, output_path, display=99):
    """截图"""
    # 先尝试CDP截图
    result = cdp_command(ws_url, "Page.captureScreenshot")
    data = result.get("result", {}).get("data")
    
    if data:
        import base64
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(data))
        print(f"截图已保存: {output_path}")
        return True
    
    # CDP失败，回退到Xvfb截图
    print("CDP截图失败，使用Xvfb截图...")
    try:
        subprocess.run(
            ["import", "-window", "root", output_path],
            env={"DISPLAY": f":{display}"},
            check=True
        )
        print(f"截图已保存: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"截图失败: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="CDP元素操作")
    parser.add_argument("--port", type=int, default=18800, help="CDP端口")
    parser.add_argument("--find", help="查找元素关键词(逗号分隔)")
    parser.add_argument("--click", nargs=2, type=int, metavar=("X", "Y"), help="点击坐标")
    parser.add_argument("--click-text", help="点击包含指定文本的元素")
    parser.add_argument("--js-click", action="store_true", help="使用JavaScript点击（绕过反爬检测，更可靠）")
    parser.add_argument("--type", dest="type_text", help="输入文本")
    parser.add_argument("--screenshot", help="截图保存路径")
    parser.add_argument("--display", type=int, default=99, help="Xvfb显示号")
    
    args = parser.parse_args()
    
    # 获取CDP连接
    ws_url = get_cdp_url(args.port)
    if not ws_url:
        print("错误: 无法连接到浏览器CDP，请确保浏览器已启动", file=sys.stderr)
        sys.exit(1)
    
    # 执行操作
    if args.find:
        keywords = [k.strip() for k in args.find.split(",")]
        find_elements(ws_url, keywords)
    
    if args.click:
        click_at(ws_url, args.click[0], args.click[1])
    
    if args.click_text:
        click_element_by_text(ws_url, args.click_text, use_js=args.js_click)
    
    if args.type_text:
        type_text(ws_url, args.type_text)
    
    if args.screenshot:
        screenshot(ws_url, args.screenshot, args.display)

if __name__ == "__main__":
    main()
