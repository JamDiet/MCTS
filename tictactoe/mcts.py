from board import Board
import math
import random
import copy

class Node():
    def __init__(self, player: int, board: Board, move: int = None, parent: 'Node' = None):
        self.player = player
        self.board = board
        self.available_moves = board.get_available_moves()
        self.move = move
        self.wins: float = 0.
        self.num_sims: float = 0.
        self.parent = parent
        self.children: list['Node'] = []

    def has_control(self):
        """Heuristic function to determine whether a player has control over a board state. In such a state,
        Villain is forced to make moves to prevent Hero from winning."""
        win_combos = self.board.get_win_combos()
        (player_sym, op_sym) = ('X', 'O') if self.player == 1 else ('O', 'X')
        reward = 0.
        op_to_win = False

        for combo in win_combos:
            if combo.count(player_sym) == 3:    # If player wins, always choose the causative move
                return math.inf
            elif combo.count(op_sym) == 2 and combo.count(player_sym) == 0:     # Avoid boards where opponent is sure to win
                op_to_win = True
            elif combo.count(player_sym) == 2 and combo.count(op_sym) == 0:     # Seek advantage or double advantage
                reward += 0.5

        if op_to_win:
            return -math.inf
        
        return reward

    def calculate_score(self, c: float = math.sqrt(2)):
        """Score used to guide leaf selection path."""
        if self.num_sims == 0.:     # Allow all child nodes to be visited at least once
            return math.inf
        else:
            exploitation_term = self.wins / self.num_sims
            explore_term = c * math.sqrt(math.log(self.parent.num_sims) / self.num_sims)

            return exploitation_term + explore_term
    
    def select(self):
        """Select leaf (i.e. node with unexplored moves) from root."""
        current = self

        while True:
            if current.available_moves or not current.children:
                return current
            
            current = max(current.children, key=lambda child: child.calculate_score(1.))
    
    def expand(self):
        """Create one possible child based on available moves from the leaf node."""
        if self.available_moves:
            player = 3 - self.player    # Opposite player
            board = copy.deepcopy(self.board)   # Copy board to prevent alteration
            move = random.choice(self.available_moves)
            self.available_moves.remove(move)   # Remove move to allow leaf expiration over time
            board.update(player, move)

            child = Node(player, board, move, self)
            self.children.append(child)

            return child
        else:
            return self

    def simulate(self):
        """Play out random simulation until the end of game from the given node."""
        player = self.player
        board = copy.deepcopy(self.board)   # Copy board to prevent alteration
        available_moves = board.get_available_moves()

        while True:
            if available_moves:
                player = 3 - player
                move = random.choice(available_moves)
                available_moves.remove(move)
                board.update(player, move)

            if board.check_for_win():
                return player
            elif board.check_for_stalemate():
                return 0
    
    def backpropagate(self, result: int):
        """Update num_sims and wins of nodes on the path to child node from which a simulation was ran. Each node
        corresponds to a player and a move made by that player. If that player won the simulation, we want to reward
        their moves that resulted in the win by updating the corresponding nodes' win counts."""
        current = self

        while current is not None:
            if current.player == result:
                current.wins += 1.
            elif not result:
                current.wins += 0.5

            current.num_sims += 1.
            current = current.parent

def choose_move(user: int, board: Board, num_playouts: int):
    """Start with the current game board, last updated by the opposing player (user).

    1) Select an appealing node with unexplored actions.
    2) Select one unexplored action.
    3) Simulate randomly the remaining events of the game.
    4) Update that action and previous actions to reflect simulation results.
    5) Repeat for num_playouts.
    5) From the root, choose the subsequent move simulated most frequently.
    
    Since paths are taken with preference to actions resulting in a higher win ratio, num_sims reflects
    the success rate of a move."""

    root = Node(user, board)

    for _ in range(num_playouts):
        leaf = root.select()
        child = leaf.expand()
        result = child.simulate()
        child.backpropagate(result)

    return max(root.children, key=lambda c: c.num_sims).move