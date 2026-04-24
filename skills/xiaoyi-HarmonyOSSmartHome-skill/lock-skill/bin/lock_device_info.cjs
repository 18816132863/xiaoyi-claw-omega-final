// ==================== 门锁设备能力映射 ====================
// 用于根据产品ID(PID)识别门锁支持的功能能力
// 配置从 lock_device_capabilities.json 加载，便于维护
// 自动生成，请勿手动修改
// 生成时间: 2026-04-16

const path = require('path');
const fs = require('fs');

// 配置文件路径
const CONFIG_FILE = path.join(__dirname, 'lock_device_capabilities.json');

// 能力标识与中文名称映射（模块级常量）
const FEATURE_NAMES = {
  'securitySetting:face': '人脸识别',
  'securitySetting:palm': '掌静脉识别',
  'fingerprint': '指纹',
  'nfc': 'NFC',
  'password': '密码',
  'card': '门卡',
  'catEyeSetting': '猫眼/视频',
  'greeting': '留言功能',
  'weather': '天气提醒',
  'familyCare': '回家提醒',
  'remoteUnlock': '远程开锁',
  'creativeDoorbell': '创意门铃',
  'multimedia': '多媒体',
  'wifi': 'WiFi'
};

/**
 * 获取默认的全功能能力集（用于未匹配的PID）
 * @returns {Object} 所有功能默认开启的能力对象
 */
function getDefaultCapabilities() {
  const capabilities = {};
  for (const key of Object.keys(FEATURE_NAMES)) {
    capabilities[key] = true;
  }
  return capabilities;
}

/**
 * 加载设备能力配置
 * @returns {Object} 配置对象
 */
function loadDeviceConfig() {
  try {
    const configData = fs.readFileSync(CONFIG_FILE, 'utf-8');
    return JSON.parse(configData);
  } catch (error) {
    console.error(`[lock_device_info] 加载配置文件失败: ${error.message}`);
    return { devices: [], capabilityProfiles: {} };
  }
}

// 从JSON配置文件加载设备信息
const config = loadDeviceConfig();
const g_lockDeviceInfo = config.devices || [];
const g_capabilityProfiles = config.capabilityProfiles || {};

/**
 * 根据profile获取设备能力
 * @param {string} profileName - profile名称
 * @returns {Object|null} 设备能力信息
 */
function getCapabilitiesByProfile(profileName) {
  if (!profileName || !g_capabilityProfiles[profileName]) {
    return null;
  }
  // 移除description字段，只返回能力boolean值
  const profile = g_capabilityProfiles[profileName];
  const capabilities = {};
  for (const [key, value] of Object.entries(profile)) {
    if (key !== 'description') {
      capabilities[key] = value;
    }
  }
  return capabilities;
}
/**
 * 根据产品ID和型号获取门锁设备能力
 * @param {string} pid - 产品ID
 * @param {string} model - 型号名称（可选）
 * @returns {Object} 设备能力信息，未找到时返回默认全功能能力集
 */
function getLockDeviceCapability(pid, model = null) {
  if (!pid) return getDefaultCapabilities();

  // 查找设备信息
  let deviceInfo = null;

  // 精确匹配：pid + model
  if (model) {
    deviceInfo = g_lockDeviceInfo.find(
      device => device.pid === pid && device.model === model
    );
  }

  // 模糊匹配：仅根据pid匹配
  if (!deviceInfo) {
    deviceInfo = g_lockDeviceInfo.find(device => device.pid === pid);
  }

  // 设备未找到，返回默认全功能能力集
  if (!deviceInfo) {
    console.warn(`[lock_device_info] 未找到PID=${pid}的门锁设备能力定义，使用默认全功能`);
    return getDefaultCapabilities();
  }

  // 如果有profile，从profile获取能力
  if (deviceInfo.profile) {
    return getCapabilitiesByProfile(deviceInfo.profile);
  }

  // 兼容旧的直接定义capabilities的方式
  return deviceInfo.capabilities || getDefaultCapabilities();
}

/**
 * 检查门锁是否支持特定功能
 * @param {string} pid - 产品ID
 * @param {string} feature - 功能名称
 * @returns {boolean} 是否支持该功能，未找到时默认返回true（支持所有功能）
 */
function isFeatureSupported(pid, feature) {
  const capabilities = getLockDeviceCapability(pid);
  // 未找到设备时，默认返回支持该功能
  return capabilities[feature] === true;
}

