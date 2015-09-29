from operator import itemgetter
import os

# Apologies in advance for some of the giant comment blocks.
# I can get carried away with explaining the way some of the code works,
# And honestly, some of it, I really like explaining because I really like some of the concepts behind it.
# I tried to make sure everything is self explanatory (for the most part) and the parts that aren't
# Self explanatory should be well/somewhat documented.

# Point/Letter reference. Point values for all letters.
letter_ref = {
    'a':1,
    'b':4,
    'c':4,
    'd':2,
    'e':1,
    'f':4,
    'g':3,
    'h':3,
    'i':1,
    'j':10,
    'k':5,
    'l':2,
    'm':4,
    'n':2,
    'o':1,
    'p':4,
    'q':10,
    'r':1,
    's':1,
    't':1,
    'u':2,
    'v':5,
    'w':4,
    'x':8,
    'y':3,
    'z':10,
    '?':0}

wildcard = '?'
min_len = 2
blank_space = ' '
bingo_bonus = 35
bingo_len = 7
board_path = 'board.txt'
score_board_path = 'wwf board.txt'
result_limit = 5
start_coords = (7, 7)

dir_ref = {'u':(-1,0), 'd':(1,0), 'l':(0,-1), 'r':(0,1)}
oppo_dir = {'u':'d', 'd':'u', 'l':'r', 'r':'l'}
# Perpendicular directions of given dir
perp_dir = {'u':'lr', 'd':'lr', 'l':'ud', 'r':'ud',}
# These are the directions that all words are oriented in.
forward_dirs = 'rd'

# Both directions used in potentials, and the semi-cross around each tile that a new tile could be placed (if valid)
cross_list = [
    [[(-1,0),(0,-1),(0,1)], 'u'],
    [[(-1,0),(0,-1),(1,0)], 'l']]
# Reference for the tile multipliers for each character found in the board reference sheet.
board_tile_ref = {
    ' ':1,
    's':1,
    'd':2,
    'D':1,
    't':3,
    'T':1}
# Reference for the word multipliers for each character found in the board reference sheet.
board_word_ref = {
    ' ':1,
    's':1,
    'd':1,
    'D':2,
    't':1,
    'T':3}
# Certainty reference. This is used as an easy way to convert the str 'c' or 'u' to their certainty counterparts of True/False respectively.
certain_ref = {
    True: 'Certain',
    False: 'Uncertain',
    'c': True,
    'u': False}

def print_board( board, mult=True ):
    output = ['╔' + '═' * len( board[0] ) + '╗']
    for y, row in enumerate( board ):
        output.append( '║' )
        for x, d in enumerate( row ):
            let = d['let']
            if let == blank_space:
                word = d['word']
                tile = d['tile']
                if word != 1 and mult:
                    output[-1] += '  ∙∙'[word]
                elif tile != 1 and mult:
                    output[-1] += '  ··'[tile]
                else:
                    output[-1] += ' '
            else:
                output[-1] += let
        output[-1] += '║'
    output.append( '╚' + '═' * len( board[-1] ) + '╝' )
    print '\n'.join( output )

def import_board( board_path, score_board_path ):
    # Function absolutely requires board_path and score_board_path to be the same dimensions
    # Otherwise it doesn't know what to do with the additional information,
    # And will allow itself to fail because of this.
    
    letter_file = open( board_path, 'r' )
    data = letter_file.read()
    letter_board = [ [ {'let': e, 'new': False} for e in row ] for row in data.split('\n') ]
    letter_file.close()
    
    score_file = open( score_board_path, 'r' )
    data = score_file.read()
    score_board = [ [ { 'tile': board_tile_ref[e], 'word': board_word_ref[e] } for e in row ] for row in data.split('\n') ]
    score_file.close()
    
    # Initialize the board with each letter and new: True value
    board = []
    for row in letter_board:
        board.append([])
        for d in row:
            let = d['let']
            new = d['new']
            board[-1].append({ 'let': let, 'new': new })
    
    # Add in tile and word values
    for y, row in enumerate( score_board ):
        for x, d in enumerate( row ):
            board[y][x]['tile'] = d['tile']
            board[y][x]['word'] = d['word']
    
    # Fix tile and word values, so all used tile/word multipliers are reset
    for y, row in enumerate( board ):
        for x, d in enumerate( row ):
            if d['let'] != blank_space:
                board[y][x]['tile'], board[y][x]['word'] = 1, 1
    
    return board

