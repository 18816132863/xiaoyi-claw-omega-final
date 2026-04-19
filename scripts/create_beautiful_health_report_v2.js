const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
        Header, Footer, AlignmentType, LevelFormat, 
        HeadingLevel, BorderStyle, WidthType, ShadingType, PageNumber, PageBreak } = require('docx');
const fs = require('fs');

// 专业配色
const COLORS = {
  primary: "0078D4",
  success: "107C10",
  warning: "FF8C00",
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

function createBeautifulHealthReport() {
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
          paragraph: { 
            spacing: { before: 400, after: 200 },
            border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: COLORS.primary, space: 8 } }
          }
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
                new TextRun({ text: "🏥 ", size: 24 }),
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
                new TextRun({ text: "AI健康助手", bold: true, size: 18, color: COLORS.primary }),
                new TextRun({ text: "  ·  第 ", size: 18, color: COLORS.gray }),
                new TextRun({ children: [PageNumber.CURRENT], size: 18, color: COLORS.primary }),
                new TextRun({ text: " 页", size: 18, color: COLORS.gray })
              ],
              alignment: AlignmentType.CENTER
            })
          ]
        })
      },
      children: [
        // 封面
        new Paragraph({ spacing: { before: 1000 } }),
        
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
                  margins: { top: 600, bottom: 600, left: 800, right: 800 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "🏥", size: 120 })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "健康数据周报", bold: true, size: 56, color: COLORS.white })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "Health Weekly Report", size: 32, color: COLORS.white })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                })
              ]
            })
          ]
        }),
        
        new Paragraph({ spacing: { before: 600 } }),
        
        new Paragraph({
          children: [new TextRun({ text: "张三，你好！", bold: true, size: 40, color: COLORS.primary })],
          alignment: AlignmentType.CENTER
        }),
        
        new Paragraph({ spacing: { before: 400 } }),
        
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
                  margins: { top: 400, bottom: 400, left: 600, right: 600 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "本周健康评分", bold: true, size: 24, color: COLORS.gray })],
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
                      children: [new TextRun({ text: "优秀 · 比上周提升10分", bold: true, size: 28, color: COLORS.success })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                })
              ]
            })
          ]
        }),
        
        new Paragraph({ children: [new PageBreak()] }),
        
        // 开篇语
        new Paragraph({
          children: [new TextRun({ 
            text: "这周你的健康表现让我印象深刻。从数据来看，你正在逐步建立更健康的生活习惯，这种改变虽然细微，但非常可贵。让我详细为你分析一下这周的情况。", 
            size: 22 
          })],
          spacing: { after: 300 }
        }),
        
        // 本周亮点
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("本周亮点")]
        }),
        
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [4680, 4680],
          rows: [
            new TableRow({
              children: [
                new TableCell({
                  borders: noBorders,
                  width: { size: 4680, type: WidthType.DXA },
                  shading: { fill: COLORS.success, type: ShadingType.CLEAR },
                  margins: { top: 200, bottom: 200, left: 300, right: 300 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "😴 睡眠改善", bold: true, size: 24, color: COLORS.white })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "7.2小时", bold: true, size: 36, color: COLORS.white })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "↑ 5.9%", size: 20, color: COLORS.white })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                }),
                new TableCell({
                  borders: noBorders,
                  width: { size: 4680, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 200, bottom: 200, left: 300, right: 300 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "🏃 运动坚持", bold: true, size: 24, color: COLORS.white })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "5次运动", bold: true, size: 36, color: COLORS.white })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "175分钟", size: 20, color: COLORS.white })],
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
            text: "这周最让我惊喜的是你的睡眠改善。记得上周你还在为睡眠不足而烦恼，这周平均睡眠时长达到了7.2小时，比上周多了将近半小时。另一个亮点是你的运动坚持，特别是周三那天，你一口气走了12,300步，创下了本周的最高纪录！", 
            size: 22 
          })],
          spacing: { after: 300 }
        }),
        
        // 睡眠分析
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("睡眠质量分析")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "这周你的睡眠质量评分为85分，比上周的78分有了明显提升。从下图可以看出，你的睡眠时长整体呈上升趋势，特别是周五达到了7.8小时。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        // 睡眠趋势图
        new Paragraph({
          children: [
            new ImageRun({
              data: fs.readFileSync('/home/sandbox/.openclaw/workspace/skills/data-tracker/output/sleep_trend.png'),
              transformation: { width: 600, height: 300 }
            })
          ],
          alignment: AlignmentType.CENTER
        }),
        
        new Paragraph({ spacing: { before: 200 } }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "从睡眠结构来看，你的深度睡眠占比达到了23%，这是一个不错的水平。不过，我注意到你的深度睡眠主要集中在凌晨2-4点，这说明你入睡时间可能偏晚。如果能提前到22:30前入睡，深度睡眠的时长可能会更长。", 
            size: 22 
          })],
          spacing: { after: 300 }
        }),
        
        // 运动分析
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("运动情况分析")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "这周你的运动表现非常出色！总共完成了175分钟的运动，消耗了2,100千卡热量。从运动类型分布来看，跑步占比最大，这是很好的有氧运动。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        // 运动饼图
        new Paragraph({
          children: [
            new ImageRun({
              data: fs.readFileSync('/home/sandbox/.openclaw/workspace/skills/data-tracker/output/exercise_pie.png'),
              transformation: { width: 450, height: 450 }
            })
          ],
          alignment: AlignmentType.CENTER
        }),
        
        new Paragraph({ spacing: { before: 200 } }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "特别值得一提的是你的跑步表现。周一和周四的两次跑步，平均配速达到了6分30秒/公里，心率控制在128次/分左右，这是一个非常健康的运动强度。不过，我注意到你的力量训练相对较少，建议下周增加力量训练的频率。", 
            size: 22 
          })],
          spacing: { after: 300 }
        }),
        
        // 步数分析
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("日常活动分析")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "这周你的日均步数为8,500步，比上周增加了18%。从下图可以看出，周三表现最好，达到了12,300步，而周日相对较少，只有5,200步。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        // 步数柱状图
        new Paragraph({
          children: [
            new ImageRun({
              data: fs.readFileSync('/home/sandbox/.openclaw/workspace/skills/data-tracker/output/steps_bar.png'),
              transformation: { width: 600, height: 300 }
            })
          ],
          alignment: AlignmentType.CENTER
        }),
        
        new Paragraph({ spacing: { before: 200 } }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "我注意到你的步数主要集中在上午和傍晚，中午时段相对较少。建议每隔1小时起来走动5-10分钟，既能增加步数，又能缓解久坐带来的不适。", 
            size: 22 
          })],
          spacing: { after: 300 }
        }),
        
        // 健康维度对比
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("健康维度对比")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "从雷达图可以看出，你在运动表现方面进步最大，从上周的75分提升到90分。睡眠质量也有明显改善，从78分提升到85分。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        // 雷达图
        new Paragraph({
          children: [
            new ImageRun({
              data: fs.readFileSync('/home/sandbox/.openclaw/workspace/skills/data-tracker/output/health_radar.png'),
              transformation: { width: 450, height: 450 }
            })
          ],
          alignment: AlignmentType.CENTER
        }),
        
        new Paragraph({ children: [new PageBreak()] }),
        
        // 下周建议
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("下周建议")]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("睡眠方面")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "尝试在22:30前入睡，让深度睡眠时段提前", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "周末也保持规律作息，避免\"补觉\"打乱生物钟", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "睡前1小时放下手机，尝试阅读或冥想", size: 22 })]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("运动方面")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "增加力量训练到每周2次，从深蹲、俯卧撑开始", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "保持现有的有氧运动频率", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "运动后记得拉伸5-10分钟", size: 22 })]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("日常活动")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "设定每小时起身活动的提醒", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "午休时间散步10-15分钟", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "周末安排一次户外活动", size: 22 })]
        }),
        
        new Paragraph({ spacing: { before: 300 } }),
        
        // 结束语
        new Paragraph({
          children: [new TextRun({ 
            text: "最后，我想说的是，健康是一个长期的过程，不要因为一时的数据波动而焦虑。你这周已经做得很好了，继续保持这种积极的态度，相信你会越来越健康。期待下周看到你更好的表现！", 
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

// 生成文档
const doc = createBeautifulHealthReport();
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/sandbox/.openclaw/workspace/skills/data-tracker/output/健康数据周报_精美版.docx", buffer);
  console.log("✅ 健康数据周报（精美版）已生成");
});
