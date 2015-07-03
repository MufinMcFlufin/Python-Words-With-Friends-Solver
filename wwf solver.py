from operator import itemgetter
import traceback

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
dir_ref = {'u':(-1,0),'d':(1,0),'l':(0,-1),'r':(0,1)}
oppo_dir = {'u':'d', 'd':'u', 'l':'r', 'r':'l'}
cross_list = [
    [[(-1,0),(0,-1),(0,1)], 'u'],
    [[(-1,0),(0,-1),(1,0)], 'l']]

bingo_bonus = 35
board_path = "wwf board.txt"
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

def import_board( path, tile_ref, word_ref ):
    f = open( path )
    board = [ [ (' ', tile_ref[e], board_ref[e], False) for e in line.strip('\n') ] for line in f ]
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

def check_board( board, word_tree ):
    # Loop through all of the board to find words that aren't valid.
    for y, row in enumerate( board ):
        for x, d in enumerate( row ):
            let, new = d['let'], d['new']
            if let != blank_space:
                # After finding a letter, first check downward then right-ward
                for dir in 'dr':
                    dir_y, dir_x = dir_ref[dir]
                    oppo_y, oppo_x = dir_ref[ oppo_dir [dir] ]
                    # If pass coordinate check on proximity slots, check if the beginning of a word.
                    # If fails coordinate check before the word, it's at the edge of the board, and beginning of a word.
                    if check_coords( board, (y+oppo_y, x+oppo_x)):
                        word_start = blank_space == board[y + oppo_y][x + oppo_x]['let']
                    else:
                        word_start = True
                    # Would rather use a boolean and put all the code in one spot than copy paste.
                    # Begin checking to see if found word is found in the word_tree
                    # Function returns False is any word does not pass this check.
                    if word_start:
                        cur_str = ''
                        cont = True
                        tree_sect = word_tree
                        while cont:
                            try:
                                if not check_coords( board, (y + dir_y * len(cur_str), x + dir_x * len(cur_str))):
                                    raise IndexError
                                let = board[ y + dir_y * len(cur_str) ][ x + dir_x * len(cur_str) ]['let']
                                cont = let != blank_space
                                if cont:
                                    cur_str += let
                                    tree_sect = tree_sect[let]
                            except KeyError:
                                return False
                            except IndexError:
                                cont = False
                        if len( cur_str ) > 1:
                            try:
                                if not tree_sect['word']:
                                    pass
                            except KeyError:
                                return False
    return True

def board_rec_search( board, full_tree, tree_sect, hand, (y, x), (dir_y, dir_x), cur_str="", req_len=min_len ):
    # If there's a 'word' key, it should be True, so there shouldn't be a need in checking if it's true.
    # After returning this result, continue with the rest of the search.
    try:
        if tree_sect['word'] and len(cur_str) >= req_len:
            yield cur_str, (y, x)
    except KeyError:
        pass
    len_cur = len(cur_str) + 1
    n_y, n_x = y + dir_y * len_cur, x + dir_x * len_cur
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
                        for result in board_rec_search( board, full_tree, wild_sect, remove_element( hand, i), (y, x), (dir_y, dir_x), cur_str + sub_let.upper(), req_len ):
                            yield result
                else:
                    try:
                        for result in board_rec_search( board, full_tree, tree_sect[let], remove_element( hand, i), (y, x), (dir_y, dir_x), cur_str + let, req_len ):
                            yield result
                    except KeyError:
                        pass
        else:
            try:
                for result in board_rec_search( board, full_tree, tree_sect[let], remove_element( hand, i), (y, x), (dir_y, dir_x), cur_str + let, req_len):
                    yield result
            except KeyError:
                pass

def rec_search( full_tree, tree_sect, hand, cur_str="", req_len=min_len ):
    # If there's a 'word' key, it should be True, so there shouldn't be a need in checking if it's true.
    # After returning this result, continue with the rest of the search.
    try:
        if tree_sect['word'] and len(cur_str) >= req_len:
            yield cur_str
    except KeyError:
        pass
    # Index and current letter being for looped through 'hand'.
    # i makes it easier to omit the current letter when running the next level of recursion.
    for i, let in enumerate( hand ):
        if let == wildcard:
            # If current letter is a wildcard, for loop through all next letters in the next iteration of word_tree, and ignores the possible 'word' iteration.
            for sub_let, wild_sect in tree_sect.items():
                if sub_let == 'word':
                    continue
                for result in rec_search( full_tree, wild_sect, remove_element( hand, i), cur_str + sub_let.upper(), req_len ):
                    yield result
        else:
            try:
                for result in rec_search( full_tree, tree_sect[let], remove_element( hand, i), cur_str + let, req_len ):
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
                                    potential_list.append(( dd_y, dd_x, oppo_dir[ cross_dir ] ))
                                    if (0,3,'r') == ( dd_y, dd_x, oppo_dir[ cross_dir ] ):
                                        print (y,x), (d_y,d_x), (dd_y,dd_x), cross_dir, (dir_y, dir_x)
                            else:
                                potential_list.append(( dd_y, dd_x, oppo_dir[ cross_dir ] ))
                    # Repeat the same thing as the previous comment, except now for just the current space itself.
                    dir_y, dir_x = dir_ref[cross_dir]
                    if check_coords( board, (dd_y + dir_y, dd_x + dir_x)):
                        if blank_space == board[dd_y + dir_y][dd_x + dir_x]['let']:
                            potential_list.append(( dd_y, dd_x, oppo_dir[ cross_dir ] ))
                    else:
                        potential_list.append(( dd_y, dd_x, oppo_dir[ cross_dir ] ))
    potential_list.sort()
    if len( potential_list ) > 1:
        potential_list = [ e for i, e in enumerate(potential_list) if e != potential_list[i-1] ]
    return potential_list

def search_base( board, full_tree, len_hand ):
    potential_list = get_potential_list( board, len_hand )

print "Loading...",
word_str = open( "enable1.txt" ).read()
word_list = word_str.lower().split( '\n' )
word_tree = tree_rec( word_list )
print "\r          \rDone!"

while True:
    # List of inputed letters. Raw_input then is changed into a list of strings so it's easier to work with.
    i_letters = [ i for i in raw_input( "Letters: " ).lower() ]
    
    result_list = [ result for result in rec_search( word_tree, word_tree, i_letters ) ]
    
    print ''
    
    if 0 == len( result_list ):
        print 'No results found.\n'
    else:
        result_list.sort()
        if 1 != len( result_list ):
            result_list = [ result for i, result in enumerate( result_list[:-1] ) if result != result_list[i-1] ]
        result_dict = {}
        
        # for word, points in result_list:
            # try:
                # result_dict[points].append( word )
            # except KeyError:
                # result_dict[points] = [word]
        
        # for k, v in sorted( result_dict.items(), key=itemgetter(0), reverse=True ):
            # print str(k) + ':\n' + ', '.join( sorted(v, key=len, reverse=True ) )
        
        for word in sorted( result_list, key=len, reverse=True ):
            print word
        
        print '\n'

