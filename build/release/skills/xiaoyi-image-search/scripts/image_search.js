/*
 * |-----------------------------------------------------------
 * | Copyright (c) 2026 huawei.com, Inc. All Rights Reserved
 * |-----------------------------------------------------------
 * | File: image_search.js
 * | Created: 2026-03-17
 * | Description: 图片搜索 Skill，搜索图片并返回结果
 * |-----------------------------------------------------------
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');
const { getEnvConfig } = require('./env_loader');

// 加载环境变量配置
const envConfig = getEnvConfig();

// 配置常量（从环境变量文件获取）
const CONFIG = {
    SERVICE_URL: envConfig['SERVICE_URL'] || envConfig['SERVICE-URL'],
    PERSONAL_UID: envConfig['PERSONAL_UID'] || envConfig['PERSONAL-UID'],
    PERSONAL_API_KEY: envConfig['PERSONAL_API_KEY'] || envConfig['PERSONAL-API-KEY'],
};

// 调试日志配置：设置 IMAGE_SEARCH_DEBUG_LOG 环境变量为日志文件路径即可启用
// 例如: IMAGE_SEARCH_DEBUG_LOG=/tmp/image_search.log
const DEBUG_LOG_PATH = process.env['IMAGE_SEARCH_DEBUG_LOG'] || '';

/**
 * 将内容追加写入调试日志文件
 * @param {string} label - 日志标签（如 REQUEST / RESPONSE）
 * @param {object} data - 要记录的数据
 */
function debugLog(label, data) {
    if (!DEBUG_LOG_PATH) return;
    try {
        const timestamp = new Date().toISOString();
        const entry = `[${timestamp}] === ${label} ===\n${JSON.stringify(data, null, 2)}\n\n`;
        fs.appendFileSync(DEBUG_LOG_PATH, entry, 'utf8');
    } catch (err) {
        console.error(`写入调试日志失败: ${err.message}`);
    }
}

// 固定值
const FIXED_VALUES = {
    // SKILL_ID: 'xiaoyi_image_search', // 已废弃
    SKILL_ID: 'xiaoyi_doc_convert',
    REQUEST_FROM: 'openclaw',
    API_PATH: '/celia-claw/v1/rest-api/skill/execute',
    MCP_SERVER_NAME: 'browser-use',
    MCP_FUNCTION_NAME: 'image_search',
};

/**
 * 生成唯一的HAG Trace ID
 * @returns {string} 唯一的trace id
 */
function generateHagTraceId() {
    const timestamp = Date.now().toString(36);
    const random = Math.random().toString(36).substr(2, 9);
    return `hag-${timestamp}-${random}`;
}

/**
 * 发送图片搜索请求
 * @param {string} query - 搜索关键词
 * @param {number} numResults - 返回结果数量
 * @param {string} store - 图片存储方式
 * @returns {Promise<object>} 响应数据
 */
async function sendRequest(query, numResults, store) {
    // 验证必要的配置
    if (!CONFIG.SERVICE_URL) {
        throw new Error('缺少SERVICE_URL配置，请设置环境变量SERVICE_URL');
    }
    if (!CONFIG.PERSONAL_UID) {
        throw new Error('缺少PERSONAL_UID配置，请设置环境变量PERSONAL_UID');
    }
    if (!CONFIG.PERSONAL_API_KEY) {
        throw new Error('缺少PERSONAL_API_KEY配置，请设置环境变量PERSONAL_API_KEY');
    }

    // 构建完整的请求URL
    const baseUrl = CONFIG.SERVICE_URL.replace(/\/$/, '');
    const apiUrl = `${baseUrl}${FIXED_VALUES.API_PATH}`;

    const sn = generateHagTraceId();

    // 构建请求体
    const body = {
        sn: sn,
        mcp_server_name: FIXED_VALUES.MCP_SERVER_NAME,
        mcp_function_name: FIXED_VALUES.MCP_FUNCTION_NAME,
        argument: {
            query: query,
            num_results: numResults,
            store: store,
        },
    };

    // 构建请求头
    const headers = {
        'Content-Type': 'application/json',
        'x-skill-id': FIXED_VALUES.SKILL_ID,
        'x-hag-trace-id': sn,
        'x-request-from': FIXED_VALUES.REQUEST_FROM,
        'x-uid': CONFIG.PERSONAL_UID,
        'x-api-key': CONFIG.PERSONAL_API_KEY,
    };

    // 记录请求日志
    debugLog('REQUEST', { url: apiUrl });

    try {
        const response = await axios.post(apiUrl, body, {
            headers,
            timeout: 120000, // 2分钟超时
        });

        // 记录响应日志
        debugLog('RESPONSE', { status: response.status, data: response.data });

        return response.data;
    } catch (error) {
        if (error.response) {
            debugLog('RESPONSE_ERROR', { status: error.response.status, data: error.response.data });
            console.error(`请求失败，状态码: ${error.response.status}`);
            console.error(`响应数据:`, error.response.data);
            throw new Error(`请求失败: ${error.response.status} - ${JSON.stringify(error.response.data)}`);
        } else if (error.request) {
            debugLog('REQUEST_ERROR', { message: error.message });
            console.error(`请求发送但未收到响应: ${error.message}`);
            throw new Error(`网络请求失败: ${error.message}`);
        } else {
            debugLog('CONFIG_ERROR', { message: error.message });
            console.error(`请求配置错误: ${error.message}`);
            throw new Error(`请求配置错误: ${error.message}`);
        }
    }
}

/**
 * 搜索图片
 * @param {string} query - 搜索关键词
 * @param {number} [numResults=5] - 返回结果数量
 * @param {string} [store='osms'] - 图片存储方式
 * @returns {Promise<object[]>} 图片搜索结果列表
 */
async function searchImages(query, numResults = 5, store = 'osms') {
    console.error(`开始图片搜索: query="${query}", num_results=${numResults}, store=${store}`);

    const response = await sendRequest(query, numResults, store);
    
    // 检查响应状态
    if (!response || response.ret !== 0) {
        const errMsg = response ? `ret=${response.ret}` : '空响应';
        throw new Error(`图片搜索失败: ${errMsg}`);
    }

    // result 是 JSON 字符串，需要二次解析
    if (!response.result) {
        throw new Error('图片搜索返回空结果');
    }

    let images;
    try {
        images = JSON.parse(response.result);
    } catch (parseError) {
        console.error(`解析result字段失败: ${parseError.message}`);
        console.error(`原始result: ${response.result}`);
        throw new Error(`解析搜索结果失败: ${parseError.message}`);
    }

    if (!Array.isArray(images)) {
        throw new Error('搜索结果格式异常：期望数组');
    }

    console.error(`图片搜索完成，共获取 ${images.length} 条结果`);
    return images;
}

module.exports = {
    searchImages,
    sendRequest,
    generateHagTraceId,
    CONFIG,
    FIXED_VALUES,
};
