const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
        Header, Footer, AlignmentType, PageOrientation, LevelFormat, 
        HeadingLevel, BorderStyle, WidthType, ShadingType, PageNumber, PageBreak,
        VerticalAlign, TableOfContents } = require('docx');
const fs = require('fs');

// ============================================
// 专业配色方案 - 参考医疗健康行业标准
// ============================================
const COLORS = {
  // 主色调 - 医疗蓝（专业、信任）
  primary: "0078D4",
  primaryLight: "4298D5",
  primaryDark: "004578",
  
  // 辅助色 - 健康绿（活力、健康）
  success: "107C10",
  successLight: "54B054",
  
  // 警告色 - 橙色（注意）
  warning: "FF8C00",
  warningLight: "FFB84D",
  
  // 危险色 - 红色（警示）
  danger: "D13438",
  dangerLight: "E87A7D",
  
  // 中性色
  dark: "323130",
  gray: "605E5C",
  lightGray: "D2D0CE",
  light: "F3F2F1",
  white: "FFFFFF",
  
  // 数据可视化配色
  chart1: "0078D4",
  chart2: "107C10",
  chart3: "FF8C00",
  chart4: "8764B8",
  chart5: "E74856"
};

// ============================================
// 边框样式
// ============================================
const thinBorder = { style: BorderStyle.SINGLE, size: 4, color: COLORS.lightGray };
const mediumBorder = { style: BorderStyle.SINGLE, size: 8, color: COLORS.primary };
const noBorder = { style: BorderStyle.NONE, size: 0, color: COLORS.white };

const thinBorders = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };
const mediumBorders = { top: mediumBorder, bottom: mediumBorder, left: mediumBorder, right: mediumBorder };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

