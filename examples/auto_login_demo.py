"""
自动登录示例 / Auto Login Demo
演示: 智能等待 + 智能输入 + 智能点击 + 通知
"""

import sys
sys.path.insert(0, '../src')

def auto_login_demo():
    """
    自动登录演示
    Auto Login Demo
    """
    print("🦞 AI 天眼通 - 自动登录演示")
    print("-" * 50)
    
    # 模拟登录流程
    try:
        from screen_controller.smart_controller_v2 import ai_type, ai_click
        from screen_controller.ai_enhancements import SmartWaiter
        from screen_controller.notifications import notify_success
        
        waiter = SmartWaiter()
        
        # 1. 等待登录页面加载
        print("1️⃣ 等待登录页面...")
        # waiter.wait_for_element("用户名", timeout=10)
        
        # 2. 输入用户名
        print("2️⃣ 输入用户名...")
        # ai_type("用户名", "admin")
        
        # 3. 输入密码
        print("3️⃣ 输入密码...")
        # ai_type("密码", "123456")
        
        # 4. 点击登录
        print("4️⃣ 点击登录...")
        # ai_click("登录")
        
        # 5. 等待登录成功
        print("5️⃣ 等待登录成功...")
        # waiter.wait_for_element("欢迎", timeout=10)
        
        # 6. 发送通知
        print("6️⃣ 发送成功通知...")
        # notify_success("登录成功！")
        
        print("✅ 演示完成！请取消注释实际代码运行")
        
    except ImportError as e:
        print(f"❌ 请确保已安装依赖: {e}")
        print("运行: pip install Pillow numpy uiautomation pywin32")

if __name__ == "__main__":
    auto_login_demo()
