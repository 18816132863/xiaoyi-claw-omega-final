// ==================== smarthome-claw.js 主入口 ====================
// 功能：智能家居技能总调度入口
// 版本：0.5.0 (重构版)
import {Command} from 'commander';

// ==================== 引入子技能模块 ====================
import {getDeviceMessages} from './get_device_messages.js';
import {getDevicesInfo} from './get_devices_info.js';
import {getHomesInfo} from './get_homes_info.js';
import {getControlRecords} from './get_control_records.js';
import {getDeviceDetail} from "./get_device_details.js";
import {controlDevice} from "./control_device.js";
import {getDeviceHistories} from './get_device_histories.js';

// ==================== 常量配置 ====================
const PROGRAM_NAME = 'smarthome-claw';
const VERSION = '0.6.0';
const DEFAULT_SKILL_ID = 'smartHome';

// ==================== 核心调度函数 ====================
async function callDeviceClaw(tools, skillId, verbose = false) {
    const output = [];

    for (const tool of tools) {
        if (verbose) console.error(`[verbose] 执行工具：${tool.name}`);

        try {
            let data;

            switch (tool.name) {
                case 'get_device_messages':
                    data = await getDeviceMessages(tool.args || {}, verbose);
                    break;

                case 'get_devices_info':
                    data = await getDevicesInfo(verbose);
                    break;

                case 'get_homes_info':
                    data = await getHomesInfo(verbose);
                    break;

                case 'get_control_records':
                    data = await getControlRecords(tool.args || {}, verbose);
                    break;

                case 'get_devices_control_record':
                    data = await getDeviceControlRecord(tool.args || {}, verbose);
                    break;

                case 'control_device':
                    data = await controlDevice(
                        tool.args?.devId,
                        tool.args?.prodId,
                        tool.args?.operation,
                        tool.args?.sid,
                        tool.args?.data,
                        verbose
                    );
                    break;

                case 'get_device_detail':
                    data = await getDeviceDetail(tool.args?.devId, verbose);
                    break;

                default:
                    console.error(`[warning] 未知工具：${tool.name}`);
                    continue;
            }

            output.push({tool: tool.name, data});
        } catch (err) {
            console.error(`[error] ${tool.name} 执行失败：${err.message}`);
            throw err;
        }
    }

    console.log(JSON.stringify(output, null, 2));
}

// ==================== 命令注册 ====================
function registerClawCommands(program) {
    // 设备消息
    program.command('get_device_messages')
        .description('获取设备消息/告警')
        .option('--date <type>', 'today/yesterday')
        .option('--last-days <n>', '最近 N 天')
        .option('--skill-id <id>', DEFAULT_SKILL_ID)
        .option('--verbose')
        .action(async (opts) => {
            await callDeviceClaw([{name: 'get_device_messages', args: opts}], opts.skillId, opts.verbose);
        });

    // 设备信息
    program.command('get_devices_info')
        .description('获取设备基础信息')
        .option('--skill-id <id>', DEFAULT_SKILL_ID)
        .option('--verbose')
        .action(async (opts) => {
            await callDeviceClaw([{name: 'get_devices_info'}], opts.skillId, opts.verbose);
        });

    // 家庭信息
    program.command('get_homes_info')
        .description('获取家庭信息')
        .option('-v, --verbose', '启用详细日志', false)
        .option('-s, --skill-id <id>', '技能 ID', DEFAULT_SKILL_ID)
        .action(async (opts) => {
            await callDeviceClaw([{name: 'get_homes_info'}], opts.skillId, opts.verbose);
        });

    // 设备控制记录（家庭维度）
    program.command('get_control_records')
        .description('获取设备控制记录（概要 + 详情）')
        .requiredOption('--home-id <id>', '指定家庭 ID（必填）')
        .option('--last-days <n>', '最近 N 天,值为0是表示当天', 1)
        .option('--skill-id <id>', DEFAULT_SKILL_ID)
        .option('--verbose')
        .action(async (opts) => {
            await callDeviceClaw([{name: 'get_control_records', args: opts}], opts.skillId, opts.verbose);
        });

    // 设备控制记录（单设备维度）
    program.command('get_devices_control_record')
        .description('获取指定设备的控制记录详情')
        .requiredOption('--device-id <id>', '指定设备 ID（必填）')
        .option('--home-id <id>', '指定家庭 ID（可选）')
        .option('--skill-id <id>', DEFAULT_SKILL_ID)
        .option('--verbose')
        .action(async (opts) => {
            await callDeviceClaw([{name: 'get_devices_control_record', args: opts}], opts.skillId, opts.verbose);
        });

    // 设备控制
    program.command('control_device')
        .description('控制设备')
        .requiredOption('--dev-id <id>', '设备 ID（必填）')
        .requiredOption('--prod-id <id>', '产品 ID（必填）')
        .requiredOption('--operation <type>', '操作类型（GET/POST）')
        .requiredOption('--sid <id>', '服务 ID')
        .requiredOption('--data <json>', '控制数据（JSON 字符串）')
        .option('--skill-id <id>', DEFAULT_SKILL_ID)
        .option('--verbose')
        .action(async (opts) => {
            await callDeviceClaw([{name: 'control_device', args: opts}], opts.skillId, opts.verbose);
        });

    // 设备详情
    program.command('get_device_detail')
        .description('获取设备详细信息')
        .requiredOption('--dev-id <id>', '设备 ID（必填）')
        .option('--skill-id <id>', DEFAULT_SKILL_ID)
        .option('--verbose')
        .action(async (opts) => {
            await callDeviceClaw([{name: 'get_device_detail', args: opts}], opts.skillId, opts.verbose);
        });

    // 历史记录
    program.command('get_device_histories')
      .description('获取设备历史上报记录')
      .requiredOption('--dev-id <id>', '设备 ID（必填）')
      .requiredOption('--sid <id>', '查询的sid（必填）')
      .option('--date <type>', 'today/yesterday')
      .option('--last-days <n>', '最近 N 天')
      .option('--skill-id <id>', DEFAULT_SKILL_ID)
      .option('--verbose')
      .action(async (opts) => {
        await callDeviceClaw([{ name: 'get_device_histories', args: opts }], opts.skillId, opts.verbose);
      });
}

// ==================== 启动 ====================
const program = new Command();

program
    .name(PROGRAM_NAME)
    .description('全屋智能家居技能 - 设备/家庭/控制记录查询（家庭维度 + 单设备维度）')
    .version(VERSION)
    .option('--tools <json>', '执行多个工具（JSON 数组）')
    .option('--skill-id <id>', DEFAULT_SKILL_ID)
    .option('--verbose')
    .action(async (opts) => {
        if (!opts.tools) {
            program.help();
            return;
        }

        // 验证JSON格式
        let parsedTools;
        try {
            parsedTools = JSON.parse(opts.tools);
        } catch (jsonError) {
            console.error('错误：tools参数不是有效的JSON格式');
            process.exit(1);
        }

        await callDeviceClaw(parsedTools, opts.skillId, opts.verbose);
    });

registerClawCommands(program);
program.parse();
