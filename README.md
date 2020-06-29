# Boggle-Game

### Module for creating Boggle board and game

 *  BoggleBoard(): Create instance of a Boggle game-board. To be used by the BoggleGame() class
 *  BoggleGame(): Create instance of a Boggle "game" to play a game using a BoggleBoard()

#### TODO:
 * Add enforcement of not using the same letter multiple times in same word.
 * Add a three-minute timer (started in separate thread) at start of new game.

---
#### Two types of usage modes:
  1) Interactive CLI
```
       $ python3
       >>> from boggle import BoggleGame
       >>> bgame = BoggleGame()
       >>> bgame.play()
      
       OR SPECIFY DIMENSION (default: 5x5) 
       >>> bgame = BoggleGame(size=4)
       >>> bgame.play()
        
       OR SPECIFY LETTERS (default: chosen from wweighted random-choice)
       >>> bgame = BoggleGame(letters='qazxswedcvfrtgbnhytgfcpod')
       >>> bgame.play()

```

  2) Use BoggleBoard() and BoggleGame() objects to populate a UI-based game
```
     from boggle import BoggleBoard, BoggleGame
     ...
     bb = BoggleBoard()  <-- use this data for display
     ...
     game = BoggleGame(board=bb)  <-- use this data for game
     ...
     # rather than keeping a boggle-board in memory, you can just recreate it by
     # putting same board letters back into a new board creation: bb = BoggleGame(letters=bb.letters)
```

---

Uses  **www.dictionaryapi.com/api/v3/references/collegiate/json/** to validate that a played word is a valid dictionary word before trying to find it on board.

Requires API-KEY from **www.dictionaryapi.com**. 

Store API-KEY in local filename: ".dictapikey"

---

```
>>> from boggle import BoggleBoard, BoggleGame
>>> bb = BoggleBoard()
>>> bb.show()
-------------------
|  e  i  r  i  n  |
|  c  t  s  d  t  |
|  h  o  e  l  e  |
|  w  i  i  n  h  |
|  g  v  s  t  i  |
-------------------
>>> bb.positions_for_letter('e')
[(0, 0), (2, 2), (2, 4)]
>>> bb.nearest_neighbor_data(2,2)
{(1, 2): 's', (3, 2): 'i', (1, 3): 'd', (2, 3): 'l', (3, 3): 'n', (3, 1): 'i', (1, 1): 't', (2, 1): 'o'}
>>>
>>> game = BoggleGame(board=bb)
>>> game.play()
-------------------
|  e  i  r  i  n  |
|  c  t  s  d  t  |
|  h  o  e  l  e  |
|  w  i  i  n  h  |
|  g  v  s  t  i  |
-------------------
Enter a playable word...  Enter QUIT to stop
lint
"lint" is playable
CURRENT SCORE: 6
SCORED-WORDS:
{'lint': 6}
-------------------
|  e  i  r  i  n  |
|  c  t  s  d  t  |
|  h  o  e  l  e  |
|  w  i  i  n  h  |
|  g  v  s  t  i  |
-------------------
Enter a playable word...  Enter QUIT to stop
who
"who" is playable
CURRENT SCORE: 11
SCORED-WORDS:
{'who': 5, 'lint': 6}
-------------------
|  e  i  r  i  n  |
|  c  t  s  d  t  |
|  h  o  e  l  e  |
|  w  i  i  n  h  |
|  g  v  s  t  i  |
-------------------
Enter a playable word...  Enter QUIT to stop
QUIT

Thanks for playing!
```
---

```
>>> from boggle import BoggleGame
>>> game = BoggleGame()
>>> game.play()
-------------------
|  e  t  h  r  t  |
|  n  n  r  c  g  |
|  m  d  l  i  u  |
|  a  b  m  o  r  |
|  e  t  t  u  a  |
-------------------
Enter a playable word...  Enter QUIT to stop
ten
"ten" is playable
CURRENT SCORE: 5
SCORED-WORDS:
{'ten': 5}
-------------------
|  e  t  h  r  t  |
|  n  n  r  c  g  |
|  m  d  l  i  u  |
|  a  b  m  o  r  |
|  e  t  t  u  a  |
-------------------
Enter a playable word...  Enter QUIT to stop
tenm
"tenm" is NOT playable
"tenm" is not in dictionary
CURRENT SCORE: 5
SCORED-WORDS:
{'ten': 5}
-------------------
|  e  t  h  r  t  |
|  n  n  r  c  g  |
|  m  d  l  i  u  |
|  a  b  m  o  r  |
|  e  t  t  u  a  |
-------------------
Enter a playable word...  Enter QUIT to stop
tenth
"tenth" is playable
CURRENT SCORE: 13
SCORED-WORDS:
{'ten': 5, 'tenth': 8}
-------------------
|  e  t  h  r  t  |
|  n  n  r  c  g  |
|  m  d  l  i  u  |
|  a  b  m  o  r  |
|  e  t  t  u  a  |
-------------------
Enter a playable word...  Enter QUIT to stop
month
"month" is NOT playable
"month" cannot be made on this board
CURRENT SCORE: 13
SCORED-WORDS:
{'ten': 5, 'tenth': 8}
-------------------
|  e  t  h  r  t  |
|  n  n  r  c  g  |
|  m  d  l  i  u  |
|  a  b  m  o  r  |
|  e  t  t  u  a  |
-------------------
Enter a playable word...  Enter QUIT to stop
bad
"bad" is playable
CURRENT SCORE: 18
SCORED-WORDS:
{'ten': 5, 'tenth': 8, 'bad': 5}
-------------------
|  e  t  h  r  t  |
|  n  n  r  c  g  |
|  m  d  l  i  u  |
|  a  b  m  o  r  |
|  e  t  t  u  a  |
-------------------
Enter a playable word...  Enter QUIT to stop
QUIT

Thanks for playing!
```

---

```
>>> from boggle import BoggleGame
>>> game = BoggleGame()
>>> game.board.show()
-------------------
|  t  t  r  t  g  |
|  a  h  d  i  i  |
|  a  h  i  y  p  |
|  u  e  a  e  h  |
|  a  n  n  r  i  |
-------------------
>>> game.board.letters
'ttrtgahdiiahiypueaehannri'
>>> game = BoggleGame(letters=game.board.letters)
>>> game.board.show()
-------------------
|  t  t  r  t  g  |
|  a  h  d  i  i  |
|  a  h  i  y  p  |
|  u  e  a  e  h  |
|  a  n  n  r  i  |
-------------------
>>> game = BoggleGame(letters='qwertyuiopasdfgh')
>>> game.board.show()
----------------
|  q  w  e  r  |
|  t  y  u  i  |
|  o  p  a  s  |
|  d  f  g  h  |
----------------
```
