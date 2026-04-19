const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, LevelFormat, 
        HeadingLevel, BorderStyle, WidthType, ShadingType, PageNumber, PageBreak,
        VerticalAlign } = require('docx');
const fs = require('fs');

// 专业配色
const COLORS = {
  primary: "0078D4",
  success: "107C10",
  warning: "FF8C00",
  danger: "D13438",
  dark: "323130",
  gray: "605E5C",
  lightGray: "D2D0CE",
  light: "F3F2F1",
  white: "FFFFFF"
};

const thinBorder = { style: BorderStyle.SINGLE, size: 4, color: COLORS.lightGray };
const thinBorders = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };
const noBorder = { style: BorderStyle.NONE, size: 0, color: COLORS.white };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

function createNaturalHealthReport() {
  const doc = new Document({
    styles: {
      default: {
        document: {
          run: { font: "Microsoft YaHei", size: 22, color: COLORS.dark }
        }
      },
      paragraphStyles: [
        {
          id: "Heading1",
          name: "Heading 1",
          run: { size: 36, bold: true, font: "Microsoft YaHei", color: COLORS.primary },
          paragraph: { spacing: { before: 400, after: 200 } }
        },
        {
          id: "Heading2",
          name: "Heading 2",
          run: { size: 28, bold: true, font: "Microsoft YaHei", color: COLORS.dark },
          paragraph: { spacing: { before: 300, after: 150 } }
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
                new TextRun({ text: "张三的健康周报", bold: true, size: 20, color: COLORS.primary }),
                new TextRun({ text: "  |  2026年4月第3周", size: 18, color: COLORS.gray })
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
                new TextRun({ text: "AI健康助手  ·  第 ", size: 18, color: COLORS.gray }),
                new TextRun({ children: [PageNumber.CURRENT], size: 18, color: COLORS.primary }),
                new TextRun({ text: " 页", size: 18, color: COLORS.gray })
              ],
              alignment: AlignmentType.CENTER
            })
          ]
        })
      },
      children: [
        // ============================================
        // 开篇语 - 自然、亲切
        // ============================================
        new Paragraph({
          children: [new TextRun({ text: "张三，你好！", bold: true, size: 32, color: COLORS.primary })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "这周你的健康表现让我印象深刻。从数据来看，你正在逐步建立更健康的生活习惯，这种改变虽然细微，但非常可贵。让我详细为你分析一下这周的情况。", 
            size: 22 
          })],
          spacing: { after: 300 }
        }),
        
        // ============================================
        // 本周亮点 - 真实、具体
        // ============================================
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("本周亮点")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "这周最让我惊喜的是你的睡眠改善。记得上周你还在为睡眠不足而烦恼，这周平均睡眠时长达到了7.2小时，比上周多了将近半小时。虽然看起来不多，但对于长期睡眠不足的人来说，这是一个很好的开始。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "另一个亮点是你的运动坚持。这周你完成了5次运动，包括2次跑步、1次游泳、1次力量训练和1次瑜伽。这种多样化的运动组合非常好，既能提高心肺功能，又能增强肌肉力量，还能放松身心。特别是周三那天，你一口气走了12,300步，创下了本周的最高纪录！", 
            size: 22 
          })],
          spacing: { after: 300 }
        }),
        
        // ============================================
        // 睡眠分析 - 深入、细致
        // ============================================
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("睡眠质量分析")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "让我们深入看看你的睡眠情况。这周你的睡眠质量评分为85分，比上周的78分有了明显提升。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        // 睡眠数据表格
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [4680, 4680],
          rows: [
            new TableRow({
              children: [
                new TableCell({
                  borders: thinBorders,
                  width: { size: 4680, type: WidthType.DXA },
                  shading: { fill: COLORS.light, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "平均睡眠时长", bold: true, size: 20, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "7.2小时", bold: true, size: 32, color: COLORS.primary })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 4680, type: WidthType.DXA },
                  shading: { fill: COLORS.light, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "深度睡眠占比", bold: true, size: 20, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "23%", bold: true, size: 32, color: COLORS.success })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                })
              ]
            })
          ]
        }),
        
        new Paragraph({ spacing: { before: 200 } }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "从睡眠结构来看，你的深度睡眠占比达到了23%，这是一个不错的水平。深度睡眠是身体恢复的关键时期，对免疫系统、记忆巩固都有重要作用。不过，我注意到你的深度睡眠主要集中在凌晨2-4点，这说明你入睡时间可能偏晚。如果能提前到22:30前入睡，深度睡眠的时长可能会更长。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "另外，我观察到你在周末的睡眠质量明显下降。周六晚上你只睡了6.5小时，可能是因为周末作息不规律。建议周末也尽量保持和工作日相同的作息时间，这样能帮助身体建立稳定的生物钟。", 
            size: 22 
          })],
          spacing: { after: 300 }
        }),
        
        // ============================================
        // 运动分析 - 具体、生动
        // ============================================
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("运动情况分析")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "这周你的运动表现非常出色！总共完成了175分钟的运动，消耗了2,100千卡热量，相当于消耗了约270克脂肪。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        // 运动数据表格
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [3120, 3120, 3120],
          rows: [
            new TableRow({
              children: [
                new TableCell({
                  borders: thinBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 100, bottom: 100, left: 150, right: 150 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "运动类型", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 100, bottom: 100, left: 150, right: 150 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "运动时长", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 100, bottom: 100, left: 150, right: 150 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "消耗热量", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                })
              ]
            }),
            createExerciseRow("跑步", "60分钟", "450千卡", 0),
            createExerciseRow("游泳", "45分钟", "380千卡", 1),
            createExerciseRow("力量训练", "40分钟", "280千卡", 0),
            createExerciseRow("瑜伽", "30分钟", "150千卡", 1)
          ]
        }),
        
        new Paragraph({ spacing: { before: 200 } }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "特别值得一提的是你的跑步表现。周一和周四的两次跑步，平均配速达到了6分30秒/公里，心率控制在128次/分左右，这是一个非常健康的运动强度。既不会给心脏造成过大负担，又能有效提高心肺功能。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "不过，我注意到你的力量训练相对较少，这周只有1次。力量训练对于提高基础代谢率、预防肌肉流失非常重要。建议下周增加力量训练的频率，可以从每周2次开始，每次20-30分钟，重点锻炼核心肌群和下肢力量。", 
            size: 22 
          })],
          spacing: { after: 300 }
        }),
        
        // ============================================
        // 步数分析 - 细节、洞察
        // ============================================
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("日常活动分析")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "这周你的日均步数为8,500步，比上周增加了18%。虽然距离10,000步的目标还有一点差距，但进步非常明显。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "从每日数据来看，周三表现最好，达到了12,300步。那天你是不是去户外活动了？这种高步数的日子对提高周平均步数很有帮助。而周日相对较少，只有5,200步，可能是因为周末休息。建议周末也可以安排一些轻松的散步，既能放松身心，又能保持活动量。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "我注意到你的步数主要集中在上午和傍晚，中午时段相对较少。这可能是因为工作原因长时间坐着。建议每隔1小时起来走动5-10分钟，既能增加步数，又能缓解久坐带来的不适。", 
            size: 22 
          })],
          spacing: { after: 300 }
        }),
        
        // ============================================
        // 健康建议 - 实用、可操作
        // ============================================
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("下周建议")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "基于这周的数据分析，我为你制定了下周的健康计划。这些建议都是根据你的实际情况量身定制的，希望能帮助你继续保持良好的习惯。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("睡眠方面")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ 
            text: "尝试在22:30前入睡，这样可以让深度睡眠时段提前，获得更充分的身体恢复", 
            size: 22 
          })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ 
            text: "周末也保持规律作息，避免\"补觉\"打乱生物钟", 
            size: 22 
          })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ 
            text: "睡前1小时放下手机，可以尝试阅读或冥想来放松身心", 
            size: 22 
          })]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("运动方面")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ 
            text: "增加力量训练到每周2次，可以从简单的深蹲、俯卧撑、平板支撑开始", 
            size: 22 
          })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ 
            text: "保持现有的有氧运动频率，跑步和游泳的组合非常好", 
            size: 22 
          })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ 
            text: "运动后记得拉伸5-10分钟，预防肌肉酸痛", 
            size: 22 
          })]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("日常活动")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ 
            text: "设定每小时起身活动的提醒，哪怕只是走几步、伸个懒腰", 
            size: 22 
          })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ 
            text: "午休时间可以散步10-15分钟，既增加步数又提神", 
            size: 22 
          })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ 
            text: "周末安排一次户外活动，比如公园散步、骑行等", 
            size: 22 
          })]
        }),
        
        new Paragraph({ spacing: { before: 300 } }),
        
        // ============================================
        // 结束语 - 温暖、鼓励
        // ============================================
        new Paragraph({
          children: [new TextRun({ 
            text: "最后，我想说的是，健康是一个长期的过程，不要因为一时的数据波动而焦虑。你这周已经做得很好了，继续保持这种积极的态度，相信你会越来越健康。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "如果这周有什么特殊情况影响了你的健康计划，比如工作压力大、身体不适等，也请告诉我，我会根据实际情况调整建议。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "期待下周看到你更好的表现！", 
            size: 22,
            bold: true,
            color: COLORS.primary
          })],
          spacing: { after: 400 }
        }),
        
        // 签名
        new Paragraph({
          children: [
            new TextRun({ text: "你的健康助手", size: 20, color: COLORS.gray }),
            new TextRun({ text: "\n2026年4月18日", size: 18, color: COLORS.lightGray })
          ],
          alignment: AlignmentType.RIGHT
        })
      ]
    }]
  });
  
  return doc;
}

// 辅助函数：创建运动行
function createExerciseRow(type, duration, calories, index) {
  const bgColor = index % 2 === 0 ? COLORS.white : COLORS.light;
  return new TableRow({
    children: [
      new TableCell({
        borders: thinBorders,
        width: { size: 3120, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        children: [new Paragraph({
          children: [new TextRun({ text: type, bold: true, size: 20, color: COLORS.dark })],
          alignment: AlignmentType.CENTER
        })]
      }),
      new TableCell({
        borders: thinBorders,
        width: { size: 3120, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        children: [new Paragraph({
          children: [new TextRun({ text: duration, size: 20, color: COLORS.dark })],
          alignment: AlignmentType.CENTER
        })]
      }),
      new TableCell({
        borders: thinBorders,
        width: { size: 3120, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        children: [new Paragraph({
          children: [new TextRun({ text: calories, size: 20, color: COLORS.dark })],
          alignment: AlignmentType.CENTER
        })]
      })
    ]
  });
}

// 生成文档
const doc = createNaturalHealthReport();
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/sandbox/.openclaw/workspace/skills/data-tracker/output/健康数据周报_自然版.docx", buffer);
  console.log("✅ 健康数据周报（自然版）已生成");
});