def check_coords( board, (y, x) ):
    """ Function to make sure that (y, x) coordinates can return a value from board, excluding negative index values. """
    try:
        return y >= 0 and x >= 0 and y < len( board ) and x < len( board[y] )
    except IndexError:
        return False

def remove_element( list, index ):
    return list[:index] + list[index+1:]

def check_word( word, tree ):
    try:
        if len(word) == 0:
            return tree['word']
        return check_word( word[1:], tree[ word[0] ] )
    except KeyError:
        return False

def tree_rec( word_list, cur_str=''):
    cur_dict = {}
    temp_dict = {}
    len_cur_str = len( cur_str )
    for word in word_list:
        cur_letter = word [len_cur_str]
        if cur_letter == '|':
            cur_dict ['word'] = word[-1]
        else:
            if temp_dict.get( cur_letter, False) == False:
                temp_dict [cur_letter] = []
            temp_dict [cur_letter].append( word )
    for letter, word_list_sect in temp_dict.items():
        cur_dict [letter] = tree_rec( word_list_sect, cur_str + letter)
    return cur_dict

def check_board( board, word_tree, (y, x), dir ):
    """Returns the certainty of the word perpendicular to a tile just laid down if it's valid and legal."""
    # cur_str will represent the current iteration of the potential word being checked.
    # It will be appended unto by adjacent perpendicular letters, while checking that this word is valid.
    cur_str = board[y][x]['let']
    dir_y, dir_x = dir_ref[dir]
    
    # Look at the two directions perpendicular to [dir]
    for p_dir in perp_dir[dir]:
        p_dir_y, p_dir_x = dir_ref[p_dir]
        p_y = y + p_dir_y
        p_x = x + p_dir_x
        try:
            if not p_dir in forward_dirs:
                cur_str = cur_str[::-1]
            while blank_space != board[p_y][p_x]['let']:
                cur_str += board[p_y][p_x]['let']
                p_y += p_dir_y
                p_x += p_dir_x
            if not p_dir in forward_dirs:
                cur_str = cur_str[::-1]
        except IndexError:
            # IndexError should only occur when checking perpendicular coordinates on the edge of the board
            # So nothing needs to be done, as it can't add any more letters to cur_str
            pass
    if len(cur_str) >= min_len:
        return check_word( cur_str, word_tree )
    return 'c'

def sub_board( board, (y,x), let, wildcard=False ):
    """Function used to mutate the board list for easier recursion without having to edit variables across recursed stacks."""
    tile = board[y][x]['tile']
    word = board[y][x]['word']
    if wildcard:
        tile = 0
    return board[:y] + [board[y][:x] + [{'let':let, 'tile':tile, 'word':word, 'new':True }] + board[y][x+1:]] + board[y+1:]

def get_new_words( board ):
    """Return all words in the current state of the board that have at least one 'new' flag as True."""
    for y, row in enumerate( board ):
        for x, d in enumerate( row ):
            let = d['let']
            if let != blank_space:
                for dir in forward_dirs:
                    new = d['new']
                    o_dir = oppo_dir[dir]
                    o_y, o_x = dir_ref[o_dir]
                    n_y = y + o_y
                    n_x = x + o_x
                    if check_coords( board, (n_y, n_x)):
                        word_start = blank_space == board[n_y][n_x]['let']
                    else:
                        word_start = True
                    if word_start:
                        cur_str = let
                        dir_y, dir_x = dir_ref[dir]
                        n_y, n_x = y + dir_y, x + dir_x
                        try:
                            while blank_space != board[n_y][n_x]['let']:
                                cur_str += board[n_y][n_x]['let']
                                new = new or board[n_y][n_x]['new']
                                n_y += dir_y
                                n_x += dir_x
                        except IndexError:
                            pass
                        if new and len(cur_str) >= min_len:
                            yield (y, x), dir

