#!/usr/bin/env python3
"""
Voyager Chat Helper
Send chat messages to the Voyager bot to provide guidance and assistance.
"""

import sys
import time
sys.path.insert(0, '/Users/dmitry/Developer/Voyager')

from voyager.env import VoyagerEnv

def interactive_chat():
    """Interactive chat session with the Voyager bot."""
    print("=== Voyager Chat Helper ===")
    print("Type messages to send to the bot. Type 'quit' to exit.")
    print("Examples:")
    print("  - 'Mine some wood logs'")
    print("  - 'Craft a pickaxe'")
    print("  - 'Go to the village'")
    print("  - 'What are you doing?'")
    print()
    
    # Create environment (this won't actually start the bot, just set up the connection)
    try:
        env = VoyagerEnv(mc_port=55594, server_port=3000)
        print("✅ Connected to Voyager environment")
    except Exception as e:
        print(f"❌ Failed to connect to Voyager: {e}")
        print("Make sure Voyager is running first!")
        return
    
    # Interactive chat loop
    while True:
        try:
            message = input("\n💬 You: ").strip()
            
            if message.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not message:
                continue
                
            # Send the message to the bot
            success = env.send_chat_message(message, sender="Human")
            
            if success:
                print(f"📤 Message sent to bot: '{message}'")
            else:
                print("❌ Failed to send message. Is Voyager running?")
                
        except KeyboardInterrupt:
            print("\n👋 Chat session ended.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    env.close()

def send_single_message(message):
    """Send a single chat message to the bot."""
    try:
        env = VoyagerEnv(mc_port=55594, server_port=3000)
        success = env.send_chat_message(message)
        env.close()
        return success
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Single message mode
        message = " ".join(sys.argv[1:])
        print(f"Sending message: '{message}'")
        send_single_message(message)
    else:
        # Interactive mode
        interactive_chat()
