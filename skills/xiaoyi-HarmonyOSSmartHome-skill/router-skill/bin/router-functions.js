// ==================== 路由器功能模块 ====================
// 版本：1.0.0
// 功能：将路由器操作的核心功能模块化

// ==================== 应用管理操作模块 ====================
/**
 * 游戏应用恢复权限操作（两步）
 */
export async function handleAllowGames(devId, prodId, deviceId, verbose = false) {
  // 第一步：调用 Homepage 接口
  const payload1 = {
    devId,
    prodId,
    mode: 'ACK',
    operation: 'POST',
    sid: '.sys/gateway/ntwk/childHomepage',
    data: {
      action: 'gameUpdate',
      data: {
        device: deviceId,
        game: 1,
        video: 0,
        social: 0,
        payEnable: 0,
        appDownload: 0,
        urlEnable: 0,
        denyEnable: 0,
        delayEnable: 0,
        allow: 0,
        increaseTime: 0
      }
    }
  };
  
  // 第二步：调用 childModelApps 接口清空应用列表
  const payload2 = {
    devId,
    prodId,
    mode: 'ACK',
    operation: 'POST',
    sid: '.sys/gateway/ntwk/childModelApps',
    data: {
      action: 'update',
      data: {
        device: deviceId,
        apps: [],
        denyAll: 0,
        type: 1
      }
    }
  };
  
  return { payload1, payload2, step1Name: 'allow_games_step1', step2Name: 'allow_games_step2' };
}

/**
 * 视频应用恢复权限操作（两步）
 */
export async function handleAllowVideos(devId, prodId, deviceId, verbose = false) {
  const payload1 = {
    devId,
    prodId,
    mode: 'ACK',
    operation: 'POST',
    sid: '.sys/gateway/ntwk/childHomepage',
    data: {
      action: 'videoUpdate',
      data: {
        device: deviceId,
        game: 0,
        video: 1,
        social: 0,
        payEnable: 0,
        appDownload: 0,
        urlEnable: 0,
        denyEnable: 0,
        delayEnable: 0,
        allow: 0,
        increaseTime: 0
      }
    }
  };
  
  const payload2 = {
    devId,
    prodId,
    mode: 'ACK',
    operation: 'POST',
    sid: '.sys/gateway/ntwk/childModelApps',
    data: {
      action: 'update',
      data: {
        device: deviceId,
        apps: [],
        denyAll: 0,
        type: 2
      }
    }
  };
  
  return { payload1, payload2, step1Name: 'allow_videos_step1', step2Name: 'allow_videos_step2' };
}

/**
 * 社交通讯应用恢复权限操作（两步）
 */
export async function handleAllowSocial(devId, prodId, deviceId, verbose = false) {
  const payload1 = {
    devId,
    prodId,
    mode: 'ACK',
    operation: 'POST',
    sid: '.sys/gateway/ntwk/childHomepage',
    data: {
      action: 'socialUpdate',
      data: {
        device: deviceId,
        game: 0,
        video: 0,
        social: 1,
        payEnable: 0,
        appDownload: 0,
        urlEnable: 0,
        denyEnable: 0,
        delayEnable: 0,
        allow: 0,
        increaseTime: 0
      }
    }
  };
  
  const payload2 = {
    devId,
    prodId,
    mode: 'ACK',
    operation: 'POST',
    sid: '.sys/gateway/ntwk/childModelApps',
    data: {
      action: 'update',
      data: {
        device: deviceId,
        apps: [],
        denyAll: 0,
        type: 3
      }
    }
  };
  
  return { payload1, payload2, step1Name: 'allow_social_step1', step2Name: 'allow_social_step2' };
}

/**
 * 购物支付应用恢复权限操作（两步）
 */
export async function handleAllowShopping(devId, prodId, deviceId, verbose = false) {
  const payload1 = {
    devId,
    prodId,
    mode: 'ACK',
    operation: 'POST',
    sid: '.sys/gateway/ntwk/childHomepage',
    data: {
      action: 'payUpdate',
      data: {
        device: deviceId,
        game: 0,
        video: 0,
        social: 0,
        payEnable: 1,
        appDownload: 0,
        urlEnable: 0,
        denyEnable: 0,
        delayEnable: 0,
        allow: 0,
        increaseTime: 0
      }
    }
  };
  
  const payload2 = {
    devId,
    prodId,
    mode: 'ACK',
    operation: 'POST',
    sid: '.sys/gateway/ntwk/childModelApps',
    data: {
      action: 'update',
      data: {
        device: deviceId,
        apps: [],
        denyAll: 0,
        type: 4
      }
    }
  };
  
  return { payload1, payload2, step1Name: 'allow_shopping_step1', step2Name: 'allow_shopping_step2' };
}

/**
 * 安装应用恢复权限操作（两步）
 */
