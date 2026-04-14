"""
AI Sky Eye - Basic Control Examples
====================================
Demonstrates fundamental screen control operations.

Author: Xiao Liangzi
Version: 2.5
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from screen_controller import (
    capture_screen,
    capture_screen_base64,
    move_mouse,
    click,
    type_text,
    press_hotkey,
    press_key,
    get_screen_size,
    get_mouse_position
)


def example_1_screenshot():
    """Example 1: Capture Screenshots"""
    print("\n" + "="*60)
    print("📸 Example 1: Screenshot Capture")
    print("="*60)

    # Capture full screen
    print("\n1. Capturing full screen...")
    screenshot = capture_screen()
    print(f"   Screenshot size: {screenshot.size}")

    # Capture as base64 (for API transmission)
    print("\n2. Capturing as base64...")
    base64_img = capture_screen_base64()
    print(f"   Base64 length: {len(base64_img)} characters")

    print("\n✅ Screenshot examples completed!")


def example_2_mouse_control():
    """Example 2: Mouse Control"""
    print("\n" + "="*60)
    print("🖱️ Example 2: Mouse Control")
    print("="*60)

    # Get current mouse position
    print("\n1. Getting mouse position...")
    x, y = get_mouse_position()
    print(f"   Current position: ({x}, {y})")

    # Get screen size
    print("\n2. Getting screen size...")
    width, height = get_screen_size()
    print(f"   Screen size: {width}x{height}")

    # Move mouse (commented out for safety)
    print("\n3. Mouse movement (commented):")
    print("   # move_mouse(500, 500, duration=0.5)")
    print("   # Moves mouse to position (500, 500) over 0.5 seconds")

    # Click (commented out for safety)
    print("\n4. Mouse click (commented):")
    print("   # click(500, 500, button='left')")
    print("   # Performs left click at position (500, 500)")

    print("\n✅ Mouse control examples completed!")


def example_3_keyboard_input():
    """Example 3: Keyboard Input"""
    print("\n" + "="*60)
    print("⌨️ Example 3: Keyboard Input")
    print("="*60)

    # Type text (commented out for safety)
    print("\n1. Typing text (commented):")
    print("   # type_text('Hello, World!', interval=0.01)")
    print("   # Types text with 0.01s interval between keystrokes")

    # Press single key (commented out for safety)
    print("\n2. Single key press (commented):")
    print("   # press_key('enter')")
    print("   # Presses the Enter key")

    # Press hotkey combination (commented out for safety)
    print("\n3. Hotkey combination (commented):")
    print("   # press_hotkey('ctrl', 'c')")
    print("   # Presses Ctrl+C (copy)")
    print("   # press_hotkey('ctrl', 'v')")
    print("   # Presses Ctrl+V (paste)")
    print("   # press_hotkey('alt', 'tab')")
    print("   # Presses Alt+Tab (switch window)")

    print("\n✅ Keyboard input examples completed!")


def example_4_screen_monitoring():
    """Example 4: Screen Monitoring"""
    print("\n" + "="*60)
    print("👁️ Example 4: Screen Monitoring")
    print("="*60)

    print("\n1. Monitoring screen for changes...")
    print("   (This would monitor for visual changes)")
    print("   # monitor_screen(callback=on_change, interval=1.0)")

    print("\n2. Waiting for specific element...")
    print("   (This would wait for an element to appear)")
    print("   # wait_for_element('Submit button', timeout=10)")

    print("\n✅ Screen monitoring examples completed!")


def main():
    """Main function to run all examples"""
    print("\n" + "🦞"*30)
    print("AI Sky Eye v2.5 - Basic Control Examples")
    print("🦞"*30)
    print("\n⚠️  Mouse and keyboard actions are commented out for safety.")
    print("   Uncomment them to test actual control.")

    try:
        example_1_screenshot()
        example_2_mouse_control()
        example_3_keyboard_input()
        example_4_screen_monitoring()

        print("\n" + "="*60)
        print("🎉 All basic control examples completed!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")


if __name__ == "__main__":
    main()
