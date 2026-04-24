#!/usr/bin/env node

/*
 * |-----------------------------------------------------------
 * | Copyright (c) 2026 huawei.com, Inc. All Rights Reserved
 * |-----------------------------------------------------------
 * | File: index.js
 * | Created: 2026-03-17
 * | Description: 图片搜索技能 CLI 入口
 * |-----------------------------------------------------------
 */

const { searchImages } = require('./image_search.js');

/**
 * 格式化输出单条图片结果
 * @param {object} image - 图片对象
 * @param {number} index - 序号（从1开始）
 */
function formatImageResult(image, index) {
    const lines = [
        `--- 图片 ${index} ---`,
        `  标题:     ${image.img_title || '(无标题)'}`,
        `  尺寸:     ${image.img_width || '?'} x ${image.img_height || '?'}`,
        `  原图URL:  ${image.img_ori_url || '(无)'}`,
        `  缩略图:   ${image.img_thumb_url || '(无)'}`,
        `  来源页面: ${image.img_from_url || '(无)'}`,
    ];
    return lines.join('\n');
}

/**
 * 主处理函数
 * @param {string} query - 搜索关键词
 * @param {number} numResults - 返回结果数量
 * @param {string} store - 图片存储方式
 */
async function main(query, numResults, store) {
    const maxRetries = 3;
    let attempt = 0;
    let lastError = null;
    while (attempt < maxRetries) {
        try {
            console.error(`=== 图片搜索开始 (第${attempt + 1}次尝试) ===`);
            const images = await searchImages(query, numResults, store);
            // 格式化输出
            console.log(`图片搜索完成，关键词: "${query}"，共 ${images.length} 条结果\n`);
            for (let i = 0; i < images.length; i++) {
                console.log(formatImageResult(images[i], i + 1));
            }
            console.log(`\n提示: 原图URL为OSMS预签名链接，可直接下载使用`);
            return;
        } catch (error) {
            lastError = error;
            console.error(`图片搜索失败 (第${attempt + 1}次): ${error.message}`);
            attempt++;
            if (attempt < maxRetries) {
                console.error('正在重试...');
            }
        }
    }
    console.error(`图片搜索失败: ${lastError ? lastError.message : '未知错误'}`);
    process.exit(1);
}

// 命令行接口
if (require.main === module) {
    const args = process.argv.slice(2);
    if (args.length < 1) {
        console.error('用法: node index.js <query> [num_results] [store]');
        console.error('  query       - 搜索关键词（必填）');
        console.error('  num_results - 返回结果数量（默认5）');
        console.error('  store       - 存储方式（默认 osms）');
        process.exit(1);
    }

    const query = args[0];
    const numResults = args[1] ? parseInt(args[1], 10) : 5;
    const store = args[2] || 'osms';

    main(query, numResults, store).catch(error => {
        console.error(`处理失败: ${error.message}`);
        process.exit(1);
    });
}

module.exports = { main };
