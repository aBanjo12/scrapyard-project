import random

def main():
    word = "word"
    display = "_" * len(word)
    correct_guess = []
    letters_guess = []
    win = False
    attempts = 6

    while win == False and attempts > 0:
        guess = input("What letter would you like to guess? ")
        guess = are_you_sure(guess)
        
        while guess.lower() in letters_guess:
            guess = input("You've already guessed that letter, try another one ")

        letters_guess.append(guess)

        if guess.lower() in word:
            print("Good boy, you got it right!\n")
            correct_guess.append(guess)

            if len(correct_guess) == len(word):
                print("Congrats, you got the word!")
                win = True
        else:
            print(guess, "was not in the word. Try again.")
            attempts -= 1
    print("You lost")




def are_you_sure(g):
    are_you_sure = random.randrange(0, 101)

    if(are_you_sure == 100):
        print("Are you sure?")
        response = input()

        if response.lower() == "yes" or response.lower() == "y":
            print("If you say so I guess\n")

        elif response.lower() == "no" or response.lower() == "n":
            g = input("Enter new guess ")

        else:
            g = input("Invalid input, enter yes or no ")

    return g



if __name__ == "__main__":
    main()