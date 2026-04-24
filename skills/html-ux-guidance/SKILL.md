---
name: html-ux-guidance
description: "该skill提供了很专业的html生成指导。当用户需求与html相关，请参考本skill指导。"
---

# 设计风格 (design Style)
## 设计哲学

"Objects in Space" — 每个元素都像漂浮在柔和光晕中的精致物件，通过弥散光效营造空气感与深度。

---

## 一、三色系统

每套方案遵循 **70-20-10 比例**：Base（背景主色）/ Flow（辅助弥散色）/ Spark（点睛强调色）

**配色原则**：三色取自色轮相邻区域（类比色/单色）。禁止高饱和度对比色组合（如红+绿、橙+蓝）。所有颜色保持低饱和度粉彩质感。

### 方案表

| 方案 | 名称 | Base 70% | Flow 20% | Spark 10% | 文字锚点 | 色相流动 |
|------|------|----------|----------|-----------|---------|---------|
| A | **极光幻影** | `#EEEBFF` 极浅紫 | `#D6E5FA` 极光蓝 | `#D1F5EA` 浅青 | `#312C51` | 紫→蓝→青 |
| B | **深海星辰** | `#EEF0FF` 极浅靛 | `#DCE8F8` 钢青 | `#C8E8E4` 浅青碧 | `#1E1B4B` | 靛→钢青→青碧 |
| C | **晴空碧蓝** | `#EAF5FF` 极浅天蓝 | `#D0EEF0` 浅水青 | `#D0EED8` 极浅薄荷 | `#1E3A5F` | 天蓝→水青→薄荷 |
| D | **薄荷森林** | `#F0F8F4` 极浅灰薄荷 | `#D6E8E0` 柔灰绿 | `#E4ECDA` 淡灰黄绿 | `#1A5244` | 薄荷→柔绿→淡黄绿 |
| E | **暖阳奶油** | `#FFF8EE` 极浅奶油 | `#FAE8D4` 浅桃 | `#F5D8C8` 浅珊瑚 | `#78350F` | 奶油→桃→珊瑚 |
| F | **薰衣草梦** | `#F5F0FF` 极浅薰衣 | `#E4E0F8` 浅蓝紫 | `#F5DCEA` 淡兰花 | `#4A3B68` | 薰衣草→蓝紫→兰花 |
| G | **晨雾玫瑰** | `#FFF0F2` 极浅玫瑰 | `#FAE0EC` 浅粉 | `#F2D8E4` 浅紫粉 | `#4A1A2E` | 玫瑰→粉→紫粉 |
| H | **珊瑚暖阳** | `#FFF4EE` 极浅珊瑚 | `#FDE8D5` 浅桃橙 | `#F5D0D0` 淡玫瑰 | `#7C2D12` | 珊瑚→桃橙→淡玫 |
| I | **暮色蔷薇** | `#F8F6FA` 极浅白 | `#F0E8F2` 淡粉紫 | `#E8EBF5` 淡蓝紫 | `#54324A` | 暖粉→冷紫 |
| J | **碧玉翡翠** | `#EEFBF5` 极浅翡翠 | `#C8EEE5` 浅翠 | `#C2DFF0` 浅水蓝 | `#134E4A` | 翡翠→翠绿→水蓝 |
| K | **烟雨青山** | `#EEF3F6` 极浅烟蓝 | `#CADCE8` 烟雨蓝 | `#C4D8D0` 青瓷绿 | `#273848` | 烟蓝→雨蓝→青瓷 |
| L | **月光白露** | `#F5F8FC` 极浅冰蓝 | `#DDF0F0` 浅水色 | `#D5DEF8` 淡冰紫 | `#0F172A` | 月白→水色→冰蓝紫 |
| M | **金玉暖辉** | `#FEF7F2` 极浅橙奶 | `#F5D8A8` 浅橙金 | `#FAF0A8` 暖鹅黄 | `#5C4A18` | 橙奶→橙金→暖黄 |

### 特殊方案 Glow 说明

