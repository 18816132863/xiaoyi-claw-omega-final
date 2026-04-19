const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        Header, Footer, AlignmentType, LevelFormat, 
        HeadingLevel, BorderStyle, WidthType, ShadingType, PageNumber, PageBreak } = require('docx');
const fs = require('fs');

// 专业配色
const COLORS = {
  primary: "3498DB",
  secondary: "2980B9",
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

function createProfessionalWeeklyReport() {
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
                new TextRun({ text: "📄 ", size: 24 }),
                new TextRun({ text: "工作周报", bold: true, size: 20, color: COLORS.primary }),
                new TextRun({ text: "  |  技术部", size: 18, color: COLORS.gray })
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
                new TextRun({ text: "AI周报助手", bold: true, size: 18, color: COLORS.primary }),
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
        // 第1页：封面 + 基本信息
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
                      children: [new TextRun({ text: "📄", size: 100 })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "工作周报", bold: true, size: 52, color: COLORS.white })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "Weekly Work Report", size: 28, color: COLORS.white })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                })
              ]
            })
          ]
        }),
        
        new Paragraph({ spacing: { before: 400 } }),
        
        // 基本信息
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
                      children: [new TextRun({ text: "👤 报告人", bold: true, size: 20, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "张三", bold: true, size: 36, color: COLORS.primary })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "技术部 · 高级工程师", size: 18, color: COLORS.gray })],
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
                      children: [new TextRun({ text: "📅 报告周期", bold: true, size: 20, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "第16周", bold: true, size: 36, color: COLORS.secondary })],
                      alignment: AlignmentType.CENTER
                    }),
                    new Paragraph({
                      children: [new TextRun({ text: "2026.4.13 - 2026.4.19", size: 18, color: COLORS.gray })],
                      alignment: AlignmentType.CENTER
                    })
                  ]
                })
              ]
            })
          ]
        }),
        
        new Paragraph({ spacing: { before: 300 } }),
        
        // 本周概述
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("本周概述")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "本周工作整体进展顺利，主要完成了技能升级系统的开发和优化。在团队协作方面，与产品、设计部门保持良好沟通，确保项目按时推进。下周将继续推进新功能的开发，同时关注用户反馈，持续优化产品体验。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "本周亮点：成功完成了11个核心技能的商业级别升级，建立了完整的技能升级体系，包括架构设计、质量门禁、审计日志等模块。所有技能通过测试验证，达到预期目标。", 
            size: 22 
          })],
          spacing: { after: 300 }
        }),
        
        // ============================================
        // 第2页：工作完成情况
        // ============================================
        new Paragraph({ children: [new PageBreak()] }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("本周工作完成情况")]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("1. 技能升级系统开发")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "本周重点完成了技能升级系统的开发，建立了完整的升级框架和机制。系统采用六层架构设计，包括核心层、记忆层、编排层、执行层、治理层和基础设施层，确保系统的可扩展性和可维护性。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        // 工作完成表格
        new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: [6240, 3120],
          rows: [
            new TableRow({
              children: [
                new TableCell({
                  borders: thinBorders,
                  width: { size: 6240, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "工作内容", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                }),
                new TableCell({
                  borders: thinBorders,
                  width: { size: 3120, type: WidthType.DXA },
                  shading: { fill: COLORS.primary, type: ShadingType.CLEAR },
                  margins: { top: 150, bottom: 150, left: 200, right: 200 },
                  children: [new Paragraph({
                    children: [new TextRun({ text: "完成状态", bold: true, size: 20, color: COLORS.white })],
                    alignment: AlignmentType.CENTER
                  })]
                })
              ]
            }),
            createWorkRow("完成11个核心技能的商业级别升级", "✅ 已完成", 0),
            createWorkRow("建立统一的升级框架和机制", "✅ 已完成", 1),
            createWorkRow("创建批量升级脚本", "✅ 已完成", 0),
            createWorkRow("所有技能通过测试验证", "✅ 已完成", 1),
            createWorkRow("建立六层架构体系", "✅ 已完成", 0),
            createWorkRow("完善层间依赖规则", "✅ 已完成", 1),
            createWorkRow("创建质量门禁系统", "✅ 已完成", 0),
            createWorkRow("实现审计日志记录", "✅ 已完成", 1)
          ]
        }),
        
        new Paragraph({ spacing: { before: 200 } }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("2. 架构优化")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "对现有架构进行了全面优化，建立了清晰的层间依赖关系，确保系统的稳定性和可维护性。同时创建了完整的文档体系，包括架构文档、API文档、使用指南等，方便团队成员快速上手。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "建立了六层架构体系，明确各层职责", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "完善了层间依赖规则，避免循环依赖", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "创建了质量门禁系统，确保代码质量", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "实现了审计日志记录，方便问题追踪", size: 22 })]
        }),
        
        new Paragraph({ spacing: { before: 200 } }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("3. 文档完善")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "本周完成了大量文档的编写和更新工作，包括技能文档、测试报告、使用说明等。文档采用Markdown格式，方便版本管理和协作编辑。", 
            size: 22 
          })],
          spacing: { after: 200 }
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "更新了所有技能的SKILL.md文档", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "创建了完整的测试报告", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "完善了使用说明和示例代码", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "建立了文档版本管理机制", size: 22 })]
        }),
        
        new Paragraph({ children: [new PageBreak()] }),
        
        // ============================================
        // 第3页：下周计划 + 问题建议
        // ============================================
        
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("下周工作计划")]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("1. 功能增强")]
        }),
        
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "集成主流API（绘图、音乐、视频）", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "添加更多模板和场景", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "优化用户体验", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "完善错误处理机制", size: 22 })]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("2. 性能优化")]
        }),
        
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "提升响应速度，优化加载时间", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "优化资源占用，减少内存使用", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "完善缓存机制，提高访问效率", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "优化数据库查询，提高性能", size: 22 })]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("3. 用户反馈")]
        }),
        
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "收集用户意见，了解使用痛点", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "分析用户行为，优化产品设计", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "持续改进优化，提升用户满意度", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "numbers", level: 0 },
          children: [new TextRun({ text: "建立用户反馈跟踪机制", size: 22 })]
        }),
        
        new Paragraph({ spacing: { before: 300 } }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("问题与建议")]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("存在问题")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "部分技能需要进一步优化，提升输出质量", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "API集成需要完善，增加更多第三方服务支持", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "文档需要持续更新，保持与代码同步", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "测试覆盖率需要提高，确保代码质量", size: 22 })]
        }),
        
        new Paragraph({
          heading: HeadingLevel.HEADING_2,
          children: [new TextRun("改进建议")]
        }),
        
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "加强测试覆盖，建立自动化测试体系", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "完善文档说明，提供更多使用示例", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "优化用户引导，降低使用门槛", size: 22 })]
        }),
        new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [new TextRun({ text: "建立定期复盘机制，持续改进优化", size: 22 })]
        }),
        
        new Paragraph({ spacing: { before: 300 } }),
        
        // 总结
        new Paragraph({
          heading: HeadingLevel.HEADING_1,
          children: [new TextRun("总结")]
        }),
        
        new Paragraph({
          children: [new TextRun({ 
            text: "本周工作进展顺利，完成了技能升级系统的开发和优化。下周将继续推进新功能的开发，同时关注用户反馈，持续优化产品体验。感谢团队成员的支持和配合！", 
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

function createWorkRow(col1, col2, index) {
  const bgColor = index % 2 === 0 ? COLORS.white : COLORS.light;
  return new TableRow({
    children: [
      new TableCell({
        borders: thinBorders,
        width: { size: 6240, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        children: [new Paragraph({
          children: [new TextRun({ text: col1, size: 20, color: COLORS.dark })]
        })]
      }),
      new TableCell({
        borders: thinBorders,
        width: { size: 3120, type: WidthType.DXA },
        shading: { fill: bgColor, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        children: [new Paragraph({
          children: [new TextRun({ text: col2, bold: true, size: 20, color: COLORS.success })],
          alignment: AlignmentType.CENTER
        })]
      })
    ]
  });
}

// 生成文档
const doc = createProfessionalWeeklyReport();
Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/sandbox/.openclaw/workspace/skills/doc-autofill/output/工作周报_专业版.docx", buffer);
  console.log("✅ 工作周报（专业版）已生成");
});
