"""Battle view implementation using rich for terminal rendering."""

from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.text import Text
from ..core.pokemon import Pokemon

class BattleView:
    """Renders battle state to the terminal."""
    
    def __init__(self) -> None:
        """Initialize the battle view."""
        self.console = Console()
        self._message_history: List[str] = []
        
    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        self.console.clear()
        
    def show_title_screen(self) -> None:
        """Display the title screen."""
        title = """
╔═══════════════════════════════════════════╗
║                 FAKEMON 2                  ║
║          A Pokemon Roguelike RPG          ║
║                                           ║
║            Press ENTER to start           ║
╚═══════════════════════════════════════════╝
        """
        self.console.print(title, style="bold green", justify="center")
        
    def show_starter_selection(self, available_starters: List[str]) -> None:
        """Display the starter Pokemon selection screen."""
        self.console.print("\nChoose your starter Pokemon:", style="bold blue")
        for i, starter in enumerate(available_starters, 1):
            self.console.print(f"{i}. {starter.title()}", style="green")
            
    def render_battle(
        self,
        player_pokemon: Pokemon,
        enemy_pokemon: Pokemon,
        messages: Optional[List[str]] = None
    ) -> None:
        """Render the current battle state."""
        self.clear_screen()
        
        # Create main layout
        layout = Layout()
        
        # Split into sections
        layout.split_column(
            Layout(name="battle"),
            Layout(name="messages", size=10),
            Layout(name="actions", size=5)
        )
        
        # Create battle panel with Pokemon info
        battle_layout = Layout()
        battle_layout.split_row(
            Layout(self._create_pokemon_panel(player_pokemon, "Player")),
            Layout(self._create_pokemon_panel(enemy_pokemon, "Enemy"))
        )
        layout["battle"].update(battle_layout)
        
        # Update message history
        if messages:
            self._message_history.extend(messages)
        if len(self._message_history) > 5:
            self._message_history = self._message_history[-5:]
            
        # Create message panel
        message_panel = Panel(
            "\n".join(self._message_history) if self._message_history else "",
            title="Battle Log",
            border_style="blue"
        )
        layout["messages"].update(message_panel)
        
        # Create action menu
        actions_text = (
            "Actions:\n"
            "1. Fight   2. Pokemon\n"
            "3. Item    4. Run"
        )
        actions_panel = Panel(
            actions_text,
            title="Menu",
            border_style="green"
        )
        layout["actions"].update(actions_panel)
        
        # Render the layout
        self.console.print(layout)
        
    def _create_pokemon_panel(self, pokemon: Pokemon, title: str) -> Panel:
        """Create a panel displaying Pokemon information."""
        # Create HP bar
        hp_percentage = pokemon.current_hp / pokemon.stats.hp
        hp_bar_width = 20
        filled = int(hp_percentage * hp_bar_width)
        hp_bar = f"[{'=' * filled}{' ' * (hp_bar_width - filled)}]"
        
        # Format moves table
        moves_table = Table(show_header=False, show_edge=False, pad_edge=False)
        for move in pokemon.moves:
            pp_text = f"PP: {move.current_pp}/{move.max_pp}"
            moves_table.add_row(
                Text(f"• {move.name}", style="bright_blue"),
                Text(pp_text, style="dim")
            )
        
        # Create content
        content = [
            f"{pokemon.name} Lv.{pokemon.level}",
            f"Types: {', '.join(t.name for t in pokemon.types)}",
            f"HP: {pokemon.current_hp}/{pokemon.stats.hp}",
            hp_bar,
            "",
            "Moves:",
            moves_table
        ]
        
        # Determine panel style based on HP
        border_style = "red" if pokemon.current_hp <= pokemon.stats.hp * 0.25 else "green"
        
        return Panel(
            "\n".join(str(line) for line in content),
            title=title,
            border_style=border_style
        )
        
    def show_game_over(self, stats: Optional[dict] = None) -> None:
        """Display the game over screen."""
        self.clear_screen()
        self.console.print("\nGame Over!", style="bold red", justify="center")
        
        if stats:
            stats_table = Table(title="Game Statistics")
            stats_table.add_column("Stat", style="cyan")
            stats_table.add_column("Value", justify="right")
            
            for stat, value in stats.items():
                stats_table.add_row(
                    stat.replace('_', ' ').title(),
                    str(value)
                )
                
            self.console.print(stats_table, justify="center")
            
        self.console.print("\nPress ENTER to return to title screen", justify="center")
        
    def show_victory(self, stats: Optional[dict] = None) -> None:
        """Display the victory screen."""
        self.clear_screen()
        victory_text = """
╔═══════════════════════════════════════════╗
║         Congratulations! You Won!          ║
║     You've completed all 200 levels!       ║
╚═══════════════════════════════════════════╝
"""
        self.console.print(victory_text, style="bold green", justify="center")
        
        if stats:
            stats_table = Table(title="Final Statistics")
            stats_table.add_column("Stat", style="cyan")
            stats_table.add_column("Value", justify="right")
            
            for stat, value in stats.items():
                stats_table.add_row(
                    stat.replace('_', ' ').title(),
                    str(value)
                )
                
            self.console.print(stats_table, justify="center")
            
        self.console.print("\nPress ENTER to return to title screen", justify="center")