/**
 * 获取门锁设备信息
 * @param {string} pid - 产品ID
 * @returns {Object|null} 设备信息，如果未找到返回null
 */
function getLockDeviceInfo(pid) {
  if (!pid) return null;
  return g_lockDeviceInfo.find(device => device.pid === pid) || null;
}

/**
 * 获取能力模板列表
 * @returns {Array} 模板列表
 */
function getCapabilityProfiles() {
  const profiles = [];
  for (const [name, profile] of Object.entries(g_capabilityProfiles)) {
    profiles.push({
      name,
      description: profile.description || ''
    });
  }
  return profiles;
}

/**
 * 获取门锁支持的功能列表（用于返回给用户或进行能力校验）
 * @param {string} pid - 产品ID
 * @param {string} model - 型号名称（可选，用于精确匹配）
 * @returns {Object} 支持的功能列表和不支持的功能列表
 * @property {string[]} supported - 支持的功能列表
 * @property {string[]} unsupported - 不支持的功能列表
 * @property {Object} capabilities - 完整的能力对象
 * @property {string} deviceName - 设备名称
 * @property {string} model - 型号
 */
function getSupportedFeatures(pid, model = null) {
  const capabilities = getLockDeviceCapability(pid, model);
  const deviceInfo = getLockDeviceInfo(pid);

  // 检查是否是默认全功能（未匹配的PID）
  const isDefault = !deviceInfo;
  const defaultCapabilities = getDefaultCapabilities();
  const isUsingDefault = isDefault ||
    (deviceInfo && JSON.stringify(capabilities) === JSON.stringify(defaultCapabilities));

  const supported = [];
  const unsupported = [];

  for (const [key, value] of Object.entries(capabilities)) {
    if (value === true) {
      supported.push(FEATURE_NAMES[key] || key);
    } else {
      unsupported.push(FEATURE_NAMES[key] || key);
    }
  }

  const result = {
    supported,
    unsupported,
    capabilities,
    deviceName: deviceInfo?.name || '未知设备',
    model: model || deviceInfo?.model || '未知',
    profile: deviceInfo?.profile || null
  };

  // 如果是默认全功能，添加标记
  if (isUsingDefault) {
    result.isDefault = true;
    result.message = `PID=${pid}未在配置文件中定义，使用默认全功能`;
  }

  return result;
}

/**
 * 检查门锁是否支持某功能，并返回友好的错误信息
 * @param {string} pid - 产品ID
 * @param {string} feature - 功能标识 (securitySetting:face/securitySetting:palm/fingerprint/nfc/password/card/catEyeSetting/greeting/weather/familyCare)
 * @returns {Object} 校验结果
 * @property {boolean} supported - 是否支持
 * @property {string} message - 友好提示信息
 * @property {string} featureCN - 功能中文名称
 */
function checkFeatureWithMessage(pid, feature) {
  const supported = isFeatureSupported(pid, feature);
  const featureCN = FEATURE_NAMES[feature] || feature;
  const deviceInfo = getLockDeviceInfo(pid);
  const deviceName = deviceInfo?.name || '您的门锁';

  let message = '';
  if (supported) {
    message = `${deviceName}支持${featureCN}功能`;
  } else if (deviceInfo) {
    message = `${deviceName}不支持${featureCN}功能`;
  } else {
    message = `PID=${pid}未在配置文件中找到，您的门锁默认支持${featureCN}功能`;
  }

  return {
    supported,
    message,
    featureCN,
    isDefault: !deviceInfo
  };
}

/**
 * 重新加载配置文件
 * @returns {boolean} 是否加载成功
 */
function reloadConfig() {
  try {
    const newConfig = loadDeviceConfig();
    if (newConfig.devices && newConfig.devices.length > 0) {
      // 更新全局设备信息
      g_lockDeviceInfo.length = 0;
      newConfig.devices.forEach(device => g_lockDeviceInfo.push(device));
      // 更新能力模板
      for (const key in newConfig.capabilityProfiles) {
        g_capabilityProfiles[key] = newConfig.capabilityProfiles[key];
      }
      console.log('[lock_device_info] 配置文件重新加载成功');
      return true;
    }
    return false;
  } catch (error) {
    console.error(`[lock_device_info] 重新加载配置文件失败: ${error.message}`);
    return false;
  }
}

