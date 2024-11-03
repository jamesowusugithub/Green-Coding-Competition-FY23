from card_elements import Card, Deck, Pile
from codecarbon import EmissionsTracker
import pprint
import random


pp = pprint.PrettyPrinter(indent=4)


with EmissionsTracker() as tracker:

    class Game:

        # x = "A"
        # y = "2"
        # z = "3"
        # a = "4"
        # b = "5"
        # c = "6"
        # d = "7"
        # e = "8"
        # f = "9"
        # g = "10"
        # h = "J"
        # i = "Q"
        # j = "K"

        color1 = "red"
        color2 = "black"

        sign1 = "diamonds"
        sign2 = "spades"
        sign3 = "hearts"
        sign4 = "clubs"


        values = ["A","2","3", "4", "5", "6", "7", "8", "9", 
                  "10", "J", "Q", "K"]
        colors = [color1, color2]
        signs = [sign1, sign2, sign3, sign4]
        list_of_values = values

                
    
        suits = { #keys are unicode symbols for suits
            u'\u2660': "black",
            u'\u2665': "red",
            u'\u2663': "black",
            u'\u2666': "red",
        }
    
        numPlayPiles = 7
    
        def __init__(self):
            self.list_of_cards = [Card(value, suit) for value in range(1, 14) for suit in ["Diamonds", "Hearts", "Clubs", "Spades"]]
            self.deck = Deck(self.list_of_values,self.suits)
            self.playPiles = []
            for i in range(self.numPlayPiles):
                thisPile = Pile()
                [thisPile.addCard(self.deck.takeFirstCard(flip=False)) for j in range(i+1)]
                thisPile.flipFirstCard()  
                self.playPiles.append(thisPile)
            self.blockPiles = {suit: Pile() for suit in self.suits}
            self.deck.cards[0].flip()

        def getGameElements(self):
            returnObject = {
                "deck": str(self.deck),
                "playPiles": [str(pile) for pile in self.playPiles],
                "blockPiles": {suit: str(pile) for suit, pile in self.blockPiles.items()}
            }
            return returnObject
        
        def checkCardOrder(self, higherCard, lowerCard):
            suitsDifferent = higherCard.suit != lowerCard.suit
            higher_index = self.list_of_values.index(higherCard.value)
            lower_index = self.list_of_values.index(lowerCard.value)
            valueConsecutive = higher_index - 1 == lower_index
            return suitsDifferent and valueConsecutive
        
        def checkIfCompleted(self):
            deck_empty = len(self.deck.cards) == 0
            piles_empty = all(len(pile.cards) == 0 for pile in self.playPiles)

            def is_in_order(cards):
                values = [card.value for card in cards]
                return values == self.list_of_values

            blocks_full_and_ordered = all(
                len(pile.cards) == 13 and is_in_order(pile.cards)
                for pile in self.blockPiles.values()
            )
            return deck_empty and piles_empty and blocks_full_and_ordered
        
        def print_deck_summary(self, ivalues, isuits):
            print("The cards in your deck are:")
            for value in ivalues:
                color_suit_combinations = [
            f"Color: {'red' if suit in ['hearts', 'diamonds'] else 'black'} Symbol: {suit}"
                for suit in isuits]
            print(f"Card: {value}", ", ".join(color_suit_combinations))
            

        def addToBlock(self, card):
            if card is None:
                return False
            elif len(self.blockPiles[card.suit].cards)>0:
                highest_value = self.blockPiles[card.suit].cards[0].value
                if self.list_of_values[self.list_of_values.index(highest_value)+1] == card.value:
                    self.blockPiles[card.suit].cards.insert(0,card)
                    return True
                else:
                    return False   
            else: 
                if card.value=="A":
                    self.blockPiles[card.suit].cards.insert(0,card)
                    return True
                else:
                    return False
        
        def takeTurn(self, verbose=False):
                
            #Pre: flip up unflipped pile end cards -> do this automatically
            [pile.cards[0].flip() for pile in self.playPiles if len(pile.cards)>0 and not pile.cards[0].flipped]
     
            #1: check if there are any play pile cards you can play to block piles
            for pile in self.playPiles:
                if len(pile.cards) > 0 and self.addToBlock(pile.cards[0]):
                    card_added = pile.cards.pop(0)
                    if verbose:
                        print("Adding play pile card to block: {0}".format(str(card_added)))
                    return True
                # else:
                #     print("Pile has cards")
                    #return False
    
    #2: check if cards in deck can be added
            if self.addToBlock(self.deck.getFirstCard()):
                card_added = self.deck.takeFirstCard()
                if verbose:
                    print("Adding card from deck to block: {0}".format(str(card_added)))
                return True
            
            #3: move kings to open piles
            for pile in self.playPiles:
                if len(pile.cards)==0: #pile has no cards
                    for pile2 in self.playPiles:
                        if len(pile2.cards)>1 and pile2.cards[0].value == "K":
                            card_added = pile2.cards.pop(0)
                            pile.addCard(card_added)
                            if verbose:
                                print("Moving {0} from Pile to Empty Pile".format(str(card_added)))
                            return True
                    
                    if self.deck.getFirstCard() is not None and self.deck.getFirstCard().value == "K":
                        card_added = self.deck.takeFirstCard()
                        pile.addCard(card_added)
                        if verbose:
                            print("Moving {0} from Deck to Empty Pile".format(str(card_added)))
                        return True
                # else:
                #     print("Pile has cards")
            
            #4: add drawn card to playPiles 
            for pile in self.playPiles:
                if len(pile.cards)>0 and self.deck.getFirstCard() is not None:
                    if self.checkCardOrder(pile.cards[0],self.deck.getFirstCard()):
                        card_added = self.deck.takeFirstCard()
                        pile.addCard(card_added) 
                        if verbose:
                            print("Moving {0} from Deck to Pile".format(str(card_added)))
                        return True
                # else:
                #     print("Pile has cards")
                            
            #5: move around cards in playPiles
            for pile1 in self.playPiles:
                pile1_flipped_cards = pile1.getFlippedCards()
                
                if not pile1_flipped_cards:
                    print("Pile has cards")
                    continue

                pile1_downcard_count = len(pile1.cards) - len(pile1_flipped_cards)

                for pile2 in self.playPiles:
                    if pile2 is pile1:
                        continue

                    pile2_flipped_cards = pile2.getFlippedCards()
                    
                    if not pile2_flipped_cards:
                        continue

                    pile2_downcard_count = len(pile2.cards) - len(pile2_flipped_cards)

                    for transfer_cards_size in range(1, len(pile1_flipped_cards) + 1):
                        cards_to_transfer = pile1_flipped_cards[:transfer_cards_size]

                        if not self.checkCardOrder(pile2.cards[0], cards_to_transfer[-1]):
                            continue

                        # Condition to prefer transferring cards to pile with fewer downcards
                        if pile2_downcard_count < pile1_downcard_count or (pile1_downcard_count == 0 and len(cards_to_transfer) == len(pile1.cards)):
                            # Move the cards
                            pile2.cards[:0] = reversed(cards_to_transfer)
                            pile1.cards = pile1.cards[transfer_cards_size:]

                            if verbose:
                                print(f"Moved {transfer_cards_size} cards between piles: {', '.join(str(card) for card in cards_to_transfer)}")
                            return True

            return False

        
                    
        def simulate(self, verbose=True):
            while True:
                move_made = self.takeTurn(verbose=verbose)
                if not move_made:
                    if len(self.deck.cards) > 0:
                        currentCard = self.deck.cards[0]
                        if currentCard in self.deck.cache:
                            if verbose:
                                print("No more moves left!")
                            break
                        else:
                            self.deck.drawCard()
                            if verbose:
                                print("Drawing new card: {0}".format(str(currentCard)))
                            self.deck.cache.append(currentCard)
                    else:
                        if verbose:
                            print("No more moves left!")
                        break


    # Define a custom key to sort by suit and then by value rank
        def timsort(self):

            sorted_cards = sorted(self.deck.cards, key=lambda card: (card.suit, self.list_of_values.index(card.value)))
            self.deck.cards = sorted_cards
            print("Sorted Cards:")
            for card in sorted_cards:
                print(card)

    def main():
        thisGame = Game()
        thisGame.simulate(verbose=True)
        
        thisGame.print_deck_summary(thisGame.values, thisGame.suits)
        
        print()
        pp.pprint(thisGame.getGameElements())
        print()
        
        if thisGame.checkIfCompleted():
            print("Congrats! You won!")
        else:
            print("Sorry, you did not win")
        
        thisGame.timsort()
        print("Sorted cards:")
        for card in thisGame.deck.cards:
            print(card)
        return

    main()
