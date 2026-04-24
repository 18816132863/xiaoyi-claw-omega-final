# K12 Smart Teacher - 智能老师辅导系统

[![Skill](https://img.shields.io/badge/Skill-k12--smart--teacher-blue)](https://skillhub.cn)
[![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen)](https://skillhub.cn)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-WorkBuddy%20%7C%20OpenClaw%20%7C%20ClaudeCode-orange)](https://skillhub.cn)

> K12智能老师辅导系统，支持作业批改、错题分析、可视化讲解、举一反三练习生成。覆盖小学/初中/高中全学段，九大学科。

---

## ✨ 核心功能

| 功能 | 描述 |
|------|------|
| 📋 **作业批改** | 自动识别试题并批改，生成详细分析报告 |
| 🎯 **错题分析** | 智能识别薄弱知识点，提供错因分析 |
| 🎨 **可视化讲解** | 图形、漫画、动画等方式讲解错题（禁止纯文字） |
| 📺 **视频推荐** | 自动搜索并推荐优质B站/学而思等解题视频 |
| 📝 **梯度练习** | 自动生成基础/提高/挑战三层次练习试卷 |
| 📊 **学习报告** | 自动生成学习报告，跟踪知识点掌握进度 |
| 🤖 **智能识别** | 自动识别学科和年级，无需手动指定 |
| 📄 **Word下载** | 自动生成精美Word试卷供打印 |

---

## 📚 支持范围

### 学段覆盖
- ✅ 小学（一年级至六年级）
- ✅ 初中（初一至初三）
- ✅ 高中（高一至高三）

### 学科覆盖
- ✅ 语文、数学、英语（全学段）
- ✅ 物理、化学、生物（初中/高中）
- ✅ 历史、地理、政治（初中/高中）

---

## 🚀 快速安装

### SkillHub 安装（推荐）

在支持 SkillHub 的 AI 工具中执行：
```
安装技能：k12-smart-teacher
```

### 手动安装

```bash
# WorkBuddy
git clone https://github.com/shellery1988/k12-smart-teacher.git ~/.workbuddy/skills/k12-smart-teacher

# OpenClaw
git clone https://github.com/shellery1988/k12-smart-teacher.git ~/.openclaw/skills/k12-smart-teacher

# ClaudeCode
git clone https://github.com/shellery1988/k12-smart-teacher.git ~/.claudecode/skills/k12-smart-teacher

# 安装依赖（首次使用，自动安装）
cd k12-smart-teacher && python3 scripts/quick_setup.py
```

---

## 🎯 核心理念

> **理解优先于练习！**

教学流程：**错题分析 → 可视化讲解 → 视频推荐 → 举一反三练习**

绝对不能跳过"错题讲解"直接生成练习题。

---

## 📁 文件结构

```
k12-smart-teacher/
├── SKILL.md                    # 核心技能指令文档
├── README.md                   # 项目说明（本文件）
├── LICENSE                     # MIT 许可证
├── scripts/
│   ├── generate_paper.py       # 试卷生成脚本
│   ├── setup_dependencies.sh   # 依赖安装脚本(Bash)
│   └── quick_setup.py          # 快速安装脚本(Python)
├── references/
│   ├── math_knowledge.md       # 数学知识点库
│   ├── subject_identification.md  # 学科识别指南
│   └── video_resources.md      # 视频资源推荐指南
└── assets/                     # 资源文件目录
```

---

## 🛠️ 依赖说明

技能首次加载时**自动安装**所有必需依赖：

- **Python**：pillow, requests, python-docx, openpyxl
- **Node.js**：docx
- **系统（可选）**：tesseract（OCR），imagemagick

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)

---

## 👤 联系方式

- 📧 **邮箱**：shelleryliu@163.com
- 💬 **微信**：naskfcode
- 🔗 **GitHub**：https://github.com/shellery1988/k12-smart-teacher
- 🔗 **GitCode**：https://gitcode.com/shellery1988/k12-smart-teacher

---

**Made with ❤️ for K12 Education**
