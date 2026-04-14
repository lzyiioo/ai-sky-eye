"""
AI Sky Eye - Smart Brain Examples
==================================
Demonstrates intelligent decision making and context awareness.

Author: Xiao Liangzi
Version: 2.5
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from screen_controller import (
    SmartBrain,
    analyze_screen,
    check_anomaly,
    make_decision
)
from screen_controller.smart_brain import (
    ScreenState,
    AnomalyType,
    DecisionType
)


def example_1_context_analysis():
    """Example 1: Screen Context Analysis"""
    print("\n" + "="*60)
    print("🧠 Example 1: Screen Context Analysis")
    print("="*60)

    # Create SmartBrain instance
    brain = SmartBrain()

    print("\n1. Analyzing current screen context...")
    context = brain.analyze_context()

    print(f"\n   📊 Analysis Results:")
    print(f"   - State: {context.state.value}")
    print(f"   - Confidence: {context.confidence:.2%}")
    print(f"   - Layout: {context.layout}")
    print(f"   - Timestamp: {context.timestamp}")

    print(f"\n   📝 Description:")
    print(f"   {context.description[:200]}...")

    print(f"\n   🔤 Text Content (first 100 chars):")
    print(f"   {context.text_content[:100]}...")


def example_2_anomaly_detection():
    """Example 2: Anomaly Detection"""
    print("\n" + "="*60)
    print("⚠️ Example 2: Anomaly Detection")
    print("="*60)

    brain = SmartBrain()

    print("\n1. Checking for anomalies...")
    anomaly = brain.detect_anomaly()

    if anomaly:
        print(f"\n   🚨 Anomaly Detected!")
        print(f"   - Type: {anomaly.type.value}")
        print(f"   - Severity: {anomaly.severity}")
        print(f"   - Description: {anomaly.description}")
        print(f"   - Suggestion: {anomaly.suggestion}")
    else:
        print("\n   ✅ No anomalies detected")
        print("   Screen state appears normal")

    # Show all anomaly types
    print("\n2. Available Anomaly Types:")
    for anomaly_type in AnomalyType:
        if anomaly_type != AnomalyType.NONE:
            print(f"   - {anomaly_type.value}")


def example_3_intelligent_decision():
    """Example 3: Intelligent Decision Making"""
    print("\n" + "="*60)
    print("🎯 Example 3: Intelligent Decision Making")
    print("="*60)

    brain = SmartBrain()

    # Example goals
    goals = [
        "Complete the login process",
        "Fill out the registration form",
        "Handle the error dialog",
        "Wait for page to load"
    ]

    print("\n1. Making decisions for different goals:")
    print("-"*60)

    for goal in goals:
        print(f"\n   🎯 Goal: {goal}")
        decision = brain.decide_action(goal)

        print(f"   📋 Decision:")
        print(f"   - Type: {decision.type.value}")
        print(f"   - Action: {decision.action}")
        print(f"   - Reason: {decision.reason}")
        print(f"   - Confidence: {decision.confidence:.2%}")

        if decision.params:
            print(f"   - Parameters: {decision.params}")


def example_4_learning_from_results():
    """Example 4: Learning from Results"""
    print("\n" + "="*60)
    print("📚 Example 4: Learning from Results")
    print("="*60)

    brain = SmartBrain()

    print("\n1. Simulating task execution and learning...")

    # Simulate some decisions and their outcomes
    scenarios = [
        ("login", True, 2.5),
        ("form_fill", True, 5.0),
        ("click_button", False, 1.0),
        ("wait_load", True, 3.0),
    ]

    for action, success, duration in scenarios:
        context = brain.analyze_context()
        decision = brain.decide_action(action)

        brain.learn_from_result(context, decision, success, duration)

        status = "✅ Success" if success else "❌ Failed"
        print(f"   {status}: {action} ({duration:.1f}s)")

    print("\n2. Getting insights from learning...")
    insights = brain.get_insights()

    print(f"\n   📊 Learning Insights:")
    print(f"   - Total contexts analyzed: {insights['total_contexts']}")
    print(f"   - Total anomalies detected: {insights['total_anomalies']}")
    print(f"   - Total decisions made: {insights['total_decisions']}")
    print(f"   - Success rate: {insights['success_rate']:.2%}")

    if insights['suggestions']:
        print(f"\n   💡 Suggestions:")
        for suggestion in insights['suggestions']:
            print(f"   - {suggestion}")


def example_5_screen_states():
    """Example 5: Understanding Screen States"""
    print("\n" + "="*60)
    print("📺 Example 5: Understanding Screen States")
    print("="*60)

    print("\n1. Available Screen States:")
    print("-"*60)

    state_descriptions = {
        ScreenState.UNKNOWN: "Unable to determine current state",
        ScreenState.LOGIN: "Login/authentication screen",
        ScreenState.MAIN: "Main application window",
        ScreenState.LOADING: "Content is loading",
        ScreenState.ERROR: "Error state or error dialog",
        ScreenState.POPUP: "Popup or dialog box present",
        ScreenState.SUCCESS: "Success message displayed",
        ScreenState.CONFIRM: "Confirmation dialog",
        ScreenState.MENU: "Menu is open",
        ScreenState.FORM: "Form input screen"
    }

    for state, description in state_descriptions.items():
        print(f"   {state.value:12} - {description}")


def example_6_quick_functions():
    """Example 6: Quick Convenience Functions"""
    print("\n" + "="*60)
    print("⚡ Example 6: Quick Convenience Functions")
    print("="*60)

    print("\n1. Quick screen analysis:")
    print("   from screen_controller import analyze_screen")
    print("   context = analyze_screen()")
    print(f"   Current state: {analyze_screen().state.value}")

    print("\n2. Quick anomaly check:")
    print("   from screen_controller import check_anomaly")
    print("   anomaly = check_anomaly()")
    anomaly = check_anomaly()
    if anomaly:
        print(f"   Result: {anomaly.type.value}")
    else:
        print("   Result: No anomaly")

    print("\n3. Quick decision:")
    print("   from screen_controller import make_decision")
    print("   decision = make_decision('Complete login')")
    decision = make_decision("Complete login")
    print(f"   Decision: {decision.type.value} - {decision.action}")


def main():
    """Main function to run all examples"""
    print("\n" + "🦞"*30)
    print("AI Sky Eye v2.5 - Smart Brain Examples")
    print("🦞"*30)

    try:
        example_1_context_analysis()
        example_2_anomaly_detection()
        example_3_intelligent_decision()
        example_4_learning_from_results()
        example_5_screen_states()
        example_6_quick_functions()

        print("\n" + "="*60)
        print("🎉 All Smart Brain examples completed!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
