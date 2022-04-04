"""
TT.py

transposition table
adapted from Martin's implementation in the 655 assignment

Jiayi
March 30, 2022
"""
class TranspositionTable(object):
    def __init__(self):
        self.table = {}

    def __repr__(self):
        return self.table.__repr__()

    #key is tuple
    def store(self, position_player, result):
        self.table[position_player] = result
    
    def lookup(self, position_player):
        return self.table.get(position_player)
