"""
AI Sky Eye - OCR and Vision Examples
====================================
Demonstrates OCR text recognition and AI vision capabilities.

Author: Xiao Liangzi
Version: 2.5
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from screen_controller import (
    capture_screen,
    vision_describe,
    vision_find,
    vision_errors,
    vision_state,
    vision_ask
)


def example_1_ocr_recognition():
    """Example 1: OCR Text Recognition"""
    print("\n" + "="*60)
    print("📖 Example 1: OCR Text Recognition")
    print("="*60)

    # Capture screen
    print("\n1. Capturing screen...")
    screenshot = capture_screen()

    # Recognize text using vision
    print("\n2. Recognizing text...")
    try:
        from screen_controller.enhanced_ocr import EnhancedOCR
        ocr = EnhancedOCR()
        result = ocr.recognize(screenshot)

        print(f"   Detected language: {result.get('language', 'unknown')}")
        print(f"   Text content:")
        print("   " + "-"*50)
        text = result.get('text', '')
        for line in text.split('\n')[:10]:  # Show first 10 lines
            if line.strip():
                print(f"   {line}")
        print("   " + "-"*50)

    except Exception as e:
        print(f"   ⚠️ OCR not available: {e}")
        print("   Install OCR engines: pip install paddleocr easyocr pytesseract")


def example_2_ai_vision_description():
    """Example 2: AI Vision Description"""
    print("\n" + "="*60)
    print("🧠 Example 2: AI Vision Description")
    print("="*60)

    print("\n1. Capturing screen...")
    screenshot = capture_screen()

    print("\n2. Analyzing with AI vision...")
    try:
        description = vision_describe(screenshot)
        print(f"\n   AI Description:")
        print("   " + "-"*50)
        print(f"   {description}")
        print("   " + "-"*50)

    except Exception as e:
        print(f"   ⚠️ Vision AI not available: {e}")
        print("   Configure AI client in settings")


def example_3_find_ui_elements():
    """Example 3: Find UI Elements"""
    print("\n" + "="*60)
    print("🔍 Example 3: Find UI Elements")
    print("="*60)

    elements_to_find = [
        "OK button",
        "Cancel button",
        "Submit button",
        "Text input field",
        "Menu bar"
    ]

    print("\nSearching for common UI elements:")
    print("-"*60)

    for element in elements_to_find:
        print(f"\n   Looking for: '{element}'")
        try:
            position = vision_find(element)
            if position:
                print(f"   ✅ Found at: {position}")
            else:
                print(f"   ❌ Not found")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")


def example_4_error_detection():
    """Example 4: Error Detection"""
    print("\n" + "="*60)
    print("⚠️ Example 4: Error Detection")
    print("="*60)

    print("\n1. Checking for error dialogs...")
    try:
        errors = vision_errors()
        if errors:
            print(f"   ⚠️ Found {len(errors)} error(s):")
            for error in errors:
                print(f"   - {error}")
        else:
            print("   ✅ No errors detected")
    except Exception as e:
        print(f"   ⚠️ Error detection not available: {e}")


def example_5_screen_state_analysis():
    """Example 5: Screen State Analysis"""
    print("\n" + "="*60)
    print("📊 Example 5: Screen State Analysis")
    print("="*60)

    print("\n1. Analyzing current screen state...")
    try:
        state = vision_state()
        print(f"\n   Current State: {state}")
        print(f"   Possible states:")
        print(f"   - LOGIN: Login screen detected")
        print(f"   - MAIN: Main application window")
        print(f"   - LOADING: Loading in progress")
        print(f"   - ERROR: Error state")
        print(f"   - POPUP: Popup/dialog present")
    except Exception as e:
        print(f"   ⚠️ State analysis not available: {e}")


def example_6_vision_qa():
    """Example 6: Vision Q&A"""
    print("\n" + "="*60)
    print("💬 Example 6: Vision Q&A")
    print("="*60)

    questions = [
        "What applications are currently open?",
        "Is there any notification on screen?",
        "What is the current time shown?"
    ]

    print("\nAsking questions about the screen:")
    print("-"*60)

    for question in questions:
        print(f"\n   Q: {question}")
        try:
            answer = vision_ask(question)
            print(f"   A: {answer}")
        except Exception as e:
            print(f"   ⚠️ Q&A not available: {e}")


def main():
    """Main function to run all examples"""
    print("\n" + "🦞"*30)
    print("AI Sky Eye v2.5 - OCR and Vision Examples")
    print("🦞"*30)

    try:
        example_1_ocr_recognition()
        example_2_ai_vision_description()
        example_3_find_ui_elements()
        example_4_error_detection()
        example_5_screen_state_analysis()
        example_6_vision_qa()

        print("\n" + "="*60)
        print("🎉 All OCR and Vision examples completed!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
