from board import Board
from mcts import choose_move

def play_game():
    """Play a game of Tic-Tac-Toe."""
    while True:
        board = Board()
        player = 1

        # Loop for valid player selection
        while True:
            try:
                user = int(input('\nChoose your player. [1/2]: '))
            except ValueError:
                print('\nInvalid choice. Please enter an integer.')
                continue

            if user in (1, 2):
                break
            else:
                print('\nInvalid choice. Try again.')

        # Game loop
        while True:
            print(f"\nIt's Player {player}'s turn!")

            if player == user:
                move = board.get_move()
            else:
                print('\nThinking...')
                move = choose_move(user, board, 700)

            board.update(player, move)
            winner = board.check_for_win()
            stalemate = board.check_for_stalemate()

            if winner:
                print(f'\nPlayer {player} won!')
                board.print_board()
                break
            elif stalemate:
                print("\nIt's a tie!")
                board.print_board()
                break
            else:
                player = 3 - player
        
        # Loop for replay
        while True:
            play_again = input('\nWould you like to play again? [Y/N]: ').lower()

            if play_again == 'n':
                print('\nThanks for playing!')
                return None
            elif play_again != 'y':
                print('\nInvalid choice. Please type "Y" or "N."')
            else:
                break

if __name__ == '__main__':
    play_game()