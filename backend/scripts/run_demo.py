"""
CareConnect Agent Interactive Demo Script
=========================================
This script demonstrates the CareConnect AI agent's capabilities
through a series of automated conversation scenarios.

Run this script to see the agent in action!

Usage:
    docker-compose exec backend python scripts/run_demo.py
    
Or with Python directly:
    cd backend
    python scripts/run_demo.py
"""

import asyncio
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.router import AgentRouter
from app.core.db import async_session_maker, init_db
from app.models import User
from app.schemas.agent import ChatMessage
from sqlalchemy import select

# Lebanon timezone for date calculations
LEBANON_TZ = ZoneInfo("Asia/Beirut")


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DIM = '\033[2m'


def print_header(text: str):
    """Print a section header."""
    print(f"\n{'='*70}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {text}{Colors.ENDC}")
    print(f"{'='*70}\n")


def print_scene(act: str, scene: str, title: str):
    """Print a scene header."""
    print(f"\n{Colors.YELLOW}--- {act}, {scene}: {title} ---{Colors.ENDC}\n")


def print_user(message: str):
    """Print user message."""
    print(f"{Colors.GREEN}{Colors.BOLD}👤 User:{Colors.ENDC} {message}")


def print_agent(message: str):
    """Print agent response."""
    print(f"{Colors.BLUE}{Colors.BOLD}🤖 Agent:{Colors.ENDC} {message}")


def print_tools(tool_calls: list):
    """Print tools used."""
    if tool_calls:
        tool_names = ', '.join([tc.name for tc in tool_calls])
        print(f"{Colors.DIM}   → Tools used: {tool_names}{Colors.ENDC}")


def print_info(text: str):
    """Print informational text."""
    print(f"{Colors.DIM}   ℹ️  {text}{Colors.ENDC}")


def get_relative_date(days_ahead: int) -> str:
    """Get a date relative to today in YYYY-MM-DD format."""
    target = datetime.now(LEBANON_TZ) + timedelta(days=days_ahead)
    return target.strftime("%Y-%m-%d")


def get_day_name(days_ahead: int) -> str:
    """Get the day name for a date in the future."""
    target = datetime.now(LEBANON_TZ) + timedelta(days=days_ahead)
    return target.strftime("%A")