// ============================================
// 创建专业健康报告
// ============================================
function createProfessionalHealthReport() {
  const doc = new Document({
    styles: {
      default: {
        document: {
          run: { font: "Microsoft YaHei", size: 22, color: COLORS.dark }
        }
      },
      paragraphStyles: [
        // 标题样式
        {
          id: "Title",
          name: "Title",
          basedOn: "Normal",
          run: { size: 72, bold: true, font: "Microsoft YaHei", color: COLORS.primary },
          paragraph: { spacing: { before: 0, after: 200 }, alignment: AlignmentType.CENTER }
        },
        {
          id: "Heading1",
          name: "Heading 1",
          basedOn: "Normal",
          next: "Normal",
          quickFormat: true,
          run: { size: 36, bold: true, font: "Microsoft YaHei", color: COLORS.primary },
          paragraph: { 
            spacing: { before: 400, after: 200 }, 
            outlineLevel: 0,
            border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: COLORS.primary, space: 8 } }
          }
        },
        {
          id: "Heading2",
          name: "Heading 2",
          basedOn: "Normal",
          next: "Normal",
          quickFormat: true,
          run: { size: 28, bold: true, font: "Microsoft YaHei", color: COLORS.primaryDark },
          paragraph: { spacing: { before: 300, after: 150 }, outlineLevel: 1 }
        },
        {
          id: "Heading3",
          name: "Heading 3",
          basedOn: "Normal",
          next: "Normal",
          quickFormat: true,
          run: { size: 24, bold: true, font: "Microsoft YaHei", color: COLORS.gray },
          paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 }
        },
        // 正文样式
        {
          id: "BodyText",
          name: "Body Text",
          basedOn: "Normal",
          run: { size: 22, font: "Microsoft YaHei", color: COLORS.dark },
          paragraph: { spacing: { before: 100, after: 100, line: 360 } }
        }
      ]
    },
    numbering: {
      config: [
        {
          reference: "bullets",
          levels: [{
            level: 0,
            format: LevelFormat.BULLET,
            text: "•",
            alignment: AlignmentType.LEFT,
            style: { 
              paragraph: { indent: { left: 720, hanging: 360 } },
              run: { color: COLORS.primary }
            }
          }]
        },
        {
          reference: "numbers",
          levels: [{
            level: 0,
            format: LevelFormat.DECIMAL,
            text: "%1.",
            alignment: AlignmentType.LEFT,
            style: { 
              paragraph: { indent: { left: 720, hanging: 360 } },
              run: { color: COLORS.primary, bold: true }
            }
          }]
        },
        {
          reference: "checklist",
          levels: [{
            level: 0,
            format: LevelFormat.BULLET,
            text: "☐",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } }
          }]
        }
      ]
    },
    sections: [{
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
        }
      },
      headers: {
        default: new Header({
          children: [
            new Table({
              width: { size: 9360, type: WidthType.DXA },
              columnWidths: [4680, 4680],
              rows: [
                new TableRow({
                  children: [
                    new TableCell({
                      borders: noBorders,
                      width: { size: 4680, type: WidthType.DXA },
                      children: [
                        new Paragraph({
                          children: [
                            new TextRun({ text: "健康数据周报", bold: true, size: 20, color: COLORS.primary }),
                            new TextRun({ text: " | Health Weekly Report", size: 18, color: COLORS.gray })
                          ]
                        })
                      ]
                    }),
                    new TableCell({
                      borders: noBorders,
                      width: { size: 4680, type: WidthType.DXA },
                      children: [
                        new Paragraph({
                          children: [new TextRun({ text: "2026年4月12日 - 2026年4月18日", size: 18, color: COLORS.gray })],
                          alignment: AlignmentType.RIGHT
                        })
                      ]
                    })
                  ]
                })
              ]
            })
          ]
        })
      },
      footers: {
        default: new Footer({
          children: [
            new Table({
              width: { size: 9360, type: WidthType.DXA },
              columnWidths: [4680, 4680],
              rows: [
                new TableRow({
                  children: [
                    new TableCell({
                      borders: { top: thinBorder, bottom: noBorder, left: noBorder, right: noBorder },
                      width: { size: 4680, type: WidthType.DXA },
                      children: [
                        new Paragraph({
                          children: [
                            new TextRun({ text: "AI健康助手", size: 18, color: COLORS.primary, bold: true }),
                            new TextRun({ text: " | 专业健康数据分析", size: 16, color: COLORS.gray })
                          ]
                        })
                      ]
                    }),
                    new TableCell({
                      borders: { top: thinBorder, bottom: noBorder, left: noBorder, right: noBorder },
                      width: { size: 4680, type: WidthType.DXA },
                      children: [
                        new Paragraph({
                          children: [
                            new TextRun({ text: "第 ", size: 18, color: COLORS.gray }),
                            new TextRun({ children: [PageNumber.CURRENT], size: 18, color: COLORS.primary, bold: true }),
                            new TextRun({ text: " 页 / 共 ", size: 18, color: COLORS.gray }),
                            new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18, color: COLORS.primary, bold: true }),
                            new TextRun({ text: " 页", size: 18, color: COLORS.gray })
                          ],
                          alignment: AlignmentType.RIGHT
                        })
                      ]
                    })
                  ]
                })
              ]
            })
          ]
        })
      },
      children: [
        // ============================================
        // 封面页
        // ============================================
        new Paragraph({ spacing: { before: 2000 } }),
        
        // Logo区域（模拟）
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [9360],
          rows: [
            new TableRow({
              children: [
                new TableCell({
                  borders: noBorders,
                  width: { size: 9360, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 400, bottom: 400, left: 600, right: 600 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "🏥", size: 96 })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "AI健康助手", bold: true, size: 48, color: COLORS.white })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "AI Health Assistant", size: 28, color: COLORS.white })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                })
              ]
            })
          ]
        }),
        
        new Paragraph({ spacing: { before: 800 } }),
        
        // 标题
        new Paragraph({
          children: [new TextRun({ text: "健康数据周报", bold: true, size: 72, color: COLORS.primary })],
          alignment: AlignmentType.CENTER
        }),
        new Paragraph({
          children: [new TextRun({ text: "Health Weekly Report", size: 36, color: COLORS.gray })],
          alignment: AlignmentType.CENTER,
          spacing: { after: 400 }
        }),
        
        // 报告期间
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [9360],
          rows: [
            new TableRow({
              children: [
                new TableCell({
                  borders: noBorders,
                  width: { size: 9360, type: WidthType.DXA },
                  shading: { fill: COLORS.light, type: ShadingType.CLEAR },
                  margins: { top: 200, bottom: 200, left: 400, right: 400 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "报告期间 Report Period", bold: true, size: 20, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "2026年4月12日 - 2026年4月18日", bold: true, size: 28, color: COLORS.primary })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                })
              ]
            })
          ]
        }),
        
        new Paragraph({ spacing: { before: 600 } }),
        
        // 用户信息卡片
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2340, 2340, 2340, 2340],
          rows: [
            new TableRow({
              children: [
                createInfoCard("👤 用户", "张三", COLORS.primary),
                createInfoCard("🎂 年龄", "30岁", COLORS.chart2),
                createInfoCard("📏 身高", "175cm", COLORS.chart3),
                createInfoCard("⚖️ 体重", "70kg", COLORS.chart4)
              ]
            })
          ]
        }),
        
        new Paragraph({ spacing: { before: 600 } }),
        
        // 健康评分大卡片
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [9360],
          rows: [
            new TableRow({
              children: [
                new TableCell({
                  borders: mediumBorders,
                  width: { size: 9360, type: WidthType.DXA },
                  shading: { fill: COLORS.white, type: ShadingType.CLEAR },
                  margins: { top: 400, bottom: 400, left: 600, right: 600 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "综合健康评分", bold: true, size: 24, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [
                        new TextRun({ text: "88", bold: true, size: 120, color: COLORS.success }),
                        new TextRun({ text: " / 100", size: 48, color: COLORS.gray })
                      ],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "优秀 · Excellent", bold: true, size: 28, color: COLORS.success })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                })
              ]
            })
          ]
        }),
        
        new Paragraph({ children: [new PageBreak()] }),
        
        // ============================================
        // 目录页
        // ============================================
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("目录 Contents")]
        }),
        
        new Paragraph({ spacing: { before: 200 } }),
        
        createTOCItem("一、执行摘要 Executive Summary", "3"),
        createTOCItem("二、数据概览 Data Overview", "4"),
        createTOCItem("三、睡眠质量分析 Sleep Analysis", "5"),
        createTOCItem("四、运动情况分析 Exercise Analysis", "6"),
        createTOCItem("五、营养摄入分析 Nutrition Analysis", "7"),
        createTOCItem("六、健康风险评估 Health Risk Assessment", "8"),
        createTOCItem("七、综合健康建议 Recommendations", "9"),
        createTOCItem("八、下周健康目标 Next Week Goals", "10"),
        
        new Paragraph({ children: [new PageBreak()] }),
        
        // ============================================
        // 一、执行摘要
        // ============================================
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("一、执行摘要 Executive Summary")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "本周健康数据整体表现优秀，各项核心指标均呈现积极改善趋势。睡眠质量稳步提升，运动量达标，营养摄入均衡，整体健康状态良好。", 
            size: 22 
          })],
          spacing: { before: 200, after: 300 }
        }),
        
        // 关键指标卡片
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2340, 2340, 2340, 2340],
          rows: [
            new TableRow({
              children: [
                createMetricCard("😴 睡眠时长", "7.2h", "↑ 5.9%", COLORS.success),
                createMetricCard("🏃 运动时长", "35min", "↑ 25%", COLORS.success),
                createMetricCard("👣 步数", "8,500", "↑ 18%", COLORS.success),
                createMetricCard("❤️ 心率", "72bpm", "↓ 4%", COLORS.success)
              ]
            })
          ]
        }),
        
        new Paragraph({ spacing: { before: 300 } }),
        
        // 关键发现
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("关键发现 Key Findings")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "睡眠质量显著改善，深度睡眠占比提升至23%", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "运动频率达标，本周完成5次有效运动", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "步数目标达成率85%，较上周提升18%", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "静息心率稳定在健康范围内", size: 22 })]
        }),
        
        new Paragraph({ children: [new PageBreak()] }),
        
        // ============================================
        // 二、数据概览
        // ============================================
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("二、数据概览 Data Overview")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "以下为本周健康数据的详细统计，包含与上周数据的对比分析。", 
            size: 22,
            color: COLORS.gray
          })],
          spacing: { after: 300 }
        }),
        
        // 数据表格
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2340, 2340, 2340, 2340],
          rows: [
            // 表头
            new TableRow({
              children: [
                createTableHeader("指标 Metric"),
                createTableHeader("本周 This Week"),
                createTableHeader("上周 Last Week"),
                createTableHeader("变化 Change")
              ]
            }),
            // 数据行
            createDataRow("睡眠时长 Sleep", "7.2小时", "6.8小时", "↑ 5.9%", COLORS.success, 0),
            createDataRow("运动时长 Exercise", "35分钟", "28分钟", "↑ 25%", COLORS.success, 1),
            createDataRow("步数 Steps", "8,500步", "7,200步", "↑ 18%", COLORS.success, 0),
            createDataRow("心率 Heart Rate", "72次/分", "75次/分", "↓ 4%", COLORS.success, 1),
            createDataRow("消耗卡路里 Calories", "2,100千卡", "1,800千卡", "↑ 17%", COLORS.success, 0),
            createDataRow("饮水量 Water", "2.1升", "1.8升", "↑ 17%", COLORS.success, 1)
          ]
        }),
        
        new Paragraph({ children: [new PageBreak()] }),
        
        // ============================================
        // 三、睡眠质量分析
        // ============================================
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("三、睡眠质量分析 Sleep Analysis")]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("睡眠质量评分 Sleep Quality Score")]
        }),
        
        // 睡眠质量大卡片
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [3120, 3120, 3120],
          rows: [
            new TableRow({
              children: [
                createLargeMetricCard("平均睡眠时长", "7.2", "小时", COLORS.primary),
                createLargeMetricCard("深度睡眠占比", "23", "%", COLORS.chart2),
                createLargeMetricCard("睡眠质量评分", "85", "分", COLORS.success)
              ]
            })
          ]
        }),
        
        new Paragraph({ spacing: { before: 300 } }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("睡眠结构分析 Sleep Structure")]
        }),
        
        // 睡眠结构表格
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [3120, 3120, 3120],
          rows: [
            new TableRow({
              children: [
                createTableHeader("睡眠阶段 Stage"),
                createTableHeader("时长 Duration"),
                createTableHeader("占比 Percentage")
              ]
            }),
            createDataRow("深度睡眠 Deep Sleep", "1.7小时", "23%", COLORS.primary, 0),
            createDataRow("浅度睡眠 Light Sleep", "3.7小时", "52%", COLORS.gray, 1),
            createDataRow("REM睡眠 REM Sleep", "1.8小时", "25%", COLORS.chart2, 0)
          ]
        }),
        
        new Paragraph({ spacing: { before: 300 } }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("睡眠建议 Sleep Recommendations")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "✅ 睡眠质量良好，继续保持规律作息", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "💡 建议增加深度睡眠时长，可通过睡前放松活动改善", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "💡 建议睡前1小时避免使用电子设备", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "💡 保持卧室温度在18-22°C，湿度在40-60%", size: 22 })]
        }),
        
        new Paragraph({ children: [new PageBreak()] }),
        
        // ============================================
        // 四、运动情况分析
        // ============================================
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("四、运动情况分析 Exercise Analysis")]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("运动统计 Exercise Statistics")]
        }),
        
        // 运动数据卡片
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2340, 2340, 2340, 2340],
          rows: [
            new TableRow({
              children: [
                createMetricCard("运动天数", "5天", "71%", COLORS.primary),
                createMetricCard("总运动时长", "175min", "25h", COLORS.chart2),
                createMetricCard("消耗卡路里", "2,100", "kcal", COLORS.chart3),
                createMetricCard("平均心率", "128", "bpm", COLORS.chart4)
              ]
            })
          ]
        }),
        
        new Paragraph({ spacing: { before: 300 } }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("运动类型分布 Exercise Types")]
        }),
        
        // 运动类型表格
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [3120, 3120, 3120],
          rows: [
            new TableRow({
              children: [
                createTableHeader("运动类型 Type"),
                createTableHeader("次数 Count"),
                createTableHeader("总时长 Duration")
              ]
            }),
            createDataRow("跑步 Running", "2次", "60分钟", COLORS.primary, 0),
            createDataRow("游泳 Swimming", "1次", "45分钟", COLORS.chart2, 1),
            createDataRow("力量训练 Strength", "1次", "40分钟", COLORS.chart3, 0),
            createDataRow("瑜伽 Yoga", "1次", "30分钟", COLORS.chart4, 1)
          ]
        }),
        
        new Paragraph({ spacing: { before: 300 } }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("运动建议 Exercise Recommendations")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "✅ 运动量达标，每周运动5天表现优秀", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "⚠️ 建议增加力量训练频率，每周至少2次", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "💡 可尝试HIIT训练，提高燃脂效率", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "💡 运动后注意拉伸，避免肌肉损伤", size: 22 })]
        }),
        
        new Paragraph({ children: [new PageBreak()] }),
        
        // ============================================
        // 七、综合健康建议
        // ============================================
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("七、综合健康建议 Recommendations")]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("1. 睡眠改善 Sleep Improvement")]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "保持规律作息，建议22:30前入睡", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "睡前可进行冥想或深呼吸练习", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "避免睡前饮用咖啡或浓茶", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "保持卧室安静、黑暗、凉爽", size: 22 })]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("2. 运动计划 Exercise Plan")]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "每周至少3次有氧运动，每次30-45分钟", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "每周2次力量训练，重点锻炼核心肌群", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "每日步行目标: 10,000步", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "运动前后做好热身和拉伸", size: 22 })]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("3. 饮食建议 Diet Recommendations")]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "控制碳水摄入，增加优质蛋白质", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "多吃蔬菜水果，保证膳食纤维摄入", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "每日饮水至少2000ml", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "避免高糖、高油、高盐食物", size: 22 })]
        }),
        
        new Paragraph({ children: [new PageBreak()] }),
        
        // ============================================
        // 八、下周健康目标
        // ============================================
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("八、下周健康目标 Next Week Goals")]
        }),
        
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [3120, 3120, 3120],
          rows: [
            new TableRow({
              children: [
                createTableHeader("目标项目 Goal"),
                createTableHeader("目标值 Target"),
                createTableHeader("当前状态 Status")
              ]
            }),
            createGoalRow("睡眠时长 Sleep", "≥ 7.5小时", "待完成 Pending", 0),
            createGoalRow("运动时长 Exercise", "≥ 40分钟/天", "待完成 Pending", 1),
            createGoalRow("步数 Steps", "≥ 9,000步/天", "待完成 Pending", 0),
            createGoalRow("力量训练 Strength", "≥ 2次/周", "待完成 Pending", 1),
            createGoalRow("饮水量 Water", "≥ 2.5升/天", "待完成 Pending", 0)
          ]
        }),
        
        new Paragraph({ spacing: { before: 400 } }),
        
        // 总结
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("总结 Summary")]
        }),
        
        new Paragraph({
          children: [
            new TextRun({ 
              text: "本周整体健康表现优秀，各项指标均有显著提升。睡眠质量稳定，运动量达标，步数有所增加。", 
              size: 22 
            })
          ]
        }),
        new Paragraph({
          children: [
            new TextRun({ 
              text: "建议下周继续保持良好习惯，重点关注力量训练和深度睡眠质量的提升。", 
              size: 22 
            })
          ]
        }),
        
        new Paragraph({ spacing: { before: 600 } }),
        
        // 免责声明
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [9360],
          rows: [
            new TableRow({
              children: [
                new TableCell({
                  borders: thinBorders,
                  width: { size: 9360, type: WidthType.DXA },
                  shading: { fill: COLORS.light, type: ShadingType.CLEAR },
                  margins: { top: 200, bottom: 200, left: 300, right: 300 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "免责声明 Disclaimer", bold: true, size: 20, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ 
                        text: "本报告仅供参考，不作为医疗诊断依据。如有严重症状，请及时就医。", 
                        size: 18, 
                        color: COLORS.gray 
                      })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                })
              ]
            })
          ]
        })
      ]
    }]
  });
  
  return doc;
}

