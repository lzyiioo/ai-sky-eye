"""
AI Agent Demo - AI 智能代理演示

功能：实时观察屏幕 + 理解指令 + 自动执行

用法:
    python ai_agent_demo.py

功能:
    1. 输入自然语言指令，AI 自动执行
    2. 实时观察屏幕，理解当前状态
    3. 自动规划执行步骤
    4. 支持语音输入 (可选)
"""

import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from screen_controller import AIAgent, VoiceAIAgent, ai_do


def demo_simple():
    """简单任务演示"""
    print("\n" + "="*60)
    print("🎯 演示 1: 简单任务")
    print("="*60)

    # 创建代理
    agent = AIAgent(auto_confirm=False, verbose=True)

    # 执行任务
    result = agent.run("截图当前屏幕")

    print(f"\n执行结果: {'成功' if result['success'] else '失败'}")
    print(f"执行了 {result['steps']} 步")


def demo_auto():
    """自动模式演示"""
    print("\n" + "="*60)
    print("🤖 演示 2: 自动模式 (无需确认)")
    print("="*60)

    # 自动执行，不询问确认
    result = ai_do("按 Ctrl+C 复制", auto=True)

    print(f"\n执行结果: {'成功' if result['success'] else '失败'}")


def demo_interactive():
    """交互式演示"""
    print("\n" + "="*60)
    print("💬 演示 3: 交互式")
    print("="*60)

    agent = AIAgent(auto_confirm=False)

    print("\n输入任务指令 (输入 'quit' 退出):")
    print("示例: '点击确定按钮', '输入用户名 admin'")
    print("-"*60)

    while True:
        task = input("\n📝 任务: ").strip()

        if task.lower() in ['quit', 'exit', 'q', '退出']:
            print("👋 再见！")
            break

        if task:
            agent.run(task)


def demo_voice():
    """语音交互演示"""
    print("\n" + "="*60)
    print("🎤 演示 4: 语音交互")
    print("="*60)

    try:
        agent = VoiceAIAgent(auto_confirm=False)
        agent.run_interactive()
    except Exception as e:
        print(f"语音模式启动失败: {e}")
        print("请安装依赖: pip install SpeechRecognition pyaudio")


def show_help():
    """显示帮助"""
    print("""
🤖 AI 智能代理演示

用法: python ai_agent_demo.py [模式]

模式:
    simple      - 简单任务演示
    auto        - 自动模式演示
    interactive - 交互式演示 (默认)
    voice       - 语音交互演示
    help        - 显示帮助

示例:
    python ai_agent_demo.py simple
    python ai_agent_demo.py interactive
    python ai_agent_demo.py voice
""")


def main():
    """主函数"""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        mode = "interactive"

    if mode == "help" or mode == "-h" or mode == "--help":
        show_help()
    elif mode == "simple":
        demo_simple()
    elif mode == "auto":
        demo_auto()
    elif mode == "interactive":
        demo_interactive()
    elif mode == "voice":
        demo_voice()
    else:
        print(f"未知模式: {mode}")
        show_help()


if __name__ == "__main__":
    main()
