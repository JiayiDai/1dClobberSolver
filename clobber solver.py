"""
Implementation of
1d clobber game play,
negamax,
abpruning,
move tracking,
parallel Negamax,
database construction


decompose and subgame algebra functions
are adapted from my implementation in 655
Clobber assignment

removePsg is adapted from Xinyue's
implementation

Jiayi
April 4, 2022
"""
import time, random, multiprocessing, sys, TT

position = ""
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
                try:#in case len = 1
                    if position[i+1] == opp:
                        moves.append((0, 1))
                except:
                    pass
            elif i == len(position) - 1:
                if position[i-1] == opp:
                    moves.append((i, i-1))
            else:
                if position[i-1] == opp:
                    moves.append((i, i-1))
                if position[i+1] == opp:
                    moves.append((i, i+1))

    return(moves)

def oppo_move(move):
    return((move[1], move[0]))

def oppo_moveset(moveset):
    oppo_moveset = []
    for move in moveset:
        oppo_moveset.append(oppo_move(move))
    return(oppo_moveset)
    
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

#return new position
def playLocal(move, position):
    list_position = list(position)
    list_position[move[1]] = list_position[move[0]]
    list_position[move[0]] = "."
    return(listToStr(list_position))   

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

def legalMovesTracking(player, moves, move, position):
    #global position
    new_moves = moves[:]
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

def negamaxBoolean(player):
    global position, winning_move, tt
    if isEnd(position, player):
        #winnin_move = None
        return(False)
    result = tt.lookup((position, player))
    if result != None:
        return(result)
    moves = legalMoves(position, player)
    for move in moves:
        play(move)
        success = not negamaxBoolean(opponent(player))
        undo(move)
        if success:
            winning_move = move
            tt.store((position, player), True)#win
            return(True)
    tt.store((position, player), False)#loss
    return(False)

def negamaxBooleanTrackingMoves(player, moves):
    global winning_move, position, tt
    if len(moves)==0:
        return(False)
    result = tt.lookup((position, player))
    if result != None:
        return(result)
    for move in moves:
        play(move)
        oppo_moves = oppo_moveset(legalMovesTracking(player, moves, move, position))
        success = not negamaxBooleanTrackingMoves(opponent(player), oppo_moves)
        undo(move)
        if success:
            winning_move = move
            tt.store((position, player), True)#win
            return(True)
    tt.store((position, player), False)#loss
    return(False)

def negamaxLocal(args):
    global tt
    player, moves, child_position = args
    if len(moves)==0:
        return(False)
    result = tt.lookup((child_position, player))
    if result != None:
        return(result)
    for move in moves:
        new_position = playLocal(move, child_position)
        oppo_moves = oppo_moveset(legalMovesTracking(player, moves, move, new_position))
        success = not negamaxLocal((opponent(player), oppo_moves, new_position))
        if success:
            tt.store((child_position, player), True)#win
            return(True)
    tt.store((child_position, player), False)#loss
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

def randomPosition3(l):
    position = ""
    for i in range(l):
        random_num = random.randint(0, 2)
        if random_num == 0:
            position = position + "B"
        elif random_num == 1:
            position = position + "W"
        else:
            position = position + "."
    return(position)

def randomPosition2(l):
    position = ""
    for i in range(l):
        random_num = random.randint(0, 1)
        if random_num == 0:
            position = position + "B"
        else:
            position = position + "W"
    return(position)

def randomPositions(n, l):
    positions = []
    for i in range(n):
        positions.append(randomPosition3(l))
    return(positions)

#get all positions of length up to 12
def positionsGeneration(upperb=13):
    import math
    s = ["B"]
    for j in range(upperb):
        for i in s[math.floor(len(s)/2):]:
            s.append(i+"B")
            s.append(i+"W")
    return(s)
    
def inverse(position):
    new_position = ""
    for color in position:
        if color == "B":
            new_color = "W"
        else:
            new_color = "B"
        new_position += new_color
    return(new_position)

def args_list(args1, args2, args3):
    result = []
    for i in range(len(args1)):
        result.append([args1[i], args2[i], args3[i]])
    return(result)