def get_word_score( board, (y, x), dir ):
    """Given the temporary state of a board that's been altered to have a complete word, 
    return the score of that word along with all other words that were affected by newly placed tiles."""
    output = 0
    for (y, x), dir in get_new_words( board ):
        score = 0
        word_mult = 1
        n_y, n_x = y, x
        dir_y, dir_x = dir_ref[dir]
        try:
            while blank_space != board[n_y][n_x]['let']:
                d = board[n_y][n_x]
                let = d['let']
                score += letter_ref[let] * d['tile']
                word_mult *= d['word']
                n_y = n_y + dir_y
                n_x = n_x + dir_x
        except IndexError:
            pass
        output += word_mult * score
    return output

def board_rec_search( board, full_tree, tree_sect, hand_len, hand_sect, (y, x), dir, cur_str="", req_len=min_len, certain=True):
    """The main recursive search function. To only be used from search_base(). 
    Given (y, x) coordinates and [dir], will attempt to place each tile from [hand_sect] down one at a time, 
    and see if that tile can follow a branch of [tree_sect] to create one or more words then recurse. 
    If a tile already exists at the current coordinates, it will use that tile in place of all hand_sect tiles, and recurse. 
    If the current hand_sect tile is a wildcard, it will loop over all currently allowed branches of tree_sect and recurse. 
    Once the current branch of tree_sect yields a word that meets the required length [req_len] then it will yield the current word, 
    and if possible continue recursing. 
    Branches of recursion are only stopped if there are no more valid branches to follow in tree_sect that can be created with the current hand and board."""
    
    dir_y, dir_x = dir_ref [dir]
    n_y = y + dir_y * len(cur_str)
    n_x = x + dir_x * len(cur_str)
    # If there's a 'word' key, it is the certainty of that word, so the program only needs to check if it exists, and return the certainty (certain/uncertain)
    # After returning this result, continue with the rest of the search.
    # Will only yield results if cur_str is a valid word, meets/exceeds required length, and if current space is at the end of a word.
    # Without final condition, function could yield words without taking following letter tiles into consideration.
    try:
        # Checking if 'word' is in this section of the tree serves two purposes
        # If 'word' exists, then it means that the currently laid tiles in this branch of recursion
        # has a word found within its own word_tree.
        # If 'word' doesn't exist, then there is nothing to yield (yet?) and will raise a KeyError, where it will continue with the rest of the function
        # The second purpose is to check the certainty of the current word, if it's certain this word is valid, or uncertain.
        # 'word' will only yield a string result of whether it's certain ('c') or uncertain ('u'), so then check the easy reference for if that's True or False
        # And apply an AND operation with the current certainty of the recursive function.
        # The function will only yield a result that it is certain exists, if the word for the result and all adjacently created words are all certain.
        certainty = certain and certain_ref[ tree_sect['word'] ]
        
        score = get_word_score( board, (y, x), dir )
        
        # number of letters in hand minus initial number of letters in hand
        # yields the total number of letters from hand used.
        # Use this figure here to determine whether or not to add bonus for using 7 letters
        if hand_len - len(hand_sect) == bingo_len:
            score += bingo_bonus
        if check_coords( board, (n_y, n_x) ):
            if blank_space != board[n_y][n_x]['let']:
                raise KeyError
                # Ok, this might be messy code, but I'm not sure, and I like the logic.
                # This replaces two copies of the same exact yield, but one required a different series of if statements to be True.
                # Specifically, the function won't yield the current result unless the next tile is empty, AKA this is a complete word that
                # Doesn't have a suffix that hasn't been accounted for 
                # Example: adding in 'works' to a board, but recursion hasn't yet found that the true result would have 'hunger' immediately following 'works'
                # The program would think the word is fine, but we know it isn't, because 'workshunger' isn't a word, and that's how WWF/Scrabble would interpret it.
                # The problem is it obviously can't check the next tile is blank if that next tile IndexError's.
                # If it would IndexError, then that means the next tile is at the edge of the board, and we know it's fine to yield.
                # These two if's will check if the next tile is available (readas won't IndexError), and if it is, then checks if it isn't blank.
                # If the next tile isn't blank, it raises a KeyError (which this whole statement is contained in a try/except block for anyways)
                # So that it'll skip the check for the yield.
                # If the next tile is in fact empty, it won't raise KeyError, and proceeds to the next if before yield'ing the current result.
        if len(cur_str) >= req_len:
            yield cur_str, (y, x), dir, score, certainty
    except KeyError:
        pass
    if check_coords( board, (n_y, n_x)):
        let = board[n_y][n_x]['let']
        if blank_space == let:
            # Index and current letter being for looped through 'hand_sect'.
            # i makes it easier to omit the current letter when running the next level of recursion.
            for i, let in enumerate( hand_sect ):
                if let == wildcard:
                    # If current letter is a wildcard, for loop through all next letters in the next iteration of word_tree, and ignores the possible 'word' iteration.
                    for sub_let, wild_sect in tree_sect.items():
                        if sub_let == 'word':
                            continue
                        # cur_certainty is the certainty of a word perpendicular to cur_str on the board.
                        # It needs to be checked to see if there is a perpendicular word, if that word is valid,
                        # Then store the certainty of the potential word.
                        cur_certainty = check_board( sub_board( board, (n_y, n_x), sub_let ), full_tree, (n_y, n_x), dir )
                        if cur_certainty:
                            for result in board_rec_search( sub_board( board, (n_y, n_x), sub_let, wildcard=True ), full_tree, wild_sect, hand_len, remove_element( hand_sect, i), (y, x), dir, cur_str + sub_let.upper(), req_len, certain and cur_certainty ):
                                yield result
                else:
                    try:
                        cur_certainty = check_board( sub_board( board, (n_y, n_x), let ), full_tree, (n_y, n_x), dir )
                        if cur_certainty:
                            for result in board_rec_search( sub_board( board, (n_y, n_x), let ), full_tree, tree_sect[let], hand_len, remove_element( hand_sect, i), (y, x), dir, cur_str + let, req_len, certain and cur_certainty ):
                                yield result
                    except KeyError:
                        pass
        else:
            try:
                for result in board_rec_search( board, full_tree, tree_sect[let], hand_len, hand_sect, (y, x), dir, cur_str + let, req_len, certain ):
                    yield result
            except KeyError:
                pass

