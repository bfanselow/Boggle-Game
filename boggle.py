"""

  Module: boggle
  Classes:
     BoggleBoard(): Create instance of a Boggle game-board. To be used by the BoggleGame() class
     BoggleGame(): Create instance of a Boggle "game" to play a game using a BoggleBoard()

  Two types of usage modes:
    1) Interactive CLI
       $ python3
       >>> from boggle import BoggleGame
       >>> bgame = BoggleGame()
       >>> bgame.play()

    2) Use BoggleBoard() and BoggleGame() objects to populate a UI-based game
        from boggle import BoggleBoard, BoggleGame
        ... 
        bb = BoggleBoard()  <-- use this data for display
        ... 
        game = BoggleGame(board=bb)  <-- use this data for game
        ... 
        # rather than keeping a boggle-board in memory, you can just recreate it by
        # board letters back into a new board creation: bb = BoggleGame(letters=bb.letters)

   Uses  https://www.dictionaryapi.com/api/v3/references/collegiate/json/<word>?key=<api-key>
   to validate that a played word is a valid dictionary word before trying to find it on board. 

   Requires API-KEY from www.dictionaryapi.com. Store API-KEY in local filename: ".dictapikey" 

"""
import collections
import requests
import random
import string
import json
import sys
   
DICT_API_URL =  'https://www.dictionaryapi.com/api/v3/references/collegiate/json/'
DICT_API_KEY_FILE = '.dictapikey'

# Rather than building our Boggle board from a totally random choice of letters,
# we weight the letter choice according to the typical english letter freqeuncy.
# We us this letter freqeuncy in relative percentage, based on a list of 40,0000
# words from:
#   http://pi.math.cornell.edu/~mec/2003-2004/cryptography/subs/frequencies.html
letter_frequency = {
     'e': 12.02,
     't': 9.10,
     'a': 8.12,
     'o': 7.68,
     'i': 7.31,
     'n': 6.95,
     's': 6.28,
     'r': 6.02,
     'h': 5.92,
     'd': 4.32,
     'l': 3.98,
     'u': 2.88,
     'c': 2.71,
     'm': 2.61,
     'f': 2.30,
     'y': 2.11,
     'w': 2.09,
     'g': 2.03,
     'p': 1.82,
     'b': 1.49,
     'v': 1.11,
     'k': 0.69,
     'x': 0.17,
     'q': 0.11,
     'j': 0.10,
     'z': 0.07
}

## word-scoring
word_length_score = {
  2: 2,
  3: 5,
  4: 6,
  5: 8
}
max_score = 10 # anything else

#-----------------------------------------------------------------------------80
class InitError(Exception):
    pass

