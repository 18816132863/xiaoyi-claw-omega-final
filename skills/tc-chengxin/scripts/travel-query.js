#!/usr/bin/env node

/**
 * 同程程心大模型 - 旅行资源专用查询 API
 * 
 * 用法：
 *   node travel-query.js --destination "三亚"
 *   node travel-query.js --destination "三亚" --extra "五一假期"
 *   node travel-query.js --destination "云南" --extra "6 天 5 晚 自由行"
 * 
 * 参数说明：
 *   --destination <城市/地区>  目的地城市或地区
 *   --extra <补充信息>        额外信息（假期、天数、类型等）
 *   --channel <渠道>          通信渠道（webchat/wechat 等）
 *   --surface <界面>          交互界面（mobile/desktop）
 * 
 * 说明：
 *   本接口用于查询自由行、跟团游等度假产品
 *   作为用户有明确旅游意向时的补充推荐
 *   如果有合适的单品资源（机票、酒店），应提供更多选择
 * 
 * 配置（优先级：环境变量 > config.json）：
 *   - CHENGXIN_API_KEY（环境变量）
 *   - 或创建 config.json 文件（见 config.example.json）
 */

const https = require('https');
const http = require('http');
const url = require('url');
const fs = require('fs');
const path = require('path');

// 接口配置
const API_BASE_URL = 'https://wx.17u.cn/skills/gateway/api/v1/gateway';
const TRAVEL_API_PATH = '/travelResource';

// 版本号
const API_VERSION = '0.2.0';

// 配置读取（优先级：环境变量 > config.json）
let API_KEY = process.env.CHENGXIN_API_KEY;

/**
 * 构建 Authorization Token
 */
function build_auth_token(key) {
  if (!key) return '';
  return `Bearer ${key}`;
}

if (!API_KEY) {
  try {
    const config_path = path.join(__dirname, '..', 'config.json');
    const config = JSON.parse(fs.readFileSync(config_path, 'utf8'));
    API_KEY = config.apiKey;
  } catch (e) {
    console.error('❌ 配置错误：未找到 CHENGXIN_API_KEY 环境变量或 config.json 文件');
    console.error('   请设置环境变量或在技能目录下创建 config.json 文件');
    process.exit(1);
  }
}

/**
 * 调用旅行资源专用 API
 * @param {object} params - 查询参数
 * @returns {Promise<object>} - API 响应
 */
function query_travel_api(params) {
  return new Promise((resolve, reject) => {
    const api_url = `${API_BASE_URL}${TRAVEL_API_PATH}`;
    const parsed_url = url.parse(api_url);
    const is_https = parsed_url.protocol === 'https:';
    const client = is_https ? https : http;
    
    const post_data = JSON.stringify({
      ...params,
      version: API_VERSION
    });
    
    const options = {
      hostname: parsed_url.hostname,
      port: parsed_url.port || (is_https ? 443 : 80),
      path: parsed_url.path,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(post_data),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://www.ly.com',
        'Referer': 'https://www.ly.com/',
        'Authorization': build_auth_token(API_KEY)
      }
    };
    
    const req = client.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          resolve(result);
        } catch (e) {
          reject(new Error(`解析响应失败：${e.message}`));
        }
      });
    });
    
    req.on('error', (e) => {
      reject(new Error(`请求失败：${e.message}`));
    });
    
    req.write(post_data);
    req.end();
  });
}

/**
 * 格式化旅行产品结果
 * @param {object} trip_data - 旅行产品数据
 * @param {boolean} use_table - 是否使用表格格式
 * @param {boolean} use_plain_link - 是否使用纯文本链接
 * @returns {string} - 格式化输出
 */