| 方案 | Glow 特殊规则 |
|------|-------------|
| D 薄荷森林 | glow 暖黄绿 `rgba(178,218,162)` opacity 0.26→0.18，冷薄荷 `rgba(165,215,198)` opacity 0.20→0.17，整体极淡 |
| F 薰衣草梦 | 文字锚点为低饱和哑光紫（约28%饱和度）。可在 glow-4/6 及 hero R4 追加暖橙黄辅光 `rgba(248,225,172)` 营造暮色感 |
| K 烟雨青山 | 青色 glow 比烟蓝更强：烟蓝 `rgba(168,202,222)` opacity 0.28→0.20，青色 `rgba(155,215,198)` opacity 0.52→0.45 |
| M 金玉暖辉 | glow 1-4 橙金 `rgba(240,205,158)` opacity 0.42→0.36；glow 5-6 暖黄 `rgba(245,232,148)` opacity 0.28→0.24 |

### 意图匹配

| 意图关键词 | 首选 | 备选 |
|-----------|------|------|
| AI、科技、未来、数据分析 | **A 极光幻影** | B 深海星辰 |
| 金融、商务、企业、专业 | **B 深海星辰** | L 月光白露 |
| 旅行、户外、天空、清爽 | **C 晴空碧蓝** | L 月光白露 |
| 健康、自然、环保、wellness | **D 薄荷森林** | J 碧玉翡翠 |
| 美食、咖啡、烘焙、温暖 | **E 暖阳奶油** | H 珊瑚暖阳 |
| 音乐、艺术、冥想、创意 | **F 薰衣草梦** | A 极光幻影 |
| 情感、浪漫、婚礼、爱情 | **G 晨雾玫瑰** | I 暮色蔷薇 |
| 时尚、设计、品牌、活力 | **H 珊瑚暖阳** | E 暖阳奶油 |
| 通用保底、社交、博客 | **I 暮色蔷薇** | G 晨雾玫瑰 |
| 奢侈品、珠宝、高端 | **J 碧玉翡翠** | D 薄荷森林 |
| 东方、传统、文化、历史、山水 | **K 烟雨青山** | B 深海星辰 |
| 极简、现代、冬季、白色系 | **L 月光白露** | B 深海星辰 |
| 黄金、贵金属、宫廷、暖奢 | **M 金玉暖辉** | K 烟雨青山 |

❌ 同一设计混用多套方案

### CSS 变量模板

```css
:root {
    --color-base:           #EEEBFF;        /* Base 70% — 替换为当前方案色值 */
    --color-flow:           #D6E5FA;        /* Flow 20% */
    --color-spark:          #D1F5EA;        /* Spark 10% */
    --color-text-anchor:    #312C51;
    --color-text-secondary: rgba(49,44,81,0.68);
    --color-text-muted:     rgba(49,44,81,0.40);
    --color-border:         rgba(49,44,81,0.08);
    --color-card:           #FFFFFF;
    --bg:                   #FAFAFA;        /* ⚠️ 永远用近纯白，禁止用 Base 色作为背景 */
}
```

---

## 二、HTML 规范

### 字体

