#!/usr/bin/env node

/**
 * 微博龙虾助手 API 测试脚本
 * 用于验证微博 OpenClaw 插件的 API 连接和功能
 * 
 * 使用方法：
 * node test_weibo_api.js --appId <appId> --appSecret <appSecret> [--action <action>]
 * 
 * action 可选值：
 * - token: 仅测试获取 token
 * - hot_search: 测试热搜榜
 * - user_status: 测试用户微博
 * - all: 测试所有功能（默认）
 */

const http = require('http');

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

// 获取 Token
function getToken(appId, appSecret) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify({
      app_id: appId,
      app_secret: appSecret
    });

    const options = {
      hostname: 'open-im.api.weibo.com',
      port: 80,
      path: '/open/auth/ws_token',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (result.data && result.data.token) {
            resolve(result.data.token);
          } else {
            reject(new Error('Token 获取失败: ' + data));
          }
        } catch (e) {
          reject(new Error('JSON 解析失败: ' + e.message));
        }
      });
    });

    req.on('error', (e) => reject(e));
    req.write(postData);
    req.end();
  });
}

// 获取热搜榜
function getHotSearch(token, category = '主榜', count = 20) {
  return new Promise((resolve, reject) => {
    const url = `http://open-im.api.weibo.com/open/weibo/hot_search?token=${encodeURIComponent(token)}&category=${encodeURIComponent(category)}&count=${count}`;
    
    http.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (result.code === 0 && result.data && result.data.data) {
            resolve(result.data.data);
          } else {
            reject(new Error('热搜获取失败: ' + data));
          }
        } catch (e) {
          reject(new Error('JSON 解析失败: ' + e.message));
        }
      });
    }).on('error', (e) => reject(e));
  });
}

// 获取用户微博
function getUserStatus(token, count = 10) {
  return new Promise((resolve, reject) => {
    const url = `http://open-im.api.weibo.com/open/weibo/user_status?token=${encodeURIComponent(token)}&count=${count}`;
    
    http.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (result.code === 0 && result.data && result.data.statuses) {
            resolve(result.data);
          } else {
            reject(new Error('用户微博获取失败: ' + data));
          }
        } catch (e) {
          reject(new Error('JSON 解析失败: ' + e.message));
        }
      });
    }).on('error', (e) => reject(e));
  });
}

// 主函数
async function main() {
  const params = parseArgs();
  
  if (!params.appId || !params.appSecret) {
    console.error('❌ 缺少必要参数');
    console.log('使用方法: node test_weibo_api.js --appId <appId> --appSecret <appSecret> [--action <action>]');
    console.log('action 可选值: token, hot_search, user_status, all');
    process.exit(1);
  }

  const action = params.action || 'all';
  
  console.log('🔍 微博龙虾助手 API 测试');
  console.log('========================\n');

  try {
    // 测试 Token
    console.log('📌 测试 1: 获取 Token');
    const token = await getToken(params.appId, params.appSecret);
    console.log('✅ Token 获取成功');
    console.log(`   Token: ${token.substring(0, 20)}...`);
    console.log();

    if (action === 'token') {
      console.log('🎉 测试完成');
      return;
    }

    // 测试热搜
    if (action === 'hot_search' || action === 'all') {
      console.log('📌 测试 2: 获取热搜榜');
      const hotSearch = await getHotSearch(token);
      console.log('✅ 热搜榜获取成功');
      console.log(`   共 ${hotSearch.length} 条热搜`);
      console.log('   Top 5:');
      hotSearch.slice(0, 5).forEach((item, i) => {
        console.log(`   ${i + 1}. ${item.word} (热度: ${item.num})`);
      });
      console.log();
    }

    // 测试用户微博
    if (action === 'user_status' || action === 'all') {
      console.log('📌 测试 3: 获取用户微博');
      const userStatus = await getUserStatus(token, 5);
      console.log('✅ 用户微博获取成功');
      console.log(`   用户: ${userStatus.user?.screen_name || '未知'}`);
      console.log(`   微博数: ${userStatus.statuses?.length || 0}`);
      if (userStatus.statuses && userStatus.statuses.length > 0) {
        console.log('   最新一条:');
        const latest = userStatus.statuses[0];
        console.log(`   内容: ${latest.text.substring(0, 50)}...`);
        console.log(`   时间: ${latest.created_at}`);
      }
      console.log();
    }

    console.log('🎉 所有测试通过！微博龙虾助手 API 连接正常。');
    
  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    process.exit(1);
  }
}

main();