def print_potential( board, potential_list ):
    """Function that prints the current state of the board and all the potentials on that board."""
    output = []
    # Potential_list contains distance values for the final element per potential
    # But it's a lot easier to find results without that value.
    edited_list = [ (y, x, dir) for (y, x), dir, dist in potential_list ]
    for y, row in enumerate( board ):
        output.append( [] )
        for x, d in enumerate( row ):
            let = d['let']
            if let == ' ':
                    d = (y, x, 'd') in edited_list
                    r = (y, x, 'r') in edited_list
                    if r:
                            if d:
                                    output[y].append( '+' )
                            else:
                                    output[y].append( '-' )
                    else:
                            if d:
                                    output[y].append( '|' )
                            else:
                                    output[y].append( ' ' )
            else:
                    output[y].append( let )
    for row in output:
        print ''.join([ let for let in row ]) + '|'

def find_empty_slots( board, num, (y, x), dir, blank=' ' ):
    """Given board, coordinates, direction and a number, returns the first [num] of [blank] spots in [board] from [y, x] in direction [dir]."""
    add = 0
    dir = dir_ref[dir]
    
    # Please excuse this mess of code. Some of it is brilliant in my opinion, but other parts sloppy.
    # For loop through num so to yield the correct [num] of coordinates, 
    # Then inside, check if current coordinate is blank or not.
    # If not blank, add+=1 repeat, else break out of while loop and yield to repeat
    # If instead the coordinates go off the board, that's as many legal coordinates as you can get
    # And instead cont = False to then break out of the for loop
    for i in range( num ):
        cont = True
        while cont:
            # Some time eventually, I want to fix up this bit of code, as there has to be a better way to do this.
            # But for now, it works and it'll do the job properly.
            d_y, d_x = dir
            d_x *= i + add
            d_y *= i + add
            if check_coords( board, ( y + d_y, x + d_x )):
                if blank == board [ y + d_y ][ x + d_x ]['let']:
                    break
                yield ( y + d_y, x + d_x, i + add + 1 )
                add += 1
            else:
                cont = False
        else:
            break
        yield ( y + d_y, x + d_x, i + add + 1 )

