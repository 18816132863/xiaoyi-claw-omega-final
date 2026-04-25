const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
        Header, Footer, AlignmentType, PageOrientation, LevelFormat, 
        HeadingLevel, BorderStyle, WidthType, ShadingType, PageNumber, PageBreak } = require('docx');
const fs = require('fs');

// 专业配色方案
const COLORS = {
  primary: "2E75B6",      // 主色调 - 蓝色
  secondary: "5B9BD5",    // 次色调 - 浅蓝
  accent: "ED7D31",       // 强调色 - 橙色
  success: "70AD47",      // 成功色 - 绿色
  warning: "FFC000",      // 警告色 - 黄色
  danger: "C00000",       // 危险色 - 红色
  dark: "1F4E79",         // 深色 - 深蓝
  light: "D6DCE4",        // 浅色 - 灰色
  white: "FFFFFF",
  black: "000000"
};

// 边框样式
const border = { style: BorderStyle.SINGLE, size: 1, color: COLORS.light };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorder = { style: BorderStyle.NONE, size: 0, color: COLORS.white };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

// 创建健康数据周报
function createHealthReport() {
  const doc = new Document({
    styles: {
      default: {
        document: {
          run: { font: "Microsoft YaHei", size: 22 }
        }
      },
      paragraphStyles: [
        {
          id: "Heading1",
          name: "Heading 1",
          basedOn: "Normal",
          next: "Normal",
          quickFormat: true,
          run: { size: 48, bold: true, font: "Microsoft YaHei", color: COLORS.primary },
          paragraph: { spacing: { before: 400, after: 200 }, outlineLevel: 0 }
        },
        {
          id: "Heading2",
          name: "Heading 2",
          basedOn: "Normal",
          next: "Normal",
          quickFormat: true,
          run: { size: 32, bold: true, font: "Microsoft YaHei", color: COLORS.dark },
          paragraph: { spacing: { before: 300, after: 150 }, outlineLevel: 1 }
        },
        {
          id: "Heading3",
          name: "Heading 3",
          basedOn: "Normal",
          next: "Normal",
          quickFormat: true,
          run: { size: 26, bold: true, font: "Microsoft YaHei", color: COLORS.secondary },
          paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 }
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
            style: { paragraph: { indent: { left: 720, hanging: 360 } } }
          }]
        },
        {
          reference: "numbers",
          levels: [{
            level: 0,
            format: LevelFormat.DECIMAL,
            text: "%1.",
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
            new Paragraph({
              children: [
                new TextRun({ text: "健康数据周报", bold: true, size: 20, color: COLORS.primary }),
                new TextRun({ text: "  |  ", color: COLORS.light }),
                new TextRun({ text: "2026年4月12日 - 2026年4月18日", size: 20, color: COLORS.secondary })
              ],
              alignment: AlignmentType.CENTER
            })
          ]
        })
      },
      footers: {
        default: new Footer({
          children: [
            new Paragraph({
              children: [
                new TextRun({ text: "AI健康助手", size: 18, color: COLORS.secondary }),
                new TextRun({ text: "  |  第 ", size: 18, color: COLORS.light }),
                new TextRun({ children: [PageNumber.CURRENT], size: 18, color: COLORS.primary }),
                new TextRun({ text: " 页", size: 18, color: COLORS.light })
              ],
              alignment: AlignmentType.CENTER
            })
          ]
        })
      },
      children: [
        // 封面标题
        new Paragraph({
          children: [new TextRun({ text: "健康数据周报", bold: true, size: 72, color: COLORS.primary })],
          alignment: AlignmentType.CENTER,
          spacing: { before: 2000, after: 400 }
        }),
        new Paragraph({
          children: [new TextRun({ text: "Health Weekly Report", size: 36, color: COLORS.secondary })],
          alignment: AlignmentType.CENTER,
          spacing: { after: 800 }
        }),
        new Paragraph({
          children: [new TextRun({ text: "2026年4月12日 - 2026年4月18日", size: 28, color: COLORS.dark })],
          alignment: AlignmentType.CENTER,
          spacing: { after: 2000 }
        }),
        
        // 用户信息卡片
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [4680, 4680],
          rows: [
            new TableRow({
              children: [
                new TableCell({
                  borders: noBorders,
                  width: { size: 4680, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 200, bottom: 200, left: 300, right: 300 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "用户", bold: true, size: 24, color: COLORS.white })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "张三", size: 32, bold: true, color: COLORS.white })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                }),
                new TableCell({
                  borders: noBorders,
                  width: { size: 4680, type: WidthType.DXA },
                  shading: { fill: COLORS.secondary, type: ShadingType.CLEAR },
                  margins: { top: 200, bottom: 200, left: 300, right: 300 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "健康评分", bold: true, size: 24, color: COLORS.white })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "88", size: 48, bold: true, color: COLORS.white })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                })
              ]
            })
          ]
        }),
        
        new Paragraph({ children: [new PageBreak()] }),
        
        // 第一部分：数据概览
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("一、数据概览")]
        }),
        
        new Paragraph({
          children: [new TextRun({ text: "本周健康数据整体表现良好，各项指标均有提升。", size: 22 })],
          spacing: { after: 300 }
        }),
        
        // 数据表格
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2340, 2340, 2340, 2340],
          rows: [
            new TableRow({
              children: [
                new TableCell({
                  borders,
                  width: { size: 2340, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 100, bottom: 100, left: 150, right: 150 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "指标", bold: true, size: 22, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                }),
                new TableCell({
                  borders,
                  width: { size: 2340, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 100, bottom: 100, left: 150, right: 150 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "本周平均", bold: true, size: 22, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                }),
                new TableCell({
                  borders,
                  width: { size: 2340, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 100, bottom: 100, left: 150, right: 150 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "上周平均", bold: true, size: 22, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                }),
                new TableCell({
                  borders,
                  width: { size: 2340, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 100, bottom: 100, left: 150, right: 150 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "变化趋势", bold: true, size: 22, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                })
              ]
            }),
            // 数据行
            ...createDataRows([
              ["睡眠时长", "7.2小时", "6.8小时", "↑ 5.9%", COLORS.success],
              ["运动时长", "35分钟", "28分钟", "↑ 25%", COLORS.success],
              ["步数", "8,500步", "7,200步", "↑ 18%", COLORS.success],
              ["心率", "72次/分", "75次/分", "↓ 4%", COLORS.success]
            ])
          ]
        }),
        
        new Paragraph({ children: [new PageBreak()] }),
        
        // 第二部分：睡眠分析
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("二、睡眠质量分析")]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("睡眠质量评分")]
        }),
        
        // 睡眠质量卡片
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [3120, 3120, 3120],
          rows: [
            new TableRow({
              children: [
                createMetricCard("平均睡眠时长", "7.2小时", COLORS.primary),
                createMetricCard("深度睡眠占比", "23%", COLORS.secondary),
                createMetricCard("睡眠质量评分", "85分", COLORS.success)
              ]
            })
          ]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("睡眠建议")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "✅ 睡眠质量良好，继续保持规律作息", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "⚠️ 建议增加深度睡眠时长，可通过睡前放松活动改善", size: 22 })]
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
        
        // 第三部分：运动分析
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("三、运动情况分析")]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("运动统计")]
        }),
        
        // 运动数据卡片
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [2340, 2340, 2340, 2340],
          rows: [
            new TableRow({
              children: [
                createMetricCard("运动天数", "5天", COLORS.primary),
                createMetricCard("总运动时长", "175分钟", COLORS.secondary),
                createMetricCard("消耗卡路里", "2,100千卡", COLORS.accent),
                createMetricCard("平均心率", "128次/分", COLORS.success)
              ]
            })
          ]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("运动建议")]
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
        
        // 第四部分：健康建议
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("四、综合健康建议")]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("1. 睡眠改善")]
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
          children: [new TextRun("2. 运动计划")]
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
          children: [new TextRun("3. 饮食建议")]
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
        
        // 第五部分：下周目标
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("五、下周健康目标")]
        }),
        
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [3120, 3120, 3120],
          rows: [
            new TableRow({
              children: [
                new TableCell({
                  borders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 100, bottom: 100, left: 150, right: 150 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "目标项目", bold: true, size: 22, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                }),
                new TableCell({
                  borders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 100, bottom: 100, left: 150, right: 150 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "目标值", bold: true, size: 22, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                }),
                new TableCell({
                  borders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 100, bottom: 100, left: 150, right: 150 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "当前状态", bold: true, size: 22, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                })
              ]
            }),
            ...createGoalRows([
              ["睡眠时长", "≥ 7.5小时", "待完成"],
              ["运动时长", "≥ 40分钟/天", "待完成"],
              ["步数", "≥ 9,000步/天", "待完成"],
              ["力量训练", "≥ 2次/周", "待完成"]
            ])
          ]
        }),
        
        new Paragraph({ spacing: { before: 400 } }),
        
        // 总结
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("总结")]
        }),
        
        new Paragraph({
          children: [
            new TextRun({ text: "本周整体健康表现良好，各项指标均有提升。睡眠质量稳定，运动量达标，步数有所增加。", size: 22 })
          ]
        }),
        new Paragraph({
          children: [
            new TextRun({ text: "建议下周继续保持良好习惯，重点关注力量训练和深度睡眠质量的提升。", size: 22 })
          ]
        })
      ]
    }]
  });
  
  return doc;
}

