const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, LevelFormat, 
        HeadingLevel, BorderStyle, WidthType, ShadingType, PageNumber, PageBreak } = require('docx');
const fs = require('fs');

// 专业配色 - 医疗健康风格
const COLORS = {
  primary: "E74C3C",
  secondary: "C0392B",
  accent: "F39C12",
  success: "27AE60",
  warning: "F39C12",
  danger: "E74C3C",
  dark: "2C3E50",
  gray: "7F8C8D",
  lightGray: "ECF0F1",
  light: "F8F9FA",
  white: "FFFFFF"
};

const thinBorder = { style: BorderStyle.SINGLE, size: 4, color: COLORS.lightGray };
const thinBorders = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };
const noBorder = { style: BorderStyle.NONE, size: 0, color: COLORS.white };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

function createProfessionalHealthAssessment() {
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
                new TextRun({ text: "🏥 ", size: 24 }),
                new TextRun({ text: "健康风险评估报告", bold: true, size: 20, color: COLORS.primary }),
                new TextRun({ text: "  |  专业健康分析", size: 18, color: COLORS.gray })
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
        // ============================================
        // 第1页：封面 + 用户信息
        // ============================================
        new Paragraph({ spacing: { before: 600 } }),
        
        // Logo和标题
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
                  margins: { top: 500, bottom: 500, left: 800, right: 800 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "🏥", size: 100 })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "健康风险评估报告", bold: true, size: 52, color: COLORS.white })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "Health Risk Assessment", size: 28, color: COLORS.white })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                })
              ]
            })
          ]
        }),
        
        new Paragraph({ spacing: { before: 400 } }),
        
        // 用户信息
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
                  margins: { top: 300, bottom: 300, left: 400, right: 400 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "👤 用户", bold: true, size: 20, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "张三", bold: true, size: 36, color: COLORS.primary })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "30岁 · 男 · 175cm · 70kg", size: 18, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 4680, type: WidthType.DXA },
                  shading: { fill: COLORS.light, type: ShadingType.CLEAR },
                  margins: { top: 300, bottom: 300, left: 400, right: 400 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "⚠️ 风险等级", bold: true, size: 20, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "中等风险", bold: true, size: 36, color: COLORS.warning })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "需要关注 · 建议改善", size: 18, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                })
              ]
            })
          ]
        }),
        
        new Paragraph({ spacing: { before: 300 } }),
        
        // 评估说明
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("评估说明")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "这份健康风险评估报告是基于你提供的症状信息和生活习惯数据生成的。报告从多个维度对你的健康状况进行了全面分析，包括症状分析、风险评估、改善建议和中医体质辨识。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "根据分析结果，你目前的健康风险等级为\"中等风险\"，主要问题集中在疲劳和失眠两个方面。这些问题虽然不会立即危及健康，但如果不及时改善，可能会逐渐加重，影响生活质量。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "建议你认真阅读本报告，按照改善建议逐步调整生活习惯。如果症状持续或加重，建议及时就医检查。", 
            size: 22 
          })],
          spacing: { after: 300 }
        }),
        
        // ============================================
        // 第2页：症状分析
        // ============================================
        new Paragraph({ children: [new PageBreak()] }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("症状分析")]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("主诉症状")]
        }),
        
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
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "症状", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "持续时间", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "严重程度", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                })
              ]
            }),
            createSymptomRow("疲劳", "2周", "中等", 0),
            createSymptomRow("失眠", "1周", "轻度", 1)
          ]
        }),
        
        new Paragraph({ spacing: { before: 200 } }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("疲劳分析")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "疲劳是现代人常见的健康问题，可能由多种原因引起。根据你的症状描述和生活习惯分析，疲劳的主要原因可能包括：", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "工作压力大，精神紧张 - 长期处于高压状态会消耗大量精力", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "睡眠质量差，休息不足 - 睡眠是恢复精力的关键", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "营养不均衡，缺乏运动 - 身体缺乏必要的营养和锻炼", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "潜在疾病（需进一步检查） - 某些疾病早期症状就是疲劳", size: 22 })]
        }),
        
        new Paragraph({ spacing: { before: 200 } }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("失眠分析")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "失眠是影响生活质量的重要因素，长期失眠会导致免疫力下降、记忆力减退、情绪波动等问题。根据你的情况，失眠的可能原因包括：", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "心理压力，焦虑情绪 - 工作和生活中的压力影响睡眠", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "作息不规律，生物钟紊乱 - 不固定的睡眠时间打乱生物钟", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "睡前使用电子设备 - 蓝光影响褪黑素分泌", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "环境因素（噪音、光线） - 睡眠环境不够舒适", size: 22 })]
        }),
        
        new Paragraph({ children: [new PageBreak()] }),
        
        // ============================================
        // 第3页：风险评估 + 改善建议
        // ============================================
        
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("风险评估")]
        }),
        
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
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "评估项目", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "评分", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "评价", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                })
              ]
            }),
            createAssessmentRow("睡眠质量", "65分", "⚠️ 需改善", 0),
            createAssessmentRow("精力状态", "70分", "⚠️ 需改善", 1),
            createAssessmentRow("心理状态", "80分", "✅ 良好", 0),
            createAssessmentRow("生活习惯", "85分", "✅ 良好", 1)
          ]
        }),
        
        new Paragraph({ spacing: { before: 200 } }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "综合评分：75分/100分。整体健康状况处于中等水平，主要问题集中在睡眠和精力方面。通过调整生活习惯和改善睡眠质量，可以有效提升整体健康水平。", 
            size: 22,
            bold: true,
            color: COLORS.primary
          })],
          spacing: { after: 300 }
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("改善建议")]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("短期建议（1-2周）")]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_3,
          children: [new TextRun("作息调整")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "22:30前入睡，保证7-8小时睡眠", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "午休20-30分钟，补充精力", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "周末保持规律作息，避免\"补觉\"", size: 22 })]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_3,
          children: [new TextRun("运动建议")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "每日散步30分钟，增加活动量", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "每周运动3次，每次30-45分钟", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "避免剧烈运动，循序渐进", size: 22 })]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_3,
          children: [new TextRun("饮食建议")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "多吃蔬菜水果，保证营养均衡", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "减少咖啡因摄入，避免影响睡眠", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "晚餐清淡为主，避免过饱", size: 22 })]
        }),
        
        new Paragraph({ spacing: { before: 200 } }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("长期建议（1-3个月）")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "定期体检：血常规、肝肾功能、甲状腺功能检查", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "心理调节：学习压力管理，培养兴趣爱好", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "保持社交：与朋友家人多交流，保持心情愉快", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "持续改善：建立健康档案，跟踪健康变化", size: 22 })]
        }),
        
        new Paragraph({ children: [new PageBreak()] }),
        
        // ============================================
        // 第4页：中医体质 + 随访计划
        // ============================================
        
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("中医体质辨识")]
        }),
        
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
                  margins: { top: 300, bottom: 300, left: 400, right: 400 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "体质类型", bold: true, size: 20, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "气虚质", bold: true, size: 48, color: COLORS.primary })],
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
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("体质特征")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "容易疲劳，气短懒言", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "自汗畏风，容易感冒", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "面色苍白，舌淡苔白", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "脉虚无力，声音低弱", size: 22 })]
        }),
        
        new Paragraph({ spacing: { before: 200 } }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("调理建议")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "食疗：黄芪、党参、山药、红枣等补气食物", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "运动：太极拳、八段锦等柔和运动", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "作息：早睡早起，避免熬夜", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "情志：保持心情舒畅，避免过度思虑", size: 22 })]
        }),
        
        new Paragraph({ spacing: { before: 300 } }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("随访计划")]
        }),
        
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [3120, 6240],
          rows: [
            new TableRow({
              children: [
                new TableCell({
                  borders: thinBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "时间", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 6240, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "随访内容", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                })
              ]
            }),
            createFollowUpRow("1周后", "症状改善情况，睡眠质量评估", 0),
            createFollowUpRow("2周后", "如无改善，建议就医检查", 1),
            createFollowUpRow("1个月后", "全面复查，调整改善方案", 0)
          ]
        }),
        
        new Paragraph({ spacing: { before: 300 } }),
        
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
                      children: [new TextRun({ text: "免责声明", bold: true, size: 20, color: COLORS.gray })],
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