#-----------------------------------------------------------------------------80
class BoggleBoard():

    def __init__(self, **kwargs):
        """Initialize a Boogle board by building char-set and loading a 2-D
           matrix of chars
        """
        self.cname = self.__class__.__name__
        self.debug = 0

        self.size = 5
        if 'size' in kwargs:
            self.size = kwargs['size']
            if not isinstance(self.size, int):
                raise InitError("%s: Invalid board size: %s" % (self.cname, str(self.size)))
        if 'debug' in kwargs:
            self.debug = kwargs['debug']
        letters = None
        if 'letters' in kwargs:
            letters = kwargs['letters']
            if not letters.isalpha():
                raise InitError("%s: Invalid input character list: %s" % (self.cname, str(letters)))
            if len(list(letters)) != self.size**2:
                raise InitError("%s: Input character list length does not match board size: 2x%d" % (self.cname, self.size))

        self.letter_list = self.build_letter_list(letters)
        self.board = self.build_board() # 2-D list of lists
        self.letters = ''.join(self.letter_list)


    def show(self):
        """Visual representation of board.  Tried numpy but this is better"""
        horiz_tile_count = (3*self.size) + 4
        print('-'*horiz_tile_count)
        for row in self.board:
            row_chars = ''.join([ " "+c+" " for c in row ])
            print("| %s |" % row_chars)
        print('-'*horiz_tile_count)


    def build_letter_list(self, letters):
        """Compile a list of size**2 letters to be arranged on the 2-D board.
           We use either the provided string of letters, or (if letters is None)
           we create the list of letters from a weighted random selection.
           Params: (str) letter string - could be None
           Returns: (list) letters to be place on board
        """
        if letters:
            letter_list = list(letters)
        else:
            char_choices =  self.__build_char_choice_list()
            letter_list = [random.choice(char_choices) for i in range(self.size**2)]
        return letter_list


    def build_board(self):
        """Create the 2D matrix (list of lists) of characters.
           Returns: 2-D matrix representing the Boggle board layout
        """
        board = [ [c for c in self.letter_list[i:i+self.size]] for i in range(0, len(self.letter_list), self.size)]
        return board


    def build_neighbor_map(self, i_row, j_col):
        """Build a dict mapping of "nearest-neighbor" matrix cell indices for passed
           row,cell indices.  "Nearest-neighbor" of a given cell in the Boggle contect
           is defined by any cell which is touching the given cell including positions
           immediately: up, down, left, right, and the 4 diagonal positions.
           Returns: (dict) { <position-id> => (i,j) }. Dict value can be None such
                    as "left" or "up" of first cell.
        """
        idx_edge = self.size - 1
        nearest_neighbors_map = {
          'left':          ((i_row, j_col-1 ) if j_col > 0 else None),
          'right':         ((i_row, j_col+1 ) if j_col < idx_edge else None),
          'up':            ((i_row-1, j_col ) if i_row > 0 else None),
          'down':          ((i_row+1, j_col ) if i_row < idx_edge else None),
          'd-up-left':     ((i_row-1, j_col-1 ) if (i_row > 0 and j_col > 0)  else None),
          'd-up-right':    ((i_row-1, j_col+1 ) if (i_row > 0 and j_col < idx_edge)  else None),
          'd-down-left':   ((i_row+1, j_col-1 ) if (i_row < idx_edge and j_col > 0)  else None),
          'd-down-right':  ((i_row+1, j_col+1 ) if (i_row < idx_edge and j_col < idx_edge)  else None)
        }
        return nearest_neighbors_map


    def get_letter_at_position(self, i_row, j_col):
        """Retieve the letter at the position i_row, j_col.
           Params: (ints) row and column indices.
           Returns" (str) letter
        """
        return self.board[i_row][j_col]

    def nearest_neighbor_data(self, i_row, j_col):
        """Build a dict of nearest-neighbor "data" for passed matrix position
           from the stored nearest-neighbor mapping dict.
           Format:  { (i1,j1): <letter1>, ...  (iN, jN): <letterN> }
           Params: (ints) row and column indices.
           Returns: (dict) nearest-neighbor data for passed matrix position.
        """
        nn_data = {}
        neighbor_positions = self.build_neighbor_map(i_row, j_col).values()
        for t_pos in neighbor_positions:
            if t_pos: # neighbor can be None for edge positions
                nn_data[t_pos] = self.get_letter_at_position(*t_pos)
        return nn_data


    def nearest_neighbor_letters(self, i_row, j_col):
        """Build a list of letters for all "nearest-neighbor" cells relative
           to position of passed row, col indices
           Params: row,col indices
           Returns: (list) nearest-neighbor letters
        """
        neighbor_letters = self.nearest_neighbor_data.values()
        return neighbor_letters


    def positions_for_letter(self, letter):
        """Return a list of one or more index tuples for passed letter. Since a letter
           might be found more than once on a board, we don't necessarily know which
           specific matrix position a letter has , so we find all possble positions for
           passed letter.
           Returns: (list) (i,j) index-tuple list.
        """
        position_tuples = []
        for i,row in enumerate(self.board):
            for j,char in enumerate(row):
                if char == letter:
                    position_tuples.append((i,j))
        return position_tuples


    def __build_char_choice_list(self):
        """Internal method for building a game-board character-list using weighted
           character frequency mapping
        """
        char_list = []
        for c,w in letter_frequency.items():
            clist = [c] * int(w * 100)
            char_list.extend(clist)
        # DEBUG
        #counter = collections.Counter(char_list)
        #print(counter)
        random.shuffle(char_list)
        return char_list