function format_travel_result(trip_data, use_table = false, use_plain_link = false) {
  if (!trip_data || !trip_data.tripList) {
    return '';
  }
  
  const trips = trip_data.tripList.slice(0, 10);
  let output = '🧳 **度假产品**\n\n';
  
  if (use_table) {
    // 表格格式
    output += '| 产品 | 目的地 | 价格 | 评分 | 特点 | PC 预订 | 手机预订 |\n';
    output += '|------|--------|------|------|------|--------|---------|\n';
    
    trips.forEach((trip) => {
      const name = trip.name || '未知产品';
      const dest_list = (trip.destList || []).join(', ');
      const price = trip.price ? `¥${trip.price}` : '暂无价格';
      const score = trip.score && trip.score !== '0.0' ? `⭐${trip.score}` : '暂无';
      const label_list = (trip.labelList || []).join(', ');
      
      // 跟团游只有 redirectUrl（手机端），没有 pcRedirectUrl
      const mobile_link = trip.clawRedirectUrl || trip.redirectUrl || '#';
      const pc_link = trip.clawRedirectUrl || trip.redirectUrl || '#';  // 同程跟团游 PC 和移动端是同一链接
      
      let pc_link_md, mobile_link_md;
      if (use_plain_link) {
        pc_link_md = pc_link !== '#' ? pc_link : '暂不可用';
        mobile_link_md = mobile_link !== '#' ? mobile_link : '暂不可用';
      } else {
        pc_link_md = pc_link !== '#' ? `[PC 端](${pc_link})` : '暂不可用';
        mobile_link_md = mobile_link !== '#' ? `[手机端](${mobile_link})` : '暂不可用';
      }
      
      output += `| ${name} | ${dest_list} | ${price} | ${score} | ${label_list} | ${pc_link_md} \\| ${mobile_link_md} |\n`;
    });
  } else {
    // 卡片格式
    trips.forEach((trip) => {
      const name = trip.name || '未知产品';
      const dest_list = (trip.destList || []).join(', ');
      const price = trip.price ? `¥${trip.price}` : '暂无价格';
      const score = trip.score && trip.score !== '0.0' ? `⭐${trip.score}` : '暂无';
      const comment_num = trip.commentNum || '0';
      const label_list = (trip.labelList || []).join(', ');
      
      // 跟团游只有 redirectUrl（手机端），没有 pcRedirectUrl
      const mobile_link = trip.clawRedirectUrl || trip.redirectUrl || '#';
      const pc_link = trip.clawRedirectUrl || trip.redirectUrl || '#';  // 同程跟团游 PC 和移动端是同一链接
      
      let pc_link_md, mobile_link_md;
      if (use_plain_link) {
        pc_link_md = pc_link !== '#' ? `PC 端：${pc_link}` : '暂不可用';
        mobile_link_md = mobile_link !== '#' ? `手机端：${mobile_link}` : '暂不可用';
      } else {
        pc_link_md = pc_link !== '#' ? `[PC 端](${pc_link})` : '暂不可用';
        mobile_link_md = mobile_link !== '#' ? `[手机端](${mobile_link})` : '暂不可用';
      }
      
      output += `### 🧳 ${name}\n`;
      output += `**目的地** ${dest_list}\n`;
      output += `**价格** ${price} | **评分** ${score}（${comment_num}条）\n`;
      if (label_list) output += `**特点** ${label_list}\n`;
      output += `**预订** ${pc_link_md} | ${mobile_link_md}\n`;
      output += '\n---\n\n';
    });
  }
  
  return output;
}

/**
 * 解析命令行参数
 * @returns {object} - 解析后的参数对象
 */
function parse_args() {
  const args = process.argv.slice(2);
  const params = {
    destination: '',
    extra: '',
    channel: '',
    surface: ''
  };
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    if (arg === '--destination' && args[i + 1]) {
      params.destination = args[++i];
    } else if (arg === '--extra' && args[i + 1]) {
      params.extra = args[++i];
    } else if (arg === '--channel' && args[i + 1]) {
      params.channel = args[++i];
    } else if (arg === '--surface' && args[i + 1]) {
      params.surface = args[++i];
    }
  }
  
  return params;
}

/**
 * 验证参数组合
 * @param {object} params - 参数对象
 * @returns {object} - { valid: boolean, error: string }
 */
function validate_params(params) {
  if (params.destination) {
    return { valid: true };
  }
  
  return { 
    valid: false, 
    error: `⚠️ 参数不完整，请提供目的地城市或地区。
  示例：--destination "三亚"`
  };
}

/**
 * 主函数
 */