def negamaxParallel(position, player, moves, pruned_moves=[]):
    moves = moveOrdering(legalMoves(position, player))
    num_workers = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(num_workers-2)
    
    #prepare arguments for workers
    child_positions = []
    move_sets = []

    left_moves = [m for m in moves if m not in pruned_moves]
    players = [opponent(player)]*len(left_moves)#opponent to go
    for move in left_moves:
        child_positions.append(playLocal(move, position))
        move_sets.append(oppo_moveset(legalMovesTracking(player, moves, move, position)))
    args = args_list(players, move_sets, child_positions)
    results = pool.imap(negamaxLocal, args)
    pool.close()
    count = 0
    for res in results:
        if res is False:#STOP when one returns false/loss
            pool.terminate()
            return(player, left_moves[count])
            break
        count += 1
    if count == len(left_moves):
        return(opponent(player), None)

def readDatabase(path):
    f = open(path, "r")
    lines = f.readlines()
    f.close()
    database = {}
    for line in lines:
        line_list = line.split()
        position = line_list[0]
        player = line_list[1]
        result = line_list[2]
        key = (position, player)
        database[key] = eval(result)
    return(database)

#win or loss or unknown
#true or false or none
def sgSum(sg1, sg2, player):
    sg1_result = sgLRNP(sg1)
    sg2_result = sgLRNP(sg2)
    #
    if sg1_result == "L" and sg2_result == "L":
        if player == "B":
            return(True)
        else:
            return(False)
    elif sg1_result == "L" and sg2_result == "P":
        if player == "B":
            return(True)
        else:
            return(False)
    elif sg1_result == "L" and sg2_result == "R":
        return(None)
    elif sg1_result == "L" and sg2_result == "N":
        if player == "B":
            return(True)
        else:
            return(None)
    #
    elif sg1_result == "P" and sg2_result == "L":
        if player == "B":
            return(True)
        else:
            return(False)
    elif sg1_result == "P" and sg2_result == "P":
        return(False)
    elif sg1_result == "P" and sg2_result == "R":
        if player == "B":
            return(False)
        else:
            return(True)
    elif sg1_result == "P" and sg2_result == "N":
        return(True)
    #
    elif sg1_result == "R" and sg2_result == "L":
        return(None)
    elif sg1_result == "R" and sg2_result == "P":
        if player == "B":
            return(False)
        else:
            return(True)
    elif sg1_result == "R" and sg2_result == "R":
        if player == "B":
            return(False)
        else:
            return(True)
    elif sg1_result == "R" and sg2_result == "N":
        if player == "B":
            return(None)
        else:
            return(True)
    #
    elif sg1_result == "N" and sg2_result == "L":
        if player == "B":
            return(True)
        else:
            return(None)
    elif sg1_result == "N" and sg2_result == "P":
        if player == "B":
            return(True)
        else:
            return(True)
    elif sg1_result == "N" and sg2_result == "R":
        if player == "B":
            return(None)
        else:
            return(True)
    elif sg1_result == "N" and sg2_result == "N":
        return(None)

def sgResult(sg, player):#win or loss
    #global position
    #if (sg, player) in database:
    #    return(database[(sg, player)])
    #else:
    #   position = sg[:]
    return(negamaxBooleanTrackingMoves(player, legalMoves(sg, player)))

    
def sgLRNP(sg):#L, R, N, P
    resultB = sgResult(sg, "B")
    resultW = sgResult(sg, "W")
    if resultB == True and resultW == False:
        return("L")
    elif resultB == False and resultW == True:
        return("R")
    elif resultB == True and resultW == True:
        return("N")
    elif resultB == False and resultW == False:
        return("P")
    else:
        print("???")

def decompose(position, player, moves):
    pruned_moves = []
    for move in moves:
        child_position = playLocal(move, position)
        sg1 = child_position[:move[0]]
        sg2 = child_position[move[0]+1:]
        if len(sg1) < len(position)/3 or len(sg2) < len(position)/3:
            continue#only do optimistic cases
        else:
            sum_result = sgSum(sg1, sg2, opponent(player))
            if sum_result == False:#opponent loses
                return(True, move)
            if sum_result == True:#opponent wins; move pruned
                pruned_moves.append(move)
    #print("Fail")
    return(None, pruned_moves)

