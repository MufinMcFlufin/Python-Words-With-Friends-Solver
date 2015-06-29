from operator import itemgetter

def import_board( path, tile_ref, word_ref ):
    f = open( path )
    tile_board = [[tile_ref[e] for e in line] for line in f]
    word_board = [[word_ref[e] for e in line] for line in f]
    return tile_board, word_board

def remove_element( list, index ):
    return list[:index] + list[index+1:]

def check_word( word, tree ):
    try:
        if len(word) == 0:
            return tree[-1]
        elif False != tree[ word[0] ]:
            return check_word( word[1:], tree[ word[0] ] )
        else:
            return False
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

def rec_search( tree, hand, cur_str="", req_len=2 ):
    # If there's a 'word' key, it should be True, so there shouldn't be a need in checking if it's true.
    # After returning this result, continue with the rest of the search.
    try:
        if tree['word'] and len(cur_str) >= req_len:
            yield cur_str
    except KeyError:
        pass
    # Index and current letter being for looped through 'hand'.
    # i makes it easier to omit the current letter when running the next level of recursion.
    for i, let in enumerate( hand ):
        if let == '_':
            for sub_let, tree_sect in tree.items():
                if sub_let == 'word':
                    continue
                for result, r_point in rec_search( tree_sect, remove_element( hand, i), cur_str + sub_let.upper(), req_len ):
                    yield result, r_point
            continue
        else:
            try:
                for result, r_point in rec_search( tree[let], remove_element( hand, i), cur_str + let, points + letter_ref[let] ):
                    yield result, r_point
            except KeyError:
                pass

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
    '_':0}

bingo_bonus = 35
board_path = "wwf board.txt"
board_tile_ref = {
    'd':2,
    't':3}
board_word_ref = {
    'D':2,
    'T':3}

print "Loading...",
word_str = open( "enable1.txt" ).read()
word_list = word_str.lower().split( '\n' )
word_tree = tree_rec( word_list )
print "\rDone!     "

while True:
    # List of inputed letters. Raw_input then is changed into a list of strings so it's easier to work with.
    i_letters = [ i for i in raw_input( "Letters: " ).lower() ]
    
    result_list = [ result for result in rec_search( word_tree, i_letters ) ]
    
    print ''
    
    if 0 == len( result_list ):
        print 'No results found.\n'
    else:
        result_list.sort()
        if 1 != len( result_list ):
            result_list = [ result for i, result in enumerate( result_list[:-1] ) if result != result_list[i-1] ]
        result_dict = {}
        
        for word, points in result_list:
            try:
                result_dict[points].append( word )
            except KeyError:
                result_dict[points] = [word]
        
        for k, v in sorted( result_dict.items(), key=itemgetter(0), reverse=True ):
            print str(k) + ':\n' + ', '.join( sorted(v, key=len, reverse=True ) )
        
        print '\n'

