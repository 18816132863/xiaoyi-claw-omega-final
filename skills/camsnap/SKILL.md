---
name: camsnap
description: Capture frames or clips from RTSP/ONVIF cameras.
homepage: https://camsnap.ai
metadata: {"clawdbot":{"emoji":"📸","requires":{"bins":["camsnap"]},"install":[{"id":"brew","kind":"brew","formula":"steipete/tap/camsnap","bins":["camsnap"],"label":"Install camsnap (brew)"}]}}
---

# camsnap

Use `camsnap` to grab snapshots, clips, or motion events from configured cameras.

Setup
- Config file: `~/.config/camsnap/config.yaml`
- Add camera: `camsnap add --name kitchen --host 192.168.0.10 --user user --pass pass`

Common commands
- Discover: `camsnap discover --info`
- Snapshot: `camsnap snap kitchen --out shot.jpg`
- Clip: `camsnap clip kitchen --dur 5s --out clip.mp4`
- Motion watch: `camsnap watch kitchen --threshold 0.2 --action '...'`
- Doctor: `camsnap doctor --probe`

Notes
- Requires `ffmpeg` on PATH.
- Prefer a short test capture before longer clips.


## 使用方法

### 命令行调用

```bash
# 查看帮助
python skill.py help

# 执行技能
python skill.py run --template default

# 列出模板
python skill.py list
```

## 示例

```bash
python skill.py run --template default
```
