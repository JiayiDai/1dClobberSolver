"""
Implementation of
1d clobber game play,
negamax,
abpruning,
enhancements

Jiayi
Jan 28, 2022
"""
import time, random

position = ""
moves = []
winning_move =  tuple()

def opponent(player):
    if player == "B":
        return("W")
    return("B")

def legalMoves(position, player):
    moves = []
    opp = opponent(player)
    for i in range(len(position)):
        if position[i] == player:
            if i == 0:
                if position[i+1] == opp:
                    moves.append((0, 1))
            elif i == len(position) - 1:
                if position[i-1] == opp:
                    moves.append((i, i-1))
            else:
                if position[i-1] == opp:
                    moves.append((i, i-1))       
                if position[i+1] == opp:
                    moves.append((i, i+1))
    return(moves)

def initialLegalMoves(player, initial_position):
    black_moves = []#reset
    white_moves = []
    for i in range(len(initial_position)):
        current_stone = initial_position[i]
        if i > 0:
            left_stone = initial_position[i-1]
        if i < len(initial_position)-1:
            right_stone = initial_position[i+1]
            
        if i == 0:
            if current_stone != right_stone and current_stone != "." and right_stone != ".":
                if current_stone == "W":
                    white_moves.append((i, i+1))
                else:
                    black_moves.append((i, i+1))
        elif i == len(initial_position) - 1:
            if current_stone != left_stone and current_stone != "." and left_stone != ".":
                if current_stone == "W":
                    white_moves.append((i, i-1))
                else:
                    black_moves.append((i, i-1))                
        else:
            if current_stone != right_stone and current_stone != "." and right_stone != ".":
                if current_stone == "W":
                    white_moves.append((i, i+1))
                else:
                    black_moves.append((i, i+1))
            if current_stone != left_stone and current_stone != "." and left_stone != ".":
                if current_stone == "W":
                    white_moves.append((i, i-1))
                else:
                    black_moves.append((i, i-1))
    if player == "B":
        return(black_moves)
    else:
        return(white_moves)

def move_set(player):
    if player == "W":
        return(white_moves)
    else:
        return(black_moves)

def oppo_move(move):
    return((move[1], move[0]))

def oppo_moveset(moveset):
    oppo_moveset = []
    for move in moveset:
        oppo_moveset.append(oppo_move(move))
    return(oppo_moveset)
        
def moves_tracking(player, move, moves):
    if player == "B":
        black_moves = moves
        black_moves.remove(move)
        if move[0] > move[1]:
            if move[0] < len(position)-1 and position[move[0]+1] == "W":
                    black_moves.remove((move[0], move[0]+1))
            if move[1] > 0:
                if position[move[1]-1] == "B":
                    black_moves.remove((move[1]-1, move[1]))
                elif position[move[1]-1] == "W":
                    black_moves.append((move[1], move[1]-1))
            
        else:
            if move[0] > 0 and position[move[0]-1] == "W":
                black_moves.remove((move[0], move[0]-1))
            if move[1] < len(position)-1:
                if position[move[1]+1] == "B":
                    black_moves.remove((move[1]+1, move[1]))
                elif position[move[1]+1] == "W":
                    black_moves.append((move[1], move[1]+1))
        return(black_moves)
    else:
        white_moves = moves
        white_moves.remove(move)
        if move[0] > move[1]:
            if move[0] < len(position)-1 and position[move[0]+1] == "B":
                    white_moves.remove((move[0], move[0]+1))
            if move[1] > 0:
                if position[move[1]-1] == "W":
                    white_moves.remove((move[1]-1, move[1]))
                elif position[move[1]-1] == "B":
                    white_moves.append((move[1], move[1]-1))
            
        else:
            if move[0] > 0 and position[move[0]-1] == "B":
                white_moves.remove((move[0], move[0]-1))
            if move[1] < len(position)-1:
                if position[move[1]+1] == "W":
                    white_moves.remove((move[1]+1, move[1]))
                elif position[move[1]+1] == "B":
                    white_moves.append((move[1], move[1]+1))
        return(white_moves)
    