opti_count = 0
notopti_count = 0
pruned_count = 0

def solver(position, player, moves):
    global opti_count, notopti_count, pruned_count
    decomp_result = decompose(position, player, moves)
    if decomp_result[0] == True:
        print("optimistic case")
        opti_count+=1
        return(player, decomp_result[1])
    else:
        print("not optimistic case")
        notopti_count+=1
        pruned_moves = decomp_result[1]
        pruned_count += len(pruned_moves)
        search_result = negamaxParallel(position, player, moves, pruned_moves)
        return(search_result[0], search_result[1])

#among B's moves in (BW)^n
#(2, 1) is the lucky move!
def moveOrdering(moves):
    new_moves = moves[:]
    if (2,1) in moves:
        new_moves.remove((2,1))
        moves = [(2,1)]
        moves = moves + new_moves
        return(moves)
    return(moves)

#adapted from Xinyue's implementation
def removePsg(position):
    subgame_list = []
    gamestr = ""
    for i in range(len(position)):
        if position[i] == "B":
            gamestr += "B"
        elif position[i] == "W":
            gamestr += "W"
        else:
            subgame_list.append(gamestr)
            subgame_list.append(".")
            gamestr = ""
    subgame_list.append(gamestr)
    for i in range(len(subgame_list)):
        if i != ".":
            key1 = (subgame_list[i], "B")
        if key1 in database:
            key2 = (subgame_list[i], "W")
            if database[key1] == False and database[key2] == False:
                lenght = len(subgame_list[i])
                subgame_list[i] = "."*lenght
    new_string = ''.join(subgame_list)
    
    return(new_string)
