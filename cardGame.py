#-*-coding: utf-8 -*-
#author:tyhj
#card.py 2017.11.15 11:56
import random
import pandas as pd
import time
import matplotlib.pyplot as plt

class Card:
    '''Represent a standard playing Card.'''

    rank_names=[None,'Ace','2','3','4','5','6','7','8','9',
                '10','Jack','Queen','King']
    suit_names = ['Clubs', 'Diamonds', 'Hearts', 'Spades']

    def __init__(self,rank,suit):
        self.rank=rank
        self.suit = suit

    def __str__(self):
        return '%s of %s'%(Card.rank_names[self.rank],
                           Card.suit_names[self.suit])

    #comparing cards,less than
    def __lt__(self,other):
        #check the suits
        t1=self.rank,self.suit
        t2=other.rank,other.suit
        return t1<t2

    def __gt__(self, other):
        if self<other:
            return False
        else:
            return True

    def is_gong(self):
        if self.rank in [11,12,13]:
            return True
        else:
            return False

class Deck:
    def __init__(self):
        self.cards=[]
        for rank in range(1,14):
            for suit in range(4):
                card=Card(rank,suit)
                self.cards.append(card)

        self.shuffle()

    def __str__(self):
        res=[]
        for card in self.cards:
            res.append(str(card))
        return '\n'.join(res)

    def shuffle(self):
        random.shuffle(self.cards)

    def __len__(self):
        return len(self.cards)

    def pop_card(self):
        return self.cards.pop()

    def add_card(self,card):
        self.cards.append(card)

    def move_cards(self,hand,num):
        for i in range(num):
            hand.add_card(self.pop_card())


class Hand(Deck):
    '''represents a hand of playing cards.'''

    def __init__(self):
        self.cards=[]

    def maxium(self):
        '''get the best maxium'''
        m=self.cards[0]
        for card in self.cards:
            if card>m:
                m=card
        return card

    def is_sanGong(self):
        for card in self.cards:
            if not card.is_gong():
                return False
        return True

    def count(self):
        total=0
        for card in self.cards:
            if card.rank not in [10,11,12,13]:
                total+=card.rank
        return total%10

    def is_malong(self):
        if (not self.is_sanGong()) and self.count()==0:
            return True
        else:
            return False

    def __lt__(self, other):
        #both hand and other are sanGong
        if self.is_sanGong() and other.is_sanGong():
            return self.maxium()<other.maxium()
        #hand is sanGong and other is not sanGong
        elif self.is_sanGong() and not other.is_sanGong():
            return False
        #hand is not sanGong and other is sanGong
        elif not self.is_sanGong() and other.is_sanGong():
            return True
        #both hand and other are not sanGong,compare the counts
        else:
            #two counts are equal,compare the maxium
            if self.count()==other.count():
                return self.maxium()<other.maxium()
            #two counts are not equal,compare the counts
            else:
                return self.count()<other.count()

    def __gt__(self, other):
        if self<other:
            return False
        else:
            return True

    def clear(self):
        self.cards=[]

class Player:
    def __init__(self,name,money=100):
        self.name=name
        self.money=money
        self.hand=Hand()
        self.hand_history=[]
        self.money_history=[]

    def clear_hand(self):
        self.hand.clear()

class Casino:
    def __init__(self,playersNumber=3,ratio=0.04,times=500):
        self.commission=Player('commission',money=0)
        self.bank=Player('bank',money=500)
        self.players=[Player('player%s'%i,100) for i in range(playersNumber)]
        self.ratio=ratio
        self.times=times

    #allocate pokers
    def allocate(self):
        #before allocate new pokers,clear the hands
        self.bank.clear_hand()
        for player in self.players:
            player.clear_hand()

        deck=Deck()#Initialize a new deck
        deck.move_cards(self.bank.hand,3)
        for player in self.players:
            deck.move_cards(player.hand,3)

    #calculte the profit and loss
    def update(self):
        #bank.hand is malong
        if self.bank.hand.is_malong():
            for player in self.players:
                #bank.hand is less than player
                if self.bank.hand<player.hand:
                    # This is the margin of the bank
                    self.bank.money-=0.5
                    player.money+=0.5
                else:
                    self.bank.money+=1*(1-self.ratio)
                    self.commission.money+=1*self.ratio
                    player.money-=1
        else:
            for player in self.players:
                if self.bank.hand<player.hand:
                    self.bank.money-=1
                    player.money+=1
                else:
                    self.bank.money+=1*(1-self.ratio)
                    self.commission.money+=1*self.ratio
                    player.money-=1

    def record(self):
        self.commission.money_history.append(self.commission.money)
        self.bank.hand_history.append(str(self.bank.hand))
        self.bank.money_history.append(self.bank.money)

        for player in self.players:
            player.hand_history.append(str(player.hand))
            player.money_history.append(player.money)

    def run(self):
        for i in xrange(self.times):
            self.allocate()
            self.update()
            self.record()

def simulate(n=1000,playersNumber=3,ratio=0.04,times=500):
    df=pd.DataFrame()
    for i in xrange(n):
        casino=Casino(playersNumber,ratio,times)
        casino.run()
        df.loc[i,'commission']=casino.commission.money
        df.loc[i,'bank']=casino.bank.money
        for j,player in enumerate(casino.players):
            df.loc[i,'player%s'%j]=player.money

    describe=df.describe()
    describe.to_csv(r'e:\aa\describe\%s_%s_%s_%s.csv'%(n,playersNumber,ratio,times))



if __name__=='__main__':
    simulate()