**中文/正文**: HarmonyOS Sans SC — **数字/数据**: Space Grotesk

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/harmonyos-sans-sc@1.0.0/index.css">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&display=swap" rel="stylesheet">
```

```css
body { font-family: 'HarmonyOS Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif; }
.number, .data { font-family: 'Space Grotesk', sans-serif; }
```

### 字号与字重层级

**禁止使用斜体。字重只用 700 Bold 和 400 Regular 两档。**

| 层级 | 用途 | 字号 | 字重 | 字体 |
|------|------|------|------|------|
| L1 | Hero 主标题 | 48px（移动端 32px） | **700** | HarmonyOS Sans SC |
| L2 | 统计大数字 | 26px | **700** | Space Grotesk |
| L3 | 章节标题 / 卡片关键名称 | 18px / 14px | **700** | HarmonyOS Sans SC |
| L4 | 正文 / 描述 | 14px | 400 | HarmonyOS Sans SC |
| L5 | 元标签 / 编号 / Footer | 12px | **700** uppercase / 400 | HarmonyOS Sans SC |

全站字号不超过 5 种（48 / 26 / 18 / 14 / 12px）。

### 圆角

- 主卡片: `24px`
- 次级容器（mini-card、alert-box、nav-card）: `14–16px`
- 按钮/标签: `8–12px`

### 卡片样式

卡片**不加 box-shadow 也不加描边**，白色背景直接浮在 Glow 上：

```css
.card { background: var(--color-card); border-radius: 24px; }
```

---

## 三、Auroral Glow

`position: fixed` 撑满视口，6 个椭圆覆盖页面不同纵向位置，flow / spark 颜色交替，opacity 随深度递减。

```css
.glow-container {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    overflow: visible; pointer-events: none; z-index: 0;
}
.glow-ellipse { position: absolute; border-radius: 50%; }

/* 以 A 极光幻影为例 */
.glow-1 { width: 800px; height: 600px; background: radial-gradient(ellipse, rgba(200,190,240,0.5) 0%, rgba(200,190,240,0.2) 40%, transparent 70%); filter: blur(80px); top: 400px; left: -200px; }
.glow-2 { width: 700px; height: 550px; background: radial-gradient(ellipse, rgba(160,200,245,0.45) 0%, rgba(160,200,245,0.15) 40%, transparent 70%); filter: blur(90px); top: 600px; right: -150px; }
.glow-3 { width: 600px; height: 500px; background: radial-gradient(ellipse, rgba(160,225,210,0.4) 0%, rgba(160,225,210,0.12) 40%, transparent 70%); filter: blur(70px); top: 1200px; left: 10%; }
.glow-4 { width: 750px; height: 580px; background: radial-gradient(ellipse, rgba(190,180,230,0.4) 0%, rgba(190,180,230,0.12) 40%, transparent 70%); filter: blur(85px); top: 1800px; right: -100px; }
.glow-5 { width: 650px; height: 520px; background: radial-gradient(ellipse, rgba(160,200,245,0.38) 0%, rgba(160,200,245,0.1) 40%, transparent 70%); filter: blur(75px); top: 2500px; left: -150px; }
.glow-6 { width: 550px; height: 450px; background: radial-gradient(ellipse, rgba(160,225,210,0.35) 0%, rgba(160,225,210,0.1) 40%, transparent 70%); filter: blur(70px); top: 3200px; right: 5%; }
```

HTML：`<div class="glow-container">` 内放 6 个 `<div class="glow-ellipse glow-N"></div>`。

---

## 四、顶部导航

固定在顶部，默认透明，Hero 滚动过半后变实色背景，支持目录展开。

```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">

<nav class="nav-container" id="navContainer">
  <div class="nav-inner">
    <div class="nav-header" onclick="toggleNav()">
      <div class="nav-title">
        <div class="nav-title-icon"><i class="fas fa-ICON"></i></div>
        <span class="nav-title-text">报告名称</span>
      </div>
      <button class="nav-toggle">
        <span class="nav-toggle-text">目录</span>
        <i class="fas fa-chevron-down nav-toggle-icon"></i>
      </button>
    </div>
    <div class="nav-card">
      <ul class="nav-list">
        <li class="nav-item"><a href="#section-1" class="nav-link" onclick="closeNav()"><i class="fas fa-ICON"></i> 章节名</a></li>
      </ul>
    </div>
  </div>
</nav>
```

```css
.nav-container {
    position: fixed; top: 0; left: 0; right: 0; z-index: 100;
    padding: 14px 20px; background: transparent; transition: background 0.3s ease;
}
.nav-container.nav-solid {
    background: rgba(250,250,250,0.88);
    backdrop-filter: blur(12px);
}
.nav-container::after {
    content: ''; position: absolute; left: 0; right: 0; top: 100%; height: 24px;
    background: linear-gradient(180deg, rgba(250,250,250,0.7) 0%, transparent 100%);
    pointer-events: none; opacity: 0; transition: opacity 0.3s ease;
}
.nav-container.nav-solid::after { opacity: 1; }
.nav-inner { max-width: 800px; margin: 0 auto; }
.nav-header { display: flex; align-items: center; justify-content: space-between; cursor: pointer; }
.nav-title  { display: flex; align-items: center; gap: 12px; }
.nav-title-icon {
    width: 36px; height: 36px; background: rgba(255,255,255,0.95);
    border-radius: 12px; display: flex; align-items: center; justify-content: center;
    box-shadow: 0 2px 12px rgba(锚点RGB, 0.10);
}
.nav-title-text { font-size: 14px; font-weight: 700; color: var(--color-text-anchor); }
.nav-toggle {
    display: flex; align-items: center; gap: 8px; padding: 10px 16px;
    background: rgba(255,255,255,0.9); border: none; border-radius: 12px;
    cursor: pointer; box-shadow: 0 2px 8px rgba(锚点RGB, 0.08); transition: all 0.2s ease;
}
.nav-toggle-text  { font-size: 12px; color: var(--color-text-secondary); }
.nav-toggle-icon  { font-size: 12px; color: var(--color-text-muted); transition: transform 0.3s ease; }
.nav-container.expanded .nav-toggle-icon { transform: rotate(180deg); }
.nav-card {
    background: rgba(255,255,255,0.82); backdrop-filter: blur(24px);
    border-radius: 16px; margin-top: 12px;
    box-shadow: 0 8px 32px rgba(锚点RGB, 0.12);
    max-height: 0; overflow: hidden; opacity: 0;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.nav-container.expanded .nav-card { max-height: 500px; padding: 8px 0; opacity: 1; }
.nav-link {
    display: flex; align-items: center; gap: 12px; padding: 14px 20px;
    text-decoration: none; color: var(--color-text-secondary); font-size: 14px; font-weight: 400;
}
.nav-link:hover { background: rgba(Base色RGB, 0.4); color: var(--color-text-anchor); }
```

```javascript
function toggleNav() { document.getElementById('navContainer').classList.toggle('expanded'); }
function closeNav()  { document.getElementById('navContainer').classList.remove('expanded'); }
document.addEventListener('click', e => {
    if (!document.getElementById('navContainer').contains(e.target)) closeNav();
});
document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
        e.preventDefault();
        document.querySelector(a.getAttribute('href'))?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
});
```

⚠️ Hero `padding-top` 至少 `80px`；各章节卡片添加 `id="section-N"` 对应导航 `href`。

---

## 五、Hero Banner 系统

`::before` 多层 radial-gradient + `::after` 噪点纹理 + 滚动淡出，是区别于普通页面的核心视觉特征。

```css
/* 容器：全宽突破 */
.hero {
    position: relative; z-index: 1;
    padding: 100px 0 60px; text-align: center;
    margin-left: calc(-50vw + 50%); margin-right: calc(-50vw + 50%);
    width: 100vw; overflow: visible;
}

