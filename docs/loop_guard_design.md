# LoopGuard - 循环防护模块设计文档

## 问题背景

用户反馈的截图显示了一个典型的**无限循环问题**：

```
任务处理已完成~
已经安装过了！让我检查一下内容：'星空鸽子王'技能已经安装了！让我看看内容：已经安装了！让我看看内容：已经安装了！……
```

**问题特征**：
1. 系统声称"任务已完成"，但继续执行
2. 相同内容无限重复输出
3. 缺乏状态判断和终止机制
4. 用户体验严重受损

## 解决方案

### 核心模块：LoopGuard

提供三层防护：

| 层级 | 检测类型 | 说明 |
|------|----------|------|
| L1 | 输出重复检测 | 检测相同/相似输出的重复 |
| L2 | 状态循环检测 | 检测状态机的死循环 |
| L3 | 动作循环检测 | 检测重复执行相同动作 |

### 专用模块：TaskCompletionGuard

针对本案例的专用防护：

```
任务开始 → 执行 → 完成 → 标记完成 → 阻止后续输出
```

## 使用方法

### 1. 基础使用

```python
from execution.loop_guard import LoopGuard, get_loop_guard

# 获取全局实例
guard = get_loop_guard()

# 检查输出
output = "已经安装了！"
alert = guard.check_output(output)

if alert:
    print(f"检测到循环: {alert.suggested_action}")
    # 终止执行
    return
```

### 2. 任务完成防护

```python
from execution.loop_guard import TaskCompletionGuard, get_task_guard

# 获取全局实例
task_guard = get_task_guard()
task_id = "install_skill_xxx"

# 任务完成时标记
task_guard.mark_completed(task_id, "安装完成！")

# 后续输出前检查
allowed = task_guard.check_and_record_output(task_id, "让我再检查一下...")
if not allowed:
    # 任务已完成，阻止输出
    return
```

### 3. 装饰器模式

```python
from execution.loop_guard import loop_protected

@loop_protected(max_repeats=3)
def install_skill(skill_name: str):
    # 如果重复执行超过3次，自动熔断
    return f"安装 {skill_name} 完成"
```

### 4. 添加告警回调

```python
def on_loop_detected(alert: LoopAlert):
    # 发送通知、记录日志等
    logger.warning(f"循环检测: {alert.loop_type.value}")
    send_alert_to_admin(alert)

guard = get_loop_guard()
guard.add_alert_callback(on_loop_detected)
```

## 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `max_repeats` | 3 | 最大重复次数 |
| `similarity_threshold` | 0.85 | 相似度阈值 |
| `window_size` | 10 | 滑动窗口大小 |
| `cooldown_seconds` | 1.0 | 冷却时间 |
| `auto_break` | True | 自动熔断 |

## 集成建议

### 在技能安装流程中集成

```python
async def install_skill(skill_name: str):
    task_id = f"install_{skill_name}"
    task_guard = get_task_guard()
    
    # 检查是否已完成
    if task_guard.is_completed(task_id):
        return "该技能已安装，无需重复操作"
    
    # 执行安装
    result = await do_install(skill_name)
    
    # 标记完成
    task_guard.mark_completed(task_id, result)
    
    return result
```

### 在输出层集成

```python
async def send_output(output: str):
    guard = get_loop_guard()
    
    # 检查循环
    alert = guard.check_output(output)
    if alert:
        # 替换为友好提示
        output = f"⚠️ 检测到可能的重复输出，已自动终止。原因: {alert.suggested_action}"
    
    # 发送输出
    await do_send(output)
```

## 测试

```bash
cd /home/sandbox/.openclaw/workspace
python execution/loop_guard.py
```

## 文件位置

- 模块代码: `execution/loop_guard.py`
- 设计文档: `docs/loop_guard_design.md`

## 版本

- V1.0.0 - 2026-04-13 - 初始版本

---

🐦 鸽子王出品，偶尔靠谱