// ============================================
// 辅助函数
// ============================================

// 创建信息卡片
function createInfoCard(title, value, color) {
  return new TableCell({
    borders: noBorders,
    width: { size: 2340, type: WidthType.DXA },
    shading: { fill: color, type: ShadingType.CLEAR },
    margins: { top: 200, bottom: 200, left: 200, right: 200 },
    verticalAlign: VerticalAlign.CENTER,
    children: [
      new Paragraph({
        children: [new TextRun({ text: title, bold: true, size: 18, color: COLORS.white })],
        alignment: AlignmentType.CENTER
      }),
      new Paragraph({
        children: [new TextRun({ text: value, bold: true, size: 28, color: COLORS.white })],
        alignment: AlignmentType.CENTER
      })
    ]
  });
}

// 创建指标卡片
function createMetricCard(title, value, change, color) {
  return new TableCell({
    borders: thinBorders,
    width: { size: 2340, type: WidthType.DXA },
    shading: { fill: COLORS.white, type: ShadingType.CLEAR },
    margins: { top: 200, bottom: 200, left: 200, right: 200 },
    verticalAlign: VerticalAlign.CENTER,
    children: [
      new Paragraph({
        children: [new TextRun({ text: title, size: 18, color: COLORS.gray })],
        alignment: AlignmentType.CENTER
      }),
      new Paragraph({
        children: [new TextRun({ text: value, bold: true, size: 32, color: color })],
        alignment: AlignmentType.CENTER
      }),
      new Paragraph({
        children: [new TextRun({ text: change, size: 18, color: COLORS.success })],
        alignment: AlignmentType.CENTER
      })
    ]
  });
}

