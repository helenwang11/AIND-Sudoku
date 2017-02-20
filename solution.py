assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

# set up all boxe labels, units, and peers dictionary
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units = [list(map(lambda x:"".join(x),list(zip(rows,cols)))),list(map(lambda x:"".join(x),list(zip(rows,reversed(cols)))))]
unitlist = row_units + column_units + square_units + diagonal_units # list of all units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes) # mapping of box -> the units the box belongs to
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes) # mapping of box -> the peers of the box

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    for unit in unitlist:
        for i in range(9):
            box1 = unit[i]
            if len(values[box1]) != 2:
                continue
            for j in range(i + 1, 9):
                box2 = unit[j]
                if values[box1] == values[box2]: # found twins
                    for peer in (set(unit) - set([box1, box2])):     # eliminate the naked twins as possibilities for their peers
                        for digit in values[box1]:
                            values = assign_value(values, peer, values[peer].replace(digit,''))
                    break

    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    assert len(grid)==81
    available = '123456789'
    values = []
    for c in grid:
        if c ==  '.':
            values.append(available)
        else:
            values.append(c)
    return dict(zip(boxes,values))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    
    for box in values:
        if len(values[box]) == 1:
            digit = values[box]
            for peer in peers[box]:
                values = assign_value(values, peer, values[peer].replace(digit,'')) # eliminate this digit from values of peers
                
    return values

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    
    for unit in unitlist:
        digits = '123456789'
        for digit in digits:
            dplaces = [box for box in unit if digit in values[box]] # list of boxes where this digit is allowed in current unit
            if len(dplaces) == 1: # if there is only one box this digit could go in this unit
                values = assign_value(values, dplaces[0], digit) # assign this digit to this box

    return values

def reduce_puzzle(values):
    """Reduce the search space for puzzle by repetitively applying eliminate, only choice, and naked twins strategy
    Stop iteration when there is no further progress
    :param dictionary values: values dictionary representing soduku
    :returns dictionary values: reduced values dictionary representing soduku
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Eliminate Strategy to confine search space
        values = eliminate(values)

        # Use the Only Choice Strategy to confine search space
        values = only_choice(values)
        
        # Use the Naked Twins Strategy to confine search space
        values = naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def get_best_box(values):
    """identify the best box for starting depth first search, which is an unsolved box containing least options
    :param dictionary values: values dictionary representing soduku
    :returns string best_box: the best box to start depth first search
    """
    min_len, best_box = min([(len(value),box)for box,value in values.items() if len(value) > 1])
    return best_box


def is_solved(values):
    """determine whether a puzzle has been solved or not
    :param dictionary values: values dictionary representing soduku
    :returns bool: True for solved, False for unsolved
    """
    unsolved_values = len([box for box in values.keys() if len(values[box]) != 1])
    return(unsolved_values == 0)


def search(values):
    """Using depth-first search and propagation, create a search tree and solve the sudoku.
    :param dictionary values: values dictionary representing soduku
    :returns dictionary values representing solved sodoku, or False if no solution is found
    """
    # First, reduce the puzzle
    values = reduce_puzzle(values)
        
    # If previous step hits a dead-end, returns False
    if values is False:
        return False
        
    # If puzzle is solved, return the answer
    if is_solved(values):
        return values
    
    # Choose one of the unfilled squares with the fewest possibilities
    best_box = get_best_box(values)
    
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for digit in values[best_box]: # choose a possible value
        values[best_box] = digit # assign that value to the box
        new_values = values.copy() # make a copy of the current puzzle for backtracking
        ans = search(new_values) # start searching
        if ans: 
            return ans # returns answer if puzzle is solved

    return False # sanity check, returns False if no solution is found
    

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    
    values = grid_values(grid)
    sudoku = search(values)
    if sudoku:
        return sudoku
    

if __name__ == '__main__':
    
    grid = "..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3.."
    
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
