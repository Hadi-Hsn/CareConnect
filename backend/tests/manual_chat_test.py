"""
Manual Chat Testing Script for CareConnect Agent
Tests conversational quality in English and Arabic Lebanese dialect
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.router import AgentRouter
from app.core.db import async_session_maker, init_db
from app.models import User
from app.schemas.agent import ChatMessage
from sqlalchemy import select
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


class ManualTester:
    """Interactive manual testing for agent."""

    def __init__(self):
        self.test_user_id = None
        self.conversation_history = []

    async def setup(self):
        """Set up test environment."""
        await init_db()
        
        # Get or create test user
        async with async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.email == "test@manual.com")
            )
            user = result.scalar_one_or_none()
            
            if not user:
                from app.core.security import get_password_hash
                from app.models.user import UserRole
                
                user = User(
                    email="test@manual.com",
                    name="Manual Test User",
                    role=UserRole.PATIENT,
                    hashed_password=get_password_hash("test123")
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
            
            self.test_user_id = user.id

    async def test_conversation(self, title: str, messages: list[str]):
        """Test a conversation sequence."""
        console.print(f"\n{'='*70}")
        console.print(Panel(f"[bold cyan]{title}[/bold cyan]", border_style="cyan"))
        console.print(f"{'='*70}\n")
        
        conversation = []
        
        for i, user_message in enumerate(messages):
            console.print(f"[bold green]User:[/bold green] {user_message}")
            
            # Add user message to conversation
            conversation.append(ChatMessage(role="user", content=user_message))
            
            # Get agent response
            async with async_session_maker() as session:
                agent = AgentRouter(session)
                final_message, tool_calls, tool_results, usage = await agent.chat_turn(
                    messages=conversation,
                    user_id=self.test_user_id
                )
            
            # Add assistant response to conversation
            conversation.append(ChatMessage(role="assistant", content=final_message.content))
            
            # Display response
            console.print(f"[bold blue]Agent:[/bold blue] {final_message.content}")
            
            if tool_calls:
                console.print(f"[dim]  → Tools used: {', '.join([tc.name for tc in tool_calls])}[/dim]")
            
            console.print()
        
        return conversation


async def run_tests():
    """Run all manual tests."""
    tester = ManualTester()
    await tester.setup()
    
    console.print("[bold magenta]🧪 CareConnect Agent Manual Testing[/bold magenta]")
    console.print("[dim]Testing conversational quality in English and Arabic Lebanese dialect[/dim]\n")
    
    # English Tests
    console.print("\n[bold yellow]📝 ENGLISH TESTS[/bold yellow]")
    
    # Test 1: Simple booking
    await tester.test_conversation(
        "Test 1: Simple Appointment Booking (English)",
        [
            "Hi, I need to book an appointment with a cardiologist next Monday"
        ]
    )
    
    # Test 2: Information query
    await tester.test_conversation(
        "Test 2: Parking Information Query (English)",
        [
            "Where can I park when I come to the hospital?"
        ]
    )
    
    # Test 3: Emergency detection
    await tester.test_conversation(
        "Test 3: Emergency Detection (English)",
        [
            "I have severe chest pain and trouble breathing"
        ]
    )
    
    # Test 4: Medical advice rejection
    await tester.test_conversation(
        "Test 4: Medical Advice Rejection (English)",
        [
            "What medicine should I take for my headache?"
        ]
    )
    
    # Test 5: Multi-turn booking with clarification
    await tester.test_conversation(
        "Test 5: Multi-turn Booking (English)",
        [
            "I need a doctor's appointment",
            "Orthopedics",
            "This Friday"
        ]
    )
    
    # Arabic Lebanese Dialect Tests
    console.print("\n[bold yellow]📝 ARABIC LEBANESE DIALECT TESTS[/bold yellow]")
    
    # Test 6: Simple greeting and booking (Lebanese Arabic)
    await tester.test_conversation(
        "Test 6: Booking in Lebanese Arabic",
        [
            "مرحبا، بدي احجز موعد عند دكتور قلب يوم الاثنين الجاي"  # "Hello, I want to book an appointment with a heart doctor next Monday"
        ]
    )
    
    # Test 7: Informal Lebanese dialect
    await tester.test_conversation(
        "Test 7: Informal Lebanese Dialect",
        [
            "مساء الخير، شو في دكتور متخصص بالعظام متاح؟"  # "Good evening, is there an orthopedic doctor available?"
        ]
    )
    
    # Test 8: Emergency in Arabic
    await tester.test_conversation(
        "Test 8: Emergency in Arabic",
        [
            "عندي وجع قوي بصدري وما عم قدر تنفس منيح"  # "I have strong chest pain and can't breathe well"
        ]
    )
    
    # Test 9: Information query in Arabic
    await tester.test_conversation(
        "Test 9: Information Query in Arabic",
        [
            "وين فيني ركن السيارة؟"  # "Where can I park the car?"
        ]
    )
    
    # Test 10: Mixed English-Arabic (code-switching - common in Lebanon)
    await tester.test_conversation(
        "Test 10: Code-Switching (English-Arabic Mix)",
        [
            "Hi, بدي appointment عند الـ cardiologist يوم Thursday"  # Mix of English and Arabic
        ]
    )
    
    # Test 11: Cancellation in Arabic
    await tester.test_conversation(
        "Test 11: Appointment Cancellation in Arabic",
        [
            "بدي الغي الموعد تبعي"  # "I want to cancel my appointment"
        ]
    )
    
    # Test 12: Polite formal Arabic
    await tester.test_conversation(
        "Test 12: Formal Arabic Request",
        [
            "من فضلك، هل يمكنني معرفة أوقات عمل قسم الأشعة؟"  # "Please, can I know the radiology department hours?"
        ]
    )
    
    console.print("\n" + "="*70)
    console.print("[bold green]✅ All manual tests completed![/bold green]")
    console.print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(run_tests())
