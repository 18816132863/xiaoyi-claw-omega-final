---
name: gesture-html
description: "创建一个通过摄像头进行手势交互的网页，利用MediaPipe实时识别手势，实现对网页元素的直观操控。当需要「通过摄像头识别手势」与网页交互时使用这个Skill。"
---

若要通过摄像头进行手势识别，除非用户原始请求指定特定库，必须使用MediaPipe，可参考以下JS代码（需在中国可访问，因此所有jsdelivr的CDN地址必须为示例中的jsdmirror）
若用户要生成地球仪，优先使用以下超链接图片作为地球仪的纹理：
https://cdn.jsdmirror.com/npm/three-globe@2.45.0/example/img/earth-blue-marble.jpg

```javascript
import {{ HandLandmarker, FilesetResolver }} from 'https://cdn.jsdmirror.com/npm/@mediapipe/tasks-vision@0.10.3';

// 1. 先加载 Wasm 运行时 (必须步骤)
const vision = await FilesetResolver.forVisionTasks(
  "https://cdn.jsdmirror.com/npm/@mediapipe/tasks-vision@0.10.3/wasm"
);

// 2. 异步创建检测器
const handLandmarker = await HandLandmarker.createFromOptions(vision, {{
  baseOptions: {{
    modelAssetPath: "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task", 
    delegate: "GPU"
  }},
  runningMode: "VIDEO",
  numHands: 2
}});

// 3. 执行检测
const results = handLandmarker.detectForVideo(video, performance.now());
```

【MediaPipe注意事项】
MediaPipe的HandLandmarker的检测结果，处理时需要注意，手部关键点坐标以已经根据图像的宽度和高度归一化到[0.0, 1.0]范围内。

【摄像头画面的处理规范】
Web API (navigator.mediaDevices.getUserMedia) 获取的摄像头原始画面默认是“客观视角”，而非“镜子视角”。为符合用户直觉，必须实现“镜像”效果：
1. 视觉层 (CSS)
`<video>` 元素必须设置 `transform: scaleX(-1)`；
`<canvas>` 元素**保持默认**（严禁翻转，防止文字反向）。
2. 逻辑层 (JavaScript/Coordinates)
模型返回的x坐标 (MediaPipe返回的`x`通常为 0~1) 必须首先在X轴上进行反转计算，以匹配CSS翻转后的画面，如：screenX = 1 - normalizedX;
y坐标保持不变;

【缩放旋转注意事项】
在摄像头交互中，若用户没有指定缩放旋转方式，默认使用单手的拇指与食指的欧几里得距离变化进行捏合缩放，用单手食指的位置变化进行旋转。
缩放旋转等均使用Lerp平滑。
参考代码：

// --- 手势识别逻辑 ---
let previousPinchDistance = null;
let targetScale = 1.0;
let previousHandPosition = null;
let targetRotation = { x: 0, y: 0 };

function processGestures(results) {{
    if (results.landmarks && results.landmarks.length > 0) {{
        const landmarks = results.landmarks[0]; // 取第一个手
        const mirroredLandmarks = landmarks.map(point => ({{
            ...point,
            x: 1.0 - point.x 
        }}));
        const thumb = mirroredLandmarks[4]; // 拇指指尖
        const index = mirroredLandmarks[8]; // 食指指尖
    
        // 1. 计算两点之间的欧几里得距离(用于缩放)
        const distance = Math.hypot(thumb.x - index.x, thumb.y - index.y);
    
        const currentX = index.x;
        const currentY = index.y;
    
        // 初始化基准值(第一帧或重置时)
        if (!previousPinchDistance) {{
            previousPinchDistance = distance;
            previousHandPosition = { x: currentX, y: currentY };
            return;
        }}
    
        // 2. 计算缩放比例 (当前距离 / 基准距离)
        // 阈值保护：距离变化太小忽略，防止抖动
        if (Math.abs(distance - previousPinchDistance) > 0.01) {{
            const zoomFactor = distance / previousPinchDistance;
            // 限制缩放范围 (例如 0.5x 到 3x)
            targetScale = Math.min(Math.max(targetScale * zoomFactor, 0.5), 3);
            // 重置基准距离，实现连续缩放
            previousPinchDistance = distance; 
        }}
    
        // 3. 计算旋转弧度
        const deltaX = currentX - previousHandPosition.x;
        const deltaY = currentY - previousHandPosition.y;
        // 更新目标旋转弧度 (注意坐标系映射)
        // 手向左/右动 -> 地球绕Y轴转
        // 手向上/下动 -> 地球绕X轴转
        // 乘以系数 2*Math.PI 增加灵敏度，代表划过整屏幕时转一圈
        targetRotation.y += deltaX * 2 * Math.PI; 
        targetRotation.x += deltaY * 2 * Math.PI;
        previousHandPosition = { x: currentX, y: currentY };
    }} else {{
        // 如果没有检测到手，重置追踪状态，防止瞬移
        let previousPinchDistance = null;
        let previousHandPosition = null;
    }}
    // 4. 应用到物体 (示例：更新Three.js对象)，旋转缩放等均使用Lerp平滑
    updateElementTransform(targetScale, targetRotation);
}}


【手指伸出的判断标准】
MediaPipe 提供 21 个手部骨骼关键点（Landmarks）。请按以下逻辑判断每一根手指是否伸出：
- 食指(8)、中指(12)、无名指(16)、小指(20)：
  - 比较 指尖(Tip) 和 指关节(PIP - 第二关节) 的 Y 轴坐标。
  - 如果 `Tip.y < PIP.y` （注意：Canvas坐标系中Y轴向下为正，所以数值越小位置越高），则判定为伸出。
- 大拇指(4)：
  - 由于大拇指方向多变，请使用“距离比较法”。
  - 计算 大拇指尖(4) 到 小指根部(17) 的欧几里得距离。
  - 计算 大拇指IP关节(3) 到 小指根部(17) 的欧几里得距离。
  - 如果 `指尖距离 > IP关节距离`，则判定为伸出。
