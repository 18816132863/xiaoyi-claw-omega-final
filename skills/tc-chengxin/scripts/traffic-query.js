#!/usr/bin/env node

/**
 * 同程程心大模型 - 交通资源智能查询 API
 * 
 * 用法：
 *   node traffic-query.js --departure "北京" --destination "上海"
 *   node traffic-query.js --departure "北京" --destination "上海" --extra "明天"
 *   node traffic-query.js --departure "苏州" --destination "南京" --extra "自驾"
 * 
 * 参数说明：
 *   --departure <城市>        出发地城市
 *   --destination <城市>      目的地城市
 *   --extra <补充信息>        额外信息（日期、偏好等）
 *   --channel <渠道>          通信渠道（webchat/wechat 等）
 *   --surface <界面>          交互界面（mobile/desktop）
 * 
 * 说明：
 *   本接口用于用户未明确指定交通方式时的智能推荐
 *   会同时返回机票、火车票、汽车票等多种交通方式
 *   调用优先级低于专用查询接口（train-query.js, flight-query.js, bus-query.js）
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
const TRAFFIC_API_PATH = '/trafficResource';

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
 * 调用交通资源智能 API
 * @param {object} params - 查询参数
 * @returns {Promise<object>} - API 响应
 */
function query_traffic_api(params) {
  return new Promise((resolve, reject) => {
    const api_url = `${API_BASE_URL}${TRAFFIC_API_PATH}`;
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
 * 格式化火车结果
 */
function format_train_result(train_data, use_table = false, use_plain_link = false) {
  if (!train_data || !train_data.trainList) {
    return '';
  }
  
  const trains = train_data.trainList.slice(0, 5);
  let output = '\n🚄 **火车票**\n\n';
  
  if (use_table) {
    output += '| 车次 | 出发站 | 到达站 | 出发时间 | 到达时间 | 时长 | 最低价 | PC 预订 | 手机预订 |\n';
    output += '|------|--------|--------|---------|---------|------|--------|--------|---------|\n';
    
    trains.forEach((train) => {
      const train_no = train.trainType === 'GD' ? `🚅 ${train.trainNo}` : `🚆 ${train.trainNo}`;
      const dep_station = train.depStationName || '-';
      const arr_station = train.arrStationName || '-';
      const dep_time = train.depTime || '-';
      const arr_time = train.arrTime || '-';
      const run_time = train.runTime || '-';
      const price = train.price ? `¥${train.price}` : '暂无价格';
      const pc_link = train.pcRedirectUrl || train.clawRedirectUrl || train.redirectUrl || '#';
      const mobile_link = train.clawRedirectUrl || train.redirectUrl || '#';
      
      let pc_link_md = pc_link !== '#' ? (use_plain_link ? pc_link : `[PC 端](${pc_link})`) : '暂不可用';
      let mobile_link_md = mobile_link !== '#' ? (use_plain_link ? mobile_link : `[手机端](${mobile_link})`) : '暂不可用';
      
      output += `| ${train_no} | ${dep_station} | ${arr_station} | ${dep_time} | ${arr_time} | ${run_time} | ${price} | ${pc_link_md} | ${mobile_link_md} |\n`;
    });
  }
  
  return output;
}

/**
 * 格式化机票结果
 */
function format_flight_result(flight_data, use_table = false, use_plain_link = false) {
  if (!flight_data || !flight_data.flightList) {
    return '';
  }
  
  const flights = flight_data.flightList.slice(0, 5);
  let output = '\n✈️ **机票**\n\n';
  
  if (use_table) {
    output += '| 航班号 | 出发机场 | 到达机场 | 出发时间 | 到达时间 | 时长 | 价格 | 航司 | PC 预订 | 手机预订 |\n';
    output += '|--------|---------|---------|---------|---------|------|------|------|--------|---------|\n';
    
    flights.forEach((flight) => {
      const flight_no = flight.flightNo || '-';
      const airline = flight.airlineName || '-';
      const dep_airport = flight.depAirportName || '-';
      const arr_airport = flight.arrAirportName || '-';
      const dep_time = flight.depTime || '-';
      const arr_time = flight.arrTime || '-';
      const run_time = flight.runTime || '-';
      const price = flight.price ? `¥${flight.price}` : '暂无价格';
      const pc_link = flight.pcRedirectUrl || flight.clawRedirectUrl || flight.redirectUrl || '#';
      const mobile_link = flight.clawRedirectUrl || flight.redirectUrl || '#';
      
      let pc_link_md = pc_link !== '#' ? (use_plain_link ? pc_link : `[PC 端](${pc_link})`) : '暂不可用';
      let mobile_link_md = mobile_link !== '#' ? (use_plain_link ? mobile_link : `[手机端](${mobile_link})`) : '暂不可用';
      
      output += `| ${flight_no} | ${dep_airport} | ${arr_airport} | ${dep_time} | ${arr_time} | ${run_time} | ${price} | ${airline} | ${pc_link_md} | ${mobile_link_md} |\n`;
    });
  }
  
  return output;
}

/**
 * 格式化汽车票结果
 */
function format_bus_result(bus_data, use_table = false, use_plain_link = false) {
  if (!bus_data || !bus_data.pageDataList) {
    return '';
  }
  
  const buses = bus_data.pageDataList.slice(0, 5);
  let output = '\n🚌 **汽车票**\n\n';
  
  if (use_table) {
    output += '| 班次 | 出发站 | 到达站 | 出发时间 | 到达时间 | 时长 | 价格 | PC 预订 | 手机预订 |\n';
    output += '|------|--------|--------|---------|---------|------|------|--------|---------|\n';
    
    buses.forEach((bus) => {
      const bus_no = bus.busNo || bus.busName || '-';
      const dep_station = bus.depName || '-';
      const arr_station = bus.arrName || '-';
      const dep_time = bus.depTime || '-';
      const arr_time = bus.arrTime || '-';
      const run_time = bus.runTime || '-';
      const price = bus.price ? `¥${bus.price}` : '暂无价格';
      const pc_link = bus.pcRedirectUrl || bus.clawRedirectUrl || bus.redirectUrl || '#';
      const mobile_link = bus.clawRedirectUrl || bus.redirectUrl || '#';
      
      let pc_link_md = pc_link !== '#' ? (use_plain_link ? pc_link : `[PC 端](${pc_link})`) : '暂不可用';
      let mobile_link_md = mobile_link !== '#' ? (use_plain_link ? mobile_link : `[手机端](${mobile_link})`) : '暂不可用';
      
      output += `| ${bus_no} | ${dep_station} | ${arr_station} | ${dep_time} | ${arr_time} | ${run_time} | ${price} | ${pc_link_md} | ${mobile_link_md} |\n`;
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
    departure: '',
    destination: '',
    extra: '',
    channel: '',
    surface: ''
  };
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    if (arg === '--departure' && args[i + 1]) {
      params.departure = args[++i];
    } else if (arg === '--destination' && args[i + 1]) {
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
  if (params.departure && params.destination) {
    return { valid: true };
  }
  
  return { 
    valid: false, 
    error: `⚠️ 参数不完整，请提供出发地和目的地。
  示例：--departure "北京" --destination "上海"`
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
    console.log('  node traffic-query.js --departure "北京" --destination "上海"');
    console.log('  node traffic-query.js --departure "北京" --destination "上海" --extra "明天"');
    console.log('\n参数说明：');
    console.log('  --departure <城市>        出发地城市');
    console.log('  --destination <城市>      目的地城市');
    console.log('  --extra <补充信息>        额外信息（日期、偏好等）');
    console.log('  --channel <渠道>          通信渠道（webchat/wechat 等）');
    console.log('  --surface <界面>          交互界面（mobile/desktop）');
    console.log('\n' + validation.error);
    process.exit(1);
  }
  
  // 构建请求参数（只包含非空字段）
  const request_params = {};
  if (params.departure) request_params.departure = params.departure;
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
  console.log('🔍 交通资源智能查询');
  console.log(`📤 请求参数：${JSON.stringify(request_params, null, 2)}`);
  console.log(`📡 渠道：${params.channel || '默认'}`);
  console.log(`📱 界面：${params.surface || '默认'}`);
  console.log(`📊 格式：${use_table ? '表格' : '卡片'} | 链接：${use_plain_link ? '纯文本' : 'Markdown'}`);
  console.log('---\n');
  
  try {
    const result = await query_traffic_api(request_params);
    
    if (result.code === '0' || result.code === 0) {
      console.log('✅ 查询成功\n');
      
      const response_data = result.data?.data || result.data;
      
      // 交通资源接口返回多种交通方式
      const trainDataList = response_data?.trainDataList || response_data?.trainData;
      const flightDataList = response_data?.flightDataList || response_data?.flightData;
      const busDataList = response_data?.busDataList || response_data?.busData;
      
      let hasOutput = false;
      
      // 火车票
      if (Array.isArray(trainDataList) && trainDataList.length > 0 && trainDataList[0].trainList) {
        console.log(format_train_result(trainDataList[0], use_table, use_plain_link));
        hasOutput = true;
      } else if (trainDataList && trainDataList.trainList) {
        console.log(format_train_result(trainDataList, use_table, use_plain_link));
        hasOutput = true;
      }
      
      // 机票
      if (Array.isArray(flightDataList) && flightDataList.length > 0 && flightDataList[0].flightList) {
        console.log(format_flight_result(flightDataList[0], use_table, use_plain_link));
        hasOutput = true;
      } else if (flightDataList && flightDataList.flightList) {
        console.log(format_flight_result(flightDataList, use_table, use_plain_link));
        hasOutput = true;
      }
      
      // 汽车票
      if (Array.isArray(busDataList) && busDataList.length > 0 && busDataList[0].pageDataList) {
        console.log(format_bus_result(busDataList[0], use_table, use_plain_link));
        hasOutput = true;
      } else if (busDataList && busDataList.pageDataList) {
        console.log(format_bus_result(busDataList, use_table, use_plain_link));
        hasOutput = true;
      }
      
      if (!hasOutput) {
        console.log('⚠️ 无结果');
        console.log('未找到符合条件的交通方式，请尝试调整查询条件。');
      } else {
        console.log('💡 **更多选择**：也可以打开 **同程旅行 APP** 或在 **微信 - 我 - 服务** 中，点击 **火车票机票** 查看更丰富的资源。\n');
      }
    } else if (result.code === '1') {
      console.log('⚠️ 无结果');
      console.log('未找到符合条件的交通方式，请尝试调整查询条件。');
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
  query_traffic_api,
  validate_params
};

// 运行主函数
if (require.main === module) {
  main();
}
