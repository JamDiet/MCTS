class Board():
    def __init__(self):
        self.board = [['_', '_', '_'] for _ in range(3)]
        self.winners = [['X'] * 3, ['O'] * 3]
        self.available_moves = [[3*i+1, 3*i+2, 3*i+3] for i in range(3)]

    def get_move(self):
        """Retrieve move input from user."""
        while True:
            try:
                for i in range(3):
                    print(f'{self.board[i]}     {self.available_moves[i]}')
                move = int(input('Choose your move: '))
                for i in range(3):
                    if move in self.available_moves[i]:
                        return move
            except ValueError:
                print('Invalid choice. Please enter an integer.')
            else:
                print('Invalid choice. Please try again.')

    def update(self, player: int, move: int):
        """Update board in place with player's symbol at the indicated move location."""
        row_idx = (move - 1) // 3
        col_idx = (move - 1) % 3

        if player == 1:
            self.board[row_idx][col_idx] = 'X'
        else:
            self.board[row_idx][col_idx] = 'O'

        self.available_moves[row_idx][col_idx] = '_'
    
    def get_win_combos(self):
        """Retrieve all potential win states from board."""
        return [self.board[0],
                self.board[1],
                self.board[2],
                [self.board[i][0] for i in range(3)],
                [self.board[i][1] for i in range(3)],
                [self.board[i][2] for i in range(3)],
                [self.board[i][i] for i in range(3)],
                [self.board[i][2-i] for i in range(3)]]
    
    def check_for_win(self):
        if any(combo in self.winners for combo in self.get_win_combos()):
            return True
        
        return False
    
    def check_for_stalemate(self):
        for i in range(3):
            if any(element != '_' for element in self.available_moves[i]):
                return False
            
        return True
    
    def print_board(self):
        for i in range(3):
            print(self.board[i])

    def get_available_moves(self):
        if self.check_for_win():
            return []
        
        return [move for row in self.available_moves for move in row if isinstance(move, int)]