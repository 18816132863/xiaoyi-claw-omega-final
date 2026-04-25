#!/usr/bin/env bash
# xiaoyi-pdf 全量功能测试脚本
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPTS="$SKILL_DIR/scripts"
OUTDIR="$(cd "$(dirname "$0")" && pwd)"
INPUTS="$OUTDIR/inputs"

cd "$SKILL_DIR"

echo "========================================"
echo " xiaoyi-pdf 全量功能测试"
echo " 输出目录: $OUTDIR"
echo "========================================"

# ── CREATE 路由: 所有文档类型 ───────────────────────────────────────────────
echo ""
echo "▶ Route A: CREATE — 测试所有文档类型"

declare -a DOC_TYPES=(
  report proposal resume portfolio academic general
  minimal stripe diagonal frame editorial
  magazine darkroom terminal poster chinese
)

for dtype in "${DOC_TYPES[@]}"; do
  out_file="$OUTDIR/02_create_${dtype}.pdf"
  echo "  生成: $dtype -> $(basename "$out_file")"
  bash "$SCRIPTS/make.sh" run \
    --title "${dtype} 类型测试" \
    --type "$dtype" \
    --author "Test Suite" \
    --date "April 2026" \
    --subtitle "CREATE 路由 — $dtype 样式验证" \
    --accent "#2D5F8A" \
    --content "$INPUTS/content_all_blocks.json" \
    --out "$out_file" > /dev/null 2>&1 || echo "    [WARN] $dtype 生成失败"
done

# ── FILL 路由 ────────────────────────────────────────────────────────────────
echo ""
echo "▶ Route B: FILL — 表单填充"
bash "$SCRIPTS/make.sh" fill \
  --input "$INPUTS/form_input.pdf" \
  --out "$OUTDIR/03_fill_filled.pdf" \
  --values '{"FirstName": "张", "LastName": "三", "Agree": "true"}' > /dev/null 2>&1 \
  && echo "  生成: 03_fill_filled.pdf" || echo "  [WARN] FILL 失败"

# 保存 inspect 结果
python3 "$SCRIPTS/fill_inspect.py" --input "$INPUTS/form_input.pdf" --out "$OUTDIR/03_fill_inspect.json" > /dev/null 2>&1

# ── REFORMAT 路由 ────────────────────────────────────────────────────────────
echo ""
echo "▶ Route C: REFORMAT — 文档重格式化"

# Markdown -> PDF
bash "$SCRIPTS/make.sh" reformat \
  --input "$INPUTS/sample.md" \
  --title "Markdown 转 PDF 测试" \
  --type report \
  --out "$OUTDIR/04_reformat_md.pdf" > /dev/null 2>&1 \
  && echo "  生成: 04_reformat_md.pdf" || echo "  [WARN] REFORMAT md 失败"

# TXT -> PDF
bash "$SCRIPTS/make.sh" reformat \
  --input "$INPUTS/sample.txt" \
  --title "TXT 转 PDF 测试" \
  --type general \
  --out "$OUTDIR/04_reformat_txt.pdf" > /dev/null 2>&1 \
  && echo "  生成: 04_reformat_txt.pdf" || echo "  [WARN] REFORMAT txt 失败"

# JSON -> PDF (content.json 格式)
bash "$SCRIPTS/make.sh" reformat \
  --input "$INPUTS/content_all_blocks.json" \
  --title "JSON 转 PDF 测试" \
  --type proposal \
  --out "$OUTDIR/04_reformat_json.pdf" > /dev/null 2>&1 \
  && echo "  生成: 04_reformat_json.pdf" || echo "  [WARN] REFORMAT json 失败"

# ── WATERMARK 路由 ───────────────────────────────────────────────────────────
echo ""
echo "▶ Route D: WATERMARK — 水印"

# Text watermark
bash "$SCRIPTS/make.sh" watermark \
  --input "$INPUTS/simple_3page.pdf" \
  --type text \
  --text "机密文件" \
  --output "$OUTDIR/05_watermark_text.pdf" \
  --pages "1-3" \
  --font-size 48 \
  --rotate 45 \
  --opacity 0.3 > /dev/null 2>&1 \
  && echo "  生成: 05_watermark_text.pdf" || echo "  [WARN] WATERMARK text 失败"

# Image watermark (使用已有的 demo PDF 页面作为水印源)
python3 "$SCRIPTS/watermark_image.py" \
  --input "$INPUTS/simple_3page.pdf" \
  --watermark-image "$OUTDIR/01_demo.pdf" \
  --output "$OUTDIR/05_watermark_image.pdf" \
  --pages "1-3" > /dev/null 2>&1 \
  && echo "  生成: 05_watermark_image.pdf" || echo "  [WARN] WATERMARK image 失败"