async function main() {
  const params = parse_args();
  
  // 验证参数
  const validation = validate_params(params);
  if (!validation.valid) {
    console.log('用法：');
    console.log('  node travel-query.js --destination "三亚"');
    console.log('  node travel-query.js --destination "三亚" --extra "五一假期"');
    console.log('  node travel-query.js --destination "云南" --extra "6 天 5 晚 自由行"');
    console.log('\n参数说明：');
    console.log('  --destination <城市/地区>  目的地城市或地区');
    console.log('  --extra <补充信息>        额外信息（假期、天数、类型等）');
    console.log('  --channel <渠道>          通信渠道（webchat/wechat 等）');
    console.log('  --surface <界面>          交互界面（mobile/desktop）');
    console.log('\n' + validation.error);
    process.exit(1);
  }
  
  // 构建请求参数（只包含非空字段）
  const request_params = {};
  if (params.destination) request_params.destination = params.destination;
  if (params.extra) request_params.extra = params.extra;
  if (params.channel) request_params.channel = params.channel;
  if (params.surface) request_params.surface = params.surface;
  
  // 检测输出格式
  let use_table = false;
  let use_plain_link = false;
  
  if (params.channel === 'webchat') {
    use_table = true;
  } else if (params.channel.includes('wechat') || params.channel.includes('weixin') || params.channel.includes('微信')) {
    use_plain_link = true;
  } else if (params.surface === 'mobile') {
    use_table = false;
  }
  
  // 输出调试信息
  console.log('🔍 旅行资源专用查询');
  console.log(`📤 请求参数：${JSON.stringify(request_params, null, 2)}`);
  console.log(`📡 渠道：${params.channel || '默认'}`);
  console.log(`📱 界面：${params.surface || '默认'}`);
  console.log(`📊 格式：${use_table ? '表格' : '卡片'} | 链接：${use_plain_link ? '纯文本' : 'Markdown'}`);
  console.log('---\n');
  
  try {
    const result = await query_travel_api(request_params);
    
    if (result.code === '0' || result.code === 0) {
      console.log('✅ 查询成功\n');
      
      const response_data = result.data?.data || result.data;
      
      // 新结构：tripDataList 是数组，每个元素包含 pageDataList, tripList, desc
      // 旧结构：tripData 是单个对象
      const tripDataList = response_data?.tripDataList;
      const tripData = response_data?.tripData;
      
      let hasOutput = false;
      
      if (Array.isArray(tripDataList) && tripDataList.length > 0) {
        // 新结构：遍历所有列表，每个列表都有 desc 说明
        tripDataList.forEach((item, index) => {
          if (item.tripList && item.tripList.length > 0) {
            // 输出列表说明（desc）
            if (item.desc) {
              console.log(`📌 ${item.desc}\n`);
            } else if (tripDataList.length > 1) {
              console.log(`📌 列表 ${index + 1}\n`);
            }
            console.log(format_travel_result(item, use_table, use_plain_link));
            hasOutput = true;
          }
        });
      } else if (tripData && tripData.tripList) {
        // 旧结构：单个对象
        console.log(format_travel_result(tripData, use_table, use_plain_link));
        hasOutput = true;
      }
      
      if (!hasOutput) {
        console.log('⚠️ 无结果');
        console.log('未找到符合条件的度假产品，请尝试调整查询条件。');
      } else {
        console.log('💡 **更多选择**：也可以打开 **同程旅行 APP** 或在 **微信 - 我 - 服务** 中，点击 **火车票机票** 以及 **酒店民宿** 查看更丰富的资源。\n');
      }
    } else if (result.code === '1') {
      console.log('⚠️ 无结果');
      console.log('未找到符合条件的度假产品，请尝试调整查询条件。');
    } else {
      console.log(`❌ 查询失败：${result.message || '未知错误'}`);
      if (result.message?.includes('鉴权') || result.message?.includes('unauthorized')) {
        console.log('\n⚠️ 同程程心 API 未配置或无效');
        console.log('请检查 config.json 中的 apiKey 是否正确。');
      }
    }
  } catch (error) {
    console.error(`❌ 错误：${error.message}`);
    process.exit(1);
  }
}

// 导出函数供其他模块使用
module.exports = {
  query_travel_api,
  validate_params,
  format_travel_result
};

// 运行主函数
if (require.main === module) {
  main();
}