positions20 = ['.WB.BB.BWB.W.WBBWW.W', 'B...WBBWBWW.WB.WWW..', '.W.BBW..BB...BW.BWW.', 'W.W.WWWBB.BWW.....WW', '..BW...WBWB.BWWWBBWB', 'WBWB.WW....WW.WWW...', 'WWWW.BBB.WWWBWBWWWWB', 'B.BWBBBBBBBW.WB.BW..', '.W.W.BW.BBBBW..W.BBB', '.BBBBBWBB.WB.B.B.BB.', 'BWBWB.BBB.BW.WB.WBWB', 'WBWW...BBBB.W.WBBBBB', '.WBBBW.BWBWBBWBWBBBW', 'WWB..WBWW..WBBB...BW', '.WBW.W.BW.WB.W.B.WBW', 'B..W.WWBBWBB.B.BB.WB', 'BBWWBWWWW.WWB.WB.WB.', 'BBW.WBW..BWBB.WBB..B', 'BWW.W.BW..W.BBBW.WBB', 'BB.WW.BBWB.BB.WW.W..', 'WB.BBBB.WBBWWBBW.B.B', 'W.BBBWBBWW.BWWBBBBW.', 'BW....BWBBB..WWBBBBB', 'W....B.BWBW.WW.BW..B', 'BWWWW..WBWBBBWBB.B..', 'BWWWBB..W..W.WB.BBBW', '.W.BBWWB...BWB.BB..B', '.BBW.BW.WBWWW.WBWW.W', '.WWBWWWWWBBBBBBB.B.B', '.B.BBWW.B.WBBWW..WBW', 'BW.WWWBW.BWW..W.BBBB', 'W.B.BBBBB..BWB.BBB..', '.BBBWBB.B..WWW..BW..', '.BWW.WW.W.WB.BB..BWB', 'BB.BWB.W.WW.BW..W.W.', 'WW.WWWB.WW.WBW.B.WBB', 'BBB.B.BWBWBBBWWW..B.', 'W...B.W..BBW.BW.BB..', '..WWWB.BWBB..B.W..B.', '.WBBBWWWWW..WWWWB.W.', 'BWW.BBW.B.B.WW...B.W', 'WBBW.W.BB.B.BBWBWBB.', 'WB.WWBB.BBBW..BBBW..', 'WWWBW.WWB..WBB.BBBBB', '.W.BW.B...W.B..WBBWW', 'WBWWWW.WWB.WBW..B..B', 'WWBBWWWW..WWWWBW.WB.', '..WWWWB..B.W.W.BB.BB', 'B.BBBW.BWW..WWBWWWWB', 'B.BWWBBBWBWB.WBWBW..']
positions30 = ['WBWW...B..WBB.BBB.BWWWB.BWBWBB', 'WWBB.B...WWB.B.WWBBBWW...B.WWW', 'B....WWW.B...W.WB.WW.BWWB.BBBW', 'BBBWWW.WB.B.B.WWWB.BWWBBB..WB.', 'WWWWBWBWBW.BB.W.WWWBB.WWWB.W..', 'W.W......BBWW..BWWBBBBBWB..B..', 'B.WB.WWWWWB..BBW..B.BBBW.WB..B', 'WBBBWWWB.BW...BW.BBW.BBWB.BW.B', 'WBB.BBB.WWBBB.W.W...W.WWWW..WW', '.W.W...WBWB.WB.BBB.BWWB.WWB..W', 'WBBBW.BBBW.BB..WBBWBBBW.WBWBBW', 'WBW....WBWB.BBWBWWW.W.B.WB...W', '.BBWBWWWWWBB.WBWW...BBB.WWBWWB', '.BBBBBWWBB..WBB.BBWWBBWBBW.BB.', 'BWB..WB..WW.WB..BW...B.WWBBBWW', 'B..WW...W.W.WBWWW.WBWWWB..BBW.', 'BWWB.WBBWBWWW....W.B....W.W.B.', 'B..BWBBWBBWBW..WWBW.WBBWWBBW.W', 'BWB.WWWBBWB..BW......BWWW..WB.', '.BWBBW.WBBWBWBWBW.BB....BW..BW', '.B.WWWWBBWBW..B.WW..WB.WB..B.W', 'BW..W.BB.....BWWB..WBW.WBWWWBW', '.BWWBB.B...WWBWWWBBWW.WWBBBW.B', '..WBBWWWWWWWWW.W.BB..B..WWWBWB', 'BWWBBB.WBWBB.BBWBBB.BWBWBW.WB.', 'W...B.WWBWBBW.BWWWB.WW.W.BW..B', 'WW...BBW..W.B.BWWBWW..BWW....B', 'BB.WBWBB.B..WWWW....BBBBWBW.B.', 'WB.WBBW....BWBWBBB.W..B.BW..BW', 'B..BB..WWWW.B.BWBW.W.WW.WWWBW.', '...BWWW.BWBBB.WBBBBWWWBBW...WW', 'BWWBW..BB..W.WBBBB.WB..WWBBB.B', 'BBB..BB.W.BWW..B..WBW.B.WBWB..', 'WW.BW..W.WW.WBW.BB.WWB...B.B..', '.B..WWBB.B..B.WWWWBBBBWBBBWW.W', 'B...BW..B.BBBW.B...WW..BWB.W.W', 'W.W.B.B.WW..BWBBWBBBB..B.BBW.W', 'WWBBBBBWBWBBBWBBWB...W.WWWB.W.', 'BBB.BWW..BB..BBB.BBWBBWW.B.WWW', 'W..WWBWBBWBBBW.WB.W.WBWBWBB...', 'WB...WWBW..B.WBWBWBB.BWW...B.W', 'WB...BWBBWBW.BBWW..B.B.W..WWB.', 'WW.B.BBBBB.WW..WB.BBBWBWBW...W', 'WW.B.BB..W...B...B..WWWWB.BBW.', '.WWBBBWWBBWB.WBBBB..BB.W.WWWBB', '..B..BBBWW.B.W.B.W.BWW.WBBWBW.', 'WW.BW.WWWBWBBB.BWBW.B..BW.B.BB', '.W.B.B.B.WW..BBBWWWBBBBBBWWW.W', 'W.WWWW.WW.BBW.WBWWWWBW.BWBB.BW', '.BBWBB.BWBBBWBWWBWW.W..W.WWBW.']
positions40 = ['W.WBW.WWWW.B.W..BBW.B.W.W.BWW..B.B.WW.B.', '.BBWBWBB..BW.B.WBW..BBWBW.BBB..BW.BW.W.W', 'WBWWB.W.WBWB.BBBBBWBBBBW.W..WBBW.B.BBWBW', '.B....W.B.WW.BBW.B.WWW.BW..BW.WB.WWBB.B.', '.BWWB.B..WW..B...B.B.B.WB..WWBW..BBBWB..', '..W..WW..B.BWB...W.B...WBBWWWB.W.WB.WBB.', 'WWBB.W.WWWB.BWWWBWW....B...WBBWWBW..W.BW', 'B..W....B..B.BBWBWWBB....W.WWBB.WW.BW.W.', 'WB.B..WB....BB...W.WBB.W.WWWBWWBBW..B.W.', 'BWBW.W..BBBW.BBWW..BBWWW.BB.W...BBWB...B', 'W.WB.BW.W.B.B.W....B.W.W.WWWW.B.WB.BBBBB', 'W..WBWBWW.WWWWBWWWBWWWWWW.BWWBWBWW.BWBBW', '.BW.WBW.W..WBWBBW...BWWB.WB.WW.BBWBBBWW.', 'W.WWWBBBW.BBWW.WBB...WBB...WW.W.B.BWBWW.', '.WWB.B.WWBWBWBBB..WWBW.B.W.B.B.BWBW.B.B.', 'BBW.W..BW.WWWWWB.W.BB.W....B..BBB.W.WWBB', 'BWW.BBWB.WW..B.BBBBBB..BW.WBW.B.BBBW.B.W', '..B..BBWWBBBWWBB..WBWB.WW...W.BWB..WWB.W', '....BW....B..BWWBB.B.BBBWWB..W.WW...BB..', 'B.B.BBBBW.B.WB.W...WWWWWW..W..BWWW..B...', 'WBB.WW.BWW.BW.BWWB.W.BB......BWWWW.WB..B', '.BB.BBWB..W..WWBBBBBBWW..W.B....BWW..BBB', '..WB..BBWWW.B...B..WWW.WBWWW.B.WW..BBWB.', 'BB.BWWBBWBBBBWBB.WB...BB..WBBB.WBWW....B', '..B.W..WWBW.WBWBW.WW.BBWW...B.BWBWBWWBWW', 'WWB.B..B.BBWWWBW....B.BBB.BBBWBW.B.B.BWB', '.BBW.W.BBW....W.BWBBW.WW..BWBBB.W.W.BB.W', 'WBWWBBB...BWWBBW.BWWBW.BB.W.B...WBBW.BB.', '..BWWWBW..BBBBW..W.BBBWWBB.B.B.B...W..WW', '..BBWWBB.WWW..B....WBW..BB.BBWW..WB.WBW.', 'BWWBB.WBWBBWBW.WBB.BB.B.W.WWB..B.W.W.WW.', 'BWBBWWBBBWBBBWWBBW.W.WWWB....B..WBWW....', 'B.WBWBWW.W..BWWBW.BB.BWBWW.WWW....BWWBB.', 'B.W..WB..B..WB.BB..W.BWBB.WWW.BW...B.BBB', '.BWBWBBB......B.B.W.BBB...WWBWBBBB.WB.BB', '..WWBW.WW.W..BBBBW.WW..BWW..BW.BBWWWW.BW', 'B.WBW..WW.WB.BW.BBBWWB...W.WB...W....BW.', '..B.BBWBW..BBWBWW.B...W..W.WBB.W...WWBBW', 'W.BWW.BWB..WBBBWWBWB.WBBWBBW.B.B..BBBWWW', 'W...B.BW.BBWWBWW...WW.BW...W.W.B.W.W.BBW', 'BW.BBW.W.B..BWWB.BWWB..BBWBB..WW..W....W', 'B.BWBBWB.BWBW.W...B..WWW.WB.BBBBB.BW.B.W', '.W.BW.B.BBB.B.BWWB.B..W.W.BB.W.WBWBWWBWB', 'BBWWWB.WB..BWBB.WWW.BWBB.W..B.W.WBBW.BB.', 'WWBWWBB.BWW.B.B...BWBB..BWWWWBWWWWWBBWBB', '..WWB.WWB.W.BW..BBB...W.WB.WBWWB.W.WWW.B', 'BWWW.WBBBWB.WBW..BBWWB..WW...BWBB.B...WB', 'BWWWW.BWWWWW.WW.WWWW.BB..BBWB.BBWWWW..W.', 'BW...BBBBBBBWBWBWW.W.BWB.BWBW.W..B.WWWWW', '.BBW.BB.W...BWWWBWBW.WBB.W.BWB..BBW..BWW']
positions50 = ['.WBWWWWWB..WBW.BBW.WBBB.W.W.B.BB.WWWWW.WW.B.WW.WBB', '.BW..WBBWB.W.W..BBWBW....B.B.WB.B.BBBWBBBBB.WB..BW', '.W..BW.WB.W....WW.WBWWWWWW..WBW.W..WW.W.W.W.WBBW.W', 'BBWWB.W.WBWWBW.WBBWWWWW.BW.BW.W.W.WWW.BBWBW..B.B.B', 'W.BBB..WBBWB..W.WBBBW.WWWWBW...WBB.WBBW.BWWW.BW.BW', 'WBBWB.W.BBBBW.W..BW.B.BW.WBWW...WW....BBWBW.BBW.W.', '.B.B..WB.BW...W...B.BBB.BWBWWWW..BWBB..BBWW...BWBW', 'BWW.WWW.BB.B.WWW.WWW.BWBW.WB.W..W..BWWBW.WWBWWBBW.', '..BWBB..BBWBWBBWWBBBW..B..WW.BB..WWBB.WWB.B.BBWWB.', 'WWBWWBB.B..WBWB..WBBWWB.W.B..BBWBB.BB.BBWB..B..WBW', '.BB.BBWB.BWWWWBBBBBWBBBBB.WB.BBBWBBWWW...BW.WW.WWW', 'BWB..BW..WBBWBBW.BWBWW.BB.WBWWWBWWB.B..W..B.BB.WWW', 'WB..WB.WBB.WW.W.WBWWW..BWWBB.BWBBBBBWBW.W.W.WB.W..', '...BW.BB...W.WBB.B.WB.B.WW.BBWWBW.BW.BBB.B.B.B.WBW', 'BBBW.W..B..WWW.W.B..WBBB.WBW..WW.W....WBWWB.B.WWB.', 'BBBB.....BWBBW.BBWW..W.WW.BB..B.B..B.W.B..BBW...WW', 'BBBWW.W...B.WWWBBBBB.BBW...WB.BB..WWBW..B.BWBBBB.W', 'WW..BWWBW.WBW.WB..WBW.B....B.WWBBWBWW.BWB...WBWBW.', 'W..B..BWWW..W.W..BB.WBBB.WWWB.BBWB.WB..BBB...WWB.B', 'BB.B.WWB.BW..B.W.WBBBWWWBWBWWWW..BBBB.BBB..BBWB..B', '...WB.WB...BWW.BBWWWB..W.WW.BW.W.W.WBBWW.BBWBBWB.W', 'W..BW.B.WWWWWWB.BW..WW.WWBB.BBW.WBWW.W.BW..WBB.WWB', 'WB.W..BBB.BW.B.W.BB...W.WWW.W..BW.WWBW.WWBWBWBWB.W', 'B.BWB..WWWWWBBBB....BBWWBW.BWWWBWB.W.BWW...BBW.WWW', 'BB.WWW.W.BWBBWW.WB.WB.BWWB...B.BWW..W..WWWBWW.BBBB', 'W...BWB.WW.BBB..BB.WW.B.WB..BW.BBWW.B.BBW.BB...W.W', 'WWWW..W.WWBB.BWB.WB.WBBBWBB.WWWWW.WWWBWWWB..WW...B', 'W..B...B.WW..W.WW.WB.....B.W.BWW.WWW.WBWWWBBWBW.WW', 'WBWWWB.BBBBBB...BWB.BWB.W.B.B.B..BW..BBBW.B.BW.BW.', 'BBB.BWWWBBB.BBW.BBBWW..B.W..BBBBW.W.WWWBBBB..WBBW.', '.BB.WB.WW.W...BWW.B.WW...BBBBBBW.WW.BB.W.WWWBBW.WW', '..BBWBBB.WWWW..BWW.W..WBB.W..BBW.BWWBWB...WWB..WB.', 'BBBW.BB.BW.W.W.B.WW.W..BWWBBB..B.BWW.B.B..B.W.WWWW', '.W.WWW.W..WBWB.W..WWBWWWB..BBWBWW.W...BWB.WW..BW..', '.WBBWWB.W.B.W.BWW.WBWWBB.WWBW.WW..B.W.WBB.WWWBBBB.', 'WWBBB.BWB.W.BBW..WBB...B.BBB.BWWBBW.BBBWW.BW..BWWB', '.B..B.W.BWWWWW..WWW.BWWWB.WWW.WWW..BWW.WW.WBBWWBW.', '..WWWBBWBWW...BWW..B...BBW.BWW..WWB...W...W.WWWW..', 'W.BWB.WWBB...W.WBW..WWBWBBB.B.W.BWWB....WWWBWW...W', 'BW.BWBB.B.BWBBWB.BBB..WB.W.BBWWB..B.BWBWWWB.B.WW..', 'WWBBW.BWWBB...BWBW.BW.W.W.WWBB..BWWWBBB.BBBWBWW.WB', 'BBBW.BWBW...W.B..BBW.WBW..WWB.WW.W...WB.W.BWW.W.WW', 'B.BWBB...WWW.W.B.WW...BWW.W.BWB.BBB.B.WBBBWW.BBBW.', 'WW.BB.WBBBW.BBB...B..W.BW..WBB.W.BWW..BW.BBBBW.WWW', 'WW.W.W.BBBWBWB.BB..WWB.WB...BBW.BW.W...B.W.BB.B..W', 'B.WB..BW.BB.WBBBB.WBWB..BW....W.W..BBBB...W..BB..B', 'WBB..B..W.B.WWWBWBBW..WBBW.BB..WB.BBW.BWWBBBWWW.BW', '.WBWW..WBWWW..BWB.W.WWWW..BBW.B.BWWB.BWBWWBBBW.WWW', 'W..BBB..BW..WWB.B.BWB.B...W.WBWWB.WWWWWB...W....W.', '..WB...B..B.BW.W.BW.BBWBBBWW.BWW..WBBB..BWWW.BB..W']