/* 渐变背景层 */
.hero::before {
    content: '';
    position: absolute; top: -80px; left: -20%; right: -20%; bottom: -100px;
    z-index: 0;
    background:
        radial-gradient(ellipse 90% 80% at 10% 20%, rgba(R1,G1,B1, 0.7) 0%, rgba(R1,G1,B1, 0.3) 30%, transparent 60%),
        radial-gradient(ellipse 80% 90% at 85% 10%, rgba(R2,G2,B2, 0.65) 0%, rgba(R2,G2,B2, 0.25) 35%, transparent 55%),
        radial-gradient(ellipse 70% 60% at 60% 90%, rgba(R3,G3,B3, 0.5) 0%, rgba(R3,G3,B3, 0.2) 30%, transparent 50%),
        radial-gradient(ellipse 60% 70% at 20% 85%, rgba(R4,G4,B4, 0.45) 0%, rgba(R4,G4,B4, 0.15) 35%, transparent 55%),
        radial-gradient(ellipse 50% 45% at 50% 45%, rgba(255,255,255, 0.9) 0%, rgba(255,255,255, 0.4) 40%, transparent 70%),
        linear-gradient(160deg, rgba(base1, 0.6) 0%, rgba(base2, 0.4) 50%, rgba(base3, 0.3) 100%);
    filter: blur(2px);
    mask-image: linear-gradient(180deg, black 0%, black 50%, rgba(0,0,0,0.5) 75%, transparent 100%);
    -webkit-mask-image: linear-gradient(180deg, black 0%, black 50%, rgba(0,0,0,0.5) 75%, transparent 100%);
    transition: opacity 0.4s ease;
}