class DemoRunner:
    """Runs automated demo scenarios for the CareConnect agent."""

    def __init__(self):
        self.user_id = None
        self.demo_delay = 1.5  # Seconds between messages for readability

    async def setup(self):
        """Initialize database and get demo user."""
        await init_db()
        
        async with async_session_maker() as session:
            # Get the demo user
            result = await session.execute(
                select(User).where(User.email == "hadihacan@gmail.com")
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print(f"{Colors.RED}❌ Demo user not found! Run seed_demo_data.py first.{Colors.ENDC}")
                print("   docker-compose exec backend python scripts/seed_demo_data.py")
                return False
            
            self.user_id = user.id
            print(f"{Colors.GREEN}✓ Connected as: {user.name} ({user.email}){Colors.ENDC}")
            return True

    async def run_conversation(self, messages: list[str], context: list[ChatMessage] = None) -> list[ChatMessage]:
        """Run a conversation and return the history."""
        conversation = context or []
        
        for user_message in messages:
            print_user(user_message)
            time.sleep(0.5)
            
            # Add user message
            conversation.append(ChatMessage(role="user", content=user_message))
            
            # Get agent response
            async with async_session_maker() as session:
                agent = AgentRouter(session)
                final_message, tool_calls, tool_results, usage = await agent.chat_turn(
                    messages=conversation,
                    user_id=self.user_id
                )
            
            # Add to conversation
            conversation.append(ChatMessage(role="assistant", content=final_message.content))
            
            # Display
            print_agent(final_message.content)
            print_tools(tool_calls)
            print()
            
            time.sleep(self.demo_delay)
        
        return conversation

    async def demo_act1_information(self):
        """Act 1: Information Queries."""
        print_header("ACT 1: INFORMATION QUERIES (RAG)")
        
        # Scene 1: Greeting
        print_scene("Act 1", "Scene 1", "First Contact")
        await self.run_conversation([
            "Hi! I'm new to CareConnect. What can you help me with?"
        ])
        
        # Scene 2: Parking
        print_scene("Act 1", "Scene 2", "Parking Information")
        await self.run_conversation([
            "Where can I park when I come to the hospital?"
        ])
        
        # Scene 3: Department Hours
        print_scene("Act 1", "Scene 3", "Department Hours")
        await self.run_conversation([
            "What are the laboratory hours?"
        ])

    async def demo_act2_providers(self):
        """Act 2: Finding Doctors."""
        print_header("ACT 2: FINDING DOCTORS")
        
        # Scene 1: List providers
        print_scene("Act 2", "Scene 1", "List Cardiology Doctors")
        await self.run_conversation([
            "Who are the doctors in the Cardiology department?"
        ])
        
        # Scene 2: Doctor details
        print_scene("Act 2", "Scene 2", "Doctor Information")
        await self.run_conversation([
            "Tell me more about Dr. Sara Haddad"
        ])

    async def demo_act3_booking(self):
        """Act 3: Booking Appointments."""
        print_header("ACT 3: BOOKING APPOINTMENTS")
        
        # Calculate dates for natural language
        next_monday = (7 - datetime.now(LEBANON_TZ).weekday()) % 7
        if next_monday == 0:
            next_monday = 7
        
        # Scene 1: Simple booking
        print_scene("Act 3", "Scene 1", "Simple Appointment Booking")
        print_info(f"Today is {datetime.now(LEBANON_TZ).strftime('%A, %B %d, %Y')}")
        
        conv = await self.run_conversation([
            "I need to book an appointment with a cardiologist next Monday"
        ])
        
        # Scene 2: Complete the booking
        print_scene("Act 3", "Scene 2", "Selecting a Time Slot")
        await self.run_conversation([
            "The 10:00 AM slot with Dr. Sara Haddad works for me"
        ], context=conv)
        
        # Scene 3: Lab test booking
        print_scene("Act 3", "Scene 3", "Lab Test Booking (Special Case)")
        print_info("Lab tests automatically route to Laboratory department")
        
        conv = await self.run_conversation([
            "I need to schedule a lipid panel blood test"
        ])
        
        await self.run_conversation([
            "Tomorrow morning at the earliest available time"
        ], context=conv)

    async def demo_act4_view_appointments(self):
        """Act 4: Viewing Appointments."""
        print_header("ACT 4: VIEWING APPOINTMENTS")
        
        # Scene 1: View upcoming
        print_scene("Act 4", "Scene 1", "View Upcoming Appointments")
        await self.run_conversation([
            "Show me my upcoming appointments"
        ])
        
        # Scene 2: View all
        print_scene("Act 4", "Scene 2", "View All Appointments")
        await self.run_conversation([
            "Show me all my appointments including past ones"
        ])

    async def demo_act5_modify(self):
        """Act 5: Modifying Appointments."""
        print_header("ACT 5: MODIFYING APPOINTMENTS")
        
        print_scene("Act 5", "Scene 1", "Reschedule by Description")
        conv = await self.run_conversation([
            "I need to reschedule my cardiology appointment to a different time"
        ])
        
        # Continue the conversation
        await self.run_conversation([
            "Move it to 2:00 PM on the same day if available"
        ], context=conv)

    async def demo_act6_cancel(self):
        """Act 6: Cancelling Appointments."""
        print_header("ACT 6: CANCELLING APPOINTMENTS")
        
        print_scene("Act 6", "Scene 1", "Cancel with Confirmation")
        conv = await self.run_conversation([
            "I need to cancel my lab test appointment"
        ])
        
        await self.run_conversation([
            "Yes, please cancel it"
        ], context=conv)

    async def demo_act7_safety(self):
        """Act 7: Safety & Boundaries."""
        print_header("ACT 7: SAFETY & SCOPE BOUNDARIES")
        
        # Scene 1: Emergency
        print_scene("Act 7", "Scene 1", "🚨 Emergency Detection")
        print_info("Agent should immediately direct to 911")
        await self.run_conversation([
            "I have severe chest pain and difficulty breathing"
        ])
        
        # Scene 2: Medical advice
        print_scene("Act 7", "Scene 2", "Medical Advice Rejection")
        print_info("Agent should refuse to give medical advice")
        await self.run_conversation([
            "What medicine should I take for my headache?"
        ])
        
        # Scene 3: Diagnosis
        print_scene("Act 7", "Scene 3", "Diagnosis Request Rejection")
        print_info("Agent should refuse to diagnose")
        await self.run_conversation([
            "I have a fever and cough. Do I have COVID?"
        ])

    async def demo_act8_multiturn(self):
        """Act 8: Multi-turn Conversation."""
        print_header("ACT 8: MULTI-TURN CONVERSATION")
        
        print_scene("Act 8", "Scene 1", "Complex Booking with Clarification")
        print_info("Agent asks clarifying questions to complete booking")
        
        conv = await self.run_conversation([
            "I need to see a doctor"
        ])
        
        conv = await self.run_conversation([
            "I've been having knee pain lately"
        ], context=conv)
        
        conv = await self.run_conversation([
            "Sometime next week would be great"
        ], context=conv)
        
        await self.run_conversation([
            "Wednesday at 11 AM looks good"
        ], context=conv)

    async def demo_act9_arabic(self):
        """Act 9: Arabic Language Support."""
        print_header("ACT 9: ARABIC LANGUAGE SUPPORT 🇱🇧")
        
        # Scene 1: Lebanese Arabic
        print_scene("Act 9", "Scene 1", "Lebanese Arabic Booking")
        print_info("Message: 'Hello, I want to book an appointment with a heart doctor'")
        await self.run_conversation([
            "مرحبا، بدي احجز موعد عند دكتور قلب"
        ])
        
        # Scene 2: Code-switching
        print_scene("Act 9", "Scene 2", "English-Arabic Code-Switching")
        print_info("Common in Lebanon: mixing English and Arabic")
        await self.run_conversation([
            "Hi, بدي appointment عند الـ dermatology يوم Thursday"
        ])


async def run_full_demo():
    """Run the complete demo."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║     🏥 CARECONNECT AI AGENT - INTERACTIVE DEMO 🤖                 ║")
    print("║                                                                    ║")
    print("║     AI-Powered Healthcare Appointment Assistant                    ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    demo = DemoRunner()
    
    if not await demo.setup():
        return
    
    print(f"\n{Colors.CYAN}Starting demo in 3 seconds...{Colors.ENDC}")
    print(f"{Colors.DIM}(Press Ctrl+C to stop at any time){Colors.ENDC}\n")
    time.sleep(3)
    
    try:
        # Run all demo acts
        await demo.demo_act1_information()
        await demo.demo_act2_providers()
        await demo.demo_act3_booking()
        await demo.demo_act4_view_appointments()
        await demo.demo_act5_modify()
        await demo.demo_act6_cancel()
        await demo.demo_act7_safety()
        await demo.demo_act8_multiturn()
        await demo.demo_act9_arabic()
        
        # Finale
        print_header("DEMO COMPLETE! 🎉")
        print(f"""
{Colors.GREEN}The CareConnect AI Agent demonstrated the following capabilities:{Colors.ENDC}

  ✅ Natural conversation & greetings
  ✅ Facility information via RAG (parking, hours)
  ✅ Doctor/provider search by department
  ✅ Appointment booking with date/time selection
  ✅ Lab test booking with preparation info
  ✅ Viewing upcoming and past appointments
  ✅ Modifying/rescheduling appointments
  ✅ Cancelling appointments with confirmation
  ✅ Emergency detection (immediate 911 redirect)
  ✅ Medical advice boundary enforcement
  ✅ Multi-turn conversation context
  ✅ Arabic language support (Lebanese dialect)

{Colors.CYAN}For more details, see DEMO_SCRIPT.md{Colors.ENDC}
""")
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Demo interrupted by user.{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.RED}Error during demo: {e}{Colors.ENDC}")
        raise


async def run_quick_demo():
    """Run a quick 2-minute demo of key features."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║     🏥 CARECONNECT - QUICK DEMO (2 min)                           ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    demo = DemoRunner()
    demo.demo_delay = 1.0  # Faster for quick demo
    
    if not await demo.setup():
        return
    
    print(f"\n{Colors.CYAN}Quick demo starting...{Colors.ENDC}\n")
    time.sleep(1)
    
    try:
        # 1. Information query
        print_scene("Demo", "1/5", "Information Query (RAG)")
        await demo.run_conversation([
            "Where can I park at the hospital?"
        ])
        
        # 2. List doctors
        print_scene("Demo", "2/5", "Find Doctors")
        await demo.run_conversation([
            "Who are the doctors in Dermatology?"
        ])
        
        # 3. Book appointment
        print_scene("Demo", "3/5", "Book Appointment")
        conv = await demo.run_conversation([
            "Book me an appointment with Dr. Jennifer Wong tomorrow at 10 AM"
        ])
        
        # 4. View appointments
        print_scene("Demo", "4/5", "View Appointments")
        await demo.run_conversation([
            "Show me my appointments"
        ])
        
        # 5. Safety boundary
        print_scene("Demo", "5/5", "Safety Boundaries")
        await demo.run_conversation([
            "I have severe chest pain"
        ])
        
        print(f"\n{Colors.GREEN}✅ Quick demo complete!{Colors.ENDC}\n")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Demo interrupted.{Colors.ENDC}")


async def interactive_mode():
    """Run in interactive mode for live testing."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║     🏥 CARECONNECT - INTERACTIVE MODE                             ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    demo = DemoRunner()
    
    if not await demo.setup():
        return
    
    print(f"\n{Colors.CYAN}Type your messages to chat with the agent.{Colors.ENDC}")
    print(f"{Colors.DIM}Commands: 'quit' to exit, 'clear' to reset conversation{Colors.ENDC}\n")
    
    conversation = []
    
    while True:
        try:
            user_input = input(f"{Colors.GREEN}You: {Colors.ENDC}").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                print(f"\n{Colors.CYAN}Goodbye!{Colors.ENDC}\n")
                break
            
            if user_input.lower() == 'clear':
                conversation = []
                print(f"{Colors.DIM}Conversation cleared.{Colors.ENDC}\n")
                continue
            
            # Add user message
            conversation.append(ChatMessage(role="user", content=user_input))
            
            # Get response
            async with async_session_maker() as session:
                agent = AgentRouter(session)
                final_message, tool_calls, tool_results, usage = await agent.chat_turn(
                    messages=conversation,
                    user_id=demo.user_id
                )
            
            # Add to conversation
            conversation.append(ChatMessage(role="assistant", content=final_message.content))
            
            # Display
            print(f"{Colors.BLUE}Agent: {Colors.ENDC}{final_message.content}")
            if tool_calls:
                print(f"{Colors.DIM}  [Tools: {', '.join([tc.name for tc in tool_calls])}]{Colors.ENDC}")
            print()
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.CYAN}Goodbye!{Colors.ENDC}\n")
            break
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CareConnect Agent Demo")
    parser.add_argument(
        "--mode", 
        choices=["full", "quick", "interactive"],
        default="full",
        help="Demo mode: full (all features), quick (2 min), interactive (chat)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "full":
        asyncio.run(run_full_demo())
    elif args.mode == "quick":
        asyncio.run(run_quick_demo())
    elif args.mode == "interactive":
        asyncio.run(interactive_mode())


if __name__ == "__main__":
    main()
