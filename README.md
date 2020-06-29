# Boggle-Game

### Module for creating Boggle board and game

 *  BoggleBoard(): Create instance of a Boggle game-board. To be used by the BoggleGame() class
 *  BoggleGame(): Create instance of a Boggle "game" to play a game using a BoggleBoard()

#### Two types of usage modes:
  1) Interactive CLI
```
       $ python3
       >>> from boggle import BoggleGame
       >>> bgame = BoggleGame()
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
        # board letters back into a new board creation: bb = BoggleGame(letters=bb.letters)
```


Uses  **https://www.dictionaryapi.com/api/v3/references/collegiate/json/<word>?key=<api-key>** to validate that a played word is a valid dictionary word before trying to find it on board.

Requires API-KEY from www.dictionaryapi.com. Store API-KEY in local filename: ".dictapikey"
