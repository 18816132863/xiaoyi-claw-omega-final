#!/usr/bin/env node

/**
 * QQ ClawBot API 测试脚本
 * 用于验证 QQ OpenClaw 插件的 API 连接和功能
 * 
 * 使用方法：
 * node test_qqbot_api.js --appId <appId> --clientSecret <clientSecret>
 */

const https = require('https');

// 解析命令行参数
function parseArgs() {
  const args = process.argv.slice(2);
  const params = {};
  
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      const value = args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true;
      params[key] = value;
      if (value !== true) i++;
    }
  }
  
  return params;
}

// 获取 Access Token
function getAccessToken(appId, clientSecret) {
  return new Promise((resolve, reject) => {
    const postData = `grant_type=client_credentials&app_id=${appId}&client_secret=${clientSecret}`;

    const options = {
      hostname: 'bots.qq.com',
      port: 443,
      path: '/oauth2/token',
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (result.access_token) {
            resolve({
              accessToken: result.access_token,
              expiresIn: result.expires_in
            });
          } else {
            reject(new Error(`获取 Token 失败: ${result.error_description || result.error || data}`));
          }
        } catch (e) {
          reject(new Error(`JSON 解析失败: ${e.message}, 原始响应: ${data}`));
        }
      });
    });

    req.on('error', (e) => reject(e));
    req.write(postData);
    req.end();
  });
}

// 获取机器人信息
function getBotInfo(accessToken) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'bots.qq.com',
      port: 443,
      path: '/users/@me',
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (result.id) {
            resolve(result);
          } else {
            reject(new Error(`获取机器人信息失败: ${data}`));
          }
        } catch (e) {
          reject(new Error(`JSON 解析失败: ${e.message}`));
        }
      });
    });

    req.on('error', (e) => reject(e));
    req.end();
  });
}

// 主函数
async function main() {
  const params = parseArgs();
  
  if (!params.appId || !params.clientSecret) {
    console.error('❌ 缺少必要参数');
    console.log('使用方法: node test_qqbot_api.js --appId <appId> --clientSecret <clientSecret>');
    process.exit(1);
  }

  console.log('🔍 QQ ClawBot API 测试');
  console.log('========================\n');

  try {
    // 测试 Access Token
    console.log('📌 测试 1: 获取 Access Token');
    const tokenResult = await getAccessToken(params.appId, params.clientSecret);
    console.log('✅ Access Token 获取成功');
    console.log(`   Token: ${tokenResult.accessToken.substring(0, 30)}...`);
    console.log(`   有效期: ${tokenResult.expiresIn} 秒`);
    console.log();

    // 测试机器人信息
    console.log('📌 测试 2: 获取机器人信息');
    const botInfo = await getBotInfo(tokenResult.accessToken);
    console.log('✅ 机器人信息获取成功');
    console.log(`   机器人名称: ${botInfo.username || '未设置'}`);
    console.log(`   机器人 ID: ${botInfo.id}`);
    console.log(`   头像: ${botInfo.avatar || '未设置'}`);
    console.log();

    console.log('🎉 所有测试通过！QQ ClawBot API 连接正常。');
    console.log('\n📋 下一步：');
    console.log('1. 在 QQ 上搜索你的机器人名称');
    console.log('2. 发送消息测试');
    console.log('3. 使用 /bot-ping 测试延迟');
    
  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    
    if (error.message.includes('invalid appid or secret')) {
      console.log('\n🔧 可能的原因：');
      console.log('1. AppID 或 clientSecret 错误');
      console.log('2. 请从 QQ 开放平台 (https://q.qq.com/) 重新获取凭证');
    }
    
    process.exit(1);
  }
}

main();
