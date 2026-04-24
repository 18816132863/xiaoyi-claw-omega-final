// ==================== get_devices_info 子技能 ====================
// 功能：获取设备基础信息
import path from 'path';
import { fileURLToPath } from 'url';
import { hagSkillServicePost, saveDataToTxt, generateTraceId } from '../../utils/hag-connect/utils.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEVICE_INFO_DIR = path.join(__dirname, '../out_put/get_devices_info');
const DEVICE_INFO_TXT = path.join(DEVICE_INFO_DIR, 'devices_info.txt');

/**
 * 获取设备基础信息
 */
export async function getDevicesInfo(verbose = false) {
  const traceId = generateTraceId();
  process.stderr.write(`[trace-id] ${traceId}\n`);
  
  if (verbose) console.error('[verbose] 开始获取设备基础信息');
  
  try {
    // HAG 请求：{"type": "getCustomData"}
    const deviceResp = await hagSkillServicePost('getCustomData', {}, verbose);
    
    // 解析响应（hag 返回格式：{"errorCode":"0","errorMsg":"success","data":{...}}）
    // data 字段包含设备列表
    const rawData = deviceResp?.data;
    if (!rawData) {
      throw new Error('设备API返回了无效的数据结构');
    }
    
    const rawDevices = Array.isArray(rawData) ? rawData : (rawData.devices || []);
    const homes = rawData.homes;
    const homeDict = {};
    for (const home of homes) {
      homeDict[home.homeId] = home.homeName;
    }
    if (!Array.isArray(rawDevices)) {
      throw new Error('设备数据不是数组格式');
    }
    
     const deviceList = rawDevices.map((item, index) => {
       // 验证每个设备对象的基本结构
       if (!item || typeof item !== 'object') {
         console.warn(`[warning] 设备数据索引${index}不是有效对象，跳过`);
         return null;
       }
       
       const prodId = item.capabilityId || '';
       
       // 过滤虚拟设备：prodId 为 'ZG28' 或 'ZG29' 的设备不会返回给用户
       if (prodId === 'ZG28' || prodId === 'ZG29') {
         if (verbose) {
           console.error(`[filter] 已过滤虚拟设备: ${item.devName} (prodId: ${prodId})`);
         }
         return null;
       }
       // 过滤子系统设备
       if (item.resourceType==='subSystem'){
         return null;
       }
       return {
         deviceId: item.devId || '',
         deviceName: item.devName || '',
         roomName: item.roomName || '未分类',
         homeId: item.homeId || '',
         homeName: homeDict[item.homeId] || '',
         productName: item.deviceTypeName|| '',
         deviceType: item.devType || '',
         prodId: item.capabilityId || ''
       };
     }).filter(Boolean); // 过滤掉无效设备    
    saveDataToTxt(DEVICE_INFO_TXT, deviceList, '设备信息');
    
    if (verbose) console.error(`[verbose] 获取到 ${deviceList.length} 个设备`);
    
    return { traceId, totalDevices: deviceList.length, devices: deviceList };
    
  } catch (apiError) {
    console.error(`[error] 获取设备信息失败: ${apiError.message}`);
    throw apiError;
  }
}
