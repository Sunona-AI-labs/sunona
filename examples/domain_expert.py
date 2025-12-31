"""
Sunona Voice AI - Domain Expert Example

Demonstrates domain-specialized voice agents using templates.

Usage:
    python examples/domain_expert.py
    
Features:
- Multiple domain templates
- Tool-enabled conversations
- Data extraction
- Domain-specific prompts
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sunona.templates import get_template, list_templates
from sunona.templates.data_extractor import DataExtractor


def display_menu():
    """Display available domains."""
    print("\n" + "=" * 60)
    print("🎯 Sunona AI - Domain Expert Demo")
    print("=" * 60)
    print("\nAvailable Domains:\n")
    
    templates = list_templates()
    for i, (name, desc) in enumerate(templates.items(), 1):
        print(f"  {i}. {name.capitalize():12} - {desc}")
    
    print("\n  0. Exit")
    return list(templates.keys())


def display_template_info(template):
    """Display template information."""
    print("\n" + "-" * 60)
    print(f"📋 Domain: {template.domain_name.upper()}")
    print(f"📝 {template.domain_description}")
    print("-" * 60)
    
    # Show tools
    tools = template.get_tools()
    print(f"\n🔧 Available Tools ({len(tools)}):")
    for tool in tools[:5]:  # Show first 5
        print(f"   • {tool.name}: {tool.description[:50]}...")
    if len(tools) > 5:
        print(f"   ... and {len(tools) - 5} more")
    
    # Show extraction fields
    fields = template.get_extraction_fields()
    required = [f.name for f in fields if f.required]
    print(f"\n📊 Extraction Fields ({len(fields)}):")
    print(f"   Required: {', '.join(required) if required else 'None'}")
    
    # Show sample prompt
    print("\n📜 System Prompt Preview:")
    prompt = template.get_system_prompt()
    lines = prompt.split('\n')[:10]
    for line in lines:
        print(f"   {line[:60]}...")


def simulate_conversation(template):
    """Simulate a conversation with the domain expert."""
    print("\n" + "=" * 60)
    print(f"💬 Simulating {template.domain_name.capitalize()} Conversation")
    print("=" * 60)
    
    # Sample conversations for each domain
    conversations = {
        "hospitality": [
            {"role": "user", "content": "Hi, I'd like to book a room for next weekend"},
            {"role": "assistant", "content": "I'd be happy to help you book a room. May I have your name please?"},
            {"role": "user", "content": "My name is John Smith, and my email is john.smith@email.com"},
            {"role": "assistant", "content": "Thank you, John. For how many nights would you like to stay?"},
            {"role": "user", "content": "2 nights, checking in December 28th. My phone is 555-123-4567"},
        ],
        "support": [
            {"role": "user", "content": "I have a problem with my order"},
            {"role": "assistant", "content": "I'm sorry to hear that. Can you provide your order number?"},
            {"role": "user", "content": "Yes, it's ORD-12345. The package was damaged"},
            {"role": "assistant", "content": "I apologize for the inconvenience. Let me look up that order."},
        ],
        "recruitment": [
            {"role": "user", "content": "Hi, I'm calling about the software engineer position"},
            {"role": "assistant", "content": "Great! Can I have your name and contact information?"},
            {"role": "user", "content": "I'm Sarah Johnson, email sarah.j@email.com, phone 555-987-6543"},
            {"role": "assistant", "content": "Thank you Sarah. How many years of experience do you have?"},
            {"role": "user", "content": "I have 5 years of experience at Google"},
        ],
        "healthcare": [
            {"role": "user", "content": "I need to schedule an appointment with a doctor"},
            {"role": "assistant", "content": "I can help with that. Can I have your name and date of birth?"},
            {"role": "user", "content": "My name is Maria Garcia, born March 15, 1985"},
            {"role": "assistant", "content": "Thank you Maria. What is the reason for your visit?"},
            {"role": "user", "content": "I've been having headaches. My phone is 555-111-2222"},
        ],
        "retail": [
            {"role": "user", "content": "Where is my order?"},
            {"role": "assistant", "content": "I can help track your order. What's your order number?"},
            {"role": "user", "content": "Order number is #98765432, email jane@email.com"},
        ],
        "banking": [
            {"role": "user", "content": "I need to check my account balance"},
            {"role": "assistant", "content": "I can help with that. For security, can I verify your name and date of birth?"},
            {"role": "user", "content": "Robert Brown, born January 20, 1980. Account ending in 4567"},
        ],
    }
    
    # Get conversation for this domain
    conv = conversations.get(template.domain_name, conversations["support"])
    
    print("\nConversation:")
    for msg in conv:
        role = "👤 User" if msg["role"] == "user" else "🤖 Agent"
        print(f"{role}: {msg['content']}")
    
    # Extract data
    print("\n" + "-" * 60)
    print("📊 Extracted Data:")
    print("-" * 60)
    
    extractor = DataExtractor(template)
    full_text = " ".join(msg["content"] for msg in conv)
    result = extractor.extract_from_text(full_text)
    
    for name, field in result.fields.items():
        status = "✓" if field.validated else "?"
        print(f"   {status} {name}: {field.value} (confidence: {field.confidence:.0%})")
    
    if result.missing_required:
        print(f"\n   ⚠️  Missing required: {', '.join(result.missing_required)}")
        prompt = extractor.get_prompt_for_missing()
        if prompt:
            print(f"   💡 Suggested prompt: {prompt}")


async def main():
    """Main demo loop."""
    while True:
        domains = display_menu()
        
        try:
            choice = input("\nSelect domain (0-6): ").strip()
            
            if choice == "0" or choice.lower() == "exit":
                print("\nGoodbye! 👋")
                break
            
            idx = int(choice) - 1
            if 0 <= idx < len(domains):
                domain = domains[idx]
                
                # Create template
                template = get_template(
                    domain,
                    business_name="Demo Company",
                    agent_name="Alex",
                    tone="friendly",
                )
                
                display_template_info(template)
                simulate_conversation(template)
                
                input("\nPress Enter to continue...")
            else:
                print("Invalid selection")
                
        except ValueError:
            print("Please enter a number")
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break


if __name__ == "__main__":
    asyncio.run(main())