def listToStr(l):
    s = str()
    for i in l:
        s = s + i
    return(s)

def play(move):
    global position
    list_position = list(position)
    list_position[move[1]] = list_position[move[0]]
    list_position[move[0]] = "."
    position = listToStr(list_position)

def undo(move):
    global position
    list_position = list(position)
    list_position[move[0]] = list_position[move[1]]
    if list_position[move[1]] == "W":
        list_position[move[1]] = "B"
    else:
        list_position[move[1]] = "W"
    position = listToStr(list_position)

def isEnd(position, player):
    return(len(legalMoves(position, player)) == 0)

def randomPosition(l):
    global position
    for i in range(l):
        random_num = random.randint(0, 1)
        if random_num == 0:
            position = position + "B"
        elif random_num == 1:
            position = position + "W"
        else:
            pass

def negamaxBoolean(player):
    global position, winning_move
    if isEnd(position, player):
        #winnin_move = None
        return(False)
    for move in legalMoves(position, player):
        play(move)
        success = not negamaxBoolean(opponent(player))
        undo(move)
        if success:
            winning_move = move
            return(True)
    return(False)

def legalMovesTracking(player, move):
    global position
    new_moves = moves
    new_moves.remove(move)
    if move[1] > move[0]:
        try:
            new_moves.remove((move[1]+1, move[1]))
        except:
            pass
        try:
            new_moves.remove((move[0], move[0]-1))
        except:
            pass
        try:
            if position[move[1] + 1] == opponent(player):
                new_moves.append((move[1], move[1]+1))
        except:
            pass
    else:
        try:
            new_moves.remove((move[1]-1, move[1]))
        except:
            pass
        try:
            new_moves.remove((move[0], move[0]+1))
        except:
            pass
        try:
            if move[1] > 0 and position[move[1] - 1] == opponent(player):
                new_moves.append((move[1], move[1]-1))
        except:
            pass
    return(new_moves)

def isEndTrack(moves):
    return(len(moves) == 0)



def negamaxBooleanTrackingMoves(player, depth=0):
    global winning_move, position, moves
    if len(moves)==0:
        return(False)
    
    old_moves = moves
    for move in moves:
        play(move)
        
        moves = oppo_moveset(legalMovesTracking(player, move))
        print(moves)
        success = not negamaxBooleanTrackingMoves(opponent(player), depth+1)
        undo(move)
        moves = old_moves
        if success:
            winning_move = move
            return(True)
        
    return(False)

def alphabeta(player, a, b):
    global position, winning_move
    if isEnd(position, player):
        return(False)
    for move in legalMoves(position, player):
        play(move)
        value = not alphabeta(opponent(player), not b, not a)
        if value > a:
            a = value
            winning_move = move
        undo(move)
        if value >= b:
            return(b)
    return(a)

def main():
    global position, winning_move, moves
    #randomPosition(10)
    #print(position)
    
    initial_position = "BWWWBB"
    position = initial_position
    for player in ["B", "W"]:
        print("player = ", player)
        print(position)
        start = time.time()
        if negamaxBoolean(player):
            print(player, winning_move)
        else:
            print(opponent(player), None)
        end = time.time()
        elasped_time = end - start
        print(elasped_time)
        print()
        """
        print(position)
        winning_move = ""
        start = time.time()
        moves = initialLegalMoves(player, position)
        if negamaxBooleanTrackingMoves(player):
            print(player, winning_move)
        else:
            print(opponent(player), None)
        end = time.time()
        elasped_time = end - start
        print(elasped_time)
        print()
        position = initial_position
        """
        """
        winning_move = tuple()#reset
        
        start = time.time()
        if alphabeta(player, False, True):
            print(player, winning_move)
        else:
            print(opponent(player), None)
        end = time.time()
        elasped_time = end - start
        print(elasped_time)
        print()
        """

main()
#initialLegalMoves("BBBBWWBWBBBBBWBWWWWBBB")#get initial black/white moves