/**
 * 获取配置信息
 * @returns {Object} 配置信息
 */
function getConfigInfo() {
  return {
    version: config.version || 'unknown',
    lastUpdate: config.lastUpdate || 'unknown',
    deviceCount: g_lockDeviceInfo.length,
    profileCount: Object.keys(g_capabilityProfiles).length,
    configFile: CONFIG_FILE
  };
}

module.exports = {
  g_lockDeviceInfo,
  g_capabilityProfiles,
  getLockDeviceCapability,
  isFeatureSupported,
  getLockDeviceInfo,
  getSupportedFeatures,
  checkFeatureWithMessage,
  reloadConfig,
  getConfigInfo,
  getCapabilityProfiles
};
// ==================== 命令行接口 ====================
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];

  if (command === 'get_capability') {
    // 获取设备能力
    const pidIndex = args.indexOf('--pid');
    if (pidIndex === -1 || !args[pidIndex + 1]) {
      console.error('请提供 --pid 参数');
      process.exit(1);
    }
    const pid = args[pidIndex + 1];
    const capabilities = getLockDeviceCapability(pid);
    if (capabilities) {
      console.log(JSON.stringify(capabilities, null, 2));
    } else {
      console.log(JSON.stringify({ error: `未找到PID=${pid}的门锁设备能力定义` }));
    }
  } else if (command === 'check_feature') {
    // 检查特定功能是否支持
    const pidIndex = args.indexOf('--pid');
    const featureIndex = args.indexOf('--feature');
    if (pidIndex === -1 || !args[pidIndex + 1] || featureIndex === -1 || !args[featureIndex + 1]) {
      console.error('请提供 --pid 和 --feature 参数');
      process.exit(1);
    }
    const pid = args[pidIndex + 1];
    const feature = args[featureIndex + 1];
    const supported = isFeatureSupported(pid, feature);
    console.log(JSON.stringify({ pid, feature, supported }));
  } else if (command === 'list') {
    // 列出所有已知的门锁设备
    console.log(JSON.stringify(g_lockDeviceInfo, null, 2));
  } else if (command === 'get_supported') {
    // 获取门锁支持的功能列表
    const pidIndex = args.indexOf('--pid');
    if (pidIndex === -1 || !args[pidIndex + 1]) {
      console.error('请提供 --pid 参数');
      process.exit(1);
    }
    const pid = args[pidIndex + 1];
    const modelIndex = args.indexOf('--model');
    const model = modelIndex !== -1 ? args[modelIndex + 1] : null;
    const result = getSupportedFeatures(pid, model);
    console.log(JSON.stringify(result, null, 2));
  } else if (command === 'check_with_message') {
    // 检查功能是否支持并返回友好信息
    const pidIndex = args.indexOf('--pid');
    const featureIndex = args.indexOf('--feature');
    if (pidIndex === -1 || !args[pidIndex + 1] || featureIndex === -1 || !args[featureIndex + 1]) {
      console.error('请提供 --pid 和 --feature 参数');
      process.exit(1);
    }
    const pid = args[pidIndex + 1];
    const feature = args[featureIndex + 1];
    const result = checkFeatureWithMessage(pid, feature);
    console.log(JSON.stringify(result, null, 2));
  } else if (command === 'config_info') {
    // 获取配置信息
    console.log(JSON.stringify(getConfigInfo(), null, 2));
  } else if (command === 'reload') {
    // 重新加载配置
    const success = reloadConfig();
    console.log(JSON.stringify({ success }));
  } else {
    console.log('用法:');
    console.log('  node lock_device_info.js get_capability --pid <PID>');
    console.log('  node lock_device_info.js check_feature --pid <PID> --feature <feature>');
    console.log('  node lock_device_info.js get_supported --pid <PID> [--model <型号>]');
    console.log('  node lock_device_info.js check_with_message --pid <PID> --feature <feature>');
    console.log('  node lock_device_info.js list');
    console.log('  node lock_device_info.js config_info');
    console.log('  node lock_device_info.js reload');
    console.log('');
    console.log('支持的 feature 值:');
    console.log('  securitySetting:face, securitySetting:palm, fingerprint, nfc, password');
    console.log('  card, catEyeSetting, greeting, weather, familyCare');
    console.log('  remoteUnlock, creativeDoorbell, multimedia, wifi');
  }
}
