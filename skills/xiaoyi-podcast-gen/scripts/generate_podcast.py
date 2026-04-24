#!/usr/bin/env python3
"""Celia Podcast Generator - 主入口脚本。

用法:
    # 链接生成
    python3 generate_podcast.py --uri "http://xhslink.com/n/2bMrQ7n1jq4"

    # 直接传入文本内容（collection 模式）
    python3 generate_podcast.py --content "荆州文物保护中心位于..."

    # 传入本地文件路径（自动读取内容，collection 模式）
    python3 generate_podcast.py --content /path/to/article.md
    python3 generate_podcast.py --content ~/docs/notes.txt
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# 添加脚本目录到 path
sys.path.insert(0, str(Path(__file__).parent))

from podcast_client import (
    submit_podcast,
    poll_task,
    extract_audio_url,
    extract_content_url,
    extract_cover_url,
    extract_title,
    extract_duration,
    extract_audio_status,
    download_file,
)


def main():
    parser = argparse.ArgumentParser(description="Celia 播客生成器")
    parser.add_argument("--uri", default=None, help="播客来源 URL 链接（与 --content 二选一）")
    parser.add_argument("--content", default=None, help="播客内容文本或本地文件路径，走 collection 模式（与 --uri 二选一）")
    parser.add_argument("--scene", default="details", help="详略程度: briefs / details")
    parser.add_argument("--vocal-enhance", default=True, action="store_true", help="启用人声增强")
    parser.add_argument("--bg-noise-reduce", default=True, action="store_true", help="启用背景降噪")
    parser.add_argument("--output", default="~/.openclaw/workspace/generated-podcasts", help="输出目录路径")
    parser.add_argument("--poll-interval", type=int, default=20, help="轮询间隔(秒)")
    parser.add_argument("--poll-timeout", type=int, default=1800, help="轮询超时(秒)")

    args = parser.parse_args()

    if not args.uri and not args.content:
        parser.error("必须提供 --uri 或 --content")

    # 解析输入源：uri / content
    resolved_url = args.uri
    resolved_content = None
    if args.content:
        resolved_content = _resolve_content(args.content)
        if resolved_content != args.content:
            print(f"[Podcast] 使用 content 模式（文件），内容长度: {len(resolved_content)} 字符")
        else:
            print(f"[Podcast] 使用 content 模式（文本），内容长度: {len(resolved_content)} 字符")
        if len(resolved_content) < 100:
            parser.error(f"内容太短（{len(resolved_content)} 字），至少需要 100 字才能生成播客")

    kwargs = {
        "style": "interview",
        "scene_type": args.scene,
        "vocal_enhance": args.vocal_enhance,
        "bg_noise_reduce": args.bg_noise_reduce,
    }

    # 1. 提交生成任务
    result, item_id, hash_id = submit_podcast(
        url=resolved_url, content=resolved_content, **kwargs
    )

    # 检查是否直接完成（极端情况）
    status = extract_audio_status(result)
    if status == "done":
        print("[Podcast] 任务已直接完成")
        _handle_result(result, args)
        return

    # 2. 轮询等待
    final_result = poll_task(
        url=resolved_url,
        content=resolved_content,
        item_id=item_id,
        hash_id=hash_id,
        interval=args.poll_interval,
        timeout=args.poll_timeout,
        **kwargs,
    )

    # 3. 处理结果
    _handle_result(final_result, args)


def _resolve_content(content):
    """解析 --content 参数。

    - 本地文件路径（文件存在，仅支持 .txt/.md）→ 读取文件内容
    - 其他 → 当作文本内容直接使用
    """
    # 长文本不可能是文件路径，跳过文件检查避免 OSError
    if len(content) > 512:
        return content
    
    local_path = Path(content).expanduser()
    if local_path.is_file():
        suffix = local_path.suffix.lower()
        if suffix not in {".txt", ".md"}:
            raise ValueError(f"--content 本地文件仅支持 .txt/.md，当前: {suffix}")
        print(f"[Podcast] 检测到本地文件: {local_path}")
        return local_path.read_text(encoding="utf-8")
    return content


def _handle_result(result, args):
    """处理完成的播客结果：下载音频、字幕、封面。"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = Path(args.output).expanduser() / ts
    base_dir.mkdir(parents=True, exist_ok=True)

    # 提取信息
    title = extract_title(result) or "podcast"
    duration = extract_duration(result)
    audio_url = extract_audio_url(result)

    # 下载音频
    audio_path = None
    if audio_url:
        audio_path = base_dir / f"{ts}_podcast.m4a"
        download_file(audio_url, audio_path)

    # 打印结果
    duration_sec = int(duration) if duration else "?"
    duration_min = f"{int(duration) // 60}:{int(duration) % 60:02d}" if duration else "?"

    print("\n" + "=" * 50)
    print("✅ 播客生成完成！")
    print("=" * 50)
    print(f"📌 标题: {title}")
    print(f"⏱️  时长: {duration_min} ({duration_sec}s)")
    if audio_path:
        print(f"🎵 音频: {audio_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()