from ast import Num
import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
from abc import ABC, abstractclassmethod

from transformers import T5Tokenizer, T5ForConditionalGeneration

# the bot stores info on your interests, maybe the bot should use it?
userInfo = {"favNumber": None, "favColor": None}

tokenizer = T5Tokenizer.from_pretrained("t5-small")
t5 = T5ForConditionalGeneration.from_pretrained("t5-small")

def infer_t5(input):
    input_ids = tokenizer(input, return_tensors="pt").input_ids
    outputs = t5.generate(input_ids)

    return tokenizer.decode(outputs[0], skip_special_tokens=True)

mini_lm = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def encode(text):
    """Procedure die text om zet in tensors."""
    return torch.tensor(mini_lm.encode(text))

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

class TranslatorState(State):
    def runState(self):
        response = input("Type the text you want to translate to German\n> ")
        german = infer_t5("translate English to German: " + response)
        print(german + "\n")
        return WorkState()

class WorkState(State):
    options = encode([
        "I want translate some text",
        "I want to talk about numbers"
    ])

    def runState(self):
        response = input("What would you like to do? I can translate or talk about colors\n> ")
        bm = best_match(self.options, encode(response))

        if bm == 0:
            return TranslatorState()
        if bm == 1:
            return NumberState()

class NumberState(State):
    def runState(self):
        try:
            favNumber = int(input("what is your favorite number?\n> "))
        except:
            print("please input an integer")
            return NumberState()

        if favNumber == 6:
            print("Wow! We're, like, the same person!")
            return EndState()
        else:
            userInfo["favNumber"] = favNumber
            print("Maybe I was wrong about you.")
            return BadEndState()

class ColorState(State):
    color = "red"
    def runState(self):
        favColor = input("what is your favorite color?\n> ")
        if userInfo["favColor"]:
            self.color = favColor
        if favColor == self.color:
            print("Wow! I love that color!")
            return NumberState()
        else:
            userInfo["favColor"] = favColor
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
            return WorkState()
        else:
            print("I'm sorry to hear that.")
            return EndState()

def main():
    state = StartState()
    while state:
        state = state.runState()

if __name__ == "__main__":
    main()
