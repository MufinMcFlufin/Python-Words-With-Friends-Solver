from operator import itemgetter
import os, sys

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
    's':2,
    't':2,
    'u':3,
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
board_path = 'board.txt'
score_board_path = 'wwf board.txt'
result_limit = 5

dir_ref = {'u':(-1,0), 'd':(1,0), 'l':(0,-1), 'r':(0,1)}
oppo_dir = {'u':'d', 'd':'u', 'l':'r', 'r':'l'}
# Perpendicular directions of given dir
perp_dir = {'u':'lr', 'd':'lr', 'l':'ud', 'r':'ud',}
# These are the directions that words are oriented in.
forward_dirs = 'rd'

cross_list = [
    [[(-1,0),(0,-1),(0,1)], 'u'],
    [[(-1,0),(0,-1),(1,0)], 'l']]
board_tile_ref = {
    ' ':1,
    's':1,
    'd':2,
    'D':1,
    't':3,
    'T':1}
board_word_ref = {
    ' ':1,
    's':1,
    'd':1,
    'D':2,
    't':1,
    'T':3}

def print_board( board ):
    print '\n'.join( ['+' + '-' * len( board[0] ) + '+'] + [ '|' + ''.join([ d['let'] for d in row ]) + '|' for row in board ] + ['+' + '-' * len( board[-1] ) + '+']) + '\n'

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
    
    # Initialize the board with letter and new values
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
    
    # Fix tile and word values
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

def find_empty_slots( board, num, (y, x), dir, blank=' ' ):
    """ Given board, coordinates, direction and a number, returns the first [num] [blank] spots in [board] from [y, x] in direction [dir] """
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
                yield ( y + d_y, x + d_x )
                add += 1
            else:
                cont = False
        else:
            break
        yield ( y + d_y, x + d_x )

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
        try:
            cur_letter = word [len_cur_str]
            if temp_dict.get( cur_letter, False) == False:
                temp_dict [cur_letter] = []
            temp_dict [cur_letter].append( word )
        except IndexError:
            pass
    for letter, word_list_sect in temp_dict.items():
        cur_dict [letter] = tree_rec( word_list_sect, cur_str + letter)
    del temp_dict
    if cur_str in word_list:
        cur_dict ['word'] = True
    return cur_dict

def check_board( board, word_tree, (y, x), dir ):
    """ Function that will check the perpendicular word to a tile just laid down to make sure it's valid and legal. """
    # cur_str will represent the current iteration of the potential word being checked.
    # It will be appended unto by adjacent perpendicular letters, while checking that this word is valid.
    # If it ever KeyError's, then the whole function fails and return False, as it is not a valid word found in word_tree.
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
    return True

def sub_board( board, (y,x), let ):
    tile = board[y][x]['tile']
    word = board[y][x]['word']
    return board[:y] + [board[y][:x] + [{'let':let, 'tile':tile, 'word':word, 'new':True }] + board[y][x+1:]] + board[y+1:]

def get_new_words( board ):
    """ All words in the current state of the board that have at least one 'new' flag as True """
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

def board_rec_search( board, full_tree, tree_sect, hand, (y, x), dir, cur_str="", req_len=min_len ):
    dir_y, dir_x = dir_ref [dir]
    n_y = y + dir_y * len(cur_str)
    n_x = x + dir_x * len(cur_str)
    # If there's a 'word' key, it should be True, so there shouldn't be a need in checking if it's true.
    # After returning this result, continue with the rest of the search.
    # Will only yield results if cur_str is a valid word, meets/exceeds required length, and if current space is at the end of a word.
    # Without final condition, function could yield words without taking following letter tiles into consideration.
    try:
        score = get_word_score( board, (y, x), dir )
        if hand == []:
            score += bingo_bonus
        if check_coords( board, (n_y, n_x) ):
            if tree_sect['word'] and len(cur_str) >= req_len and blank_space == board[n_y][n_x]['let']:
                yield cur_str, (y, x), dir, score
        else:
            if tree_sect['word'] and len(cur_str) >= req_len:
                yield cur_str, (y, x), dir, score
    except KeyError:
        pass
    if check_coords( board, (n_y, n_x)):
        let = board[n_y][n_x]['let']
        if blank_space == let:
            # Index and current letter being for looped through 'hand'.
            # i makes it easier to omit the current letter when running the next level of recursion.
            for i, let in enumerate( hand ):
                if let == wildcard:
                    # If current letter is a wildcard, for loop through all next letters in the next iteration of word_tree, and ignores the possible 'word' iteration.
                    for sub_let, wild_sect in tree_sect.items():
                        if sub_let == 'word':
                            continue
                        if check_board( sub_board( board, (n_y, n_x), sub_let ), full_tree, (n_y, n_x), dir ):
                            for result in board_rec_search( sub_board( board, (n_y, n_x), sub_let ), full_tree, wild_sect, remove_element( hand, i), (y, x), dir, cur_str + sub_let.upper(), req_len ):
                                yield result
                else:
                    try:
                        if check_board( sub_board( board, (n_y, n_x), let ), full_tree, (n_y, n_x), dir ):
                            for result in board_rec_search( sub_board( board, (n_y, n_x), let ), full_tree, tree_sect[let], remove_element( hand, i), (y, x), dir, cur_str + let, req_len ):
                                yield result
                    except KeyError:
                        pass
        else:
            try:
                for result in board_rec_search( board, full_tree, tree_sect[let], hand, (y, x), dir, cur_str + let, req_len):
                    yield result
            except KeyError:
                pass

