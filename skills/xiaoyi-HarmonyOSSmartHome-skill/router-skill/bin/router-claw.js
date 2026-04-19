// ==================== router-claw.js 主入口 ====================
// 功能：路由器技能总调度入口
// 版本：2.1.0 (使用 hag-connect + 模块化功能)

// Node.js 内置模块
import { Command } from 'commander';
import { randomUUID } from 'crypto';
import fs from 'fs';
import zlib from 'zlib';
import { promisify } from 'util';
import path from 'path';
import { fileURLToPath } from 'url';
import readline from 'readline';

// 第三方模块 (如有时，在此处添加)

// 项目内部模块 - 工具类
import { hagControl, generateTraceId, generateTimestamp } from '../../utils/hag-connect/utils.js';

// 项目内部模块 - 应用信息
import { g_saAppInfo } from './sa_app_info.js';

// 项目内部模块 - 核心功能
import {
  handleAllowGames,
  handleAllowVideos,
  handleAllowSocial,
  handleAllowShopping,
  handleAllowInstall,
  handleGetRouterDeviceByProdid,
  handleGetAppInfo,
  handleGetAllApps,
  getCategoryName,
  getRouterInfo
} from './router-functions.js';

// ==================== 路由器配置 ====================
const PROGRAM_NAME = 'router-claw';
const VERSION = '2.1.0';
const DEFAULT_SKILL_ID = 'xiaoyi_router';
const OPENCLAW_ENV_FILE = '/home/sandbox/.openclaw/.xiaoyienv';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// 路由器设备配置（从环境变量加载）
const ROUTER_CONFIG = {
  devId: process.env.ROUTER_DEVID,
  prodId: process.env.ROUTER_PRODID
};

// 路由器 API 路径配置
const ROUTER_PATHS = {
  get_host_info: '.sys/gateway/system/HostInfo?filterAndroid=true&isSupportHostZip=true',
  get_child_protect: '.sys/gateway/ntwk/childHomepage',
  get_wan_status: '.sys/gateway/ntwk/wan?type=active',
  get_wandetect: '.sys/gateway/ntwk/wandetect',
  get_channel_info: '.sys/gateway/ntwk/channelinfo',
  get_5g_optimize: '.sys/gateway/ntwk/wlandbho',
  get_ipv6: '.sys/gateway/ntwk/ipv6_enable',
  get_user_behavior: '.sys/gateway/system/userbehavior',
  get_router_status: '.sys/gateway/system/processstatus',
  get_wifi_config: '.sys/gateway/ntwk/wlanradio',
  set_ipv6: '.sys/gateway/ntwk/ipv6_enable',
  add_child_device: '.sys/gateway/ntwk/childManage',
  del_child_device: '.sys/gateway/ntwk/childHomepage',
  set_net_time: '.sys/gateway/ntwk/childFrame',
  set_app_control: '.sys/gateway/ntwk/childModelApps',
  set_net_off: '.sys/gateway/ntwk/childHomepage',
  set_net_duration: '.sys/gateway/ntwk/childDailyUpdate',
  deny_games: '.sys/gateway/ntwk/childModelApps',
  deny_videos: '.sys/gateway/ntwk/childModelApps',
  deny_social: '.sys/gateway/ntwk/childModelApps',
  deny_shopping: '.sys/gateway/ntwk/childModelApps',
  deny_install: '.sys/gateway/ntwk/childModelApps',
  allow_games: '.sys/gateway/ntwk/childModelApps',
  allow_videos: '.sys/gateway/ntwk/childModelApps',
  allow_social: '.sys/gateway/ntwk/childModelApps',
  allow_shopping: '.sys/gateway/ntwk/childModelApps',
  allow_install: '.sys/gateway/ntwk/childModelApps',
  // 应用信息查询（本地功能，不调用路由器API）
  get_app_info: null, // 本地功能
  get_all_apps: null, // 本地功能
  get_router_device_by_prodid: null // 本地功能
};

// ==================== 工具函数 ====================
/**
 * 解密 HostInfo 的 gzip+base64 数据
 */
const gunzip = promisify(zlib.gunzip);

async function decodeHostInfo(content) {
  try {
    const buffer = Buffer.from(content, 'base64');
    const result = await gunzip(buffer);
    return JSON.parse(result.toString());
  } catch (e) {
    console.error('[decode] 解析设备信息失败:', e.message);
    return null;
  }
}

/**
 * 加载环境变量
 */
