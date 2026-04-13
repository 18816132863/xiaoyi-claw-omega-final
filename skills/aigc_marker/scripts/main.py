#!/usr/bin/env python3
"""
AIGC Marker Skill - Add AIGC mark to existing documents

Usage:
    python main.py <file_path>

Arguments:
    file_path    Path to the target file (.docx, .pdf, .xlsx, .pptx)
"""
import argparse
import os
import sys
import uuid
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from decorators import docx_aigc_decorator, pdf_aigc_decorator, excel_aigc_decorator, ppt_aigc_decorator, md_aigc_decorator


def get_file_extension(file_path: str) -> str:
    """Get file extension in lowercase."""
    return Path(file_path).suffix.lower()


def validate_file(file_path: str) -> bool:
    """Validate if file exists and is supported."""
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False

    ext = get_file_extension(file_path)
    supported = ['.docx', '.pdf', '.xlsx', '.pptx', '.md']
    if ext not in supported:
        print(f"Error: Unsupported file format '{ext}'. Supported: {', '.join(supported)}")
        return False

    return True


def add_aigc_mark(file_path: str, request_id: str = "", add_visible_mark: bool = True):
    """Add AIGC mark to file based on its type."""
    ext = get_file_extension(file_path)

    # Generate a simple content hash based on file info
    content = f"{file_path}_{os.path.getmtime(file_path)}"

    if ext == '.docx':
        docx_aigc_decorator.decorate(file_path, content, request_id, add_visible_mark)
        print(f"[OK] AIGC mark added to Word document: {file_path}")
    elif ext == '.pdf':
        pdf_aigc_decorator.decorate(file_path, content, request_id, add_visible_mark)
        print(f"[OK] AIGC mark added to PDF document: {file_path}")
    elif ext == '.xlsx':
        excel_aigc_decorator.decorate(file_path, content, request_id, add_visible_mark)
        print(f"[OK] AIGC mark added to Excel file: {file_path}")
    elif ext == '.pptx':
        ppt_aigc_decorator.decorate(file_path, content, request_id, add_visible_mark)
        print(f"[OK] AIGC mark added to PowerPoint presentation: {file_path}")
    elif ext == '.md':
        md_aigc_decorator.decorate(file_path, content, request_id, add_visible_mark)
        print(f"[OK] AIGC mark added to Markdown file: {file_path}")
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Add AIGC mark to DOCX/PDF/XLSX/PPTX files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py document.docx
    python main.py report.pdf
    python main.py data.xlsx
    python main.py presentation.pptx
    python main.py document.docx --skip-visible  # Skip visible mark
        """
    )
    parser.add_argument('file_path', help='Path to the target file (.docx, .pdf, .xlsx, .pptx)')
    parser.add_argument('--skip-visible', action='store_true',
                        help='Skip adding visible AIGC mark, only add metadata')

    args = parser.parse_args()

    # Validate input file
    if not validate_file(args.file_path):
        sys.exit(1)

    # Generate request ID
    request_id = str(uuid.uuid4())[:8]
    print(f"Adding AIGC mark to: {args.file_path}")
    print(f"Request ID: {request_id}")
    if args.skip_visible:
        print("Mode: Implicit metadata only (no visible mark)")

    try:
        # Add AIGC mark
        add_aigc_mark(args.file_path, request_id, add_visible_mark=not args.skip_visible)
        print("Success!")

    except Exception as e:
        print(f"Error: Failed to add AIGC mark: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