def reduce_potential_list( potential_list ):
    """Given the raw output from get_potential_list, reduces the number of potentials by ~75% by finding potentials that share coordinates and direction. 
    Returns the potential that has the smallest distance requirement value."""
    output_list = []
    output_d = {}
    for potential in potential_list:
        (y, x), dir, dist = potential
        try:
            if output_d[y]:
                pass
        except KeyError:
            output_d[y] = {}
        try:
            if output_d[y][x]:
                pass
        except KeyError:
            output_d[y][x] = {}
        try:
            output_d[y][x][dir].append( dist )
        except KeyError:
            output_d[y][x][dir] = [dist]
    for y, val_1 in output_d.items():
        for x, val_2 in val_1.items():
            for dir, val_3 in val_2.items():
                output_list.append(( (y, x), dir, min(val_3) ))
    return output_list

def get_potential_list( board, len_hand ):
    """Given current state of [board], returns a list of all potential locations for all recursive searches to start. 
    Potentials found based on intersecting with, or running parallel to existing words on board, or in the event of a blank board, around the center."""
    potential_list = []
    count_blanks = 0
    for y, row in enumerate( board ):
        for x, d in enumerate( row ):
            let = d['let']
            if let != blank_space:
                count_blanks += 1
                for cross_coords, cross_dir in cross_list:
                    # Delta x and y from a list of constants, chosen so it goes in a semi-cross pattern around the current letter.
                    # First pass is for words that will be going downwards in direction, then second pass left-wards.
                    for d_y, d_x in cross_coords:
                        # Find empty slots above/left the semi-cross slots.
                        for dd_y, dd_x, dist in find_empty_slots( board, len_hand, ( y + d_y, x + d_x ), cross_dir ):
                            # Syntax check to make sure next slot is valid.
                            # This will check the next slot up if it's blank.
                            # This is necessary because otherwise it'll start trying to place a word in the middle
                            # of another one, which would lead to invalid situations.
                            dir_y, dir_x = dir_ref[ cross_dir ]
                            if check_coords( board, (dd_y + dir_y, dd_x + dir_x)):
                                if blank_space == board[dd_y + dir_y][dd_x + dir_x]['let']:
                                    potential_list.append(( (dd_y, dd_x), oppo_dir[ cross_dir ], dist ))
                            else:
                                potential_list.append(( (dd_y, dd_x), oppo_dir[ cross_dir ], dist ))
                    # Repeat the same thing as the previous comment, except now for just the current space itself.
                    dir_y, dir_x = dir_ref[cross_dir]
                    if check_coords( board, (dd_y + dir_y, dd_x + dir_x)):
                        if blank_space == board[dd_y + dir_y][dd_x + dir_x]['let']:
                            potential_list.append(( (dd_y, dd_x), oppo_dir[ cross_dir ], dist ))
                    else:
                        potential_list.append(( (dd_y, dd_x), oppo_dir[ cross_dir ], dist ))
    if count_blanks == 0:
        # Count_blanks is a bit backwards, because it counts non-blanks.
        # If at the end of the full board run, the number of non-blanks equals 0,
        # The board must be blank, and add in potentials based around the starting coordinates (7, 7)
        y, x = start_coords
        for dir in forward_dirs:
            dir_y, dir_x = dir_ref [oppo_dir [dir] ]
            for i in range( len_hand ):
                d_y = i * dir_y + y
                d_x = i * dir_x + x
                potential_list.append(( (d_y, d_x), dir, i ))
    return potential_list