// 创建大指标卡片
function createLargeMetricCard(title, value, unit, color) {
  return new TableCell({
    borders: mediumBorders,
    width: { size: 3120, type: WidthType.DXA },
    shading: { fill: COLORS.white, type: ShadingType.CLEAR },
    margins: { top: 300, bottom: 300, left: 300, right: 300 },
    verticalAlign: VerticalAlign.CENTER,
    children: [
      new Paragraph({
        children: [new TextRun({ text: title, size: 20, color: COLORS.gray })],
        alignment: AlignmentType.CENTER
      }),
      new Paragraph({
        children: [
          new TextRun({ text: value, bold: true, size: 56, color: color }),
          new TextRun({ text: " " + unit, size: 24, color: COLORS.gray })
        ],
        alignment: AlignmentType.CENTER
      })
    ]
  });
}

// 创建表头
function createTableHeader(text) {
  return new TableCell({
    borders: thinBorders,
    width: { size: 2340, type: WidthType.DXA },
    shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
    margins: { top: 150, bottom: 150, left: 200, right: 200 },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      children: [new TextRun({ text: text, bold: true, size: 20, color: COLORS.white })],
      alignment: AlignmentType.CENTER
    })]
  });
}

// 创建数据行
function createDataRow(col1, col2, col3, col4, colorStr, index) {
  const bgColor = index % 2 === 0 ? COLORS.white : COLORS.light;
  const textColor = typeof colorStr === 'string' ? colorStr : COLORS.dark;
  return new TableRow({
    children: [
      new TableCell({
        borders: thinBorders,
        width: { size: 2340, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 200, right: 200 },
        verticalAlign: VerticalAlign.CENTER,
        children: [new Paragraph({
          children: [new TextRun({ text: col1, bold: true, size: 20, color: COLORS.dark })],
          alignment: AlignmentType.LEFT
        })]
      }),
      new TableCell({
        borders: thinBorders,
        width: { size: 2340, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 200, right: 200 },
        verticalAlign: VerticalAlign.CENTER,
        children: [new Paragraph({
          children: [new TextRun({ text: col2, size: 20, color: COLORS.dark })],
          alignment: AlignmentType.CENTER
        })]
      }),
      new TableCell({
        borders: thinBorders,
        width: { size: 2340, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 200, right: 200 },
        verticalAlign: VerticalAlign.CENTER,
        children: [new Paragraph({
          children: [new TextRun({ text: col3, size: 20, color: COLORS.dark })],
          alignment: AlignmentType.CENTER
        })]
      }),
      new TableCell({
        borders: thinBorders,
        width: { size: 2340, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 200, right: 200 },
        verticalAlign: VerticalAlign.CENTER,
        children: [new Paragraph({
          children: [new TextRun({ text: col4, bold: true, size: 20, color: textColor })],
          alignment: AlignmentType.CENTER
        })]
      })
    ]
  });
}