#main
tt = TT.TranspositionTable()
#start = time.time()
#database = readDatabase("database11.txt")
#print("loading:", time.time()-start)
if __name__ == "__main__":
    t1 = 0
    t2 = 0
    n = 50
    player = "B"
    """
    for i in positions40:#testing
        tt = TT.TranspositionTable()
        position = i
        print(position)
        moves = legalMoves(position, player)
        
        #method 1
        start = time.time()
        print(position)
        print(solver(position, player, moves))
        end = time.time()
        elasped_time1 = end - start
        print("not remove P:", elasped_time1)
        t1 += elasped_time1
        print()

        position = i
        tt = TT.TranspositionTable()#reset
        moves = legalMoves(position, player)
        
        #method 2
        start = time.time()
        position = removePsg(position)
        print(position)
        #print(negamaxParallel(position, player, moves, pruned_moves=[]))
        print(solver(position, player, moves))
        end = time.time()
        elasped_time2 = end - start
        print("remove P:", elasped_time2)
        t2 += elasped_time2
        print("========================")

    """
    """
    for i in range(16):#"BW"*i
        position = "BW"*i
        print(position)
        moves = legalMoves(position, player)
        start = time.time()
        #position = removePsg(position)
        print(solver(position, player, moves))
        end = time.time()
        elasped_time = end - start
        print("time:", elasped_time)
        t2 += elasped_time
        print("========================")
    """
    #print("not remove P:", t1/n)
    #print("remove P:", t2/n)
    #print("opti_count:", opti_count)
    #print("notopti_count:", notopti_count)
    #print("avg. pruned_count:", pruned_count/n)
    
#performanceTest()