#-------------------------------------------------------------------------------
class BoggleGame():

    def __init__(self, **kwargs):
        """Initialize a Boogle game using one of three possible game-initialization options:
            1) Pass in no parameters in which case a new default BoggleBoard() object will be created
               to be used for the game.
            2) Pass in a BoggleBoard() object to be used for the game.
            3) pass in a letter-list string - this will automatically create a BoggleBoard()
               object with the passed lettters to be used for the game.
        """
        self.cname = self.__class__.__name__
        self.debug = 0
        if 'debug' in kwargs:
            self.debug = kwargs['debug']

        board = kwargs.get('board', None)
        letters = kwargs.get('letters', None)
        if board:
            if not isinstance(board, BoggleBoard):
                raise InitError("%s: Invalid BoggleBoard input object" % (self.cname))
            self.board = board
        elif letters:
            # take square-root of length to get size. But size MUST be an integer
            N_letters = len(list(letters))
            size = N_letters**(1/2.0)
            if not size.is_integer():
                raise InitError("%s: Input character string has length=%d which does not have an integer square root (%s)" % (self.cname, N_letters, size))
            self.board = BoggleBoard(letters=letters, size=int(size), debug=self.debug)
        else:
            self.board = BoggleBoard(debug=self.debug)

        # load dictionary API key
        try:
            self.DICT_API_KEY = self.__load_dict_api_key()
        except Exception as e:
            raise InitError("%s: __load_dict_api_key() failed with exception: %s" % (self.cname, e))

        # Track all valid words with score { <word1>: <score1>, .... <wordN>: <scoreN> }
        # This will provide constraint of only keeping one copy of each word, and give ability to
        # tally current score at any time
        self.scored_words = {}



    def play(self):
        """Start a CLI interactive game. Seek input from user and exucte play_word()
           Keep track of score. Re-display board on each move.
        """
        word = None
        self.board.show()
        while word != 'QUIT':
            word = input("Enter a playable word...  Enter QUIT to stop\n")
            d_result = self.play_word(word.strip())
            if not d_result:
                print("\"%s\" is not a playable word" % (word))
            score = self.current_score()
            print("CURRENT SCORE: %d\nSCORED-WORDS:\n%s" % (score, self.scored_words))
            self.board.show()
        print("\nThanks for playing!")
        sys.exit(0)


    def play_word(self, word):
        """Identify if the passed word is "playable" (valid word and on board). If it is,
           add the word to the self.scored_words attribute.
           Params: (str) word text
           Returns: (dict) word and corresponding score for word. Score is None (not zero) if NOT a playable word.
        """
        self.dprint(1, "Checking if word is playable: [%s]" % (word))
        if not self.is_playable_word(word):
            self.dprint(1, "\"%s\" is not a valid Boggle word" % (word))
            return None

        self.dprint(1, "Checking if word is on board: [%s]" % (word))
        if self.check_word_on_board(word):
            score = word_length_score.get(len(list(word)), None)
            if not score:
                score = max_score
            self.scored_words[word] = score
            return { word: score }
        else:
            self.dprint(1, "\"%s\" is not playable on this board" % (word))
            return None


    def play_word_list(self, word_list):
        """Identify if any of the passed word are "playable" (valid word and on board). For those that
           are playable, add them to the self.scored_words attribute.
           Params: (list) list of word strings
           Returns: (dict) words and corresponding scores for word. Score is None (not zero) if NOT a playable word.
        """
        all_results = {}
        for word in word_list:
            d_result = self.play_word(word)
            all_results.update(d_result)
        return all_results

    def check_word_on_board(self, word):
        """Identify if the passed word is "playable" and can be made on the current
           Boggle board based on standard Boggle rules.
           Params: (str) word text
           Returns: (bool) status of playable word on the current board (True|False)
        """
        status = False

        letter_list = list(word)
        self.dprint(1, "Letter list: [%s]" % (letter_list))

        # we have to check all possible start-postions since letters can be repeated on board
        start_positions = self.board.positions_for_letter(letter_list[0])
        if len(start_positions):
            self.dprint(1, "Start-positions: [%s]" % (start_positions))
            for (i_row, j_col) in start_positions:
                self.dprint(1, "Starting at position %d,%d with letter %s" % (i_row, j_col, letter_list[0]) )
                status = self.recursive_string_search(i_row, j_col, letter_list)
                if status: # if we can play it, don't check other starting points
                    self.dprint(1, "Valid boggle word (%s) starting at (%d,%d)" % (word, i_row, j_col) )
                    break

        return status


    def recursive_string_search(self, i_row, j_col, letter_list):
        """Recursively identify if the passed letter list can be strung together with "touching"
           letters beginning from the (i_row,j_col) start-position.
           NOTE: we have implicitely already verified that the letter at the initial starting-
                 position is present on the board.
           Params: (list) letter list - remaining letters to check for neighboring connection.
           Returns: (bool) status of "boggle string" (i.e. all letters in list are touching)
        """
        current_letter = letter_list.pop(0)
        next_letter = letter_list[0] # since we popped, i=0 is "next" letter
        nn_data = self.board.nearest_neighbor_data(i_row, j_col)
        nn_letters = nn_data.values()
        self.dprint(1, "Current-letter=(%s); Next-letter=(%s);  Neighboring letters: %s" % (current_letter, next_letter, nn_letters) )
        if next_letter not in nn_letters:
            self.dprint(1, "Next-letter=(%s) not found in any of the neighboring letters" % (next_letter) )
            return False
        else: # iterate over neighbors and try from each possible starting point
            for t_pos, letter in nn_data.items():
                self.dprint(1, "Trying NN letter (%s) at position %s" % (letter, str(t_pos)) )
                if letter == next_letter:
                    self.dprint(1, "Found possible next letter (%s) Checking from next start point (%s)" % (letter, str(t_pos)) )
                    if len(letter_list) == 1:
                        return True # recursion STOP case - we have arrived at end of letter_list
                    else:
                        return self.recursive_string_search(t_pos[0], t_pos[1], letter_list)

    def is_playable_word(self, word):
        """Identify if the passed word is a "playable" word according to
           Boggle rules:
            * first see if the word is a valid English word.
            * discard Proper pronouns
           Params: (str) word text
           Returns: (bool) status of playable word (True|False)

           ## TODO: fill out last check according to Boggle rules
        """
        status = True
        # is string?
        if not isinstance(word, str):
            status = False

        # is 2 or more letters?
        if len(list(word)) < 2:
            status = False

        status = self.__is_in_dictionary(word) 
        if not status:
            self.dprint(1, "Word (%s) not found in dictionary" % (word) )

        # is valid Boggle word? # Filter pronouns etc.

        return status
   
 
    def __is_in_dictionary(self, word):
        """Identify if the passed word is a word in the English dictionary 
           Params: (str) word text
           Returns: (bool) status of dictionary lookup (True|False)
        """
        status = False 
        url = "%s/%s" % (DICT_API_URL, word)
        self.dprint(1, "Checking if word (%s) is in dictionary" % (word) )
        query_params = { 'key': self.DICT_API_KEY }
        try:
            resp = requests.get( url, params=query_params ) 
        except Exception as e:
            print("%s: Dictionary lookup failed with exception: %s" % (self.cname, e))
            sys.exit(1) # definelty should bail if this ever fails

        l_resp = json.loads(resp.text)
        ##print(l_resp)
        o_resp = l_resp[0]
        if isinstance(o_resp, dict):
            if 'meta' in o_resp: 
                if 'id' in o_resp['meta']: 
                    if word in o_resp['meta']['id']: 
                        status = True
        return status


    def __load_dict_api_key(self):
        """Read credentials to retrieve API key"""
        ...
        with open(DICT_API_KEY_FILE, "r") as file:
            api_key = file.readline()
        return api_key.strip() 


    def current_words(self):
        """Return a list of the valid/scored words currently played"""
        return( self.scored_words.keys())

    def current_score(self):
        """Return the total score for all valid/scored words currently played"""
        score = sum(self.scored_words.values())
        return(score)

    def dprint(self, d_level, msg):
        """Internal debug-print functionality"""
        if d_level <= self.debug:
            print("(%d): %s" % (d_level, msg))

#-------------------------------------------------------------------------------
if __name__ == '__main__':

    bb = BoggleBoard(size=5)
    bb.show()

    bb.get_letter_at_position(1,1)
    game = BoggleGame(board=bb, debug=2)
    game.current_score()

    game.play_word('men')
