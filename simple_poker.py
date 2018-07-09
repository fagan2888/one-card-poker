import numpy as np
class Game:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    def resolve(self, pot_size):
        if self.p1.card < self.p2.card:
            self.p2.wealth += pot_size
        else:
            self.p1.wealth += pot_size
        print("{}'s card is {}".format(self.p1.name, self.p1.card))
        print("{}'s card is {}".format(self.p2.name, self.p2.card))

    def play_hand(self):
        x,y = np.random.choice(list(range(52)), size=2, replace=False)
        self.p1.card, self.p2.card = x, y
        self.p1.start = True
        self.p2.start = False

        # wealth prior to play
        w1, w2 = self.p1.wealth, self.p2.wealth

        pot_size = 2
        opponent_bet = 0


        for p in [self.p1, self.p2]:
            p.wealth -=  1

        p2_played = False

        while True:
            d1 = self.p1.decide(pot_size, opponent_bet)
            self.p1.start = None

            if d1 is None: # p1 folds
                self.p2.wealth += pot_size + opponent_bet
                print('{} folds'.format(self.p1.name))
                break
            elif d1 == 0 and p2_played: # p1 calls
                pot_size += 2 * opponent_bet
                self.resolve(pot_size)
                break
            elif d1 < 0: # p1 forced all in
                pot_size += 2 * opponent_bet + d1
                extra = pot_size - 2 * w1
                self.p2.wealth += extra
                pot_size = 2 * w1
                self.resolve(pot_size)
                break

            else: # p1 raises
                pot_size += 2 * opponent_bet
                opponent_bet = d1
                d2 = self.p2.decide(pot_size, opponent_bet)
                self.p2.start = None
                p2_played = True

                if d2 is None: # p2 folds
                    self.p1.wealth += pot_size + opponent_bet
                    print('{} folds'.format(self.p2.name))
                    break
                elif d2 == 0: # p2 calls
                    pot_size += 2 * opponent_bet
                    self.resolve(pot_size)
                    break
                elif d2 < 0: # p2 forced all-in
                    pot_size += 2 * opponent_bet + d2
                    extra = pot_size - 2 * w2
                    self.p1.wealth += extra
                    pot_size = 2 * w2
                    self.resolve(pot_size)
                    break
                else: # p2 raises
                    pot_size += 2 * opponent_bet
                    opponent_bet = d2


        # Game ends
        for p in [self.p1, self.p2]:
            p.card = None

        # Swap sequence of play
        self.p1, self.p2 = self.p2, self.p1

    def play_all(self):
        wealth_history = {self.p1.name : [], self.p2.name : []}
        while True:
            self.play_hand()
            wealth_history[self.p1.name].append(self.p1.wealth)
            wealth_history[self.p2.name].append(self.p2.wealth)

            if self.p1.wealth <= 0 or self.p2.wealth <= 0:
                return wealth_history

class Player:
    def __init__(self, name, wealth):
        self.name = name
        self.wealth = wealth
        self.card = None

    def decide(self, pot_size, opponent_bet):
        if self.card is None:
            raise ValueError

        decision = self.strategy(pot_size, opponent_bet)
        if decision is None and opponent_bet == 0:
            return 0
        elif decision is None:
            return decision
        elif self.wealth < decision + opponent_bet: # No wealth
            raise ValueError
        elif decision < 0 and self.wealth != decision + opponent_bet: # Wrong all-in
            raise ValueError
        else:
            self.wealth -= decision + opponent_bet
            return decision

    def strategy(self, pot_size, opponent_bet):
        pass

class HumanPlayer(Player):
    def strategy(self, pot_size, opponent_bet):
        print()
        print('Player: {}'.format(self.name))
        print('-'*10)
        if self.start is not None:
            if self.start:
                print("You're starting")
            else:
                print("Your opponent already started")
        print('Your card: {}'.format(self.card))
        print('Your wealth: {}'.format(self.wealth))
        print('Pot size: {}'.format(pot_size))
        print('Opponent bet: {}'.format(opponent_bet))
        decision = input('Your play (f/c/r):')
        if decision.lower() == 'f':
            return None
        elif decision.lower() == 'c':
            return min(self.wealth - opponent_bet, 0)
        else:
            while True:
                try:
                    raise_amount = int(input('Amount you wish to raise:'))
                    if raise_amount >= 0:
                        break
                except:
                    pass

            if self.wealth < opponent_bet:
                print('Cannot raise, assume all-in')
                return max(self.wealth - opponent_bet, 0)
            print('Raised {}'.format(min(self.wealth - opponent_bet, raise_amount)))
            return min(self.wealth - opponent_bet, raise_amount)