/* 噪点纹理层 */
.hero::after {
    content: '';
    position: absolute; top: 0; left: -20%; right: -20%; bottom: 0;
    z-index: 1; opacity: 0.04;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.7' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
    pointer-events: none;
    mask-image: linear-gradient(180deg, black 0%, black 60%, transparent 100%);
    -webkit-mask-image: linear-gradient(180deg, black 0%, black 60%, transparent 100%);
    transition: opacity 0.4s ease;
}

/* 滚动淡出状态 */
.hero.fading::before { opacity: var(--banner-opacity, 1); }
.hero.fading::after  { opacity: calc(0.04 * var(--banner-opacity, 1)); }
.hero.faded::before  { opacity: 0; }
.hero.faded::after   { opacity: 0; }

/* ⚠️ 文字层级必须高于渐变层 */
.hero > * { position: relative; z-index: 2; }
```

```css
/* hero-subtitle 宽度与卡片容器对齐 */
.hero-subtitle { max-width: 800px; padding: 0 16px; margin: 0 auto; }
```

```javascript
const navEl  = document.querySelector('.nav-container');
const heroEl = document.querySelector('.hero');
function handleScrollEffects() {
    const scrollY = window.scrollY;
    const bannerFadeStart = 30;
    const bannerFadeEnd = heroEl.offsetHeight * 0.6;
    if (scrollY <= bannerFadeStart) {
        heroEl.classList.remove('fading', 'faded');
        heroEl.style.removeProperty('--banner-opacity');
    } else if (scrollY < bannerFadeEnd) {
        const progress = (scrollY - bannerFadeStart) / (bannerFadeEnd - bannerFadeStart);
        heroEl.classList.add('fading');
        heroEl.classList.remove('faded');
        heroEl.style.setProperty('--banner-opacity', (1 - progress).toFixed(3));
    } else {
        heroEl.classList.remove('fading');
        heroEl.classList.add('faded');
    }
    navEl.classList.toggle('nav-solid', scrollY > bannerFadeEnd);
}
window.addEventListener('scroll', handleScrollEffects, { passive: true });
handleScrollEffects();
```

### Hero::before 颜色推导

颜色从方案实际色值出发轻微提升饱和度，保持低饱和粉彩质感。❌ 禁止使用深饱和色（如 `rgba(210,165,80)` 这类深琥珀）。

| 位置 | 推导方法 |
|------|---------|
| R1（左上，flow色） | 取 Flow 色 RGB，最大通道轻微提升 |
| R2（右上） | Flow 与 Spark 之间的色相 |
| R3（中下，spark色） | 取 Spark 色，轻微提升 |
| R4（左下） | R1/R2 中间值 |

**各方案参考色：**

| 方案 | R1/G1/B1 | R2/G2/B2 | R3/G3/B3 | R4/G4/B4 |
|------|---------|---------|---------|---------|
| A 极光幻影 | `200,190,240` | `160,200,245` | `160,225,210` | `190,180,230` |
| C 晴空碧蓝 | `160,205,235` | `120,195,240` | `145,215,190` | `150,208,230` |
| D 薄荷森林 | `178,218,162`（暖黄绿） | `175,210,190` | `185,215,170` | `168,212,194` |
| F 薰衣草梦 | `218,210,245` | `228,215,238` | `242,210,230` | `248,225,172`（暖橙黄辅光） |
| K 烟雨青山 | `168,202,222` | `160,196,218` | `155,215,198` | `165,200,220` |
| M 金玉暖辉 | `248,228,205` | `248,225,198` | `250,240,195` | `248,228,205` |

---

## 六、内容组件规范

### 章节标题区（Section Header）

编号在上、标题在下，左边缘统一对齐：

```
section-header（flex-direction: column; align-items: flex-start; gap: 6px）
├── 编号行（row; gap: 4px）
│   ├── 序号值（Space Grotesk, 12px, 700, muted）
│   └── 标签（12px, 400, "· CHAPTER" 等）
└── 标题区
    ├── 中文标题（18px, 700, anchor）
    └── 英文副标题（14px, 400, muted）
