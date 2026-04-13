#!/usr/bin/env node

/**
 * 同程程心大模型 - 火车票专用查询 API
 * 
 * 用法：
 *   node train-query.js --departure "北京" --destination "上海"
 *   node train-query.js --train-number "G1234"
 *   node train-query.js --departure-station "北京南站" --arrival-station "上海虹桥站"
 *   node train-query.js --departure "北京" --destination "上海" --extra "明天 高铁"
 * 
 * 参数说明：
 *   --departure <城市>        出发地城市
 *   --destination <城市>      目的地城市
 *   --departure-station <站>  出发站
 *   --arrival-station <站>    到达站
 *   --train-number <车次>     车次号
 *   --extra <补充信息>        额外信息（日期、偏好等）
 *   --channel <渠道>          通信渠道（webchat/wechat等）
 *   --surface <界面>          交互界面（mobile/desktop）
 * 
 * 合法组合：
 *   1. 出发地 + 目的地
 *   2. 车次号
 *   3. 出发站 + 到达站
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
const TRAIN_API_PATH = '/trainResource';

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
 * 调用火车票专用 API
 * @param {object} params - 查询参数
 * @returns {Promise<object>} - API 响应
 */
function query_train_api(params) {
  return new Promise((resolve, reject) => {
    const api_url = `${API_BASE_URL}${TRAIN_API_PATH}`;
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
 * 格式化火车票结果
 * @param {object} train_data - 火车数据
 * @param {boolean} use_table - 是否使用表格格式
 * @param {boolean} use_plain_link - 是否使用纯文本链接
 * @returns {string} - 格式化输出
 */
function format_train_result(train_data, use_table = false, use_plain_link = false) {
  if (!train_data || !train_data.trainList) {
    return '未找到相关火车票信息';
  }
  
  const trains = train_data.trainList;
  let output = '🚄 火车票查询结果：\n\n';
  
  if (use_table) {
    // 表格格式
    output += '| 车次 | 出发站 | 到达站 | 出发时间 | 到达时间 | 运行时长 | 最低价 | 余票 | PC 预订 | 手机预订 |\n';
    output += '|------|--------|--------|---------|---------|---------|--------|------|--------|---------|\n';
    
    trains.forEach((train) => {
      const train_no = train.trainType === 'GD' ? `🚅 ${train.trainNo}` : `🚆 ${train.trainNo}`;
      const dep_station = train.depStationName || '-';
      const arr_station = train.arrStationName || '-';
      const dep_time = train.depTime || '-';
      const arr_time = train.arrTime || '-';
      const run_time = train.runTime || '-';
      const price = train.price ? `¥${train.price}` : '暂无价格';
      
      let ticket_info = '查询中';
      if (train.ticketList && train.ticketList.length > 0) {
        const available_tickets = train.ticketList.filter(t => parseInt(t.ticketLeft) > 0);
        if (available_tickets.length > 0) {
          ticket_info = available_tickets.map(t => `${t.ticketType}(${t.ticketLeft})`).join(', ');
        } else {
          ticket_info = '售罄';
        }
      }
      
      const pc_link = train.pcRedirectUrl || train.clawRedirectUrl || train.redirectUrl || '#';
      const mobile_link = train.clawRedirectUrl || train.redirectUrl || '#';
      
      let pc_link_md, mobile_link_md;
      if (use_plain_link) {
        pc_link_md = pc_link !== '#' ? pc_link : '暂不可用';
        mobile_link_md = mobile_link !== '#' ? mobile_link : '暂不可用';
      } else {
        pc_link_md = pc_link !== '#' ? `[PC 端](${pc_link})` : '暂不可用';
        mobile_link_md = mobile_link !== '#' ? `[手机端](${mobile_link})` : '暂不可用';
      }
      
      output += `| ${train_no} | ${dep_station} | ${arr_station} | ${dep_time} | ${arr_time} | ${run_time} | ${price} | ${ticket_info} | ${pc_link_md} | ${mobile_link_md} |\n`;
    });
  } else {
    // 卡片格式
    trains.forEach((train) => {
      const train_no = train.trainType === 'GD' ? `🚅 ${train.trainNo}` : `🚆 ${train.trainNo}`;
      const dep_station = train.depStationName || '-';
      const arr_station = train.arrStationName || '-';
      const dep_time = train.depTime || '-';
      const arr_time = train.arrTime || '-';
      const run_time = train.runTime || '-';
      const price = train.price ? `¥${train.price}` : '暂无价格';
      
      let ticket_info = '';
      if (train.ticketList && train.ticketList.length > 0) {
        const available_tickets = train.ticketList.filter(t => parseInt(t.ticketLeft) > 0);
        if (available_tickets.length > 0) {
          ticket_info = available_tickets.map(t => `${t.ticketType}(${t.ticketLeft})`).join(', ');
        } else {
          ticket_info = '售罄';
        }
      }
      
      const pc_link = train.pcRedirectUrl || train.clawRedirectUrl || train.redirectUrl || '#';
      const mobile_link = train.clawRedirectUrl || train.redirectUrl || '#';
      
      let pc_link_md, mobile_link_md;
      if (use_plain_link) {
        pc_link_md = pc_link !== '#' ? `PC 端：${pc_link}` : '暂不可用';
        mobile_link_md = mobile_link !== '#' ? `手机端：${mobile_link}` : '暂不可用';
      } else {
        pc_link_md = pc_link !== '#' ? `[PC 端](${pc_link})` : '暂不可用';
        mobile_link_md = mobile_link !== '#' ? `[手机端](${mobile_link})` : '暂不可用';
      }
      
      output += `### ${train_no} | ${dep_station} → ${arr_station}\n`;
      output += `**出发时间** ${dep_time} | **到达时间** ${arr_time} | **时长** ${run_time}\n`;
      output += `**最低价** ${price}\n`;
      if (ticket_info) output += `**余票** ${ticket_info}\n`;
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
    departureStation: '',
    arrivalStation: '',
    trainNumber: '',
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
    } else if (arg === '--departure-station' && args[i + 1]) {
      params.departureStation = args[++i];
    } else if (arg === '--arrival-station' && args[i + 1]) {
      params.arrivalStation = args[++i];
    } else if (arg === '--train-number' && args[i + 1]) {
      params.trainNumber = args[++i];
    } else if (arg === '--extra' && args[i + 1]) {
      params.extra = args[++i];
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
 * @returns {object} - { valid: boolean, error: string }
 */
function validate_params(params) {
  const has_departure_dest = params.departure && params.destination;
  const has_train_number = params.trainNumber;
  const has_stations = params.departureStation && params.arrivalStation;
  
  if (has_departure_dest || has_train_number || has_stations) {
    return { valid: true };
  }
  
  // 检查部分参数
  const has_partial = params.departure || params.destination || 
                      params.departureStation || params.arrivalStation;
  
  if (has_partial) {
    let error = '⚠️ 参数不完整，请提供以下组合之一：\n';
    error += '  1. 出发地 + 目的地（--departure "北京" --destination "上海"）\n';
    error += '  2. 车次号（--train-number "G1234"）\n';
    error += '  3. 出发站 + 到达站（--departure-station "北京南站" --arrival-station "上海虹桥站"）';
    return { valid: false, error };
  }
  
  return { valid: false, error: '请提供查询参数' };
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
    console.log('  node train-query.js --departure "北京" --destination "上海"');
    console.log('  node train-query.js --train-number "G1234"');
    console.log('  node train-query.js --departure-station "北京南站" --arrival-station "上海虹桥站"');
    console.log('  node train-query.js --departure "北京" --destination "上海" --extra "明天 高铁"');
    console.log('\n参数说明：');
    console.log('  --departure <城市>        出发地城市');
    console.log('  --destination <城市>      目的地城市');
    console.log('  --departure-station <站>  出发站');
    console.log('  --arrival-station <站>    到达站');
    console.log('  --train-number <车次>     车次号');
    console.log('  --extra <补充信息>        额外信息（日期、偏好等）');
    console.log('  --channel <渠道>          通信渠道（webchat/wechat等）');
    console.log('  --surface <界面>          交互界面（mobile/desktop）');
    console.log('\n' + validation.error);
    process.exit(1);
  }
  
  // 构建请求参数（只包含非空字段）
  const request_params = {};
  if (params.departure) request_params.departure = params.departure;
  if (params.destination) request_params.destination = params.destination;
  if (params.departureStation) request_params.departureStation = params.departureStation;
  if (params.arrivalStation) request_params.arrivalStation = params.arrivalStation;
  if (params.trainNumber) request_params.trainNumber = params.trainNumber;
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
  console.log('🔍 火车票专用查询');
  console.log(`📤 请求参数：${JSON.stringify(request_params, null, 2)}`);
  console.log(`📡 渠道：${params.channel || '默认'}`);
  console.log(`📱 界面：${params.surface || '默认'}`);
  console.log(`📊 格式：${use_table ? '表格' : '卡片'} | 链接：${use_plain_link ? '纯文本' : 'Markdown'}`);
  console.log('---\n');
  
  try {
    const result = await query_train_api(request_params);
    
    if (result.code === '0' || result.code === 0) {
      console.log('✅ 查询成功\n');
      
      const response_data = result.data?.data || result.data;
      
      // 新结构：trainDataList 是数组，每个元素包含 pageDataList, trainList, desc
      // 旧结构：trainData 是单个对象
      const trainDataList = response_data?.trainDataList;
      const trainData = response_data?.trainData;
      
      if (Array.isArray(trainDataList) && trainDataList.length > 0) {
        // 新结构：遍历所有列表，每个列表都有 desc 说明
        let hasOutput = false;
        trainDataList.forEach((item, index) => {
          if (item.trainList && item.trainList.length > 0) {
            // 输出列表说明（desc）
            if (item.desc) {
              console.log(`📌 ${item.desc}\n`);
            } else if (trainDataList.length > 1) {
              console.log(`📌 列表 ${index + 1}\n`);
            }
            console.log(format_train_result(item, use_table, use_plain_link));
            hasOutput = true;
          }
        });
        if (!hasOutput) {
          console.log('⚠️ 无结果');
          console.log('未找到符合条件的火车票，请尝试调整查询条件。');
        }
      } else if (trainData) {
        // 旧结构：单个对象
        console.log(format_train_result(trainData, use_table, use_plain_link));
      } else {
        console.log('⚠️ 无结果');
        console.log('未找到符合条件的火车票，请尝试调整查询条件。');
      }
    } else if (result.code === '1') {
      console.log('⚠️ 无结果');
      console.log('未找到符合条件的火车票，请尝试调整查询条件。');
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
  query_train_api,
  validate_params,
  format_train_result
};

// 运行主函数
if (require.main === module) {
  main();
}
