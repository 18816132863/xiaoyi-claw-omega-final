const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, LevelFormat, 
        HeadingLevel, BorderStyle, WidthType, ShadingType, PageNumber, PageBreak } = require('docx');
const fs = require('fs');

// 专业配色 - 小说创作风格
const COLORS = {
  primary: "9B59B6",
  secondary: "8E44AD",
  accent: "E74C3C",
  success: "27AE60",
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

function createProfessionalNovel() {
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
                new TextRun({ text: "📚 ", size: 24 }),
                new TextRun({ text: "重生之都市巅峰", bold: true, size: 20, color: COLORS.primary }),
                new TextRun({ text: "  |  都市重生", size: 18, color: COLORS.gray })
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
                new TextRun({ text: "AI小说创作", bold: true, size: 18, color: COLORS.primary }),
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
        // 第1页：封面 + 作品信息
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
                      children: [new TextRun({ text: "📚", size: 100 })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "重生之都市巅峰", bold: true, size: 52, color: COLORS.white })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "Rebirth: Urban Peak", size: 28, color: COLORS.white })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                })
              ]
            })
          ]
        }),
        
        new Paragraph({ spacing: { before: 400 } }),
        
        // 作品信息
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
                      children: [new TextRun({ text: "📖 题材", bold: true, size: 20, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "都市重生", bold: true, size: 36, color: COLORS.primary })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "爽文 · 逆袭 · 商战", size: 18, color: COLORS.gray })],
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
                      children: [new TextRun({ text: "✍️ 作者", bold: true, size: 20, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "AI创作", bold: true, size: 36, color: COLORS.secondary })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "2026年4月18日", size: 18, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                })
              ]
            })
          ]
        }),
        
        new Paragraph({ spacing: { before: 300 } }),
        
        // 作品简介
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("作品简介")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "林峰，一个在商海沉浮中失败的创业者，在一场车祸中意外重生回到了十年前。带着前世的记忆和经验，他决心改写命运，在都市商战中崛起，最终站在巅峰俯瞰众生。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "这是一个关于重生、逆袭、商战的故事。主角林峰拥有未来十年的记忆，知道哪些行业会崛起，哪些股票会暴涨，哪些机会稍纵即逝。但他也面临着来自前世敌人的威胁，以及如何在改变命运的同时，不重蹈覆辙的挑战。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "故事节奏紧凑，爽点密集，既有商业博弈的智慧较量，也有情感纠葛的人性探索。适合喜欢都市重生、商战爽文的读者。", 
            size: 22 
          })],
          spacing: { after: 300 }
        }),
        
        // ============================================
        // 第2页：世界观设定
        // ============================================
        new Paragraph({ children: [new PageBreak()] }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("世界观设定")]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("时代背景")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "故事发生在2016年的中国都市。这是一个充满机遇的时代，移动互联网蓬勃发展，共享经济方兴未艾，人工智能初露锋芒。对于拥有未来十年记忆的林峰来说，这是一个遍地黄金的时代。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("社会规则")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "这是一个弱肉强食的商业世界。强者制定规则，弱者遵守规则。金钱、权力、人脉是衡量一个人成功的标准。但同时，这也是一个法治社会，任何违法行为都会受到法律的制裁。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("力量体系")]
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
                    children: [new TextRun({ text: "力量类型", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 6240, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "说明", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                })
              ]
            }),
            createPowerRow("商业帝国", "通过创业、投资建立商业版图，掌控经济命脉", 0),
            createPowerRow("科技巨头", "掌握核心技术，引领行业发展，拥有话语权", 1),
            createPowerRow("人脉网络", "建立广泛的社会关系，获得信息优势和资源支持", 0),
            createPowerRow("资本力量", "通过资本运作，收购、并购、投资实现快速扩张", 1)
          ]
        }),
        
        new Paragraph({ spacing: { before: 300 } }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("主角人设")]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("基本信息")]
        }),
        
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
                  margins: { top: 200, bottom: 200, left: 300, right: 300 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "姓名", bold: true, size: 20, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "林峰", bold: true, size: 28, color: COLORS.primary })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 4680, type: WidthType.DXA },
                  shading: { fill: COLORS.light, type: ShadingType.CLEAR },
                  margins: { top: 200, bottom: 200, left: 300, right: 300 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "年龄", bold: true, size: 20, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "28岁（重生后）", bold: true, size: 28, color: COLORS.secondary })],
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
          children: [new TextRun("性格特点")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "坚韧不拔，永不放弃 - 前世的失败让他更加坚强", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "有仇必报，快意恩仇 - 对待敌人绝不手软", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "智勇双全，善于谋略 - 商战中的运筹帷幄", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "重情重义，护短护犊 - 对待朋友和家人全力保护", size: 22 })]
        }),
        
        new Paragraph({ children: [new PageBreak()] }),
        
        // ============================================
        // 第3页：第一章正文
        // ============================================
        
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("第1章 重生归来")]
        }),
        
        new Paragraph({
          children: [new TextRun({ text: "2026年4月18日 晴", size: 20, color: COLORS.gray })],
          alignment: AlignmentType.RIGHT,
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "林峰睁开眼睛，发现自己躺在熟悉的出租屋里。墙上贴着泛黄的海报，桌上堆满了泡面盒和可乐瓶。阳光从窗帘的缝隙中透进来，在地板上投下一道道光斑。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "\"我...重生了？\"", 
            size: 22,
            bold: true
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "林峰难以置信地看着自己的双手，年轻、有力，没有那道车祸留下的伤疤。他猛地坐起身，看向床头的日历——2016年4月18日。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "十年前。", 
            size: 22,
            bold: true,
            color: COLORS.accent
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "那个改变他命运的日子。", 
            size: 22,
            bold: true,
            color: COLORS.accent
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "林峰深吸一口气，脑海中浮现出前世的记忆：创业失败、负债累累、众叛亲离，最后在一场车祸中结束了自己短暂的一生。那些痛苦的画面如同潮水般涌来，让他几乎窒息。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "\"这一次，我绝不会重蹈覆辙。\"", 
            size: 22,
            bold: true
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "林峰握紧拳头，眼中闪过一丝坚定。他拥有未来十年的记忆，知道哪些行业会崛起，哪些股票会暴涨，哪些机会稍纵即逝。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "这一次，他要站在巅峰，俯瞰众生。", 
            size: 22,
            bold: true,
            color: COLORS.primary
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "手机突然响起，是母亲打来的电话。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "\"小峰啊，你爸的手术费还差十万，你那边能想办法吗？\"", 
            size: 22,
            italics: true
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "林峰心中一痛。前世，正是因为拿不出这笔钱，父亲的病情一拖再拖，最终...", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "\"妈，别担心，钱的事我来想办法。\"", 
            size: 22,
            bold: true
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "挂断电话，林峰看向窗外。阳光正好，微风不燥。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "新的生活，开始了。", 
            size: 22,
            bold: true,
            color: COLORS.success
          })],
          spacing: { after: 400 }
        }),
        
        // 章节统计
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [3120, 3120, 3120],
          rows: [
            new TableRow({
              children: [
                new TableCell({
                  borders: thinBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.light, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "字数", bold: true, size: 20, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "856字", bold: true, size: 24, color: COLORS.primary })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.light, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "爽点", bold: true, size: 20, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "重生·金手指", bold: true, size: 24, color: COLORS.accent })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.light, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [
                    new Paragraph({
                      children: [new TextRun({ text: "下章预告", bold: true, size: 20, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "第一桶金", bold: true, size: 24, color: COLORS.success })],
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

function createPowerRow(col1, col2, index) {
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
const doc = createProfessionalNovel();
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/sandbox/.openclaw/workspace/skills/novel-generator/output/小说创作_专业版.docx", buffer);
  console.log("✅ 小说创作（专业版）已生成");
});
