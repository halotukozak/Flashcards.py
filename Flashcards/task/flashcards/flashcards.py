import random
import sys


class LoggerOut:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.filename = filename

    def write(self, message):
        self.terminal.write(message)
        with open(self.filename, "a") as file:
            print(message, file=file, flush=True, end='')

    def flush(self):
        pass


class LoggerIn:
    def __init__(self, filename):
        self.terminal = sys.stdin
        self.filename = filename

    def readline(self):
        entry = self.terminal.readline()
        with open(self.filename, "a") as file:
            print(entry.rstrip(), file=file, flush=True)
        return entry


default_log = 'default.txt'
sys.stdout = LoggerOut(default_log)
sys.stdin = LoggerIn(default_log)


class Card:
    number_of_cards = 0
    all = []
    stats = {}

    def __init__(self, term, definition):
        self.term = term
        self.definition = definition
        Card.all.append(self)

    @classmethod
    def term_exists(cls, term):
        return term in map(lambda x: x.term, Card.all)

    @classmethod
    def definition_exists(cls, definition):
        return definition in map(lambda x: x.definition, Card.all)

    @classmethod
    def remove_card(cls, term):
        card_to_delete = Card.get_card_by_term(term)
        Card.all.remove(card_to_delete)

    @classmethod
    def get_card_by_term(cls, term):
        return [card for card in Card.all if card.term == term][0]

    @classmethod
    def get_card_by_definition(cls, definition):
        return [card for card in Card.all if card.definition == definition][0]

    @classmethod
    def get_random_cards(cls, n=1):
        return random.choices(Card.all, k=n)

    @classmethod
    def reset_stats(cls):
        Card.stats.clear()

    @classmethod
    def get_hardest_cards(cls):
        if not Card.stats:
            return [], 0
        max_number_of_mistakes = max(Card.stats.values())
        hardest_cards = []
        for term, number_of_mistakes in Card.stats.items():
            if number_of_mistakes > max_number_of_mistakes:
                max_number_of_mistakes = number_of_mistakes
                hardest_cards.clear()
                hardest_cards.append(term)
            elif number_of_mistakes == max_number_of_mistakes:
                hardest_cards.append(term)
        return hardest_cards, max_number_of_mistakes

    def inc_mistakes(self):
        if self.term in Card.stats:
            Card.stats[self.term] += 1
        else:
            Card.stats[self.term] = 1

    def number_of_mistakes(self):
        try:
            return Card.stats[self.term]
        except KeyError:
            return 0


def add_card():
    term = input(f"The card:\n")
    while Card.term_exists(term):
        term = input(f'The card "{term}" already exists. Try again:\n')
    definition = input(f"The definition of the card:\n")
    while Card.definition_exists(definition):
        definition = input(f'The definition "{definition}" already exists. Try again:\n')
    Card(term, definition)
    print(f'The pair ("{term}":"{definition}") has been added.')


def remove_card():
    term = input("which card?\n")
    try:
        Card.remove_card(term)
        print("The card has been removed.")
    except IndexError:
        print(f"Can't remove \"{term}\": there is no such card.")


def import_cards(file_name):
    try:
        with open(file_name, "r") as file:
            n = 0
            for line in file.readlines():
                term, definition, number_of_mistakes = line.strip().split(":")
                Card(term, definition)
                Card.stats[term] = int(number_of_mistakes)
                n += 1
            print(f"{n} cards have been loaded.")
    except FileNotFoundError:
        print("File not found.")


def export_cards(file_name):
    try:
        with open(file_name, "w") as file:
            for card in Card.all:
                print(card.term, card.definition, card.number_of_mistakes(), sep=":", end="\n", file=file)
                print(f"{len(Card.all)} cards have been saved.")
    except FileNotFoundError:
        print("File not found.")


def ask_for_card(term, definition):
    answer = input(f'Print the definition of "{term}"\n')

    if answer == definition:
        print("Correct!")
    elif Card.definition_exists(answer):
        correct_card = Card.get_card_by_definition(answer)
        print(f'Wrong. The right answer is "{definition}", but your definition is correct for "{correct_card.term}".')
    else:
        print(f'Wrong. The right answer is "{definition}".')
    return answer == definition


def ask():
    n = int(input("How many times to ask?\n"))
    chosen_cards = Card.get_random_cards(n)
    for card in chosen_cards:
        result = ask_for_card(card.term, card.definition)
        if result is False:
            card.inc_mistakes()


def ask_for_log():
    file_name = input("File name:\n")
    logging_text = open(default_log, "r").read()
    file = open(file_name, "w")
    file.write(logging_text)
    file.close()
    print("The log has been saved.")


def show_hardest_card():
    hardest_cards, max_number_of_mistakes = Card.get_hardest_cards()
    if max_number_of_mistakes == 0:
        print("There are no cards with errors.")
    elif len(hardest_cards) == 1:
        print(
            f'The hardest card is "{", ".join(hardest_cards)}". You have {max_number_of_mistakes} errors answering it.')
    else:
        print(
            'The hardest cards are "{0}". You have {1} errors answering them.'.format(
                '", "'.join(hardest_cards), max_number_of_mistakes))


def reset_stats():
    Card.reset_stats()
    print("Card statistics have been reset.")


def run():
    while True:
        action = input("Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):\n")
        if action == "ask":
            ask()
        elif action == "add":
            add_card()
        elif action == "remove":
            remove_card()
        elif action == "import":
            file_name = input("File name:\n")
            import_cards(file_name)
        elif action == "export":
            file_name = input("File name:\n")
            export_cards(file_name)
        elif action == "log":
            ask_for_log()
        elif action == "hardest card":
            show_hardest_card()
        elif action == "reset stats":
            reset_stats()
        elif action == "exit":
            print("Bye bye!")
            break


export_file = ""
for arg in sys.argv[1:]:
    try:
        command, argument = arg.split("=")
        if command == "--import_from":
            import_cards(argument)
        elif command == "--export_to":
            export_file = argument
    except Exception as e:
        print("Unknown argument:", e)

run()

if export_file:
    export_cards(export_file)