function createSymptomRow(col1, col2, col3, index) {
  const bgColor = index % 2 === 0 ? COLORS.white : COLORS.light;
  return new TableRow({
    children: [
      new TableCell({
        borders: thinBorders,
        width: { size: 3120, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        children: [new Paragraph({
          children: [new TextRun({ text: col1, bold: true, size: 20, color: COLORS.dark })],
          alignment: AlignmentType.CENTER
        })]
      }),
      new TableCell({
        borders: thinBorders,
        width: { size: 3120, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        children: [new Paragraph({
          children: [new TextRun({ text: col2, size: 20, color: COLORS.dark })],
          alignment: AlignmentType.CENTER
        })]
      }),
      new TableCell({
        borders: thinBorders,
        width: { size: 3120, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        children: [new Paragraph({
          children: [new TextRun({ text: col3, size: 20, color: COLORS.warning })],
          alignment: AlignmentType.CENTER
        })]
      })
    ]
  });
}

function createAssessmentRow(col1, col2, col3, index) {
  const bgColor = index % 2 === 0 ? COLORS.white : COLORS.light;
  return new TableRow({
    children: [
      new TableCell({
        borders: thinBorders,
        width: { size: 3120, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        children: [new Paragraph({
          children: [new TextRun({ text: col1, bold: true, size: 20, color: COLORS.dark })],
          alignment: AlignmentType.CENTER
        })]
      }),
      new TableCell({
        borders: thinBorders,
        width: { size: 3120, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        children: [new Paragraph({
          children: [new TextRun({ text: col2, bold: true, size: 20, color: COLORS.primary })],
          alignment: AlignmentType.CENTER
        })]
      }),
      new TableCell({
        borders: thinBorders,
        width: { size: 3120, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        children: [new Paragraph({
          children: [new TextRun({ text: col3, size: 20, color: col3.includes('✅') ? COLORS.success : COLORS.warning })],
          alignment: AlignmentType.CENTER
        })]
      })
    ]
  });
}

function createFollowUpRow(col1, col2, index) {
  const bgColor = index % 2 === 0 ? COLORS.white : COLORS.light;
  return new TableRow({
    children: [
      new TableCell({
        borders: thinBorders,
        width: { size: 3120, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        children: [new Paragraph({
          children: [new TextRun({ text: col1, bold: true, size: 20, color: COLORS.primary })],
          alignment: AlignmentType.CENTER
        })]
      }),
      new TableCell({
        borders: thinBorders,
        width: { size: 6240, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        children: [new Paragraph({
          children: [new TextRun({ text: col2, size: 20, color: COLORS.dark })]
        })]
      })
    ]
  });
}

// 生成文档
const doc = createProfessionalHealthAssessment();
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/sandbox/.openclaw/workspace/skills/xiaoyi-health/output/健康评估_专业版.docx", buffer);
  console.log("✅ 健康评估（专业版）已生成");
});
