#!/usr/bin/env python3
"""
Test script for White Clinic Telegram Bot
This script checks if all requirements are met before running the bot
"""

import sys

def check_requirements():
    """Check if required packages are installed"""
    print("🔍 Checking requirements...")
    
    errors = []
    
    # Check Python version
    import platform
    python_version = platform.python_version_tuple()
    if int(python_version[0]) < 3 or (int(python_version[0]) == 3 and int(python_version[1]) < 8):
        errors.append(f"❌ Python 3.8+ required. Current: {platform.python_version()}")
    else:
        print(f"✅ Python {platform.python_version()}")
    
    # Check required packages
    try:
        import telegram
        print(f"✅ python-telegram-bot {telegram.__version__}")
    except ImportError:
        errors.append("❌ python-telegram-bot not installed")
    
    try:
        import dotenv
        print(f"✅ python-dotenv installed")
    except ImportError:
        errors.append("❌ python-dotenv not installed")
    
    # Check .env file
    import os
    from pathlib import Path
    
    env_file = Path(".env")
    if not env_file.exists():
        errors.append("❌ .env file not found. Run: cp .env.example .env")
    else:
        print("✅ .env file exists")
        
        # Check if .env can be loaded
        try:
            from dotenv import load_dotenv
            load_dotenv()
            token = os.getenv("BOT_TOKEN")
            if not token:
                errors.append("❌ BOT_TOKEN not set in .env")
            elif len(token) < 40:
                errors.append("❌ BOT_TOKEN looks invalid (too short)")
            else:
                print("✅ BOT_TOKEN configured")
        except Exception as e:
            errors.append(f"❌ Error loading .env: {e}")
    
    # Check bot script syntax
    try:
        with open("bot.py", "r") as f:
            compile(f.read(), "bot.py", "exec")
        print("✅ bot.py syntax is valid")
    except SyntaxError as e:
        errors.append(f"❌ Syntax error in bot.py: {e}")
    
    print()
    if errors:
        print("❌ Found the following issues:")
        for error in errors:
            print(error)
        print("\n💡 To fix these issues:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Copy .env.example to .env: cp .env.example .env")
        print("3. Edit .env and add your bot token from @BotFather")
        print("4. Run this test again")
        return False
    else:
        print("✅ All checks passed! You can run the bot:")
        print("   python bot.py")
        return True

if __name__ == "__main__":
    success = check_requirements()
    sys.exit(0 if success else 1)