export async function handleAllowInstall(devId, prodId, deviceId, verbose = false) {
  const payload1 = {
    devId,
    prodId,
    mode: 'ACK',
    operation: 'POST',
    sid: '.sys/gateway/ntwk/childHomepage',
    data: {
      action: 'installUpdate',
      data: {
        device: deviceId,
        game: 0,
        video: 0,
        social: 0,
        payEnable: 0,
        appDownload: 1,
        urlEnable: 0,
        denyEnable: 0,
        delayEnable: 0,
        allow: 0,
        increaseTime: 0
      }
    }
  };
  
  const payload2 = {
    devId,
    prodId,
    mode: 'ACK',
    operation: 'POST',
    sid: '.sys/gateway/ntwk/childModelApps',
    data: {
      action: 'update',
      data: {
        device: deviceId,
        apps: [],
        denyAll: 0,
        type: 5
      }
    }
  };
  
  return { payload1, payload2, step1Name: 'allow_install_step1', step2Name: 'allow_install_step2' };
}

// ==================== 本地功能模块 ====================
/**
 * 根据产品ID获取路由器设备信息
 */
export async function handleGetRouterDeviceByProdid(prodid = 'K1AP') {
  try {
    const deviceInfoData = await import('../router_device_info.js');
    
    // 查找匹配的 prodid
    const match = deviceInfoData.default.g_routerDeviceInfo.find(info => 
      info[1].toLowerCase() === String(prodid).toLowerCase()
    );
    
    let deviceInfo;
    if (match) {
      deviceInfo = {
        isRouter: true,
        prodId: match[1],
        device: match[0],
        chineseName: match[2],
        englishName: match[3],
        fromLocal: true,
        totalCount: deviceInfoData.default.g_routerDeviceInfo.length,
        note: '使用本地路由设备信息映射'
      };
    } else {
      deviceInfo = {
        isRouter: false,
        prodId: String(prodid),
        chineseName: '未识别的设备',
        englishName: 'Unrecognized Device',
        fromLocal: false,
        suggestion: '请检查prodid是否正确，查看支持的路由器设备列表'
      };
    }
    
    return {
      success: deviceInfo.isRouter,
      data: deviceInfo,
      message: deviceInfo.isRouter ? 
        `路由器识别成功: ${deviceInfo.chineseName} (${deviceInfo.englishName})` : 
        '该prodid在路由器设备映射表中未找到'
    };
  } catch (error) {
    return {
      success: false,
      data: null,
      message: `加载路由器设备信息映射表失败: ${error.message}`
    };
  }
}

/**
 * 根据应用ID查询具体应用信息
 */
export async function handleGetAppInfo(appId) {
  if (!appId) {
    return {
      success: false,
      data: null,
      message: '请提供要查询的应用ID'
    };
  }
  
  try {
    const appInfo = g_saAppInfo.find(app => 
      String(app[1]) === String(appId)
    );
    
    if (appInfo) {
      return {
        success: true,
        data: {
          appName: appInfo[0],
          appId: appInfo[1],
          categ: appInfo[2],
          message: `应用查询成功: ${appInfo[0]} (ID: ${appInfo[1]}, 分类: ${appInfo[2]})`
        }
      };
    } else {
      return {
        success: false,
        data: null,
        message: `未找到ID为 ${appId} 的应用`
      };
    }
  } catch (error) {
    return {
      success: false,
      data: null,
      message: `应用信息查询失败: ${error.message}`
    };
  }
}

/**
 * 查询所有可用的应用列表
 */
export async function handleGetAllApps() {
  try {
    const categorizedApps = {};
    
    // 按分类整理应用
    g_saAppInfo.forEach(app => {
      const categ = app[2];
      const categoryName = getCategoryName(categ);
      
      if (!categorizedApps[categoryName]) {
        categorizedApps[categoryName] = [];
      }
      
      categorizedApps[categoryName].push({
        name: app[0],
        id: app[1],
        categ: app[2]
      });
    });
    
    return {
      success: true,
      data: {
        totalApps: g_saAppInfo.length,
        categories: categorizedApps,
        message: `共找到 ${g_saAppInfo.length} 个应用，按分类显示`
      }
    };
  } catch (error) {
    return {
      success: false,
      data: null,
      message: `应用列表查询失败: ${error.message}`
    };
  }
}

// ==================== 工具函数模块 ====================
/**
 * 根据应用分类ID获取分类名称
 */
export function getCategoryName(categ) {
  const categoryMap = {
    1: '默认节点',
    2: '应用商店',
    4: '游戏',
    8: '应用服务',
    16: '视频类',
    32: '直播类',
    128: '社交类',
    256: '办公类',
    512: '购物类',
    1024: '支付类',
    2048: 'WiFi相关',
    4096: '教育类',
    8192: '学习类'
  };
  
  return categoryMap[categ] || `未知分类(${categ})`;
}

/**
 * 从映射表中获取路由器信息
 */
export async function getRouterInfo(deviceId, prodId) {
  try {
    const routerDeviceInfo = (await import('../router_device_info.js')).default;
    const routerInfo = routerDeviceInfo.find(info => 
      info[0] === deviceId || info[1] === prodId
    );
    
    if (routerInfo) {
      return {
        name: routerInfo[2],      // 中文名称
        model: routerInfo[3],     // 英文名称
        deviceId: routerInfo[0],  // 设备标识
        prodId: routerInfo[1]     // 产品ID
      };
    }
    return null;
  } catch (error) {
    // 如果加载映射表失败，返回null
    return null;
  }
}