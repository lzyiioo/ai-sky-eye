"""
AI Sky Eye - AI Agent Examples
==============================
Demonstrates autonomous AI agent capabilities.

Author: Xiao Liangzi
Version: 2.5
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from screen_controller import (
    AIAgent,
    VoiceAIAgent,
    ai_do
)
from screen_controller.ai_agent import (
    Action,
    ActionType,
    Observation
)


def example_1_simple_task():
    """Example 1: Simple Task Execution"""
    print("\n" + "="*60)
    print("🎯 Example 1: Simple Task Execution")
    print("="*60)

    print("\n1. Creating AI Agent (manual confirmation mode)...")
    agent = AIAgent(auto_confirm=False, verbose=True)

    print("\n2. Running simple task...")
    print("   Task: 'Take a screenshot'")

    # This would actually execute if run
    print("\n   (Execution commented for safety)")
    print("   # result = agent.run('Take a screenshot')")
    print("   # print(f'Result: {result}')")

    print("\n   Expected workflow:")
    print("   1. Agent observes current screen")
    print("   2. Plans steps to take screenshot")
    print("   3. Executes capture_screen()")
    print("   4. Returns result with success status")


def example_2_auto_mode():
    """Example 2: Auto Mode (No Confirmation)"""
    print("\n" + "="*60)
    print("🤖 Example 2: Auto Mode (No Confirmation)")
    print("="*60)

    print("\n1. Using ai_do() for quick auto-execution...")

    tasks = [
        "Press Ctrl+C to copy",
        "Move mouse to center of screen",
        "Type 'Hello World'"
    ]

    print("\n2. Example tasks:")
    for task in tasks:
        print(f"\n   Task: '{task}'")
        print(f"   Code: ai_do('{task}', auto=True)")
        print("   (Auto-executes without confirmation)")


def example_3_complex_workflow():
    """Example 3: Complex Multi-Step Workflow"""
    print("\n" + "="*60)
    print("🔄 Example 3: Complex Multi-Step Workflow")
    print("="*60)

    print("\n1. Complex task example:")
    complex_task = """
    Find the login form on screen,
    enter username 'admin' and password 'secret',
    click the login button,
    wait for the dashboard to load,
    and confirm successful login
    """

    print(f"   Task: {complex_task.strip()}")

    print("\n2. How the agent handles this:")
    print("   Step 1: Observe - Scan screen for login form")
    print("   Step 2: Plan - Break into sub-tasks")
    print("   Step 3: Execute - Find and fill username field")
    print("   Step 4: Execute - Find and fill password field")
    print("   Step 5: Execute - Find and click login button")
    print("   Step 6: Wait - Monitor for dashboard")
    print("   Step 7: Verify - Confirm success state")

    print("\n3. Agent execution:")
    print("   agent = AIAgent(auto_confirm=False)")
    print("   result = agent.run(complex_task)")
    print("   print(f'Success: {result[\"success\"]}')")
    print("   print(f'Steps: {result[\"steps\"]}')")


def example_4_voice_control():
    """Example 4: Voice Control"""
    print("\n" + "="*60)
    print("🎤 Example 4: Voice Control")
    print("="*60)

    print("\n1. Setting up voice agent...")
    print("   from screen_controller import VoiceAIAgent")
    print("   agent = VoiceAIAgent()")

    print("\n2. Voice commands you can use:")
    voice_commands = [
        "Take a screenshot",
        "Click the OK button",
        "Type my password",
        "Scroll down",
        "Open Chrome",
        "Close this window"
    ]

    for cmd in voice_commands:
        print(f"   🎤 '{cmd}'")

    print("\n3. Interactive mode:")
    print("   agent.run_interactive()")
    print("   # Continuously listens for voice commands")
    print("   # Say 'exit' or 'quit' to stop")

    print("\n   ⚠️  Requires: pip install SpeechRecognition pyaudio")


def example_5_action_types():
    """Example 5: Understanding Action Types"""
    print("\n" + "="*60)
    print("📋 Example 5: Understanding Action Types")
    print("="*60)

    print("\n1. Available Action Types:")
    print("-"*60)

    action_types = {
        ActionType.CLICK: "Mouse click on element or coordinates",
        ActionType.TYPE: "Type text into input field",
        ActionType.HOTKEY: "Press keyboard shortcut",
        ActionType.MOVE: "Move mouse to position",
        ActionType.WAIT: "Wait for condition or time",
        ActionType.SCROLL: "Scroll up/down/left/right",
        ActionType.DRAG: "Drag and drop operation",
        ActionType.FIND: "Find element on screen",
        ActionType.CAPTURE: "Take screenshot",
        ActionType.EXECUTE: "Execute custom function"
    }

    for action_type, description in action_types.items():
        print(f"   {action_type.value:12} - {description}")


def example_6_observation_system():
    """Example 6: Observation System"""
    print("\n" + "="*60)
    print("👁️ Example 6: Observation System")
    print("="*60)

    print("\n1. How the agent observes the screen:")
    print("-"*60)

    observations = [
        "Screenshot capture - Full screen image",
        "OCR text recognition - Readable text",
        "UI element detection - Buttons, inputs, etc.",
        "Visual analysis - AI description of screen",
        "Error detection - Popups, warnings",
        "State analysis - Current screen state"
    ]

    for obs in observations:
        print(f"   • {obs}")

    print("\n2. Observation data structure:")
    print("   observation = Observation(")
    print("       screenshot=image,")
    print("       text='Detected text on screen',")
    print("       elements=[button1, input1, ...],")
    print("       state='login',")
    print("       errors=[]")
    print("   )")


def example_7_custom_agent_behavior():
    """Example 7: Custom Agent Behavior"""
    print("\n" + "="*60)
    print("⚙️ Example 7: Custom Agent Behavior")
    print("="*60)

    print("\n1. Customizing agent parameters:")
    print("-"*60)

    configs = [
        ("auto_confirm=True", "Execute without asking"),
        ("auto_confirm=False", "Ask before each action"),
        ("verbose=True", "Print detailed logs"),
        ("max_steps=50", "Limit execution steps"),
        ("timeout=300", "5 minute timeout"),
    ]

    for param, description in configs:
        print(f"   {param:25} - {description}")

    print("\n2. Example configuration:")
    print("   agent = AIAgent(")
    print("       auto_confirm=False,")
    print("       verbose=True,")
    print("       max_steps=100,")
    print("       timeout=600")
    print("   )")


def example_8_error_handling():
    """Example 8: Error Handling"""
    print("\n" + "="*60)
    print("🛡️ Example 8: Error Handling")
    print("="*60)

    print("\n1. Agent error handling capabilities:")
    print("-"*60)

    capabilities = [
        "Detects when actions fail",
        "Retries failed actions (configurable)",
        "Adapts strategy on repeated failures",
        "Reports detailed error information",
        "Suggests alternative approaches"
    ]

    for cap in capabilities:
        print(f"   • {cap}")

    print("\n2. Handling agent results:")
    print("   result = agent.run('Some task')")
    print("   if result['success']:")
    print("       print('Task completed successfully')")
    print("       print(f'Steps: {result[\"steps\"]}')")
    print("   else:")
    print("       print(f'Failed: {result[\"error\"]}')")
    print("       print(f'Completed: {result[\"steps\"]} steps')")


def main():
    """Main function to run all examples"""
    print("\n" + "🦞"*30)
    print("AI Sky Eye v2.5 - AI Agent Examples")
    print("🦞"*30)

    try:
        example_1_simple_task()
        example_2_auto_mode()
        example_3_complex_workflow()
        example_4_voice_control()
        example_5_action_types()
        example_6_observation_system()
        example_7_custom_agent_behavior()
        example_8_error_handling()

        print("\n" + "="*60)
        print("🎉 All AI Agent examples completed!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