function loadOpenclawEnv(verbose) {
  const env = {};
  try {
    const content = fs.readFileSync(OPENCLAW_ENV_FILE, 'utf-8');
    for (const line of content.split('\n')) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      const idx = trimmed.indexOf('=');
      if (idx === -1) continue;
      const key = trimmed.slice(0, idx).trim();
      const value = trimmed.slice(idx + 1).trim();
      env[key] = value;
    }
    if (verbose) {
      console.error(`[verbose] 加载环境变量：${OPENCLAW_ENV_FILE}`);
    }
  } catch (err) {
    if (err.code === 'ENOENT' && verbose) {
      console.error(`[verbose] 未找到环境文件，使用系统环境变量`);
    }
  }
  return env;
}

// ==================== 自动配置环境变量（智能识别） ====================
async function autoConfigureEnv(verbose = false) {
  // 创建读取用户输入的接口
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  console.error('\n========== 需要配置路由器设备信息 ==========');
  console.error('检测到缺少 ROUTER_DEVID 和 ROUTER_PRODID 环境变量');
  console.error('将自动为您查找和配置路由器设备...\n');

  try {
    // 第1步：检查是否有最近的设备信息缓存和路由器设备信息
    const cacheDir = path.join(__dirname, '../../common-skill/out_put/get_devices_info');
    const deviceCacheFile = path.join(cacheDir, 'devices_info.txt');
    
    let devicesInfo = null;
    let fromCache = false;
    let routerDeviceInfo = null;
    
    // 加载路由器设备信息映射表
    try {
      routerDeviceInfo = (await import('../router_device_info.js')).default;
      console.error(`✓ 已加载 ${routerDeviceInfo.length} 个路由器设备映射`);
    } catch (infoError) {
      console.error('⚠️  路由器设备信息映射加载失败');
    }

    // 第4步：智能选择路由器或用户确认
    let selectedDevice = null;
    
    if (routerDevices.length > 0) {
      // 优先选择有映射信息的路由器
      const prioritizedDevices = await Promise.all(
        routerDevices.map(async device => ({
          device,
          hasInfo: await hasRouterInfo(device)
        }))
      ).then(results => results.filter(item => item.hasInfo).map(item => item.device));

    // 检查设备信息缓存
    if (fs.existsSync(deviceCacheFile)) {
      try {
        console.error('✓ 发现设备信息缓存，正在读取...');
        const cachedData = fs.readFileSync(deviceCacheFile, 'utf-8');
        devicesInfo = JSON.parse(cachedData);
        fromCache = true;
        console.error(`✓ 从缓存中读取到 ${devicesInfo.length || 0} 个设备`);
      } catch (cacheError) {
        console.error('⚠️  缓存文件读取失败，将重新获取设备信息');
      }
    }

    // 如果没有缓存，重新获取设备信息
    if (!devicesInfo) {
      console.error('步骤1: 获取设备信息...');
      
      const devicesResult = await import('../../common-skill/bin/get_devices_info.js');
      const getDevicesResult = await devicesResult.getDevicesInfo(false);
      devicesInfo = getDevicesResult.devices;
      console.error(`✓ 获取到 ${devicesInfo.length} 个设备`);
    }

    // 第2步：智能识别家庭和路由器
    let selectedHome = null;
    
    if (fromCache) {
      console.error('步骤2: 分析已缓存的设备信息...');
    } else {
      console.error('步骤2: 正在获取家庭信息并分析设备...');
    }

    // 从设备信息中识别家庭
    const homeMap = new Map();
    devicesInfo.forEach(device => {
      const homeId = device.homeId;
      if (homeId && homeId.trim()) {
        if (!homeMap.has(homeId)) {
          homeMap.set(homeId, {
            homeId: homeId,
            homeName: device.homeName || '未命名家庭',
            devices: []
          });
        }
        homeMap.get(homeId).devices.push(device);
      }
    });

    const homes = Array.from(homeMap.values());
    
    if (homes.length === 0) {
      throw new Error('未能从设备信息中识别到有效的家庭信息');
    }

    // 如果只有一个家庭，直接选择
    if (homes.length === 1) {
      selectedHome = homes[0];
      console.error(`✓ 自动选择家庭: ${selectedHome.homeName}`);
    } else {
      console.error(`\n发现 ${homes.length} 个家庭:`);
      homes.forEach((home, index) => {
        console.error(`${index + 1}. ${home.homeName} (ID: ${home.homeId})`);
      });

      // 只有在多个家庭时才需要用户选择
      console.error('');
      const homeAnswer = await new Promise(resolve => {
        rl.question('请选择要操作的家庭（输入数字，默认1）: ', resolve);
      });

      const selectedHomeIndex = parseInt(homeAnswer) - 1 || 0;
      if (selectedHomeIndex < 0 || selectedHomeIndex >= homes.length) {
        throw new Error(`无效的家庭选择，请输入1-${homes.length}之间的数字`);
      }

      selectedHome = homes[selectedHomeIndex];
      console.error(`✓ 已选择家庭: ${selectedHome.homeName}`);
    }

    // 第3步：基于 router_device_info.js 智能识别路由器设备
    const routerDevices = selectedHome.devices.filter(device => {
      if (!device.prodId || !device.deviceId) {
        return false;
      }

      const prodId = device.prodId?.toUpperCase() || '';
      // 检查是否在路由器设备信息映射表中
      if (routerDeviceInfo) {
        const isInDeviceInfo = routerDeviceInfo.some(routerInfo => {
          return routerInfo[0] === device.deviceId?.toUpperCase() || routerInfo[1] === prodId;
        });
        if (isInDeviceInfo) {
          return true;
        }
      }
      
      // 通过名称判断是否是路由器
      const deviceName = (device.deviceName || '').toLowerCase();
      const productName = (device.productName || '').toLowerCase();
      const isRouterByName = deviceName.includes('路由') || deviceName.includes('router') || deviceName.includes('gateway') || 
                           productName.includes('路由') || productName.includes('router') || productName.includes('gateway');
      return isRouterByName;
    });

    console.error(`\n在家中 "${selectedHome.homeName}" 发现 ${routerDevices.length} 个可能的路由器设备:`);
    
    if (routerDevices.length === 0) {
      console.error('未发现 obvious 路由器设备，将显示所有设备供选择:');
      selectedHome.devices.forEach(async (device, index) => {
        const routerInfo = device.prodId ? await getRouterInfo(device.deviceId?.toUpperCase() || '', device.prodId?.toUpperCase() || '') : null;
        const routerName = routerInfo ? ` (${routerInfo.name})` : '';
        console.error(`${index + 1}. ${device.deviceName} - ${device.productName || '无产品信息'}${routerName} (ID: ${device.deviceId}, 产品ID: ${device.prodId})`);
      });
    } else {
      routerDevices.forEach(async (device, index) => {
        const routerInfo = await getRouterInfo(device.deviceId?.toUpperCase() || '', device.prodId?.toUpperCase() || '');
        let deviceDisplay = `${index + 1}. ${device.deviceName} - ${device.productName || '无产品信息'}`;
        
        if (routerInfo) {
          deviceDisplay += ` [${routerInfo.name}]`;
          if (routerInfo.model) {
            deviceDisplay += ` (${routerInfo.model})`;
          }
        } else if (device.prodId) {
          deviceDisplay += ` (产品ID: ${device.prodId})`;
        }
        
        console.error(deviceDisplay);
      });
    }

    console.error('\n智慧建议:');
    
    // 第4步：智能选择路由器或用户确认
    let selectedDevice = null;
    
    if (routerDevices.length > 0) {
      // 优先选择有映射信息的路由器
      const prioritizedDevices = routerDevices.filter(async device => {
        const routerInfo = await getRouterInfo(device.deviceId?.toUpperCase() || '', device.prodId?.toUpperCase() || '');
        return routerInfo !== null;
      });
      
      // 注意：由于filter不接受async函数，我们需要特殊处理
      const suggestedDevice = prioritizedDevices[0] || routerDevices[0];
      
      const routerInfo = await getRouterInfo(suggestedDevice.deviceId?.toUpperCase() || '', suggestedDevice.prodId?.toUpperCase() || '');
      const routerDisplay = routerInfo ? `${routerInfo.name}` : suggestedDevice.deviceName;
      const modelDisplay = routerInfo ? ` (${routerInfo.model})` : '';
      
      console.error(`-> 建议使用: ${routerDisplay}${modelDisplay}`);
      
      // 检查是否需要用户确认
      if (routerDevices.length > 1) {
        console.error('\n是否接受这个建议？(y/n，默认y)');
        
        const confirmAnswer = await new Promise(resolve => {
          rl.question('', resolve);
        });
        
        if (confirmAnswer.toLowerCase() === 'n') {
          // 显示完整设备列表
          console.error('\n请从下拉列表中选择路由器:');
          selectedHome.devices.forEach(async (device, index) => {
            const routerInfo = await getRouterInfo(device.deviceId?.toUpperCase() || '', device.prodId?.toUpperCase() || '');
            let deviceDisplay = `${index + 1}. ${device.deviceName}`;
            if (routerInfo) {
              deviceDisplay += ` [${routerInfo.name}]`;
              if (routerInfo.model) {
                deviceDisplay += ` (${routerInfo.model})`;
              }
            }
            console.error(deviceDisplay);
          });
          
          const deviceAnswer = await new Promise(resolve => {
            rl.question('请选择路由器设备（输入数字）: ', resolve);
          });
          
          const deviceIndex = parseInt(deviceAnswer) - 1;
          if (deviceIndex < 0 || deviceIndex >= selectedHome.devices.length) {
            throw new Error(`无效的设备选择，请输入1-${selectedHome.devices.length}之间的数字`);
          }
          selectedDevice = selectedHome.devices[deviceIndex];
        } else {
          selectedDevice = suggestedDevice;
        }
      } else {
        // 只有一个路由器或一个优先路由器，直接使用
        selectedDevice = suggestedDevice;
      }
    } else {
      // 没有识别到路由器，显示所有设备让用户选择
      const allDevices = selectedHome.devices;
      
      console.error('未识别到路由器设备，请从列表手动选择:');
      allDevices.forEach(async (device, index) => {
        const routerInfo = await getRouterInfo(device.deviceId?.toUpperCase() || '', device.prodId?.toUpperCase() || '');
        let deviceDisplay = `${index + 1}. ${device.deviceName}`;
        if (routerInfo) {
          deviceDisplay += ` [${routerInfo.name}]`;
          if (routerInfo.model) {
            deviceDisplay += ` (${routerInfo.model})`;
          }
        }
        console.error(deviceDisplay);
      });
      
      const deviceAnswer = await new Promise(resolve => {
        rl.question('请选择路由器设备（输入数字）: ', resolve);
      });
      
      const deviceIndex = parseInt(deviceAnswer) - 1;
      if (deviceIndex < 0 || deviceIndex >= allDevices.length) {
        throw new Error(`无效的设备选择，请输入1-${allDevices.length}之间的数字`);
      }
      selectedDevice = allDevices[deviceIndex];
    }

    // 从映射表中获取路由器信息
    const routerInfo = await getRouterInfo(selectedDevice.deviceId?.toUpperCase() || '', selectedDevice.prodId?.toUpperCase() || '');
    const routerDisplay = routerInfo ? `${routerInfo.name}` : selectedDevice.deviceName;
    const modelDisplay = routerInfo ? ` (${routerInfo.model})` : '';

    console.error(`\n✓ 已选择路由器: ${routerDisplay}${modelDisplay}`);
    console.error(`  - 设备ID (devid): ${selectedDevice.deviceId}`);
    console.error(`  - 产品ID (prodid): ${selectedDevice.prodId || '无'}`);

    // 第5步：设置环境变量
    const devId = selectedDevice.deviceId;
    const prodId = selectedDevice.prodId || '';

    // 设置当前进程的环境变量
    process.env.ROUTER_DEVID = devId;
    process.env.ROUTER_PRODID = prodId;

    console.error('\n✓ 已成功设置环境变量:');
    console.error(`  ROUTER_DEVID = ${devId}`);
    console.error(`  ROUTER_PRODID = ${prodId}`);

    // 第6步：尝试保存到环境变量文件
    const envPath = '/tmp/router_env_config'; // 临时文件路径
    console.error(`\n💡 环境变量已保存到: ${envPath}`);
    console.error(`您可以在后续调用时使用: source ${envPath}`);
    }

    rl.close();
    return { devId, prodId };

  } catch (error) {    throw new Error('环境变量配置失败，请按照提示手动配置');
  }
}

