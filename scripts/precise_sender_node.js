#!/usr/bin/env node
/**
 * 精确定时发送器 - V2.0.0
 * 
 * 在指定时间精确发送消息到聊天界面。
 * 使用 Node.js 直接调用 OpenClaw 的消息发送接口。
 * 
 * 使用方式：
 *     node scripts/precise_sender_node.js --time "2026-04-20 10:45:00" --message "消息内容"
 */

const fs = require('fs');
const path = require('path');
const http = require('http');

// 获取项目根目录
function getProjectRoot() {
    let current = __dirname;
    while (current !== '/') {
        if (fs.existsSync(path.join(current, 'core', 'ARCHITECTURE.md'))) {
            return current;
        }
        current = path.dirname(current);
    }
    return path.dirname(__dirname);
}

// 解析时间
function parseTime(timeStr) {
    // 支持多种格式
    // "2026-04-20 10:45:00" (本地时间)
    // "2026-04-20T02:45:00Z" (UTC)
    if (timeStr.endsWith('Z')) {
        return new Date(timeStr);
    }
    return new Date(timeStr);
}

// 等待到指定时间
async function waitUntil(targetTime) {
    const now = new Date();
    
    if (targetTime <= now) {
        console.log(`目标时间已过: ${targetTime.toISOString()}`);
        return false;
    }
    
    let diff = targetTime - now;
    console.log(`等待 ${(diff / 1000).toFixed(1)} 秒到 ${targetTime.toISOString()}...`);
    
    // 分段等待
    while (diff > 1000) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        diff = targetTime - new Date();
        process.stdout.write(`\r剩余 ${(diff / 1000).toFixed(1)} 秒...`);
    }
    
    // 最后精确等待
    if (diff > 0) {
        await new Promise(resolve => setTimeout(resolve, diff));
    }
    
    console.log(`\n✅ 到达目标时间: ${new Date().toISOString()}`);
    return true;
}

// 通过 Gateway API 发送消息
async function sendMessageViaGateway(message) {
    return new Promise((resolve, reject) => {
        const data = JSON.stringify({
            action: 'send',
            channel: 'xiaoyi-channel',
            message: message
        });
        
        const options = {
            hostname: 'localhost',
            port: 18789,
            path: '/internal/message',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': data.length
            }
        };
        
        const req = http.request(options, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                if (res.statusCode === 200) {
                    resolve({ success: true, body });
                } else {
                    resolve({ success: false, statusCode: res.statusCode, body });
                }
            });
        });
        
        req.on('error', reject);
        req.write(data);
        req.end();
    });
}

// 写入待发送队列（备用方案）
function writeToQueue(message) {
    const root = getProjectRoot();
    const queueFile = path.join(root, 'reports', 'ops', 'pending_sends.jsonl');
    
    const entry = {
        action: 'send',
        channel: 'xiaoyi-channel',
        target: 'default',
        message: message,
        timestamp: new Date().toISOString()
    };
    
    fs.appendFileSync(queueFile, JSON.stringify(entry, null, 0) + '\n', 'utf8');
    console.log(`✅ 消息已写入队列: ${queueFile}`);
}

// 主函数
async function main() {
    const args = process.argv.slice(2);
    
    // 解析参数
    let targetTime = null;
    let message = '';
    
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--time' && i + 1 < args.length) {
            targetTime = parseTime(args[i + 1]);
            i++;
        } else if (args[i] === '--message' && i + 1 < args.length) {
            message = args[i + 1];
            i++;
        }
    }
    
    // 从定时消息文件读取
    if (!targetTime || !message) {
        const root = getProjectRoot();
        const scheduledFile = path.join(root, 'reports', 'ops', 'scheduled_messages.jsonl');
        
        if (fs.existsSync(scheduledFile)) {
            const lines = fs.readFileSync(scheduledFile, 'utf8').trim().split('\n');
            if (lines.length > 0) {
                const scheduled = JSON.parse(lines[0]);
                targetTime = parseTime(scheduled.scheduled_time);
                message = scheduled.content;
                
                // 清空文件
                fs.writeFileSync(scheduledFile, '', 'utf8');
            }
        }
    }
    
    if (!targetTime || !message) {
        console.error('❌ 请提供时间和消息，或创建定时消息文件');
        process.exit(1);
    }
    
    console.log('='.repeat(60));
    console.log('  精确定时发送器 V2.0.0 (Node.js)');
    console.log('='.repeat(60));
    console.log(`  计划时间: ${targetTime.toISOString()} (UTC)`);
    console.log(`  北京时间: ${targetTime.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' })}`);
    console.log(`  消息长度: ${message.length} 字符`);
    console.log('='.repeat(60));
    
    // 等待到指定时间
    if (!await waitUntil(targetTime)) {
        process.exit(1);
    }
    
    // 尝试通过 Gateway API 发送
    console.log('\n📤 发送消息...');
    
    try {
        const result = await sendMessageViaGateway(message);
        if (result.success) {
            console.log('✅ 消息已通过 Gateway 发送');
        } else {
            console.log(`⚠️ Gateway 返回 ${result.statusCode}，使用备用方案`);
            writeToQueue(message);
        }
    } catch (error) {
        console.log(`⚠️ Gateway 调用失败: ${error.message}，使用备用方案`);
        writeToQueue(message);
    }
    
    console.log('='.repeat(60));
    console.log('  ✅ 发送完成');
    console.log('='.repeat(60));
}

main().catch(console.error);
