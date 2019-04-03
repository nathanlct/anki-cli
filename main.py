import ankiconnect as ac

# name displayed at the start
APP_NAME = 'Anki CLI'

# whether or not to display the "Default" deck
HIDE_DEFAULT_DECK = True


def main():
    print '~~~~~ {} ~~~~~'.format(APP_NAME)

    print 'Syncing...'
    ac.invoke('sync')
    print 'Done\n'
    
    print 'Available decks:'

    deck_names = get_deck_names()
    decks = get_decks_data(deck_names)

    print_decks(decks)

    while True:
        print '\n>>>',
        cmd = str(raw_input())
        
        if cmd == 'help':
            print 'Available commands: help, quit, decks, update'

        elif cmd == 'quit':
            print 'Syncing...'
            ac.invoke('sync')
            print 'Done, quitting now.'
            return

        elif cmd == 'update':
            print 'Updating...'
            ac.invoke('sync')
            deck_names = get_deck_names()
            decks = get_decks_data(deck_names)
            print 'Done.'

        elif cmd == 'decks':
            print_decks(decks)

        else:
            print 'Unknown command, type \"help\" for more information.'
            
def get_deck_names():
    """
    Returns a list containing the names of all the decks
    """
    return ac.invoke('deckNames')

def get_cards_in_deck(deck_name):
    """
    Returns a list containing the IDs of all cards in deck `deck_name` 
    """
    card_ids = ac.invoke('findCards', query='deck:"{}"'.format(deck_name))  
    return card_ids

def print_decks(decks):
    """
    Prints some information about all the decks
    """
    n_cards = 0
    n_cards_due = 0

    for key in sorted(decks.keys()):
        print '\t' * key.count('.'),
        print '{} : {} ({} card{}, {} due)'.format(
            key, 
            decks[key]['name'], 
            decks[key]['n_cards'],
            '' if decks[key]['n_cards'] == 1 else 's',
            decks[key]['n_cards_due']
        )
        n_cards += decks[key]['n_cards']
        n_cards_due += decks[key]['n_cards_due']
    print 'Total: {} cards, {} due'.format(n_cards, n_cards_due)

def get_decks_data(deck_names):
    """
    Returns a dict containing information about all the decks whose names are in `deck_names`

    Structure of the dict:
        [custom_deck_id] => {
            'name': [deck name],
            'fullname': [entire deck name, including parent decks separed with '::'],
            'n_cards': [number of cards in the deck],
            'cards': [list containing the ids of all the cards in the deck],
            'n_cards_due': [number of due cards in the deck],
            'cards_due': [list containing the ids of all the due cards in the deck]
        }
    """
    decks = __get_decks_indexes(deck_names)

    for key in decks:
        cards = get_cards_in_deck(decks[key]['fullname'])
        due_filter = ac.invoke('areDue', cards=cards)
        cards_due = [i for (i, v) in zip(cards, due_filter) if v]
        decks[key]['n_cards'] = len(cards)
        decks[key]['cards'] = cards
        decks[key]['n_cards_due'] = len(cards_due)
        decks[key]['cards_due'] = cards_due

    return decks

def __get_decks_indexes(deck_names):
    """
    Returns a custom indexing of the decks whose names are in `deck_names`,
    and return the decks as a dict of the following form:

        [custom_deck_id] => {
            'name': [deck name],
            'fullname': [entire deck name, including parent decks separed with '::']
        }
    """
    deck_names.sort()

    indexes = {}
    current_index = 1

    i = 0
    while i < len(deck_names):
        deck = deck_names[i]

        if deck == 'Default' and HIDE_DEFAULT_DECK: 
            i += 1
            continue

        indexes[str(current_index)] = {'name': deck, 'fullname': deck}

        sub_decks_end = i + 1
        while sub_decks_end < len(deck_names) and deck_names[sub_decks_end].startswith(deck):
            sub_decks_end += 1
        sub_decks = deck_names[i+1:sub_decks_end]
        sub_decks = list(map(lambda s: s[len(deck)+2:], sub_decks))
        sub_decks_indexes = get_decks_indexes(sub_decks)
        for idx in sub_decks_indexes.keys():
            indexes[str(current_index) + '.' + idx] = {'name': sub_decks_indexes[idx]['name'], 'fullname': deck + '::' + sub_decks_indexes[idx]['fullname']}

        i = sub_decks_end
        current_index += 1

    return indexes


if __name__== '__main__':
    main()