def print_potential( board, potential_list ):
    output = []
    for y, row in enumerate( board ):
        output.append( [] )
        for x, d in enumerate( row ):
            let = d['let']
            if let == ' ':
                    d = (y,x,'d') in potential_list
                    r = (y,x,'r') in potential_list
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

def get_potential_list( board, len_hand ):
    potential_list = []
    for y, row in enumerate( board ):
        for x, d in enumerate( row ):
            let = d['let']
            if let != blank_space:
                for cross_coords, cross_dir in cross_list:
                    # Delta x and y from a list of constants, chosen so it goes in a semi-cross pattern around the current letter.
                    # First pass is for words that will be going downwards in direction, then second pass left-wards.
                    for d_y, d_x in cross_coords:
                        # Find empty slots above/left the semi-cross slots.
                        for dd_y, dd_x in find_empty_slots( board, len_hand, ( y + d_y, x + d_x ), cross_dir ):
                            # Syntax check to make sure next slot is valid.
                            # This will check the next slot up if it's blank.
                            # This is necessary because otherwise it'll start trying to place a word in the middle
                            # of another one, which would lead to invalid situations.
                            dir_y, dir_x = dir_ref[ cross_dir ]
                            if check_coords( board, (dd_y + dir_y, dd_x + dir_x)):
                                if blank_space == board[dd_y + dir_y][dd_x + dir_x]['let']:
                                    potential_list.append(( (dd_y, dd_x), oppo_dir[ cross_dir ] ))
                            else:
                                potential_list.append(( (dd_y, dd_x), oppo_dir[ cross_dir ] ))
                    # Repeat the same thing as the previous comment, except now for just the current space itself.
                    dir_y, dir_x = dir_ref[cross_dir]
                    if check_coords( board, (dd_y + dir_y, dd_x + dir_x)):
                        if blank_space == board[dd_y + dir_y][dd_x + dir_x]['let']:
                            potential_list.append(( (dd_y, dd_x), oppo_dir[ cross_dir ] ))
                    else:
                        potential_list.append(( (dd_y, dd_x), oppo_dir[ cross_dir ] ))
    potential_list.sort()
    if len( potential_list ) > 1:
        potential_list = [ e for i, e in enumerate(potential_list) if e != potential_list[i-1] ]
    return potential_list

def search_base( board, full_tree, hand ):
    potential_list = get_potential_list( board, len( hand) )
    result_list = []
    for (y, x), dir in potential_list:
        result_list += [result for result in board_rec_search( board, full_tree, full_tree, hand, (y, x), dir )]
    # Sort by score, descending.
    result_list.sort( key=itemgetter(3), reverse=True )
    if len( result_list ) > 1:
        result_list = [result for i, result in enumerate( result_list ) if result != result_list[i-1] and result[3] > 0 ]
    return result_list

print "Loading...",
word_str = open( "enable1.txt" ).read()
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
        print '\nProcessing...',
        
        result_list = search_base( board, word_tree, hand )
        result_words = []
        result_d = {}
        
        print '\r             \rComplete!\n'
        
        for word, coords, dir, score in result_list:
            result_words.append( word )
            try:
                result_d[score].append((word, coords, dir))
            except KeyError:
                result_d[score] = [(word, coords, dir)]
        
        print '%s results found.' % (len(result_list))
        if len(result_d.items()) > result_limit and result_limit != 0:
            print 'Showing results for %s highest scores:\n' % (result_limit)
        else:
            print 'Showing all results sorted by score:\n'
        
        display_list = sorted( result_d.items(), key=itemgetter(0), reverse=True )
        for score, word_list in display_list[:result_limit]:
            print str( score ) + ':\n' + ', '.join([ '%s (%s, %s, %s)' % (word, str(y), str(x), dir) for word, (y, x), dir in word_list ]) + '\n'
        
        s = raw_input('Press [ENTER] when board.txt is ready to be refreshed.')

ejrr
