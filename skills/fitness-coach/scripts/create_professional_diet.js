const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, LevelFormat, 
        HeadingLevel, BorderStyle, WidthType, ShadingType, PageNumber, PageBreak } = require('docx');
const fs = require('fs');

// 专业配色 - 健康饮食风格
const COLORS = {
  primary: "27AE60",
  secondary: "2ECC71",
  accent: "F39C12",
  success: "3498DB",
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

function createProfessionalDietPlan() {
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
            new Paragraph({
              children: [
                new TextRun({ text: "🥗 ", size: 24 }),
                new TextRun({ text: "减脂食谱方案", bold: true, size: 20, color: COLORS.primary }),
                new TextRun({ text: "  |  专业营养定制", size: 18, color: COLORS.gray })
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
                new TextRun({ text: "AI营养师", bold: true, size: 18, color: COLORS.primary }),
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
                      children: [new TextRun({ text: "🥗", size: 100 })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "减脂食谱方案", bold: true, size: 52, color: COLORS.white })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "Professional Diet Plan", size: 28, color: COLORS.white })],
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
          columnWidths: [2340, 2340, 2340, 2340],
          rows: [
            new TableRow({
              children: [
                new TableCell({
                  borders: thinBorders,
                  width: { size: 2340, type: WidthType.DXA },
                  shading: { fill: COLORS.light, type: ShadingType.CLEAR },
                  margins: { top: 200, bottom: 200, left: 200, right: 200 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "👤 用户", bold: true, size: 18, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "张三", bold: true, size: 24, color: COLORS.primary })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 2340, type: WidthType.DXA },
                  shading: { fill: COLORS.light, type: ShadingType.CLEAR },
                  margins: { top: 200, bottom: 200, left: 200, right: 200 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "🎯 目标", bold: true, size: 18, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "减脂", bold: true, size: 24, color: COLORS.accent })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 2340, type: WidthType.DXA },
                  shading: { fill: COLORS.light, type: ShadingType.CLEAR },
                  margins: { top: 200, bottom: 200, left: 200, right: 200 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "🔥 热量", bold: true, size: 18, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "1500kcal", bold: true, size: 24, color: COLORS.success })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 2340, type: WidthType.DXA },
                  shading: { fill: COLORS.light, type: ShadingType.CLEAR },
                  margins: { top: 200, bottom: 200, left: 200, right: 200 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "📅 周期", bold: true, size: 18, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "7天", bold: true, size: 24, color: COLORS.secondary })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                })
              ]
            })
          ]
        }),
        
        new Paragraph({ spacing: { before: 300 } }),
        
        // 方案说明
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("方案说明")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "这是一份为你量身定制的减脂食谱方案。根据你的身体状况和减脂目标，我为你设计了每日1500千卡的热量摄入，既能保证营养均衡，又能实现健康减脂。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "这个方案的特点是：高蛋白、适量碳水、低脂肪。蛋白质摄入量达到120g，占总热量的32%，可以有效保护肌肉，提高基础代谢率。碳水化合物控制在150g，主要来自全谷物和蔬菜，提供稳定的能量供应。脂肪控制在40g，主要来自优质植物油和坚果。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "建议配合每周3-5次有氧运动，每次30-45分钟，可以加速脂肪燃烧，提高减脂效果。同时保证每日饮水量至少2000ml，帮助代谢废物排出。", 
            size: 22 
          })],
          spacing: { after: 300 }
        }),
        
        // ============================================
        // 第2页：早餐 + 午餐
        // ============================================
        new Paragraph({ children: [new PageBreak()] }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("早餐方案")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "早餐是一天中最重要的一餐，建议在7:00-8:00之间完成。这顿早餐提供400千卡热量，包含优质蛋白质、复合碳水化合物和新鲜蔬菜，为你的一天提供充足的能量。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        // 早餐表格
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
                    children: [new TextRun({ text: "食物", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "份量", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "热量", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                })
              ]
            }),
            createFoodRow("全麦面包", "2片", "160千卡", 0),
            createFoodRow("水煮蛋", "2个", "140千卡", 1),
            createFoodRow("黄瓜", "1根", "20千卡", 0),
            createFoodRow("番茄", "1个", "20千卡", 1),
            createFoodRow("黑咖啡", "1杯", "5千卡", 0)
          ]
        }),
        
        new Paragraph({ spacing: { before: 200 } }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("营养说明")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "全麦面包：提供优质碳水化合物，富含膳食纤维，饱腹感强", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "水煮蛋：优质蛋白质来源，含有人体必需氨基酸，吸收率高", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "黄瓜和番茄：富含维生素和矿物质，热量低，增加饱腹感", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "黑咖啡：提高新陈代谢，促进脂肪燃烧，提神醒脑", size: 22 })]
        }),
        
        new Paragraph({ spacing: { before: 300 } }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("午餐方案")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "午餐建议在12:00-13:00之间完成，提供600千卡热量。这顿午餐包含糙米饭、鸡胸肉、清蒸鱼和多种蔬菜，营养均衡，蛋白质丰富。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        // 午餐表格
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [3120, 3120, 3120],
          rows: [
            new TableRow({
              children: [
                new TableCell({
                  borders: thinBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.secondary, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "食物", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.secondary, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "份量", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.secondary, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "热量", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                })
              ]
            }),
            createFoodRow("糙米饭", "1碗", "180千卡", 0),
            createFoodRow("鸡胸肉", "150g", "165千卡", 1),
            createFoodRow("清蒸鱼", "100g", "120千卡", 0),
            createFoodRow("西兰花", "200g", "60千卡", 1),
            createFoodRow("紫菜蛋花汤", "1碗", "40千卡", 0)
          ]
        }),
        
        new Paragraph({ spacing: { before: 200 } }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("营养说明")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "糙米饭：低GI主食，血糖上升缓慢，提供持久能量", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "鸡胸肉和鱼肉：优质蛋白质，脂肪含量低，易消化吸收", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "西兰花：富含维生素C和膳食纤维，抗氧化能力强", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "紫菜：富含碘和矿物质，有助于甲状腺功能和新陈代谢", size: 22 })]
        }),
        
        new Paragraph({ children: [new PageBreak()] }),
        
        // ============================================
        // 第3页：晚餐 + 购物清单
        // ============================================
        
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("晚餐方案")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "晚餐建议在18:00-19:00之间完成，提供500千卡热量。这顿晚餐以红薯、虾仁、豆腐和蔬菜为主，清淡易消化，适合晚上食用。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        // 晚餐表格
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [3120, 3120, 3120],
          rows: [
            new TableRow({
              children: [
                new TableCell({
                  borders: thinBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.accent, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "食物", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.accent, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "份量", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.accent, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "热量", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                })
              ]
            }),
            createFoodRow("红薯", "1个", "120千卡", 0),
            createFoodRow("虾仁", "100g", "95千卡", 1),
            createFoodRow("豆腐", "100g", "80千卡", 0),
            createFoodRow("菠菜", "200g", "50千卡", 1),
            createFoodRow("苹果", "1个", "95千卡", 0)
          ]
        }),
        
        new Paragraph({ spacing: { before: 200 } }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("营养说明")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "红薯：优质碳水，富含β-胡萝卜素和膳食纤维", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "虾仁和豆腐：优质蛋白质，脂肪含量低，易消化", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "菠菜：富含铁和叶酸，有助于血液循环", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "苹果：富含果胶，有助于肠道健康和排毒", size: 22 })]
        }),
        
        new Paragraph({ spacing: { before: 300 } }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("一周购物清单")]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("蛋白质类")]
        }),
        
        new Paragraph({
          numbering: { reference: "checklist", level: 0 },
          children: [new TextRun({ text: "鸡胸肉 500g", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "checklist", level: 0 },
          children: [new TextRun({ text: "鸡蛋 1盒（10个）", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "checklist", level: 0 },
          children: [new TextRun({ text: "虾仁 300g", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "checklist", level: 0 },
          children: [new TextRun({ text: "豆腐 2块", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "checklist", level: 0 },
          children: [new TextRun({ text: "鱼 300g（鲈鱼或鳕鱼）", size: 22 })]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("蔬菜类")]
        }),
        
        new Paragraph({
          numbering: { reference: "checklist", level: 0 },
          children: [new TextRun({ text: "西兰花 1颗", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "checklist", level: 0 },
          children: [new TextRun({ text: "菠菜 1把", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "checklist", level: 0 },
          children: [new TextRun({ text: "黄瓜 3根", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "checklist", level: 0 },
          children: [new TextRun({ text: "番茄 5个", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "checklist", level: 0 },
          children: [new TextRun({ text: "胡萝卜 2根", size: 22 })]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("主食类")]
        }),
        
        new Paragraph({
          numbering: { reference: "checklist", level: 0 },
          children: [new TextRun({ text: "全麦面包 1袋", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "checklist", level: 0 },
          children: [new TextRun({ text: "糙米 1袋（500g）", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "checklist", level: 0 },
          children: [new TextRun({ text: "红薯 3个", size: 22 })]
        }),
        
        new Paragraph({ children: [new PageBreak()] }),
        
        // ============================================
        // 第4页：注意事项 + 建议
        // ============================================
        
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("重要注意事项")]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("烹饪方式")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "优先选择清蒸、水煮、凉拌等低油烹饪方式", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "炒菜时使用橄榄油或椰子油，控制用油量", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "避免油炸、红烧等高油高盐烹饪方式", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "调味以清淡为主，少盐少糖", size: 22 })]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("饮水建议")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "每日饮水量至少2000ml", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "最佳饮水时间：起床后、餐前30分钟、运动后", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "避免饮用含糖饮料和碳酸饮料", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "可以喝绿茶、黑咖啡等无糖饮品", size: 22 })]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("运动配合")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "每周至少3-5次有氧运动，每次30-45分钟", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "推荐运动：快走、慢跑、游泳、骑行", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "运动时间：早餐前或晚餐后1小时", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "运动后注意补充水分和蛋白质", size: 22 })]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("作息建议")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "规律作息，避免熬夜", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "保证每日7-8小时睡眠", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "睡前3小时避免进食", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "保持心情愉快，避免压力过大", size: 22 })]
        }),
        
        new Paragraph({ spacing: { before: 300 } }),
        
        // 总结
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("总结")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "这份减脂食谱方案是根据你的身体状况和减脂目标量身定制的。只要坚持执行，配合适量运动，相信你一定能达到理想的减脂效果。记住，减脂是一个循序渐进的过程，不要急于求成，保持耐心和毅力，你一定能成功！", 
            size: 22,
            bold: true,
            color: COLORS.primary
          })],
          spacing: { after: 400 }
        })
      ]
    }]
  });
  
  return doc;
}

function createFoodRow(col1, col2, col3, index) {
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
          children: [new TextRun({ text: col3, size: 20, color: COLORS.primary })],
          alignment: AlignmentType.CENTER
        })]
      })
    ]
  });
}

// 生成文档
const doc = createProfessionalDietPlan();
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/sandbox/.openclaw/workspace/skills/fitness-coach/output/减脂食谱_专业版.docx", buffer);
  console.log("✅ 减脂食谱（专业版）已生成");
});
