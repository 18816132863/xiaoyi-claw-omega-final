#!/usr/bin/env node

/**
 * 同程程心大模型 - 酒店专用查询 API
 * 
 * 用法：
 *   node hotel-query.js --destination "上海"
 *   node hotel-query.js --destination "上海" --extra "明天入住"
 *   node hotel-query.js --destination "上海" --extra "外滩附近 明天入住"
 * 
 * 参数说明：
 *   --destination <城市>      目的地城市
 *   --extra <补充信息>        额外信息（日期、位置偏好等）
 *   --channel <渠道>          通信渠道（webchat/wechat 等）
 *   --surface <界面>          交互界面（mobile/desktop）
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
const HOTEL_API_PATH = '/hotelResource';

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
 * 调用酒店专用 API
 * @param {object} params - 查询参数
 * @returns {Promise<object>} - API 响应
 */
function query_hotel_api(params) {
  return new Promise((resolve, reject) => {
    const api_url = `${API_BASE_URL}${HOTEL_API_PATH}`;
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
 * 格式化酒店结果
 * @param {object} hotel_data - 酒店数据
 * @param {boolean} use_table - 是否使用表格格式
 * @param {boolean} use_plain_link - 是否使用纯文本链接
 * @returns {string} - 格式化输出
 */
function format_hotel_result(hotel_data, use_table = false, use_plain_link = false) {
  if (!hotel_data || !hotel_data.hotelList) {
    return '未找到相关酒店信息';
  }
  
  const hotels = hotel_data.hotelList;
  let output = '🏨 酒店查询结果：\n\n';
  
  if (use_table) {
    // 表格格式
    output += '| 酒店名称 | 价格 | 类型 | 评分 | 地址 | PC 预订 | 手机预订 |\n';
    output += '|----------|------|------|------|------|--------|---------|\n';
    
    hotels.forEach((hotel) => {
      const name = hotel.name || '未知酒店';
      const price = hotel.price ? `¥${hotel.price}` : '暂无价格';
      const star = hotel.star || '未评级';
      const score = hotel.score || '暂无';
      const comment_num = hotel.commentNum || '0';
      const address = hotel.address || '';
      const resource_id = hotel.resourceId || '';
      
      // 构建链接 - PC 详情页使用酒店 ID 构建
      let pc_link = '#';
      if (resource_id) {
        const raw_pc_link = hotel.pcRedirectUrl || '';
        if (raw_pc_link.includes('hoteldetail')) {
          pc_link = raw_pc_link;
        } else if (raw_pc_link.includes('hotellist')) {
          const in_date_match = raw_pc_link.match(/inDate=([^&]+)/);
          const out_date_match = raw_pc_link.match(/outDate=([^&]+)/);
          const in_date = in_date_match ? in_date_match[1] : '2026-04-04';
          const out_date = out_date_match ? out_date_match[1] : '2026-04-05';
          pc_link = `https://www.ly.com/hotel/hoteldetail?hotelid=${resource_id}&inDate=${in_date}&outDate=${out_date}`;
        } else {
          pc_link = raw_pc_link || '#';
        }
      } else {
        pc_link = hotel.pcRedirectUrl || hotel.clawRedirectUrl || hotel.redirectUrl || '#';
      }
      
      const mobile_link = hotel.clawRedirectUrl || hotel.redirectUrl || '#';
      
      let pc_link_md, mobile_link_md;
      if (use_plain_link) {
        pc_link_md = pc_link !== '#' ? pc_link : '暂不可用';
        mobile_link_md = mobile_link !== '#' ? mobile_link : '暂不可用';
      } else {
        pc_link_md = pc_link !== '#' ? `[PC 端](${pc_link})` : '暂不可用';
        mobile_link_md = mobile_link !== '#' ? `[手机端](${mobile_link})` : '暂不可用';
      }
      
      output += `| ${name} | ${price} | ${star} | ⭐${score}（${comment_num}条） | ${address} | ${pc_link_md} | ${mobile_link_md} |\n`;
    });
  } else {
    // 卡片格式
    hotels.forEach((hotel) => {
      const name = hotel.name || '未知酒店';
      const price = hotel.price ? `¥${hotel.price}` : '暂无价格';
      const star = hotel.star || '未评级';
      const score = hotel.score || '暂无';
      const comment_num = hotel.commentNum || '0';
      const describe = hotel.describe || '无';
      const address = hotel.address || '';
      const resource_id = hotel.resourceId || '';
      
      // 构建链接 - PC 详情页使用酒店 ID 构建
      let pc_link = '#';
      if (resource_id) {
        const raw_pc_link = hotel.pcRedirectUrl || '';
        if (raw_pc_link.includes('hoteldetail')) {
          pc_link = raw_pc_link;
        } else if (raw_pc_link.includes('hotellist')) {
          const in_date_match = raw_pc_link.match(/inDate=([^&]+)/);
          const out_date_match = raw_pc_link.match(/outDate=([^&]+)/);
          const in_date = in_date_match ? in_date_match[1] : '2026-04-04';
          const out_date = out_date_match ? out_date_match[1] : '2026-04-05';
          pc_link = `https://www.ly.com/hotel/hoteldetail?hotelid=${resource_id}&inDate=${in_date}&outDate=${out_date}`;
        } else {
          pc_link = raw_pc_link || '#';
        }
      } else {
        pc_link = hotel.pcRedirectUrl || hotel.clawRedirectUrl || hotel.redirectUrl || '#';
      }
      
      const mobile_link = hotel.clawRedirectUrl || hotel.redirectUrl || '#';
      
      let pc_link_md, mobile_link_md;
      if (use_plain_link) {
        pc_link_md = pc_link !== '#' ? `PC 端：${pc_link}` : '暂不可用';
        mobile_link_md = mobile_link !== '#' ? `手机端：${mobile_link}` : '暂不可用';
      } else {
        pc_link_md = pc_link !== '#' ? `[PC 端](${pc_link})` : '暂不可用';
        mobile_link_md = mobile_link !== '#' ? `[手机端](${mobile_link})` : '暂不可用';
      }
      
      output += `### 🏨 ${name}\n`;
      output += `**价格** ${price}/晚起 | **类型** ${star} | **评分** ⭐${score}（${comment_num}条）\n`;
      output += `**特点** ${describe}\n`;
      if (address) output += `**地址** ${address}\n`;
      output += `**预订** ${pc_link_md} | ${mobile_link_md}\n`;
      output += '\n---\n\n';
    });
  }
  
  output += '💡 **更多选择**：也可以打开 **同程旅行 APP** 或在 **微信 - 我 - 服务** 中，点击 **酒店民宿** 查看更丰富的资源。\n';
  output += '\n';
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
    } else if (!arg.startsWith('--') && !params.destination) {
      // 支持简写：第一个非选项参数作为目的地
      params.destination = arg;
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
    error: `⚠️ 参数不完整，请提供目的地城市。
  示例：--destination "上海"`
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
    console.log('  node hotel-query.js --destination "上海"');
    console.log('  node hotel-query.js --destination "上海" --extra "明天入住"');
    console.log('  node hotel-query.js --destination "上海" --extra "外滩附近 明天入住"');
    console.log('\n参数说明：');
    console.log('  --destination <城市>      目的地城市');
    console.log('  --extra <补充信息>        额外信息（日期、位置偏好等）');
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
  console.log('🔍 酒店专用查询');
  console.log(`📤 请求参数：${JSON.stringify(request_params, null, 2)}`);
  console.log(`📡 渠道：${params.channel || '默认'}`);
  console.log(`📱 界面：${params.surface || '默认'}`);
  console.log(`📊 格式：${use_table ? '表格' : '卡片'} | 链接：${use_plain_link ? '纯文本' : 'Markdown'}`);
  console.log('---\n');
  
  try {
    const result = await query_hotel_api(request_params);
    
    if (result.code === '0' || result.code === 0) {
      console.log('✅ 查询成功\n');
      
      const response_data = result.data?.data || result.data;
      
      // 新结构：hotelDataList 是数组，每个元素包含 pageDataList, hotelList, desc
      // 旧结构：hotelData 是单个对象
      const hotelDataList = response_data?.hotelDataList;
      const hotelData = response_data?.hotelData;
      
      if (Array.isArray(hotelDataList) && hotelDataList.length > 0) {
        // 新结构：遍历所有列表，每个列表都有 desc 说明
        let hasOutput = false;
        hotelDataList.forEach((item, index) => {
          if (item.hotelList && item.hotelList.length > 0) {
            // 输出列表说明（desc）
            if (item.desc) {
              console.log(`📌 ${item.desc}\n`);
            } else if (hotelDataList.length > 1) {
              console.log(`📌 列表 ${index + 1}\n`);
            }
            console.log(format_hotel_result(item, use_table, use_plain_link));
            hasOutput = true;
          }
        });
        if (!hasOutput) {
          console.log('⚠️ 无结果');
          console.log('未找到符合条件的酒店，请尝试调整查询条件。');
        }
      } else if (hotelData) {
        // 旧结构：单个对象
        console.log(format_hotel_result(hotelData, use_table, use_plain_link));
      } else {
        console.log('⚠️ 无结果');
        console.log('未找到符合条件的酒店，请尝试调整查询条件。');
      }
    } else if (result.code === '1') {
      console.log('⚠️ 无结果');
      console.log('未找到符合条件的酒店，请尝试调整查询条件。');
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
  query_hotel_api,
  validate_params,
  format_hotel_result
};

// 运行主函数
if (require.main === module) {
  main();
}