// 创建目标行
function createGoalRow(goal, target, status, index) {
  const bgColor = index % 2 === 0 ? COLORS.white : COLORS.light;
  return new TableRow({
    children: [
      new TableCell({
        borders: thinBorders,
        width: { size: 3120, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 200, right: 200 },
        verticalAlign: VerticalAlign.CENTER,
        children: [new Paragraph({
          children: [new TextRun({ text: goal, bold: true, size: 20, color: COLORS.dark })],
          alignment: AlignmentType.LEFT
        })]
      }),
      new TableCell({
        borders: thinBorders,
        width: { size: 3120, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 200, right: 200 },
        verticalAlign: VerticalAlign.CENTER,
        children: [new Paragraph({
          children: [new TextRun({ text: target, size: 20, color: COLORS.primary })],
          alignment: AlignmentType.CENTER
        })]
      }),
      new TableCell({
        borders: thinBorders,
        width: { size: 3120, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 200, right: 200 },
        verticalAlign: VerticalAlign.CENTER,
        children: [new Paragraph({
          children: [new TextRun({ text: status, size: 20, color: COLORS.gray })],
          alignment: AlignmentType.CENTER
        })]
      })
    ]
  });
}

// 创建目录项
function createTOCItem(text, page) {
  return new Paragraph({
    children: [
      new TextRun({ text: text, size: 24, color: COLORS.dark }),
      new TextRun({ text: " ", size: 24 }),
      new TextRun({ text: ".".repeat(50), size: 24, color: COLORS.lightGray }),
      new TextRun({ text: " ", size: 24 }),
      new TextRun({ text: page, bold: true, size: 24, color: COLORS.primary })
    ],
    spacing: { before: 100, after: 100 }
  });
}

// 生成文档
const doc = createProfessionalHealthReport();
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/sandbox/.openclaw/workspace/skills/data-tracker/output/健康数据周报_专业版.docx", buffer);
  console.log("✅ 健康数据周报（专业版）已生成");
});
