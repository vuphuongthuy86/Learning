import random

def hangman(word):
    wrong = 0
    stages = ["",
              "_______       ",
              "|             ",
              "|      |      ",
              "|      O      ",
              "|    / | \    ",
              "|     / \     ",
              "|             "
             ]
    rletters = list(word)
    board = ["_"] * len(word)
    win = False
    
    print("\n")
    print("Welcome to Hangman game!".upper())
    print("Be ready! The word has {} letters.".format(len(word)))
    
    while wrong < len(stages):
        print("\n")
        msg = "Please! Guess a letter: "
        char = input(msg)
        if char in rletters:
            for i in range(len(word)):
                if char == rletters[i]:
                    # cind = rletters.index(char)
                    board[i] = char
                    # rletters[cind] = '$'
        else:
            wrong += 1
        print(" ".join(board))
        e = wrong + 1
        print("\n".join(stages[0:e]))
        if "_" not in board:
            print("Your win! Congratulation!")
            print(" ".join(board))
            win = True
            break
    if not win:
        print("\n".join(stages[0:wrong + 1]))
        print("You lose! The correct answer is {}.".format(word))

if __name__ == "__main__":
    words = ["bee", "dog", "tiger", "elephant", "monkey", "cat"]
    msg = "Do you want to continue!? (y/n): "
    while True:
        word_idx = random.randrange(0, len(words))
        hangman(words[word_idx])
        print("\n")
        check = input(msg)
        if check == 'n':
            break