```

❌ 禁止：编号列 + 标题列横排（导致左边缘错位）

### 正文条目（Info-item）

```css
.info-item { display: flex; align-items: flex-start; gap: 8px; }
.info-item::before {
    content: "·"; font-size: 14px; line-height: 1.8;
    color: var(--color-flow); flex-shrink: 0;
}
/* ⚠️ font-size 和 line-height 必须与正文一致，否则序列点垂直偏移 */
```

### 图标一致性规则

同一层级下的图标必须系统统一、背景统一：

| 维度 | 要求 |
|------|------|
| 图标系统 | 全部 Font Awesome **或**全部 emoji，同组禁止混用 |
| 背景色 | 同组按 spark → flow → base → rgba(锚点,0.08) 顺序轮换 |
| 背景形状 | 同组 width / height / border-radius 完全一致 |
| 图标大小 | 同组 font-size 完全相同 |

```css
/* 推荐模式 */
.icon-box { width: 44px; height: 44px; border-radius: 14px; display: flex; align-items: center; justify-content: center; }
.icon-box i { font-size: 18px; color: var(--color-text-anchor); }
.icon-box.t1 { background: var(--color-spark); }
.icon-box.t2 { background: var(--color-flow); }
.icon-box.t3 { background: var(--color-base); }
.icon-box.t4 { background: rgba(锚点RGB, 0.08); }
```

### 关键洞察框（Alert-box）

```css
.alert-box {
    background: rgba(flow色RGB, 0.26);
    border-radius: 12px; padding: 16px 18px;
    /* ❌ 不加 border-left */
}
```

⚠️ Alert-box **必须**放在白色 `.card` 内，禁止直接叠放在 Glow 背景上。

### ECharts 字体

```javascript
textStyle: {
    fontFamily: 'HarmonyOS Sans SC, PingFang SC, Microsoft YaHei, sans-serif',
    // ❌ 不加 fontStyle: 'italic'
}
```

---

## 检查清单

- [ ] `--bg: #FAFAFA` 近纯白，不用 Base 色作页面背景
- [ ] Auroral Glow：`position: fixed; bottom: 0`，6 椭圆，flow/spark 交替，opacity 随深度递减
- [ ] 字体：HarmonyOS Sans SC（中文）+ Space Grotesk（数字），无斜体，字重只用 700/400
- [ ] 字号 5 种：48 / 26 / 18 / 14 / 12px
- [ ] 卡片无 box-shadow 无 border，白色背景直接浮在 Glow 上
- [ ] 顶部导航：fixed + 滚动变实色 + 目录展开 + 平滑滚动，各章节有 `id="section-N"`
- [ ] Hero：`width:100vw` 全宽 + `::before` 5层渐变 + `::after` 噪点 + `handleScrollEffects()` 滚动淡出
- [ ] `.hero > * { position: relative; z-index: 2 }` — 文字层级高于渐变层
- [ ] `hero-subtitle` 用 `max-width: 800px; padding: 0 16px`
- [ ] Hero 渐变色从方案色值轻微提升，禁止深饱和色
- [ ] Alert-box 在白色 card 内，不直接放在 Glow 背景上
- [ ] 同组图标系统统一（全 FA 或全 emoji），背景色/尺寸/字号一致
- [ ] ECharts fontFamily 在 JS 中显式设置
- [ ] 内容信息量充足，卡片无内容裁切