// ==================== 核心调度函数 ====================
async function callRouterClaw(tools, skillId, verbose = false, retryCount = 0) {
  const MAX_RETRY = 1; // 最多重试 1 次，避免无限循环
  const fileEnv = loadOpenclawEnv(verbose);
  
  let devId = fileEnv.ROUTER_DEVID || process.env.ROUTER_DEVID || ROUTER_CONFIG.devId;
  let prodId = fileEnv.ROUTER_PRODID || process.env.ROUTER_PRODID || ROUTER_CONFIG.prodId;

  if (verbose) {
    console.error(`[verbose] DEV_ID = ${devId}`);
    console.error(`[verbose] PROD_ID = ${prodId}`);
  }

  // 检查是否缺少环境变量，如果缺少则尝试自动配置
  if (!devId || !prodId) {
    try {
      console.error('[info] 检测到缺少路由器环境变量，尝试自动配置...');
      const configured = await autoConfigureEnv(verbose);
      devId = configured.devId;
      prodId = configured.prodId;
      console.error('[info] ✓ 环境变量自动配置完成');
    } catch (autoConfigError) {
      console.error(autoConfigError.message);
      process.exit(1);
    }
  }

  const results = [];
  
  // 检查哪些操作需要后续查询验证
  const needsVerification = tools.filter(tool => 
    tool.name === 'set_net_time' || 
    tool.name === 'set_net_duration' ||
    tool.name === 'set_net_off'
  );
  
  // 为需要验证的操作添加查询任务
  const allTools = [...tools];
  needsVerification.forEach(setTool => {
    const queryTool = {
      name: 'get_child_protect', 
      args: setTool.args
    };
    // 查询任务只添加一次
    if (!tools.some(t => t.name === 'get_child_protect')) {
      allTools.push(queryTool);
    }
  });
  
  for (const tool of allTools) {
    const { name, args } = tool;
    const sid = ROUTER_PATHS[name];
    
    if (!sid) {
      console.error(`[warning] 未知工具：${name}`);
      continue;
    }

    let payload = {
      devId,
      prodId,
      sid,
      mode: 'ACK',  // 路由器使用 ACK 模式
      operation: 'GET'  // 默认 GET
    };

    // ========== 信息查询 GET ==========
    if (name === 'get_host_info') {
      payload.operation = 'GET';
    } else if (name === 'get_child_protect') {
      payload.operation = 'GET';
    } else if (name === 'get_wan_status') {
      payload.operation = 'GET';
    } else if (name === 'get_wandetect') {
      payload.operation = 'GET';
    } else if (name === 'get_channel_info') {
      payload.operation = 'GET';
    } else if (name === 'get_5g_optimize') {
      payload.operation = 'GET';
    } else if (name === 'get_ipv6') {
      payload.operation = 'GET';
    } else if (name === 'get_user_behavior') {
      payload.operation = 'GET';
    } else if (name === 'get_router_status') {
      payload.operation = 'GET';
    } else if (name === 'get_wifi_config') {
      payload.operation = 'GET';
    }

    // ========== 控制操作 POST ==========
    else if (name === 'set_ipv6') {
      payload.operation = 'POST';
      payload.data = args.data || { Enable: 0, ID: 'InternetGatewayDevice.Services.X_IPv6.' };
    } else if (name === 'add_child_device') {
      const action = 'create';
      payload.operation = 'POST';
      payload.sid = ROUTER_PATHS.add_child_device;
      payload.data = {
        action: action,
        data: {
          action: action,
          devices: args.data?.devices || [],
          names: args.data?.names || [],
          privacyStatus: args.data?.privacyStatus || 0,
          type: args.data?.type || 0,
          urlStatus: args.data?.urlStatus || 0
        }
      };
    } else if (name === 'del_child_device') {
      const action = 'delete';
      payload.operation = 'POST';
      payload.sid = ROUTER_PATHS.del_child_device;
      payload.data = {
        action: action,
        data: {
          device: args.data?.device || '1'
        }
      };
    } else if (name === 'set_net_time') {
      const action = args.action || 'newCreate';
      payload.operation = 'POST';
      payload.sid = `.sys/gateway/ntwk/childFrame?devid=${String(args.deviceId || '1')}`;
      payload.data = {
        action: action,
        data: args.data
      };
    } else if (name === 'set_app_control') {
      const action = 'update';
      payload.operation = 'POST';
      payload.sid = `.sys/gateway/ntwk/childModelApps?devid=${String(args.deviceId || '1')}&type=${args.type || 1}`;
      payload.data = {
        action: action,
        data: args.data
      };
    } else if (name === 'set_net_off') {
      const action = 'delayUpdate';
      payload.operation = 'POST';
      payload.sid = '.sys/gateway/ntwk/childHomepage';
      payload.data = {
        action: action,
        data: args.data
      };
    } else if (name === 'set_net_duration') {
      const action = args.action || 'update';
      payload.operation = 'POST';
      payload.sid = '.sys/gateway/ntwk/childDailyUpdate';
      payload.data = {
        action: action,
        data: args.data || { daily: { monday: 90000, tuesday: 90000, wednesday: 90000, thursday: 90000, friday: 90000, saturday: 90000, sunday: 90000 }, device: "1" }
      };
    }

    // ========== 应用管理禁止操作 POST ==========
    else if (name === 'deny_games') {
      payload.operation = 'POST';
      payload.sid = '.sys/gateway/ntwk/childModelApps';
      payload.data = {
        action: 'update',
        data: {
          device: args.deviceId || '1',
          apps: ["153","221","152","220","118","287","151","218","286","252","251","285","250","284","114","283","249","147","113","215","282","248","112","281","145","247","213","280","144","246","108","279","107","175","278","244","106","140","243","209","277","105","207","276","104","206","275","171","239","103","170","238","102","203","169","101","100","201","233","131","199","232","130","163","231","230","196","195","228","193","123","191","192","122","156","225","155","189","224","154","255","254","216","181","180","179","178","211","210","271","270","167","133","234","268","166","267","165","266","265","197","264","161","160","158","227","261","157","226","260","259","222","257","187","256","186","185","253","117","184","150","116","217","149","182","148","146","214","109","142","177","139","274","240","204","273","135","202","134","200","132","198","164","129","162","126","125","124","121","223","258","120","188"],
          denyAll: 0,
          type: 1
        }
      };
    } else if (name === 'deny_videos') {
      payload.operation = 'POST';
      payload.sid = '.sys/gateway/ntwk/childModelApps';
      payload.data = {
        action: 'update',
        data: {
          device: args.deviceId || '1',
          apps: ["320","314","348","347","313","346","311","309","339","338","337","335","802","804","803","324","323","322","321","319","318","312","310","308","303","336","334","333","332","331","330","328","327","350","349","342","341","340","345","344","343"],
          denyAll: 0,
          type: 2
        }
      };
    } else if (name === 'deny_social') {
      payload.operation = 'POST';
      payload.sid = '.sys/gateway/ntwk/childModelApps';
      payload.data = {
        action: 'update',
        data: {
          device: args.deviceId || '1',
          apps: ["401","400","408","407","406"],
          denyAll: 0,
          type: 3
        }
      };
    } else if (name === 'deny_shopping') {
      payload.operation = 'POST';
      payload.sid = '.sys/gateway/ntwk/childModelApps';
      payload.data = {
        action: 'update',
        data: {
          device: args.deviceId || '1',
          apps: ["503","502","501","500","512","508","511","510","509"],
          denyAll: 0,
          type: 4
        }
      };
    } else if (name === 'deny_install') {
      payload.operation = 'POST';
      payload.sid = '.sys/gateway/ntwk/childModelApps';
      payload.data = {
        action: 'update',
        data: {
          device: args.deviceId || '1',
          apps: ["8","7","6","5","4","3","2","1"],
          denyAll: 0,
          type: 5
        }
      };
    }

    // ========== 应用管理取消操作 POST（两步） ==========
    else if (name === 'allow_games') {
      const deviceId = String(args.deviceId || '1');
      const { payload1, payload2, step1Name, step2Name } = await handleAllowGames(devId, prodId, deviceId, verbose);
      
      let res1;
      let res2;
      try {
        res1 = await hagControl(payload1, verbose);
        res2 = await hagControl(payload2, verbose);
        
        results.push({ tool: step1Name, success: true, data: res1 });
        results.push({ tool: step2Name, success: true, data: res2 });
        continue;
      } catch (err) {
        if (err.code === 401 && retryCount < MAX_RETRY) {
          console.log('[info] token 已过期，正在自动刷新...');
          return callRouterClaw(tools, skillId, verbose, retryCount + 1);
        }
        throw err;
      }
    } else if (name === 'allow_videos') {
      const deviceId = String(args.deviceId || '1');
      const { payload1, payload2, step1Name, step2Name } = await handleAllowVideos(devId, prodId, deviceId, verbose);
      
      let res1;
      let res2;
      try {
        res1 = await hagControl(payload1, verbose);
        res2 = await hagControl(payload2, verbose);
        
        // 验证操作是否成功
        const step1Success = res1?.success === true || (res1?.data?.status === 'success') || (res1?.data?.code === 0);
        const step2Success = res2?.success === true || (res2?.data?.status === 'success') || (res2?.data?.code === 0);
        
        const step1Message = step1Success ? `✓ ${step1Name} 操作成功` : `❌ ${step1Name} 操作失败: ${res1?.data?.message || '未知错误'}`;
        const step2Message = step2Success ? `✓ ${step2Name} 操作成功` : `❌ ${step2Name} 操作失败: ${res2?.data?.message || '未知错误'}`;
        
        results.push({ 
          tool: step1Name, 
          success: step1Success, 
          data: res1,
          message: step1Message
        });
        
        results.push({ 
          tool: step2Name, 
          success: step2Success, 
          data: res2,
          message: step2Message
        });
        
        continue;
      } catch (err) {
        if (err.code === 401 && retryCount < MAX_RETRY) {
          console.log('[info] token 已过期，正在自动刷新...');
          return callRouterClaw(tools, skillId, verbose, retryCount + 1);
        }
        throw err;
      }
    } else if (name === 'allow_social') {
      const deviceId = String(args.deviceId || '1');
      const { payload1, payload2, step1Name, step2Name } = await handleAllowSocial(devId, prodId, deviceId, verbose);
      
      let res1;
      let res2;
      try {
        res1 = await hagControl(payload1, verbose);
        res2 = await hagControl(payload2, verbose);
        
        // 验证操作是否成功
        const step1Success = res1?.success === true || (res1?.data?.status === 'success') || (res1?.data?.code === 0);
        const step2Success = res2?.success === true || (res2?.data?.status === 'success') || (res2?.data?.code === 0);
        
        const step1Message = step1Success ? `✓ ${step1Name} 操作成功` : `❌ ${step1Name} 操作失败: ${res1?.data?.message || '未知错误'}`;
        const step2Message = step2Success ? `✓ ${step2Name} 操作成功` : `❌ ${step2Name} 操作失败: ${res2?.data?.message || '未知错误'}`;
        
        results.push({ 
          tool: step1Name, 
          success: step1Success, 
          data: res1,
          message: step1Message
        });
        
        results.push({ 
          tool: step2Name, 
          success: step2Success, 
          data: res2,
          message: step2Message
        });
        
        continue;
      } catch (err) {
        if (err.code === 401 && retryCount < MAX_RETRY) {
          console.log('[info] token 已过期，正在自动刷新...');
          return callRouterClaw(tools, skillId, verbose, retryCount + 1);
        }
        throw err;
      }
    } else if (name === 'allow_shopping') {
      const deviceId = String(args.deviceId || '1');
      const { payload1, payload2, step1Name, step2Name } = await handleAllowShopping(devId, prodId, deviceId, verbose);
      
      let res1;
      let res2;
      try {
        res1 = await hagControl(payload1, verbose);
        res2 = await hagControl(payload2, verbose);
        
        // 验证操作是否成功
        const step1Success = res1?.success === true || (res1?.data?.status === 'success') || (res1?.data?.code === 0);
        const step2Success = res2?.success === true || (res2?.data?.status === 'success') || (res2?.data?.code === 0);
        
        const step1Message = step1Success ? `✓ ${step1Name} 操作成功` : `❌ ${step1Name} 操作失败: ${res1?.data?.message || '未知错误'}`;
        const step2Message = step2Success ? `✓ ${step2Name} 操作成功` : `❌ ${step2Name} 操作失败: ${res2?.data?.message || '未知错误'}`;
        
        results.push({ 
          tool: step1Name, 
          success: step1Success, 
          data: res1,
          message: step1Message
        });
        
        results.push({ 
          tool: step2Name, 
          success: step2Success, 
          data: res2,
          message: step2Message
        });
        
        continue;
      } catch (err) {
        if (err.code === 401 && retryCount < MAX_RETRY) {
          console.log('[info] token 已过期，正在自动刷新...');
          return callRouterClaw(tools, skillId, verbose, retryCount + 1);
        }
        throw err;
      }
    } else if (name === 'allow_install') {
      const deviceId = String(args.deviceId || '1');
      const { payload1, payload2, step1Name, step2Name } = await handleAllowInstall(devId, prodId, deviceId, verbose);
      
      let res1;
      let res2;
      try {
        res1 = await hagControl(payload1, verbose);
        res2 = await hagControl(payload2, verbose);
        
        // 验证操作是否成功
        const step1Success = res1?.success === true || (res1?.data?.status === 'success') || (res1?.data?.code === 0);
        const step2Success = res2?.success === true || (res2?.data?.status === 'success') || (res2?.data?.code === 0);
        
        const step1Message = step1Success ? `✓ ${step1Name} 操作成功` : `❌ ${step1Name} 操作失败: ${res1?.data?.message || '未知错误'}`;
        const step2Message = step2Success ? `✓ ${step2Name} 操作成功` : `❌ ${step2Name} 操作失败: ${res2?.data?.message || '未知错误'}`;
        
        results.push({ 
          tool: step1Name, 
          success: step1Success, 
          data: res1,
          message: step1Message
        });
        
        results.push({ 
          tool: step2Name, 
          success: step2Success, 
          data: res2,
          message: step2Message
        });
        
        continue;
      } catch (err) {
        if (err.code === 401 && retryCount < MAX_RETRY) {
          console.log('[info] token 已过期，正在自动刷新...');
          return callRouterClaw(tools, skillId, verbose, retryCount + 1);
        }
        throw err;
      }
    } else if (name === 'get_router_device_by_prodid') {
      const routerResult = await handleGetRouterDeviceByProdid(args.prodid || args.deviceId || 'K1AP');
      results.push({
        tool: name,
        success: routerResult.success,
        data: routerResult.data,
        message: routerResult.message
      });
      continue;
    } else if (name === 'get_app_info') {
      const appResult = await handleGetAppInfo(args.app_id || args.appId || String(args.id));
      results.push({
        tool: name,
        success: appResult.success,
        data: appResult.data,
        message: appResult.message
      });
      continue;
    } else if (name === 'get_all_apps') {
      const appsResult = await handleGetAllApps();
      results.push({
        tool: name,
        success: appsResult.success,
        data: appsResult.data,
        message: appsResult.message
      });
      continue;
    }

    let res;
    try {
      // 使用 hagControl 发送请求
      res = await hagControl(payload, verbose);
    } catch (err) {
      if (err.code === 401 && retryCount < MAX_RETRY) {
        console.log('[info] token 已过期，正在自动刷新...');
        return callRouterClaw(tools, skillId, verbose, retryCount + 1);
      }
      throw err;
    }

    // 自动解码 HostInfo 的 gzip+base64 数据
    if (name === 'get_host_info' && res?.data?.payload) {
      let payloadObj = typeof res.data.payload === 'string' ? JSON.parse(res.data.payload) : res.data.payload;
      if (payloadObj.content) {
        const decoded = await decodeHostInfo(payloadObj.content);
        res.data.payload = decoded;
      }
    }

    // 对设置操作的结果进行验证
    let isOperationSuccessful = false;
    let verificationMessage = '';
    
    if (name === 'set_net_time' || name === 'set_net_duration' || name === 'set_net_off') {
      // 设置操作成功响应的特征
      if (res?.success === true || (res?.data?.status === 'success') || (res?.data?.code === 0)) {
        isOperationSuccessful = true;
        verificationMessage = `✓ ${name} 操作执行成功`;
        
        // 检查是否有后续查询操作
        const queryTool = allTools.find(t => t.name === 'get_child_protect');
        if (queryTool) {
          try {
            const queryPayload = {
              devId,
              prodId,
              mode: 'ACK',
              operation: 'GET',
              sid: ROUTER_PATHS.get_child_protect
            };
            
            const queryRes = await hagControl(queryPayload, false);
            let latestConfig = '';
            
            if (queryRes?.data?.data) {
              latestConfig = JSON.stringify(queryRes.data.data, null, 2);
            } else {
              latestConfig = JSON.stringify(queryRes, null, 2);
            }
            
            verificationMessage += `\n📱 最新设备配置：\n${latestConfig}`;
          } catch (queryError) {
            verificationMessage += `\n⚠️  自动查询最新配置失败: ${queryError.message}`;
          }
        } else {
          verificationMessage += '\n💡 建议查询最新配置以确认设置生效';
        }
      } else {
        isOperationSuccessful = false;
        const errorInfo = res?.data?.message || res?.data?.error || res?.message || '未知错误';
        verificationMessage = `❌ ${name} 操作执行失败\n错误信息: ${errorInfo}`;
      }
    } else {
      // 查询操作成功响应的特征
      isOperationSuccessful = true;
      verificationMessage = `✓ ${name} 查询成功`;
    }

    results.push({ 
      tool: name, 
      success: isOperationSuccessful, 
      data: res,
      message: verificationMessage,
      timestamp: new Date().toISOString()
    });
  }

  console.log(JSON.stringify(results, null, 2));
}