// 辅助函数：创建数据行
function createDataRows(data) {
  return data.map((row, index) => {
    const bgColor = index % 2 === 0 ? COLORS.white : "F8F9FA";
    return new TableRow({
      children: [
        new TableCell({
          borders,
          width: { size: 2340, type: WidthType.DXA },
          shading: { fill: bgColor, type: ShadingType.CLEAR },
          margins: { top: 100, bottom: 100, left: 150, right: 150 },
          children: [new Paragraph({
            children: [new TextRun({ text: row[0], bold: true, size: 22, color: COLORS.dark })],
            alignment: AlignmentType.CENTER
          })]
        }),
        new TableCell({
          borders,
          width: { size: 2340, type: WidthType.DXA },
          shading: { fill: bgColor, type: ShadingType.CLEAR },
          margins: { top: 100, bottom: 100, left: 150, right: 150 },
          children: [new Paragraph({
            children: [new TextRun({ text: row[1], size: 22 })],
            alignment: AlignmentType.CENTER
          })]
        }),
        new TableCell({
          borders,
          width: { size: 2340, type: WidthType.DXA },
          shading: { fill: bgColor, type: ShadingType.CLEAR },
          margins: { top: 100, bottom: 100, left: 150, right: 150 },
          children: [new Paragraph({
            children: [new TextRun({ text: row[2], size: 22 })],
            alignment: AlignmentType.CENTER
          })]
        }),
        new TableCell({
          borders,
          width: { size: 2340, type: WidthType.DXA },
          shading: { fill: bgColor, type: ShadingType.CLEAR },
          margins: { top: 100, bottom: 100, left: 150, right: 150 },
          children: [new Paragraph({
            children: [new TextRun({ text: row[3], bold: true, size: 22, color: row[4] })],
            alignment: AlignmentType.CENTER
          })]
        })
      ]
    });
  });
}

