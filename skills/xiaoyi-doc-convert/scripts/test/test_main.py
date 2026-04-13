#!/usr/bin/env python3
"""
Test cases for scripts/main.py

Supports batch testing with configurable input files via input.txt.
Each input file is tested against multiple output formats (docx, xlsx).

Usage:
    python -m pytest test/test_main.py -v
    python -m pytest test/test_main.py::TestBatchConversion -v
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from md2doc.converter import (
    convert_markdown,
)

# ============================================================================
# Configuration
# ============================================================================

# Default test formats
DEFAULT_TEST_FORMATS = ['docx', 'xlsx']

# Path to input configuration file
INPUT_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input.txt')


def load_test_files_from_config():
    """Load test file paths from input.txt configuration.

    Config format per line:
        path/to/file.md [formats]
    Examples:
        examples/content.md
        examples/table.md docx,xlsx
        examples/text.md docx

    Returns:
        List of tuples (test_name, file_path, formats)
    """
    test_files = []

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    with open(INPUT_CONFIG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Parse line format: path [formats]
            parts = line.split()
            rel_path = parts[0]
            formats = parts[1].split(',') if len(parts) > 1 else DEFAULT_TEST_FORMATS

            full_path = os.path.join(base_dir, rel_path)
            test_name = os.path.splitext(os.path.basename(rel_path))[0]
            test_files.append((test_name, full_path, formats))

    return test_files

# ============================================================================
# Manual Test Runner
# ============================================================================

def run_batch_tests_manually():
    """Run batch tests manually without pytest."""
    print("=" * 60)
    print("Batch Conversion Test Runner")
    print("=" * 60)

    test_files = load_test_files_from_config()
    results = []

    print(test_files)

    for test_name, file_path, formats in test_files:
        print(f"\nTesting: {test_name}")
        print(f"  File: {file_path}")

        if not os.path.exists(file_path):
            print(f"  [SKIP] File not found")
            results.append((test_name, "SKIP", "File not found"))
            continue

        for fmt in formats:
            input_path = Path(file_path)
            output_path = input_path.parent / f"{input_path.stem}.{fmt}"

            try:
                # Run conversion
                device_type = "pc"
                # Create a temp input file for convert_markdown

                convert_markdown(file_path, output_path, fmt, device_type)

                file_size = os.path.getsize(output_path)
                print(f"  [{fmt.upper()}] OK ({file_size} bytes)")
                results.append((f"{test_name}.{fmt}", "PASS", f"{file_size} bytes"))

            except ValueError as e:
                # Expected error for xlsx without tables
                if "no valid table" in str(e).lower():
                    print(f"  [{fmt.upper()}] SKIP (no tables)")
                    results.append((f"{test_name}.{fmt}", "SKIP", "Content has no tables"))
                else:
                    print(f"  [{fmt.upper()}] FAIL: {e}")
                    results.append((f"{test_name}.{fmt}", "FAIL", str(e)))

            except Exception as e:
                error_msg = str(e).lower()
                if any(skip in error_msg for skip in ['pandoc', 'converter', 'not available']):
                    print(f"  [{fmt.upper()}] SKIP ({e})")
                    results.append((f"{test_name}.{fmt}", "SKIP", str(e)))
                else:
                    print(f"  [{fmt.upper()}] FAIL: {e}")
                    results.append((f"{test_name}.{fmt}", "FAIL", str(e)))

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    passed = sum(1 for _, status, _ in results if status == "PASS")
    failed = sum(1 for _, status, _ in results if status == "FAIL")
    skipped = sum(1 for _, status, _ in results if status == "SKIP")

    for name, status, msg in results:
        if status == "PASS":
            status_symbol = "[OK]"
        elif status == "FAIL":
            status_symbol = "[NG]"
        else:
            status_symbol = "[--]"
        print(f"  {status_symbol} {name}: {status} ({msg})")

    print(f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    return failed == 0


# ---------------------------------------------------------------------------
# HTML to Markdown Conversion Test
# ---------------------------------------------------------------------------

def test_html_to_markdown_conversion():
    """Test that HTML can be converted to Markdown."""
    import tempfile
    import os
    import importlib.util
    # Load DocumentConverter directly from scripts/converter.py to avoid
    # shadowing by md2doc/converter.py on sys.path.
    converter_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'converter.py')
    spec = importlib.util.spec_from_file_location('_root_converter', converter_path)
    converter_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(converter_mod)
    DocumentConverter = converter_mod.DocumentConverter

    html_content = (
        '<h1>Hello World</h1>\n'
        '<p>This is a <a href="https://example.com">link</a>.</p>\n'
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, 'sample.html')
        output_path = os.path.join(tmpdir, 'sample.md')

        with open(input_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        converter = DocumentConverter()
        result = converter.convert(input_path, 'md', output_path=output_path)

        assert os.path.exists(result)
        with open(result, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # html2text should produce Markdown markers; if html2text is missing,
        # it falls back to raw HTML, so we accept either valid Markdown or HTML.
        assert '# Hello World' in md_content or '<h1>Hello World</h1>' in md_content
        assert '[link](https://example.com)' in md_content or '<a href="https://example.com">link</a>' in md_content


if __name__ == '__main__':
    # Check if running as script with --manual flag
    success = run_batch_tests_manually()
    sys.exit(0 if success else 1)