# PDF watermark (使用第一页作为水印)
python3 "$SCRIPTS/watermark_merge.py" \
  --input "$INPUTS/simple_3page.pdf" \
  --watermark "$OUTDIR/01_demo.pdf" \
  --output "$OUTDIR/05_watermark_pdf.pdf" \
  --pages "1,2,3" > /dev/null 2>&1 \
  && echo "  生成: 05_watermark_pdf.pdf" || echo "  [WARN] WATERMARK pdf 失败"

# ── MERGE 路由 ───────────────────────────────────────────────────────────────
echo ""
echo "▶ Route E: MERGE — 合并 PDF"
python3 "$SCRIPTS/pdf_merge.py" \
  --inputs "$INPUTS/simple_3page.pdf" "$INPUTS/simple_2page.pdf" \
  --out "$OUTDIR/06_merged.pdf" > /dev/null 2>&1 \
  && echo "  生成: 06_merged.pdf" || echo "  [WARN] MERGE 失败"

# ── SPLIT 路由 ───────────────────────────────────────────────────────────────
echo ""
echo "▶ Route F: SPLIT — 拆分 PDF"

mkdir -p "$OUTDIR/07_split_pages"
python3 "$SCRIPTS/pdf_split.py" \
  --input "$INPUTS/simple_3page.pdf" \
  --outdir "$OUTDIR/07_split_pages" > /dev/null 2>&1 \
  && echo "  生成: 07_split_pages/page_*.pdf" || echo "  [WARN] SPLIT pages 失败"

mkdir -p "$OUTDIR/07_split_ranges"
python3 "$SCRIPTS/pdf_split.py" \
  --input "$INPUTS/simple_3page.pdf" \
  --outdir "$OUTDIR/07_split_ranges" \
  --ranges "1-2,3" > /dev/null 2>&1 \
  && echo "  生成: 07_split_ranges/range_*.pdf" || echo "  [WARN] SPLIT ranges 失败"

# ── ENCRYPT / DECRYPT 路由 ───────────────────────────────────────────────────
echo ""
echo "▶ Route G: ENCRYPT / DECRYPT — 加密解密"

python3 "$SCRIPTS/pdf_encrypt.py" \
  --input "$INPUTS/simple_3page.pdf" \
  --out "$OUTDIR/08_encrypted.pdf" \
  --password "testpass123" > /dev/null 2>&1 \
  && echo "  生成: 08_encrypted.pdf" || echo "  [WARN] ENCRYPT 失败"

python3 "$SCRIPTS/pdf_decrypt.py" \
  --input "$OUTDIR/08_encrypted.pdf" \
  --out "$OUTDIR/08_decrypted.pdf" \
  --password "testpass123" > /dev/null 2>&1 \
  && echo "  生成: 08_decrypted.pdf" || echo "  [WARN] DECRYPT 失败"

# ── EXTRACT TEXT ─────────────────────────────────────────────────────────────
echo ""
echo "▶ Route H: EXTRACT TEXT — 提取文本"
python3 "$SCRIPTS/pdf_extract_text.py" \
  --input "$INPUTS/simple_3page.pdf" \
  --out "$OUTDIR/09_extracted_text.txt" > /dev/null 2>&1 \
  && echo "  生成: 09_extracted_text.txt" || echo "  [WARN] EXTRACT TEXT 失败"

# ── EXTRACT TABLES ───────────────────────────────────────────────────────────
echo ""
echo "▶ Route I: EXTRACT TABLES — 提取表格"
python3 "$SCRIPTS/pdf_extract_tables.py" \
  --input "$INPUTS/table_source.pdf" \
  --out "$OUTDIR/10_extracted_tables.xlsx" > /dev/null 2>&1 \
  && echo "  生成: 10_extracted_tables.xlsx" || echo "  [WARN] EXTRACT TABLES xlsx 失败"

python3 "$SCRIPTS/pdf_extract_tables.py" \
  --input "$INPUTS/table_source.pdf" \
  --out "$OUTDIR/10_extracted_tables.csv" --format csv > /dev/null 2>&1 \
  && echo "  生成: 10_extracted_tables.csv" || echo "  [WARN] EXTRACT TABLES csv 失败"

echo ""
echo "========================================"
echo " 全量测试执行完毕"
echo " 请检查输出目录: $OUTDIR"
echo "========================================"
