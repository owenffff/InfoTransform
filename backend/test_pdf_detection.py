#!/usr/bin/env python
"""
Quick test script to demonstrate PDF intelligent detection
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from infotransform.processors.pdf_processor import PdfAnalyzer

def test_pdf_analyzer():
    """Test the PdfAnalyzer with example scenarios"""

    print("=" * 70)
    print("PDF INTELLIGENT DETECTION TEST")
    print("=" * 70)
    print()

    analyzer = PdfAnalyzer()

    print(f"Configuration:")
    print(f"  - Min chars per page (scanned threshold): {analyzer.min_chars_per_page}")
    print(f"  - Text page threshold: {analyzer.text_page_threshold_percent}%")
    print()
    print("=" * 70)
    print()

    # Simulate different PDF scenarios
    scenarios = [
        {
            "name": "Scenario 1: All text-based pages (Business Report)",
            "pages": [500, 650, 720, 480, 590, 710, 660, 530],  # 8 pages, all text
        },
        {
            "name": "Scenario 2: Mix of text and scanned (Invoice Batch)",
            "pages": [620, 30, 680, 45, 710, 550, 20, 600, 35, 730],  # 10 pages, 4 scanned
        },
        {
            "name": "Scenario 3: Mostly scanned pages (Old Documents)",
            "pages": [25, 35, 20, 500, 30, 40, 15, 480],  # 8 pages, 6 scanned
        },
        {
            "name": "Scenario 4: All scanned pages (Photo PDF)",
            "pages": [10, 15, 20, 12, 18, 25],  # 6 pages, all scanned
        },
        {
            "name": "Scenario 5: Large document with few scanned pages",
            "pages": [600, 550, 720, 680, 590, 30, 710, 650, 720, 680,
                     590, 610, 35, 700, 660, 720, 580, 610, 690, 720],  # 20 pages, 2 scanned
        },
    ]

    for scenario in scenarios:
        print(f"{scenario['name']}")
        print("-" * 70)

        total_pages = len(scenario['pages'])
        text_pages = sum(1 for chars in scenario['pages'] if chars >= analyzer.min_chars_per_page)
        scanned_pages = total_pages - text_pages
        text_percentage = (text_pages / total_pages) * 100
        needs_ocr = text_percentage < analyzer.text_page_threshold_percent

        print(f"  Total pages: {total_pages}")
        print(f"  Text-based pages: {text_pages} ({text_percentage:.1f}%)")
        print(f"  Scanned pages: {scanned_pages}")
        print()

        if needs_ocr:
            print(f"  ❌ DECISION: Route to Azure OCR ($$$)")
            print(f"     Reason: Only {text_percentage:.1f}% have text (threshold: {analyzer.text_page_threshold_percent}%)")
        else:
            print(f"  ✅ DECISION: Use markitdown text extraction (FREE)")
            print(f"     Reason: {text_percentage:.1f}% have text (above {analyzer.text_page_threshold_percent}% threshold)")
            if scanned_pages > 0:
                print(f"     Note: {scanned_pages} scanned pages will be skipped")

        print()
        print("=" * 70)
        print()

    # Cost savings analysis
    print()
    print("COST SAVINGS ANALYSIS")
    print("=" * 70)
    print()
    print("Assuming 50 PDFs uploaded:")
    print("  - 40 text-based PDFs → markitdown extraction (FREE)")
    print("  - 10 scanned PDFs → Azure Document Intelligence OCR ($$$)")
    print()
    print("  Savings: 80% reduction in OCR costs!")
    print("  (vs. processing all 50 PDFs with Azure)")
    print()
    print("=" * 70)

if __name__ == "__main__":
    test_pdf_analyzer()
