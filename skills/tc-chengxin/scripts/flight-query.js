#!/usr/bin/env node

/**
 * 同程程心大模型 - 机票专用查询 API
 * 
 * 用法：
 *   node flight-query.js --departure "北京" --destination "上海"
 *   node flight-query.js --departure "北京" --low-price
 *   node flight-query.js --flight-number "CA1234"
 *   node flight-query.js --departure "北京" --destination "上海" --extra "明天"
 * 
 * 参数说明：
 *   --departure <城市>        出发地城市
 *   --destination <城市>      目的地城市
 *   --flight-number <航班号>  航班号
 *   --extra <补充信息>        额外信息（日期、偏好等）
 *   --low-price               查询特价机票（仅出发地时有效）
 *   --channel <渠道>          通信渠道（webchat/wechat 等）
 *   --surface <界面>          交互界面（mobile/desktop）
 * 
 * 合法组合：
 *   1. 出发地 + 目的地
 *   2. 航班号
 *   3. 出发地 + lowPrice=true（查询特价机票）
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
const FLIGHT_API_PATH = '/flightResource';

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
 * 调用机票专用 API
 * @param {object} params - 查询参数
 * @returns {Promise<object>} - API 响应
 */
function query_flight_api(params) {
  return new Promise((resolve, reject) => {
    const api_url = `${API_BASE_URL}${FLIGHT_API_PATH}`;
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
 * 格式化机票结果
 * @param {object} flight_data - 机票数据
 * @param {boolean} use_table - 是否使用表格格式
 * @param {boolean} use_plain_link - 是否使用纯文本链接
 * @returns {string} - 格式化输出
 */
function format_flight_result(flight_data, use_table = false, use_plain_link = false) {
  if (!flight_data || !flight_data.flightList) {
    return '未找到相关机票信息';
  }
  
  const flights = flight_data.flightList;
  // 获取顶层 PC 链接（列表页）作为备选
  const page_pc_link = flight_data.pageDataList?.[0]?.pcRedirectUrl || '';
  
  // 检测是否为特价机票场景（字段为 null 表示特价推荐）
  const is_special_price = flights.length > 0 && (flights[0].flightNo === null || flights[0].flightNo === undefined);
  
  let output = '✈️ 机票查询结果：\n\n';
  
  if (is_special_price && use_table) {
    // 特价机票格式：表格
    output += '| 目的地 | 价格 | 日期 | 折扣 | 原价 | 预订链接 |\n';
    output += '|--------|------|------|------|------|----------|\n';
    
    flights.forEach((flight) => {
      const dep_name = flight.depName || '-';
      const arr_name = flight.arrName || '-';
      const price = flight.price ? `¥${flight.price}` : '暂无价格';
      const week = flight.week || '-';
      const discount = flight.discount || '-';
      const origin_price = flight.originPrice ? `¥${flight.originPrice}` : '-';
      const pc_link = flight.clawRedirectUrl || flight.redirectUrl || '#';
      const mobile_link = flight.clawRedirectUrl || flight.redirectUrl || '#';
      
      let pc_link_md, mobile_link_md;
      if (use_plain_link) {
        pc_link_md = pc_link !== '#' ? `PC 端：${pc_link}` : '暂不可用';
        mobile_link_md = mobile_link !== '#' ? `手机端：${mobile_link}` : '暂不可用';
      } else {
        pc_link_md = pc_link !== '#' ? `[PC 端](${pc_link})` : '暂不可用';
        mobile_link_md = mobile_link !== '#' ? `[手机端](${mobile_link})` : '暂不可用';
      }
      
      output += `| ${dep_name}→${arr_name} | ${price} | ${week} | ${discount} | ${origin_price} | ${pc_link_md} \\| ${mobile_link_md} |\n`;
    });
  } else {
    // 常规航班格式：卡片
    flights.forEach((flight) => {
      const flight_no = flight.flightNo || '-';
      const airline = flight.airlineName || '-';
      const dep_airport = flight.depAirportName || '-';
      const arr_airport = flight.arrAirportName || '-';
      const dep_time = flight.depTime || '-';
      const arr_time = flight.arrTime || '-';
      const run_time = flight.runTime || '-';
      const price = flight.price ? `¥${flight.price}` : '暂无价格';
      
      // 构建链接 - 航班对象没有 pcRedirectUrl，使用顶层列表页链接
      const pc_link = page_pc_link || flight.clawRedirectUrl || flight.redirectUrl || '#';
      const mobile_link = flight.clawRedirectUrl || flight.redirectUrl || '#';
      
      let pc_link_md, mobile_link_md;
      if (use_plain_link) {
        pc_link_md = pc_link !== '#' ? `PC 端：${pc_link}` : '暂不可用';
        mobile_link_md = mobile_link !== '#' ? `手机端：${mobile_link}` : '暂不可用';
      } else {
        pc_link_md = pc_link !== '#' ? `[PC 端](${pc_link})` : '暂不可用';
        mobile_link_md = mobile_link !== '#' ? `[手机端](${mobile_link})` : '暂不可用';
      }
      
      output += `### ✈️ ${flight_no} | ${dep_airport} → ${arr_airport}\n`;
      output += `**出发时间** ${dep_time} | **到达时间** ${arr_time} | **时长** ${run_time}\n`;
      output += `**价格** ${price}\n`;
      output += `**航司** ${airline}\n`;
      output += `**预订** ${pc_link_md} | ${mobile_link_md}\n`;
      output += '\n---\n\n';
    });
  }
  
  output += '💡 **更多选择**：也可以打开 **同程旅行 APP** 或在 **微信 - 我 - 服务** 中，点击 **火车票机票** 查看更丰富的资源。\n';
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
    departure: '',
    destination: '',
    flightNumber: '',
    extra: '',
    lowPrice: false,
    channel: '',
    surface: ''
  };
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    if (arg === '--departure' && args[i + 1]) {
      params.departure = args[++i];
    } else if (arg === '--destination' && args[i + 1]) {
      params.destination = args[++i];
    } else if (arg === '--flight-number' && args[i + 1]) {
      params.flightNumber = args[++i];
    } else if (arg === '--extra' && args[i + 1]) {
      params.extra = args[++i];
    } else if (arg === '--low-price') {
      params.lowPrice = true;
    } else if (arg === '--channel' && args[i + 1]) {
      params.channel = args[++i];
    } else if (arg === '--surface' && args[i + 1]) {
      params.surface = args[++i];
    } else if (!arg.startsWith('--') && !params.departure) {
      // 支持简写：第一个非选项参数作为查询文本
      params.query = arg;
    }
  }
  
  return params;
}

/**
 * 验证参数组合
 * @param {object} params - 参数对象
 * @returns {object} - { valid: boolean, error: string, suggestLowPrice: boolean }
 */
function validate_params(params) {
  const has_departure_dest = params.departure && params.destination;
  const has_flight_number = params.flightNumber;
  const has_low_price = params.departure && params.lowPrice;
  
  if (has_departure_dest || has_flight_number || has_low_price) {
    return { valid: true };
  }
  
  if (params.departure && !params.destination) {
    // 只有出发地，建议用户使用 lowPrice 查询特价机票
    return { 
      valid: false, 
      error: `⚠️ 参数不完整，请提供以下组合之一：
  1. 出发地 + 目的地（--departure "北京" --destination "上海"）
  2. 航班号（--flight-number "CA1234"）
  3. 仅出发地查询特价机票（--departure "北京" --low-price）`,
      suggestLowPrice: true
    };
  }
  
  return { valid: false, error: '请提供查询参数', suggestLowPrice: false };
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
    console.log('  node flight-query.js --departure "北京" --destination "上海"');
    console.log('  node flight-query.js --flight-number "CA1234"');
    console.log('  node flight-query.js --departure "北京" --low-price --extra "明天"');
    console.log('\n参数说明：');
    console.log('  --departure <城市>        出发地城市');
    console.log('  --destination <城市>      目的地城市');
    console.log('  --flight-number <航班号>  航班号');
    console.log('  --extra <补充信息>        额外信息（日期、偏好等）');
    console.log('  --low-price               查询特价机票（仅出发地时有效）');
    console.log('  --channel <渠道>          通信渠道（webchat/wechat 等）');
    console.log('  --surface <界面>          交互界面（mobile/desktop）');
    console.log('\n' + validation.error);
    
    if (validation.suggestLowPrice) {
      console.log('\n💡 提示：如果您想查看从该地出发到全国各地的特价机票，请添加 --low-price 参数');
    }
    process.exit(1);
  }
  
  // 构建请求参数（只包含非空字段）
  const request_params = {};
  if (params.departure) request_params.departure = params.departure;
  if (params.destination) request_params.destination = params.destination;
  if (params.flightNumber) request_params.flightNumber = params.flightNumber;
  if (params.extra) request_params.extra = params.extra;
  if (params.lowPrice) request_params.lowPrice = true;
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
  console.log('🔍 机票专用查询');
  console.log(`📤 请求参数：${JSON.stringify(request_params, null, 2)}`);
  console.log(`📡 渠道：${params.channel || '默认'}`);
  console.log(`📱 界面：${params.surface || '默认'}`);
  console.log(`📊 格式：${use_table ? '表格' : '卡片'} | 链接：${use_plain_link ? '纯文本' : 'Markdown'}`);
  console.log('---\n');
  
  try {
    const result = await query_flight_api(request_params);
    
    if (result.code === '0' || result.code === 0) {
      console.log('✅ 查询成功\n');
      
      const response_data = result.data?.data || result.data;
      
      // 新结构：flightDataList 是数组，每个元素包含 pageDataList, flightList, desc
      // 旧结构：flightData 是单个对象
      const flightDataList = response_data?.flightDataList;
      const flightData = response_data?.flightData;
      
      if (Array.isArray(flightDataList) && flightDataList.length > 0) {
        // 新结构：遍历所有列表，每个列表都有 desc 说明
        let hasOutput = false;
        flightDataList.forEach((item, index) => {
          if (item.flightList && item.flightList.length > 0) {
            // 输出列表说明（desc）
            if (item.desc) {
              console.log(`📌 ${item.desc}\n`);
            } else if (flightDataList.length > 1) {
              console.log(`📌 列表 ${index + 1}\n`);
            }
            console.log(format_flight_result(item, use_table, use_plain_link));
            hasOutput = true;
          }
        });
        if (!hasOutput) {
          console.log('⚠️ 无结果');
          console.log('未找到符合条件的机票，请尝试调整查询条件。');
        }
      } else if (flightData) {
        // 旧结构：单个对象
        console.log(format_flight_result(flightData, use_table, use_plain_link));
      } else {
        console.log('⚠️ 无结果');
        console.log('未找到符合条件的机票，请尝试调整查询条件。');
      }
    } else if (result.code === '1') {
      console.log('⚠️ 无结果');
      console.log('未找到符合条件的机票，请尝试调整查询条件。');
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
  query_flight_api,
  validate_params,
  format_flight_result
};

// 运行主函数
if (require.main === module) {
  main();
}
