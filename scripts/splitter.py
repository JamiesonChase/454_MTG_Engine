import json


def main():
    with open('results.json', 'r') as f:
        results = json.load(f)

    decks = []
    for result in results:
        deck = {}
        main = []
        sideboard = []

        for key, value in result.items():
            reading_sideboard = False
            if key == 'url':
                deck['url'] = value

            elif key == 'text':
                lines = value.split('\r\n')

                for line in lines:
                    if len(line) == 0:
                        continue
                    if line == 'Sideboard':
                        reading_sideboard = True
                    else:
                        parts = line.split()
                        cnt = parts[0]
                        name = ' '.join(parts[1:])

                    card = { "count": cnt, "name": name }
                    main.append(card)
                    if reading_sideboard:
                        sideboard.append(card)

                deck['main'] = main
                if reading_sideboard:
                    deck['sideboard'] = sideboard
                        
        decks.append(deck)
    
    with open('../data/decks.json', 'w') as f:
        json.dump(decks, f, indent=4)


if __name__ == '__main__':
    main()