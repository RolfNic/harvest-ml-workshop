import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
from abc import ABC, abstractclassmethod

sentences = ["This is an example sentence", "Each sentence is converted"]

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
embeddings = model.encode(sentences)

# inventory of items for your adventure
inventory = {"hasKey": False, "hasRock": False}

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

class AdventureStart(State):
    options = encode([
        "where am i?",
        "look around",
        "open the door with the key",
        "go to the door",
        "look at the door",
        "go to the wall",
        "look at the wall",
        "go to the table and chair",
        "look at the table and chair",
        "use the chair to pry at the wall",
        "hit the wall with the chair",
        "hit the hinge with the rock",
        "go to the closet",
        "look at the closet",
        ])

    def runState(self):
        response = input("You find yourself in a dimly lit room, what you do?\n> ")
        bm = best_match(self.options, encode(response))
        if bm == 0:
            print("...you ask yourself")
            return AdventureStart()
        if bm == 1:
            print("Peering through the darkness you see a closet on your left,\na table and chair on your right, a damaged wall behind you,\nand a closed door in front of you.")
            return AdventureStart()
        if bm == 2:
            if inventory["hasKey"]:
                print("you open the door and go through it.")
                return None
            else:
                print("you dont have the key")
                return AdventureStart()
        if bm in [3, 4]:
            print("The door is looks heavy, it is locked, it has a clear keyhole under the handle.")
            return AdventureStart()
        if bm in [5, 6]:
            print("You move closer to the wall, it appears to have been damaged\nby time. Some rocks look loose but you can't pry them out")
            return AdventureStart()
        if bm in [7, 8]:
            print("The table is covered in a layer of dust, it appears to have stood here untouched for a long time.\nThe chair has a soft cushion, one of its legs appears to be broken and makes a sharp point.")
            return AdventureStart()
        if bm == 9:
            if not inventory["hasRock"]:
                print("You use the broken leg to pry at the rocks.\nA fist sized rock falls on the floor, you pick it up.")
                inventory["hasRock"] = True
                return AdventureStart()
            else:
                print("Nothing happens")
                return AdventureStart()
        if bm == 10:
            print("You hit the wall with the chair, it makes a loud bang and some dust falls on the floor.")
            return AdventureStart()
        if bm == 11:
            print("You hit the hinge with the rock, both the hinge and the rock break.\nThe door of the closet falls off. You can see a key inside,\nyou pick it up.")
            inventory["hasRock"] = False
            inventory["hasKey"] = True
            return AdventureStart()
        if bm in [12, 13]:
            print("The closet is made of wood. As you try to open it\nyou notice that the hinge on the door is rusted in place.")
            return AdventureStart()
        else:
            print("Nothing happened.")
            return AdventureStart()

class BrownCorridor(State):
    options = encode([
        "look around",
    ])

    def runState(self):
        response = input("You are in a dimly lit corridor with dark brown walls, what do you do?\n> ")
        bm = best_match(self.options, encode(response))
        if bm == 0:
            print("In front of you...")
            return None
        else:
            print("work in progress")
            return None


def main():
    state = AdventureStart()
    while state:
        state = state.runState()

if __name__ == "__main__":
    main()
