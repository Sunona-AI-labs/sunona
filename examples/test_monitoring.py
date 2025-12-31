"""
Sunona Voice AI - Monitoring Example

Demonstrates analytics and cost tracking.

Usage:
    python examples/test_monitoring.py
"""

import asyncio
import os
import sys
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sunona.monitoring import Analytics, CostTracker, ConversationLogger


async def main():
    print("=" * 60)
    print("Sunona AI - Monitoring Example")
    print("=" * 60)
    
    # Initialize analytics
    analytics = Analytics()
    cost_tracker = CostTracker()
    logger = ConversationLogger()
    
    # Simulate multiple conversations
    print("\n📊 Simulating 3 conversations...")
    
    agents = ["customer_support", "sales_assistant", "tech_helper"]
    
    for i, agent_id in enumerate(agents):
        print(f"\n🤖 Agent: {agent_id}")
        
        # Start conversation
        conv_id = analytics.start_conversation(agent_id)
        logger.log_turn(conv_id, "system", f"Agent {agent_id} initialized")
        
        # Simulate 3-5 turns per conversation
        num_turns = random.randint(3, 5)
        
        for turn in range(num_turns):
            # Simulate latencies
            transcription_ms = random.randint(100, 300)
            llm_ms = random.randint(200, 800)
            synthesis_ms = random.randint(100, 200)
            
            # Simulate tokens
            input_tokens = random.randint(50, 200)
            output_tokens = random.randint(100, 400)
            
            # Record turn
            analytics.record_turn(
                conv_id,
                transcription_latency_ms=transcription_ms,
                llm_latency_ms=llm_ms,
                synthesis_latency_ms=synthesis_ms,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
            
            # Track costs
            cost_tracker.track_transcription("deepgram", duration_seconds=5)
            cost_tracker.track_llm(
                "openai", "gpt-4o-mini",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                conversation_id=conv_id,
            )
            cost_tracker.track_synthesis("elevenlabs", character_count=output_tokens * 5)
            
            # Log turn
            logger.log_turn(conv_id, "user", f"User message {turn + 1}")
            logger.log_turn(conv_id, "assistant", f"Assistant response {turn + 1}", llm_ms)
        
        # End conversation
        analytics.end_conversation(conv_id)
        print(f"   Completed {num_turns} turns")
    
    # Display analytics summary
    print("\n" + "=" * 60)
    print("📈 Analytics Summary")
    print("=" * 60)
    
    summary = analytics.get_summary()
    print(f"""
Total Conversations: {summary['total_conversations']}
Total Turns: {summary['total_turns']}
Total Tokens: {summary['total_tokens']}
Success Rate: {summary['success_rate'] * 100:.1f}%
Avg Turn Latency: {summary['avg_turn_latency_ms']:.1f}ms
Latency P50: {summary['latency_p50_ms']:.1f}ms
Latency P90: {summary['latency_p90_ms']:.1f}ms
""")
    
    # Per-agent summary
    print("📊 Per-Agent Summary:")
    agent_summary = analytics.get_agent_summary()
    for agent_id, stats in agent_summary.items():
        print(f"   {agent_id}: {stats['conversation_count']} convs, {stats['total_turns']} turns")
    
    # Cost summary
    print("\n" + "=" * 60)
    print("💰 Cost Tracking")
    print("=" * 60)
    
    cost_summary = cost_tracker.get_summary()
    print(f"""
Total Cost: ${cost_summary['total_cost_usd']:.4f}

By Category:
""")
    for category, cost in cost_summary['by_category'].items():
        print(f"   {category}: ${cost:.4f}")
    
    print("\nBy Provider:")
    for provider, cost in cost_summary['by_provider'].items():
        print(f"   {provider}: ${cost:.4f}")
    
    # Show conversation log
    print("\n" + "=" * 60)
    print("📝 Sample Conversation Log")
    print("=" * 60)
    
    # Get first conversation
    if analytics._completed_conversations:
        sample_conv = analytics._completed_conversations[0].conversation_id
        log_entries = logger.get_conversation(sample_conv)
        print(f"\n(Conversation {sample_conv[:8]}... has {len(log_entries)} entries)")
    
    print("\n" + "=" * 60)
    print("Monitoring Example Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
