#!/usr/bin/env python3
"""
LUCY Chat Interface - Interactive CLI for your 1978 Triumph Spitfire RAG System
"""
import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich import print as rprint
from rich.prompt import Prompt, Confirm

from spitfire_rag import TriumphSpitfireRAG
from config import SpitfireConfig


class LucyChatInterface:
    """Interactive chat interface for LUCY"""
    
    def __init__(self):
        self.console = Console()
        self.lucy = None
        self.running = True
        
    def display_banner(self):
        """Display LUCY's welcome banner"""
        banner_text = """
    🚗 LUCY - 1978 Triumph Spitfire RAG System 🚗
    
    Your charming British classic with technical knowledge and personality!
    """
        
        self.console.print(Panel(
            banner_text,
            style="bold blue",
            border_style="bright_blue"
        ))
    
    def check_api_keys(self) -> bool:
        """Check if required API keys are configured"""
        try:
            SpitfireConfig.validate_api_keys()
            return True
        except ValueError as e:
            self.console.print(f"\n[bold red]Configuration Error:[/bold red] {e}")
            self.console.print("\nPlease create a .env file with your API keys:")
            self.console.print("ANTHROPIC_API_KEY=your_anthropic_key_here")
            self.console.print("OPENAI_API_KEY=your_openai_key_here")
            return False
    
    def initialize_lucy(self):
        """Initialize LUCY RAG system"""
        try:
            with self.console.status("[bold blue]Starting LUCY's engine..."):
                self.lucy = TriumphSpitfireRAG()
            
            self.console.print("[bold green]✓ LUCY is ready to chat!")
            return True
            
        except Exception as e:
            self.console.print(f"[bold red]Error starting LUCY:[/bold red] {e}")
            return False
    
    def display_help(self):
        """Display available commands"""
        help_text = """
[bold cyan]Available Commands:[/bold cyan]

[bold]Chat Commands:[/bold]
• Just type your question naturally
• "Tell me about your carburettors"
• "I changed your oil yesterday"
• "How do I adjust your timing?"

[bold]System Commands:[/bold]
• [cyan]/help[/cyan] or [cyan]?[/cyan] - Show this help
• [cyan]/memory[/cyan] - Show maintenance history
• [cyan]/todo[/cyan] - Show current todo list
• [cyan]/clear[/cyan] - Clear conversation (keeps maintenance log)
• [cyan]/status[/cyan] - Show LUCY's current status
• [cyan]/quit[/cyan] or [cyan]/exit[/cyan] - Exit chat

[bold]Tips:[/bold]
• LUCY remembers maintenance work you mention
• She has technical knowledge from service manuals
• Say "add [task] to todo list" to add maintenance tasks
• Mention completing work and she'll offer to cross it off
• Ask specific questions for detailed instructions
• Mention parts by name for exact specifications
        """
        
        self.console.print(Panel(help_text, title="LUCY Help", border_style="cyan"))
    
    def display_maintenance_memory(self):
        """Display LUCY's maintenance memory"""
        if not self.lucy:
            return
        
        summary = self.lucy.get_maintenance_summary()
        
        memory_text = f"""
[bold cyan]LUCY's Maintenance Memory:[/bold cyan]

[bold]Recent Work Count:[/bold] {summary['recent_work_count']} entries
[bold]Last Service:[/bold] {summary['last_service'] or 'Not recorded'}
[bold]Current Mileage:[/bold] {summary['current_mileage']}

[bold]Recent Work:[/bold]
"""
        
        if summary['recent_work']:
            for work in summary['recent_work']:
                memory_text += f"• {work['date']}: {work['action']}\n"
                if work.get('notes'):
                    memory_text += f"  Notes: {work['notes']}\n"
        else:
            memory_text += "No recent work recorded\n"
        
        if summary['current_issues']:
            memory_text += f"\n[bold]Current Issues:[/bold]\n"
            for issue in summary['current_issues']:
                memory_text += f"• {issue}\n"
        
        self.console.print(Panel(memory_text, title="Maintenance Memory", border_style="yellow"))
    
    def display_status(self):
        """Display LUCY's current status"""
        if not self.lucy:
            return
        
        config = SpitfireConfig()
        status_text = f"""
[bold cyan]LUCY System Status:[/bold cyan]

[bold]Car Details:[/bold]
• Year: {config.LUCY_YEAR}
• Model: {config.LUCY_MODEL}
• Engine: {config.LUCY_ENGINE}
• Age: {config.LUCY_AGE} years old

[bold]System Configuration:[/bold]
• LLM Model: {config.LLM_MODEL}
• Embedding Model: {config.EMBEDDING_MODEL}
• Vector Database: ChromaDB
• Memory Window: {config.CONVERSATION_MEMORY_SIZE} exchanges

[bold]Files & Directories:[/bold]
• Documents: {config.DOCS_DIR}
• Vector DB: {config.VECTORDB_DIR}
• Maintenance Log: {config.MAINTENANCE_LOG_PATH}
        """
        
        self.console.print(Panel(status_text, title="System Status", border_style="green"))
    
    def display_todo_list(self):
        """Display current todo list"""
        if not self.lucy:
            self.console.print("[red]LUCY not initialized[/red]")
            return
        
        todo_summary = self.lucy.get_todo_summary()
        
        if not self.lucy.todo_list:
            todo_text = "[dim]No pending or completed todos![/dim]\n\nJust say something like:\n• 'Add oil change to the todo list'\n• 'Put brake inspection on my list'\n• 'I finished the spark plug replacement'"
        else:
            todo_text = todo_summary + "\n\n[dim]Tip: Mention completing work and I'll help cross it off![/dim]"
        
        self.console.print(Panel(todo_text, title="🔧 LUCY's Todo List", border_style="yellow"))
    
    def process_command(self, user_input: str) -> bool:
        """Process system commands, return True if command was handled"""
        command = user_input.strip().lower()
        
        if command in ['/help', '?']:
            self.display_help()
            return True
        elif command == '/memory':
            self.display_maintenance_memory()
            return True
        elif command == '/clear':
            if Confirm.ask("Clear conversation memory? (Maintenance log will be preserved)"):
                self.lucy.clear_conversation_memory()
                self.console.print("[green]✓ Conversation memory cleared")
            return True
        elif command == '/status':
            self.display_status()
            return True
        elif command == '/todo':
            self.display_todo_list()
            return True
        elif command in ['/quit', '/exit']:
            self.running = False
            return True
        
        return False
    
    def handle_todo_confirmation(self, todo_result: dict):
        """Handle todo completion confirmation with user"""
        matches = todo_result.get("matches", [])
        completed_work = todo_result.get("completed_work", "")
        
        if not matches:
            return
        
        self.console.print(f"\n[yellow]You mentioned completing: {completed_work}[/yellow]")
        self.console.print("[yellow]Found potentially matching todo items:[/yellow]\n")
        
        for i, match in enumerate(matches, 1):
            todo_id = match["todo_id"]
            confidence = match["confidence"]
            reason = match["reason"]
            
            # Find the actual todo item
            todo_item = None
            for todo in self.lucy.todo_list:
                if todo["id"] == todo_id:
                    todo_item = todo
                    break
            
            if todo_item:
                confidence_color = {"high": "green", "medium": "yellow", "low": "red"}.get(confidence, "white")
                self.console.print(f"[bold]{i}.[/bold] {todo_item['task']}")
                self.console.print(f"   [dim]ID: {todo_id} | Confidence: [{confidence_color}]{confidence}[/{confidence_color}][/dim]")
                self.console.print(f"   [dim]Reason: {reason}[/dim]\n")
        
        # Ask for confirmation
        while True:
            try:
                choice = Prompt.ask(
                    "[bold cyan]Which todo should be marked complete? (number, 'none', or 'all')[/bold cyan]",
                    choices=[str(i) for i in range(1, len(matches) + 1)] + ["none", "all"]
                ).lower()
                
                if choice == "none":
                    self.console.print("[dim]No todos marked as complete.[/dim]")
                    break
                elif choice == "all":
                    completed_count = 0
                    for match in matches:
                        if self.lucy.confirm_todo_completion(match["todo_id"], completed_work):
                            completed_count += 1
                    self.console.print(f"[green]✓ Marked {completed_count} todo(s) as complete![/green]")
                    break
                else:
                    # Single selection
                    choice_num = int(choice) - 1
                    if 0 <= choice_num < len(matches):
                        selected_match = matches[choice_num]
                        if self.lucy.confirm_todo_completion(selected_match["todo_id"], completed_work):
                            self.console.print("[green]✓ Todo marked as complete![/green]")
                        else:
                            self.console.print("[red]Failed to mark todo as complete.[/red]")
                        break
                    else:
                        self.console.print("[red]Invalid selection.[/red]")
                        
            except (ValueError, KeyboardInterrupt):
                self.console.print("[dim]Cancelled todo confirmation.[/dim]")
                break
    
    def format_response(self, response: dict):
        """Format and display LUCY's response"""
        # Display main answer
        answer_panel = Panel(
            Markdown(response["answer"]),
            title="🚗 LUCY Says",
            border_style="bright_blue"
        )
        self.console.print(answer_panel)
        
        # Handle todo confirmation if needed
        todo_result = response.get("todo_result", {})
        if todo_result.get("confirmation_needed"):
            self.handle_todo_confirmation(todo_result)
        
        # Show if maintenance was detected
        if response.get("maintenance_detected"):
            self.console.print("[dim green]✓ Maintenance work recorded in memory[/dim green]")
        
        # Show if technical knowledge was detected
        if response.get("technical_knowledge_detected"):
            self.console.print("[dim green]✓ Technical knowledge saved[/dim green]")
        
        # Show todo operation results
        if todo_result.get("operation") == "add":
            self.console.print(f"[dim green]✓ {todo_result['message']}[/dim green]")
        elif todo_result.get("operation") == "complete" and not todo_result.get("confirmation_needed"):
            self.console.print(f"[dim green]✓ {todo_result['message']}[/dim green]")
        
        # Show source documents if available (optional debug info)
        sources = response.get("source_documents", [])
        if sources and len(sources) > 0:
            source_info = f"[dim]Sources: {len(sources)} document(s)[/dim]"
            self.console.print(source_info)
    
    def chat_loop(self):
        """Main chat interaction loop"""
        # Display greeting
        greeting = self.lucy.get_greeting()
        greeting_panel = Panel(
            greeting,
            title="🚗 LUCY - Ready to Chat!",
            border_style="bright_blue"
        )
        self.console.print(greeting_panel)
        
        # Show help hint
        self.console.print("[dim]Type '/help' for commands or just ask me anything![/dim]\n")
        
        while self.running:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]").strip()
                
                if not user_input:
                    continue
                
                # Check for system commands
                if self.process_command(user_input):
                    continue
                
                # Get response from LUCY
                with self.console.status("[bold blue]LUCY is thinking..."):
                    response = self.lucy.ask_lucy(user_input)
                
                # Display response
                self.format_response(response)
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Interrupted by user[/yellow]")
                break
            except EOFError:
                break
            except Exception as e:
                self.console.print(f"[bold red]Error:[/bold red] {e}")
    
    def run(self):
        """Main application entry point"""
        self.display_banner()
        
        # Check configuration
        if not self.check_api_keys():
            return 1
        
        # Initialize LUCY
        if not self.initialize_lucy():
            return 1
        
        try:
            # Start chat
            self.chat_loop()
        except Exception as e:
            self.console.print(f"[bold red]Fatal error:[/bold red] {e}")
            return 1
        finally:
            self.console.print("\n[cyan]Thanks for chatting with LUCY! Keep her running smoothly! 🚗[/cyan]")
        
        return 0


def main():
    """Main entry point"""
    chat = LucyChatInterface()
    sys.exit(chat.run())


if __name__ == "__main__":
    main()