"""
AI Sky Eye - Learning & Recording Examples
===========================================
Demonstrates action recording, replay, and learning capabilities.

Author: Xiao Liangzi
Version: 2.5
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from screen_controller import (
    LearningEngine,
    record_flow,
    replay_flow,
    optimize_flow
)
from screen_controller.learning import (
    ActionRecord,
    FlowPattern,
    LearningResult
)


def example_1_basic_recording():
    """Example 1: Basic Recording"""
    print("\n" + "="*60)
    print("🎬 Example 1: Basic Recording")
    print("="*60)

    # Create learning engine
    engine = LearningEngine()

    print("\n1. Starting recording session...")
    engine.start_recording("Sample Workflow")

    print("\n2. Simulating user actions (normally these would be captured automatically)...")

    # Simulate recording some actions
    actions = [
        ("click", "500,300", {"button": "left"}),
        ("type", "username_field", {"text": "admin"}),
        ("type", "password_field", {"text": "password123"}),
        ("click", "login_button", {}),
        ("wait", "", {"seconds": 2})
    ]

    for action_type, target, params in actions:
        engine.record_action(action_type, target, params)
        print(f"   Recorded: {action_type} -> {target}")

    print("\n3. Stopping recording...")
    flow = engine.stop_recording()

    print(f"\n   ✅ Recording Complete!")
    print(f"   - Flow ID: {flow.pattern_id}")
    print(f"   - Name: {flow.name}")
    print(f"   - Actions: {len(flow.actions)}")
    print(f"   - Created: {flow.created_at}")

    return flow


def example_2_flow_replay(flow):
    """Example 2: Flow Replay"""
    print("\n" + "="*60)
    print("▶️ Example 2: Flow Replay")
    print("="*60)

    engine = LearningEngine()

    print(f"\n1. Replaying flow: {flow.name}")
    print("   (Actions are commented out for safety)")

    # Replay with adaptive mode (adjusts to current context)
    print("\n2. Adaptive replay options:")
    print("   engine.replay(flow, adaptive=True)")
    print("   - Adjusts actions based on current screen state")
    print("   - Handles minor UI changes")

    # Replay with confirmation
    print("\n3. Confirm mode:")
    print("   engine.replay(flow, confirm=True)")
    print("   - Asks for confirmation before each action")
    print("   - Useful for debugging or sensitive operations")

    print("\n   📋 Replay would execute:")
    for i, action in enumerate(flow.actions, 1):
        print(f"   {i}. {action.action_type}: {action.target}")


def example_3_flow_optimization(flow):
    """Example 3: Flow Optimization"""
    print("\n" + "="*60)
    print("🔧 Example 3: Flow Optimization")
    print("="*60)

    engine = LearningEngine()

    print(f"\n1. Optimizing flow: {flow.name}")
    result = engine.optimize(flow)

    print(f"\n   ✅ Optimization Complete!")
    print(f"   - Original actions: {result.original_actions}")
    print(f"   - Optimized actions: {result.optimized_actions}")
    print(f"   - Removed redundancy: {result.removed_redundancy}")
    print(f"   - Added smart waits: {result.added_waits}")
    print(f"   - Confidence: {result.confidence:.2%}")

    if result.suggestions:
        print(f"\n   💡 Suggestions:")
        for suggestion in result.suggestions:
            print(f"   - {suggestion}")


def example_4_learning_patterns():
    """Example 4: Learning from Multiple Flows"""
    print("\n" + "="*60)
    print("📚 Example 4: Learning from Multiple Flows")
    print("="*60)

    engine = LearningEngine()

    print("\n1. Creating sample flows...")

    # Create multiple similar flows to demonstrate pattern learning
    flows = []

    for i in range(3):
        engine.start_recording(f"Login Flow {i+1}")

        # Similar actions with slight variations
        actions = [
            ("click", f"app_icon_{i+1}", {}),
            ("type", "username", {"text": f"user{i+1}"}),
            ("type", "password", {"text": "pass"}),
            ("click", "login", {}),
        ]

        for action_type, target, params in actions:
            engine.record_action(action_type, target, params)

        flow = engine.stop_recording()
        flows.append(flow)
        print(f"   Created: {flow.name}")

    print(f"\n2. Learning patterns from {len(flows)} flows...")
    patterns = engine.learn_from_flows(flows)

    print(f"\n   ✅ Learned {len(patterns)} common pattern(s)")
    for pattern in patterns:
        print(f"   - {pattern.name}")


def example_5_flow_management():
    """Example 5: Flow Management"""
    print("\n" + "="*60)
    print("📂 Example 5: Flow Management")
    print("="*60)

    engine = LearningEngine()

    print("\n1. Listing all saved flows...")
    flows = engine.list_flows()

    print(f"   Found {len(flows)} saved flow(s):")
    for flow in flows:
        print(f"   - {flow.name} (ID: {flow.pattern_id})")
        print(f"     Actions: {len(flow.actions)}, Success: {flow.success_count}")

    if flows:
        print("\n2. Flow operations:")
        sample_flow = flows[0]

        print(f"\n   Getting flow by ID:")
        print(f"   flow = engine.get_flow('{sample_flow.pattern_id}')")
        retrieved = engine.get_flow(sample_flow.pattern_id)
        print(f"   Retrieved: {retrieved.name if retrieved else 'Not found'}")

        print(f"\n   Flow can be deleted:")
        print(f"   engine.delete_flow('{sample_flow.pattern_id}')")


def example_6_quick_functions():
    """Example 6: Quick Convenience Functions"""
    print("\n" + "="*60)
    print("⚡ Example 6: Quick Convenience Functions")
    print("="*60)

    print("\n1. Quick record:")
    print("   from screen_controller import record_flow")
    print("   engine = record_flow('My Workflow')")
    print("   # ... perform actions ...")
    print("   flow = engine.stop_recording()")

    print("\n2. Quick replay:")
    print("   from screen_controller import replay_flow")
    print("   result = replay_flow('flow_id_here')")
    print("   # Returns: {'success': True, 'completed': 5, ...}")

    print("\n3. Quick optimize:")
    print("   from screen_controller import optimize_flow")
    print("   result = optimize_flow('flow_id_here')")
    print("   # Returns LearningResult with optimization details")


def example_7_action_record_structure():
    """Example 7: Understanding ActionRecord Structure"""
    print("\n" + "="*60)
    print("📝 Example 7: Understanding ActionRecord Structure")
    print("="*60)

    print("\n1. ActionRecord fields:")
    print("-"*60)

    fields = {
        "action_type": "Type of action: click, type, hotkey, move, wait",
        "target": "Target element or coordinates",
        "params": "Additional parameters for the action",
        "timestamp": "When the action was recorded",
        "screenshot_hash": "Hash of screen state at recording time",
        "context": "Screen context when action was recorded",
        "duration": "How long the action took to execute",
        "success": "Whether the action succeeded"
    }

    for field, description in fields.items():
        print(f"   {field:20} - {description}")

    print("\n2. Creating a manual ActionRecord:")
    print("   record = ActionRecord(")
    print("       action_type='click',")
    print("       target='submit_button',")
    print("       params={'button': 'left'},")
    print("       timestamp=time.time(),")
    print("       screenshot_hash='abc123',")
    print("       context={'state': 'form'},")
    print("       duration=0.5,")
    print("       success=True")
    print("   )")


def main():
    """Main function to run all examples"""
    print("\n" + "🦞"*30)
    print("AI Sky Eye v2.5 - Learning & Recording Examples")
    print("🦞"*30)

    try:
        # Example 1 creates a flow used by subsequent examples
        flow = example_1_basic_recording()
        example_2_flow_replay(flow)
        example_3_flow_optimization(flow)
        example_4_learning_patterns()
        example_5_flow_management()
        example_6_quick_functions()
        example_7_action_record_structure()

        print("\n" + "="*60)
        print("🎉 All Learning & Recording examples completed!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
