# UI Components Documentation

## BattleView

The BattleView component is responsible for rendering the game's battle interface using the Rich library for terminal-based UI.

### Overview

BattleView provides a rich terminal interface for Pokemon battles with:
- Split-screen layout showing both Pokemon
- Battle log with message history
- Action menu for player choices
- Dynamic HP bars with color changes
- Move lists with PP tracking
- Victory and game over screens with statistics

### Class Structure

```python
class BattleView:
    def __init__(self) -> None
    def clear_screen(self) -> None
    def show_title_screen(self) -> None
    def show_starter_selection(self, available_starters: List[str]) -> None
    def render_battle(self, player_pokemon: Pokemon, enemy_pokemon: Pokemon, messages: Optional[List[str]] = None) -> None
    def _create_pokemon_panel(self, pokemon: Pokemon, title: str) -> Panel
    def show_game_over(self, stats: Optional[dict] = None) -> None
    def show_victory(self, stats: Optional[dict] = None) -> None
```

### Key Features

#### Battle Screen Layout
- Three-section vertical split:
  1. Battle area (Pokemon displays)
  2. Message log (last 5 messages)
  3. Action menu

#### Pokemon Information Display
- Name and level
- Type(s)
- HP bar with numerical values
- Move list with PP counters
- Dynamic border colors (green for healthy, red for low HP)

#### Message System
- Maintains history of last 5 battle messages
- Scrolling message log with blue border
- Centered message display

#### Menu System
- Four standard battle options:
  1. Fight
  2. Pokemon
  3. Item
  4. Run
- Green-bordered menu panel

#### Statistics Display
- Game over and victory screens include stats tables
- Two-column format (Stat name | Value)
- Cyan styling for stat names
- Right-aligned values

### Implementation Details

#### Rich Library Integration
- Uses Rich's Layout system for screen organization
- Panel components for bordered sections
- Table components for move lists and stats
- Text styling for visual hierarchy

#### HP Bar Implementation
```python
hp_percentage = pokemon.current_hp / pokemon.stats.hp
hp_bar_width = 20
filled = int(hp_percentage * hp_bar_width)
hp_bar = f"[{'=' * filled}{' ' * (hp_bar_width - filled)}]"
```

#### Message History Management
```python
if messages:
    self._message_history.extend(messages)
if len(self._message_history) > 5:
    self._message_history = self._message_history[-5:]
```

### Testing

The BattleView component has comprehensive test coverage using pytest and the unittest.mock library.

#### Test Structure
```python
# Key test fixtures
def mock_console()  # Mocks Rich console
def test_pokemon()  # Creates test Pokemon instance
def dual_type_pokemon()  # Pokemon with multiple types
def multi_move_pokemon()  # Pokemon with multiple moves
```

#### Test Categories

1. **Screen Rendering Tests**
   - Title screen
   - Starter selection
   - Battle screen layout
   - Game over screen
   - Victory screen

2. **Pokemon Panel Tests**
   - Basic information display
   - Dual-type handling
   - Move table rendering
   - HP bar colors

3. **Battle State Tests**
   - Layout creation
   - Message history management
   - Action menu content

4. **UI Component Tests**
   - Table rendering
   - Panel creation
   - Text styling

#### Mock System

The test suite includes custom mock implementations:
- MockTable for Rich's Table component
- Layout class for Rich's Layout system
- Mock console for output verification

### Common Issues and Solutions

1. **Text Rendering**
   - Issue: Rich Text objects store content in _text list
   - Solution: Join list elements for string representation

2. **Table Content**
   - Issue: Table content needs exact string matching
   - Solution: Standardize content formatting in tests

3. **Layout Testing**
   - Issue: Complex nested layouts
   - Solution: Mock layout system with simplified behavior

### Performance Considerations

- Message history limited to 5 items for memory efficiency
- Screen clearing on each render
- Minimal string concatenation in render loops

### Future Improvements

1. **Planned Enhancements**
   - Animated HP bar changes
   - Color-coded move types
   - Extended message history option
   - Detailed move information display

2. **Technical Debt**
   - Move table creation could be extracted
   - Panel style determination could be more flexible
   - Message history could use a proper queue

### Usage Example

```python
view = BattleView()
view.render_battle(
    player_pokemon=player.active_pokemon,
    enemy_pokemon=enemy.active_pokemon,
    messages=["Battle started!", "Choose your move"]
)
```

### Dependencies

- rich.console.Console
- rich.panel.Panel
- rich.layout.Layout
- rich.table.Table
- rich.text.Text

### Test Coverage

The BattleView component maintains 100% test coverage across all methods and branches.