def search_base( board, full_tree, hand, verbose=False ):
    """Main function involved in searching [board] for all possible words found in [full_tree] that can be made with [hand]."""
    print '\r' + ' '*78,
    
    # Pretty self explanatory, finds all potential points on the board.
    # Each potential is a place on the board where a word could potentially start.
    # Because of word_tree, a word cannot be checked in a given list if you start with the final letter of the word or in the middle
    # You must start with the first letter first, then all the remaining ones.
    # Due to this, the search for all words must begin with their first possible letter,
    # As the recursive search checks the possibilities of word_tree in reference to the hand to find results.
    potential_list = get_potential_list( board, len( hand) )
    # All potential beginning points for results are relative to existing tiles, or the center-point if there are no tiles,
    # And thus there are a vast many repeat potential points. This function purges all redundant potential points.
    # In practice, I've found this function reduces the potential_list length by ~70-80%, and thereby the time required to search by that amount too.
    potential_list = reduce_potential_list( potential_list )
    
    result_list = []
    pot_len = len( potential_list )
    for i, ((y, x), dir, dist) in enumerate( potential_list ):
        if verbose:
            print '\r%s of %s tiles checked.' % (i, pot_len),
        if dist < min_len:
            # Distance is often 1, so make sure that distance is greater than minimum word length
            dist = min_len
        result_list += [ result for result in board_rec_search( board, full_tree, full_tree, len( hand ), hand, (y, x), dir, req_len=dist )]
    if verbose:
        print '\r%s of %s tiles checked.' % (pot_len, pot_len),
    # First sort by word, ascending.
    result_list.sort( key=itemgetter(0) )
    
    # This removes any repeat results. After being sorted, the first result shouldn't be the same as the last.
    # If it is, then that means that repeat result is the only one in the entire list, so only use one.
    if result_list[0] != result_list[-1]:
        
        # Because the result_list is sorted, repeat results should be next to one another.
        # Omit all results that are the same as the previous one.
        result_list = [ result for i, result in enumerate( result_list ) if result != result_list[i-1] and result[3] > 0 ]
    else:
        result_list = [result_list[0]]
    
    # Then sort by score, descending.
    result_list.sort( key=itemgetter(3), reverse=True )
    return result_list

print "Loading...",

word_str = open( "enable.txt" ).read()
word_list = word_str.lower().split( '\n' )
word_tree = tree_rec( word_list )

print "\r          \rDone!"

while True:
    if not os.path.isfile( board_path ):
        # If given board's file doesn't exist, create a blank one
        # Of the same size and dimensions as (required) wwf board.txt [wwf_board_path]
        board = []
        
        f = open( score_board_path, 'r' )
        data = f.read()
        f.close()
        
        f = open( board_path, 'w' )
        for row in data.split('\n'):
            board.append( [' ' for let in row] )
        
        f.write( '\n'.join([ ''.join(row) for row in board ]) )
        f.close()
        del( f )
    
    board = import_board( board_path, score_board_path )
    print_board( board )
    
    hand = [e for e in raw_input('Letters: ')]
    
    if hand == []:
        print "Refreshing board...\n\n"
    else:
        print '\nProcessing...'
        
        result_list = search_base( board, word_tree, hand, verbose=True )
        result_d = {}
        
        print '\nComplete!'
        
        for word, coords, dir, score, certainty in result_list:
            try:
                result_d[score].append((word, coords, dir, certainty))
            except KeyError:
                result_d[score] = [(word, coords, dir, certainty)]
        
        print '\n%s results found.' % ( len(result_list) )
        if len(result_d.items()) > result_limit and result_limit != 0:
            print 'Showing results for %s highest scores:\n' % (result_limit)
        else:
            print 'Showing all results sorted by score:\n'
        
        display_list = sorted( result_d.items(), key=itemgetter(0), reverse=True )
        for score, word_list in display_list[:result_limit]:
            print str( score ) + ':\n' + ', '.join([ '%s (%s, %s, %s, %s)' % (word, str(y), str(x), dir, certain_ref [certainty] ) for word, (y, x), dir, certainty in word_list ]) + '\n'
        
        s = raw_input('\nPress [ENTER] when board.txt is ready to be refreshed.')

