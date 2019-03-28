import random
import time
import math
from BaseAI_3 import BaseAI
from queue import Queue
from Grid_3 import Grid

maxTime = 0.193
probability_of_two = 0.9
probability_of_four = 1 - probability_of_two

#multiplied this by 10 lol
MONOTONICITY_1_WEIGHT = 4508.35#3003 #3211 #3125
MONOTONICITY_2_WEIGHT = 3005#3003
MAX_TILE_MULTIPLIER = 1.1
SMOOTHNESS_WEIGHT = 4402.85 #200#128#121 #2.8
EMPTY_TILES_WEIGHT = 251.5#250.5#4000 #10000
AVG_TILES_WEIGHT = 2#2.18

class PlayerAI(BaseAI):

    def overtime(self):
        if time.process_time() - self.prevTime > maxTime:
            return True

        return False

    def getMove(self, grid):
        # # Selects a random move and returns it
        # moveset = grid.getAvailableMoves()
        # return random.choice(moveset)[0] if moveset else None
        d = self.decision(grid)
        print("PMOVE: " + str(d[0]))
        if d[0] == None:
            return 0
        return d[0]

    def decision(self,grid):
        # root = self.makeTheKids(grid, defaultDepthLimit)
        self.prevTime = time.process_time()
        max_child_tuples = []
        i = 1
        while len(max_child_tuples) == 0 or max_child_tuples[-1][1] != float("-inf"):
            # max_child_tuple = self.maximize((None,grid), float("-inf"), float("inf"), 0, defaultDepthLimit)
            max_child_tuples.append(self.maximize((None,grid), float("-inf"), float("inf"), 0, i))
            i+= 1
        while max_child_tuples[-1][1] == float("-inf"):
            max_child_tuples.pop(-1)
        print("decision: ")
        max_child_tuple = max_child_tuples[-1]
        print(max_child_tuple)
        print(time.process_time() - self.prevTime)
        print("heuristics: " + str(max_child_tuple[1]))

        #return data (grid) of max Node

        return max_child_tuple[0]

    def maximize(self,state, alpha, beta, depth, depthLimit, calledByMax=True):
        depth += 1
        # gridt = node.data
        # grid = gridt[1]
        grid = state[1]

        children = grid.getAvailableMoves()

        #return MIN TILE
        if self.overtime():
            return (state, float("-inf"))
        if not grid.canMove() or self.overtime() or depth > depthLimit: #
            # if not grid.canMove():
            #     return (state,grid.getMaxTile())
            monotonicity = self.monotonicity(state[1])
            monotonicity2 = self.monotonicity2(state[1])
            # monotonicity = math.log(monotonicity)
            #print("monotonicity: " + str(monotonicity))
            smoothness = self.smoothness(state[1])
            # if smoothness != 0:
            #     smoothness = math.log(smoothness)
            #print("smoothness: " + str(smoothness))
            num_empty_tiles = self.num_empty_tiles(state[1])
            #print("num empty tiles: " + str(num_empty_tiles))
            average_val = self.sum_of_tiles(state[1])/(16-len(grid.getAvailableCells()))
            # sum_of_tiles = math.log(sum_of_tiles)
            #print("sum_of_tiles: " + str(sum_of_tiles))

            heuristics = monotonicity*MONOTONICITY_1_WEIGHT
            heuristics += monotonicity2*MONOTONICITY_2_WEIGHT
            heuristics += smoothness*SMOOTHNESS_WEIGHT
            heuristics += num_empty_tiles*EMPTY_TILES_WEIGHT
            heuristics += average_val*AVG_TILES_WEIGHT

            max_tile = grid.getMaxTile()
            heuristics *= max_tile

            # if max_tile < 32 and depth == 1 and (state[0] == 1 or state[0] == 2):
            #     heuristics *= 6
            #print("heuristics: " + str(heuristics))

            return (state, heuristics)

        maxC_maxU = (state, float("-inf"))

        for child in children:

            min_utility = self.minimze(child, alpha, beta, depth, depthLimit)

            if min_utility > maxC_maxU[1]:
                maxC_maxU = (child, min_utility)

            if maxC_maxU[1] >= beta:
                break

            if maxC_maxU[1] > alpha:
                alpha = maxC_maxU[1]

        return maxC_maxU

    def minimze(self,state, alpha, beta, depth, depthLimit, calledByMax=False):
        # gridt = node.data
        # grid = gridt[1]

        grid = state[1]
        move = state[0]

        availableCells = grid.getAvailableCells()

        #return what was passed
        if not grid.canMove(): #or depth > depthLimit or self.overtime():
            return (state, grid.getMaxTile())

        min_utility = float("inf")

        for cell in availableCells:

            gridCopy2 = grid.clone()
            gridCopy2.setCellValue(cell, 2)

            max_node_tuple_2 = self.maximize((move,gridCopy2), alpha, beta, depth, depthLimit)

            gridCopy4 = grid.clone()
            gridCopy4.setCellValue(cell, 4)

            max_node_tuple_4 = self.maximize((move,gridCopy4), alpha, beta, depth, depthLimit)
            # max_node_tuple = self.chance(child, alpha, beta, depth, depthLimit, calledByMax)

            utility_of_2 = probability_of_two * max_node_tuple_2[1]
            utility_of_4 = probability_of_four * max_node_tuple_4[1]
            weighted_utility = utility_of_2 + utility_of_4

            if weighted_utility < min_utility:
                # if depth == 1:
                #     minC_minU = (state, max_node_tuple[1])
                # else:
                #     minC_minU = (minC_minU[0], max_node_tuple[1])
                min_utility = weighted_utility

            if min_utility <= alpha:
                break

            if min_utility < beta:
                beta = min_utility

        return min_utility

    def sum_of_tiles(self, grid):
        values = set()

        for r in range(len(grid.map)):
            for c in range(len(grid.map[r])):
                values.add(grid.map[r][c])

        values = list(values)
        values.sort()        

        score = 0;

        for r in range(len(grid.map)):
            for c in range(len(grid.map[r])):
                score += grid.map[r][c]*values.index(grid.map[r][c])

        return score

    def num_empty_tiles(self, grid):
        score = 0;

        for r in range(len(grid.map)):
            for c in range(len(grid.map[r])):
                if grid.map[r][c] == 0:
                    score += 1

        return score


    def smoothness(self, grid):
        gmatrix = grid.map
        diff_across_rows = 0
        diff_across_columns = 0

        for r in range(len(gmatrix)):
            for c in range(len(gmatrix[r]) -1):
                # if gmatrix[r][c] != 0 and gmatrix[r][c+1] != 0:
                diff_across_columns += abs(gmatrix[r][c] - gmatrix[r][c+1])

        for r in range(len(gmatrix)-1):
            for c in range(len(gmatrix[r])):
                # if gmatrix[r+1][c] != 0 and gmatrix[r][c] != 0:
                diff_across_rows += abs(gmatrix[r+1][c] - gmatrix[r][c])

        # if diff_across_columns + diff_across_rows == 0:
        #     return 0
        # else:
        #     return 1/(diff_across_rows + diff_across_columns)
        return 10/math.log(diff_across_rows + diff_across_columns)

    def monotonicity2(self, grid):
        gmatrix = grid.map
        score_rows_1 = score_rows_2 = 0
        score_columns_1 = score_columns_2 = 0

        for r in range(len(gmatrix)):
            for c in range(len(gmatrix[r]) -1):
                # if gmatrix[r][c] != 0 and gmatrix[r][c+1] != 0:
                score_columns_1 += gmatrix[r][c] - gmatrix[r][c+1]
                # score_columns_2 += gmatrix[r][c+1] - gmatrix[r][c]

        for r in range(len(gmatrix)-1):
            for c in range(len(gmatrix[r])):
                # if gmatrix[r+1][c] != 0 and gmatrix[r][c] != 0:
                score_rows_1 += gmatrix[r][c] - gmatrix[r+1][c]
                # score_rows_2 += gmatrix[r+1][c] - gmatrix[r][c]

        # r = max(score_rows_1, score_rows_2)
        # c = max(score_columns_1, score_columns_2)

        # if r + c <= 0:
        #     return r+c

        # return math.log(r + c)  
        if score_rows_1 + score_columns_1 == 0:
            return 0
        return math.log(abs(score_rows_1 + score_columns_1))     


    def monotonicity(self, grid):
        # scores = [self.max_at_upper_left(grid), self.max_at_lower_left(grid), 
        #             self.max_at_lower_right(grid), self.max_at_upper_right(grid)]

        max_tile = grid.getMaxTile()

        ul_score = self.max_at_upper_left(grid)
        if grid.map[0][0] == max_tile:
            ul_score *= MAX_TILE_MULTIPLIER    
            
        ll_score = self.max_at_lower_left(grid)
        if grid.map[3][0] == max_tile:
            ll_score *= MAX_TILE_MULTIPLIER   

        lr_score = self.max_at_lower_right(grid)
        if grid.map[3][3] == max_tile:
            lr_score *= MAX_TILE_MULTIPLIER   

        ur_score = self.max_at_upper_right(grid)
        if grid.map[0][3] == max_tile:
            ur_score *= MAX_TILE_MULTIPLIER

        scores = [ul_score, ll_score, lr_score, ur_score]   

        score = max(scores)

        index = scores.index(score)

        max_tile = grid.getMaxTile()

        if index == 0:
            if grid.map[0][0] == max_tile:
                score *= MAX_TILE_MULTIPLIER
        elif index == 1:
            if grid.map[3][0] == max_tile:
                score *= MAX_TILE_MULTIPLIER
        elif index == 2:
            if grid.map[3][3] == max_tile:
                score *= MAX_TILE_MULTIPLIER
        else:
            if grid.map[0][3] == max_tile:
                score *= MAX_TILE_MULTIPLIER

        if max_tile >= 32:
            if grid.map[0][0] != max_tile and grid.map[3][0] != max_tile and grid.map[0][3] != max_tile and grid.map[3][3] != max_tile:
                if score > 0:
                    score = math.log(score)

        if score <= 0:
            return score
        else:
            return math.log(score)

    def max_at_upper_left(self, grid):
        scaling_matrix = [[10,7,3,0],
                            [7,3,0,-3],
                            [3,0,-3,-7],
                            [0,-3,-7,-10]]

        return self.get_monotonicity_score(grid, scaling_matrix)

    def max_at_lower_right(self, grid):
        scaling_matrix = [[-3,-2,-1,0],
                            [-2,-1,0,1],
                            [-1,0,1,2],
                            [0,1,2,3]]
        return self.get_monotonicity_score(grid, scaling_matrix)

    def max_at_lower_left(self, grid):
        scaling_matrix = [[0,-1,-2,-3],
                            [1,0,-1,-2],
                            [2,1,0,-1],
                            [3,2,1,0]]
        return self.get_monotonicity_score(grid, scaling_matrix)

    def max_at_upper_right(self, grid):
        scaling_matrix = [[0,1,2,3],
                            [-1,0,1,2],
                            [-2,-1,0,1],
                            [-3,-2,-1,0]]
        return self.get_monotonicity_score(grid, scaling_matrix)

    def get_monotonicity_score(self, grid, scaling_matrix):
        score = 0;

        for r in range(len(grid.map)):
            for c in range(len(grid.map[r])):
                score += grid.map[r][c] * scaling_matrix[r][c]

        return score

    # def minimze(self,state, alpha, beta, depth, depthLimit, calledByMax=False):
    #     # gridt = node.data
    #     # grid = gridt[1]
    #     depth += 1

    #     grid = state[1]

    #     children = grid.getAvailableMoves()

    #     #return what was passed
    #     if not grid.canMove() or depth > depthLimit or self.overtime():
    #         return (state, grid.getMaxTile())

    #     minC_minU = (state, float("inf"))

    #     for child in children:
    #         max_node_tuple = self.maximize(child, alpha, beta, depth, depthLimit)
    #         # max_node_tuple = self.chance(child, alpha, beta, depth, depthLimit, calledByMax)

    #         if max_node_tuple[1] < minC_minU[1]:
    #             if depth == 1:
    #                 minC_minU = (child, max_node_tuple[1])
    #             else:
    #                 minC_minU = (minC_minU[0], max_node_tuple[1])

    #         if minC_minU[1] <= alpha:
    #             break

    #         if minC_minU[1] < beta:
    #             beta = minC_minU[1]

    #     return minC_minU

    # def chance2(self, state, alpha, beta, depth, depthLimit, calledByMax):
    #     grid = state[1]
    #     move = state[0]
    #     availableCells = grid.getAvailableCells()

    #     # Insert a 2
    #     for cell in availableCells:
    #         gridCopy = grid.clone()
    #         gridCopy.setCellValue(cell, 2)
    #         child = (move,gridCopy)
    #         if calledByMax:
    #             # keep the move that it took to get here but use new state w/ computer input
    #             result2 = self.minimize(child, alpha, beta, depth, depthLimit)
    #         else:
    #             result2 = self.maximize(child, alpha, beta, depth, depthLimit)

    #     # Insert a 4
    #     for cell in availableCells:
    #         gridCopy = grid.clone()
    #         gridCopy.setCellValue(cell, 4)
    #         if calledByMax:
    #             result4 = self.minimize((move,gridCopy), alpha, beta, depth, depthLimit)
    #         else:
    #             result4 = self.maximize((move,gridCopy), alpha, beta, depth, depthLimit)

    #     weighted_utility = probability_of_two*result2[1] + probability_of_four*result4[1]

    #     return (state, weighted_utility)

    # def maximize(self,state, alpha, beta, depth, depthLimit, calledByMax=True):
    #     depth += 1
    #     # gridt = node.data
    #     # grid = gridt[1]
    #     grid = state[1]

    #     children = grid.getAvailableMoves()

    #     # print("children: " )
    #     # print(children)


    #     #return MIN TILE
    #     if not grid.canMove() or depth > depthLimit or self.overtime(): #
    #         return (state, getGridMinTile(grid))

    #     maxC_maxU = (state, float("-inf"))

    #     for child in children:

    #         # move = state[0]
    #         # availableCells = grid.getAvailableCells()
    #         # #insert 2
    #         # for cell in availableCells:
    #         #     gridCopy = grid.clone()
    #         #     gridCopy.setCellValue(cell, 2)


    #         min_node_tuple = self.minimze(child, alpha, beta, depth, depthLimit)
    #         # min_node_tuple = self.chance(child, alpha, beta, depth, depthLimit, calledByMax)

    #         if min_node_tuple[1] > maxC_maxU[1]:
    #             if depth == 1:
    #                 maxC_maxU = (child, min_node_tuple[1])
    #             else:
    #                 maxC_maxU = (maxC_maxU[0], min_node_tuple[1])

    #         if maxC_maxU[1] >= beta:
    #             break

    #         if maxC_maxU[1] > alpha:
    #             alpha = maxC_maxU[1]

    #     return maxC_maxU

    # def maximize(self,state, alpha, beta, depth, depthLimit, calledByMax=True):
    #     depth += 1
    #     # gridt = node.data
    #     # grid = gridt[1]
    #     grid = state[1]
    #     move = state[0]

    #     if not grid.canMove() or depth > depthLimit or self.overtime(): #
    #         return (state, getGridMinTile(grid))

    #     availableCells = grid.getAvailableCells()

    #     maxC_maxU = (state, float("-inf"))

    #     #for each possible next configuration
    #     for cell in availableCells:

    #         maxC_maxU_2 = (state, float("-inf"))

    #         #Insert 2
    #         gridCopy2 = grid.clone()
    #         gridCopy2.setCellValue(cell, 2)

    #         if not gridCopy2.canMove() or depth > depthLimit or self.overtime(): #
    #             continue

    #         childrenOf2 = gridCopy2.getAvailableMoves()

    #         for child in childrenOf2:
    #             min_node_tuple_2 = self.minimze(child, alpha, beta, depth, depthLimit)

    #             if min_node_tuple_2[1] > maxC_maxU_2[1]:
    #                 if depth == 1:
    #                     maxC_maxU_2 = (child, min_node_tuple_2[1])
    #                 else:
    #                     maxC_maxU_2 = (maxC_maxU_2[0], min_node_tuple_2[1])

    #             if maxC_maxU_2[1] >= beta:
    #                 break

    #             if maxC_maxU_2[1] > alpha:
    #                 alpha = maxC_maxU_2[1] 
    #         print(maxC_maxU_2) 

    #         maxC_maxU_4 = (state, float("-inf"))

    #         #Insert 4
    #         gridCopy4 = grid.clone()
    #         gridCopy4.setCellValue(cell, 4)

    #         if not gridCopy2.canMove() or depth > depthLimit or self.overtime(): #
    #             continue

    #         childrenOf4 = gridCopy4.getAvailableMoves()

    #         for child in childrenOf4:
    #             min_node_tuple_4 = self.minimze(child, alpha, beta, depth, depthLimit)                

    #             if min_node_tuple_4[1] > maxC_maxU_4[1]:
    #                 if depth == 1:
    #                     maxC_maxU_4 = (child, min_node_tuple_4[1])
    #                 else:
    #                     maxC_maxU_4 = (maxC_maxU_4[0], min_node_tuple_4[1])

    #             if maxC_maxU_4[1] >= beta:
    #                 break

    #             if maxC_maxU_4[1] > alpha:
    #                 alpha = maxC_maxU_4[1] 

    #         print(maxC_maxU_4)

    #         utility_of_2 = maxC_maxU_2[1]*probability_of_two;
    #         utility_of_4 = maxC_maxU_4[1]*probability_of_four;

    #         next_move = maxC_maxU_2[0] if utility_of_2 > utility_of_4 else maxC_maxU_4[0];
    #         min_node_tuple = (next_move, utility_of_2+utility_of_4)

    #         if min_node_tuple[1] > maxC_maxU[1]:
    #             if depth == 1:
    #                 maxC_maxU = min_node_tuple
    #             else:
    #                 maxC_maxU = (maxC_maxU[0], min_node_tuple[1])

    #         if maxC_maxU[1] >= beta:
    #             break

    #         if maxC_maxU[1] > alpha:
    #             alpha = maxC_maxU[1]            


    #     return maxC_maxU



def getGridMinTile(grid):
    return min(min(row) for row in grid.map)


# class Node:
#     def __init__(self,gridt):
#         self.data = gridt
#         self.children = list()

