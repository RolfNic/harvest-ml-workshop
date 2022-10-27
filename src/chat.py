import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
from abc import ABC, abstractclassmethod

sentences = ["This is an example sentence", "Each sentence is converted"]

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
embeddings = model.encode(sentences)

def encode(text):
    """Procedure die text om zet in tensors."""
    return torch.tensor(model.encode(text))

def best_match(options, query):
    """Procedure die meerdere opties vergelijkt met een query,
    de beste match word terug gegeven als deze mimimaal een waarde heeft van 0.5.
    """
    value, index = torch.max(nn.functional.cosine_similarity(options, query), 0)
    if value > 0.5:
        return index
    else:
        return None

class State(ABC):
    @abstractclassmethod
    def runState(self):
        pass

class EndState(State):
    def runState(self):
        print("I hope to see you again")

class BadEndState(State):
    def runState(self):
        print("Bye")

class NumberState(State):
    def runState(self):
        try:
            favNumber = int(input("what is your favorite number?\n> "))
            if favNumber == 6:
                print("Wow! We're, like, the same person!")
                return EndState()
            else:
                print("Maybe I was wrong about you.")
                return BadEndState()
        except:
            print("please input an integer")
            return NumberState()

class ColorState(State):
    def runState(self):
        favColor = input("what is your favorite color?\n> ")
        if favColor == "red":
            print("Wow! I love that color!")
            return NumberState()
        else:
            print("I don't think we have a lot in common.")
            return BadEndState()

class NumColState(State):
    options = encode([
        "I want to talk about colors",
        "I want to talk about numbers"
    ])

    def runState(self):
        response = input("would you like to talk about colors or numbers?\n> ")
        bm = best_match(self.options, encode(response))
        if bm == 0:
            return ColorState()
        if bm == 1:
            return NumberState()
        else:
            print("Please answer the question")
            return NumColState()

class StartState(State):
    options = encode(["good", "fine", "wonderful"])

    def runState(self):
        response = input("how do you do?\n> ")
        bm = best_match(self.options, encode(response))
        if bm != None:
            print("Good to hear")
            return NumColState()
        else:
            print("I'm sorry to hear that.")
            return EndState()

def main():
    state = StartState()
    while state:
        state = state.runState()

if __name__ == "__main__":
    main()