// 辅助函数：创建目标行
function createGoalRows(data) {
  return data.map((row, index) => {
    const bgColor = index % 2 === 0 ? COLORS.white : "F8F9FA";
    return new TableRow({
      children: row.map(cell => new TableCell({
        borders,
        width: { size: 3120, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        children: [new Paragraph({
          children: [new TextRun({ text: cell, size: 22 })],
          alignment: AlignmentType.CENTER
        })]
      }))
    });
  });
}

// 辅助函数：创建指标卡片
function createMetricCard(title, value, color) {
  return new TableCell({
    borders: noBorders,
    width: { size: 3120, type: WidthType.DXA },
    shading: { fill: color, type: ShadingType.CLEAR },
    margins: { top: 200, bottom: 200, left: 300, right: 300 },
    children: [
      new Paragraph({
        children: [new TextRun({ text: title, bold: true, size: 20, color: COLORS.white })],
        alignment: AlignmentType.CENTER
      }),
      new Paragraph({
        children: [new TextRun({ text: value, size: 36, bold: true, color: COLORS.white })],
        alignment: AlignmentType.CENTER
      })
    ]
  });
}

// 生成文档
const doc = createHealthReport();
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/sandbox/.openclaw/workspace/skills/data-tracker/output/健康数据周报_商业版.docx", buffer);
  console.log("✅ 健康数据周报（商业版）已生成");
});