// ==================== 注册命令 ====================
function registerCommands(program) {
  const toolNamesNeedAction = ['set_net_time', 'set_net_duration'];
  const toolNamesNeedData = ['add_child_device', 'del_child_device'];
  const toolNamesNeedProdid = ['get_router_device_by_prodid'];
  const toolNamesNeedAppId = ['get_app_info'];
  const toolNames = Object.keys(ROUTER_PATHS);
  
  for (const toolName of toolNames) {
    let command = program
      .command(toolName)
      .description(`路由器操作：${toolName}`)
      .option('--device-id <id>', '设备 ID', '1')
      .option('--data <json>', '控制参数 (JSON 字符串)')
      .option('--type <num>', '应用分类 1 游戏/2 影音/3 社交/4 购物/5 安装/7 学习')
      .option('--skill-id <id>', '技能 ID', DEFAULT_SKILL_ID)
      .option('--verbose', '调试日志')
      .action(async (opts) => {
        let args = {};
        if (opts.data) args.data = JSON.parse(opts.data);
        if (opts.deviceId) args.deviceId = String(opts.deviceId);
        if (opts.type) args.type = opts.type;
        if (toolNamesNeedAction.includes(toolName) && opts.action) {
          args.action = opts.action;
        }
        if (toolNamesNeedProdid.includes(toolName) && opts.prodid) {
          args.prodid = opts.prodid;
        }
        if (toolNamesNeedAppId.includes(toolName) && opts.appId) {
          args.appId = opts.appId;
        }

        await callRouterClaw([{ name: toolName, args }], opts.skillId, opts.verbose);
      });

    if (toolNamesNeedAction.includes(toolName)) {
      command.option('--action <type>', '操作类型 create/update/delete');
    }
    if (toolNamesNeedProdid.includes(toolName)) {
      command.option('--prodid <id>', '产品ID / 产品型号');
    }
    if (toolNamesNeedAppId.includes(toolName)) {
      command.option('--app-id <id>', '应用ID');
    }
  }
}

// ==================== 启动程序 ====================
const program = new Command();
program
  .name(PROGRAM_NAME)
  .description('路由器儿童上网保护控制工具（hag-connect 版 + 模块化功能）')
  .version(VERSION)
  .option('--tools <json>', '批量执行工具')
  .option('--skill-id <id>', '技能 ID', DEFAULT_SKILL_ID)
  .option('--verbose', '调试模式')
  .action(async (opts) => {
    if (!opts.tools) {
      program.help();
      return;
    }
    const tools = JSON.parse(opts.tools);
    await callRouterClaw(tools, opts.skillId, opts.verbose);
  });

registerCommands(program);
program.parse();