"""Main game loop and entry point."""

from typing import NoReturn
from services.game_state import GameState, GamePhase
from services.battle_manager import BattleManager
from ui.battle_view import BattleView
from ui.input_handler import InputHandler

def main() -> NoReturn:
    """Main game loop."""
    # Initialize components
    game_state = GameState()
    view = BattleView()
    
    while True:
        if game_state.phase == GamePhase.TITLE:
            view.show_title_screen()
            InputHandler.get_enter()
            game_state.phase = GamePhase.STARTER
            
        elif game_state.phase == GamePhase.STARTER:
            available_starters = game_state.get_available_starters()
            view.show_starter_selection(available_starters)
            
            choice = InputHandler.get_starter_choice(len(available_starters))
            if choice is not None:
                starter_id = available_starters[choice]
                if game_state.start_new_game(starter_id):
                    # Start first battle
                    player, enemy = game_state.start_battle()
                    view.render_battle(player, enemy, game_state.get_messages())
                    
        elif game_state.phase == GamePhase.BATTLE:
            # Get and handle player action
            action_tuple = InputHandler.get_battle_action()
            if action_tuple:
                action, kwargs = action_tuple
                result = game_state.battle_manager.execute_turn(action, **kwargs)
                
                if result:
                    # Show turn results
                    view.render_battle(
                        game_state.battle_manager.current_battle.player_pokemon,
                        game_state.battle_manager.current_battle.enemy_pokemon,
                        result.messages
                    )
                    
                    # Check if battle is over
                    if game_state.battle_manager.current_battle.is_over:
                        game_state.handle_battle_end()
                        if game_state.phase == GamePhase.BATTLE:
                            # Start next battle if we haven't won/lost the game
                            player, enemy = game_state.start_battle()
                            view.render_battle(player, enemy, game_state.get_messages())
                            
        elif game_state.phase == GamePhase.GAME_OVER:
            view.show_game_over(vars(game_state.stats))
            InputHandler.get_enter()
            game_state = GameState()  # Reset game
            game_state.phase = GamePhase.TITLE
            
        elif game_state.phase == GamePhase.VICTORY:
            view.show_victory(vars(game_state.stats))
            InputHandler.get_enter()
            game_state = GameState()  # Reset game
            game_state.phase = GamePhase.TITLE

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nThanks for playing!")
