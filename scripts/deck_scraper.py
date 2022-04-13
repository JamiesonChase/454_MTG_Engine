import json
import requests
import time



def main():
    base_url = 'https://old.starcitygames.com/assets/deck-files/'
    ext = '-MODO.txt'

    decks = []
    for i in range(11300, 11500):
        time.sleep(0.05)
        url = f'{base_url}{i}{ext}'
        res = requests.get(url)
        if res.status_code != 200:
            print(res.status_code)
            continue
        decks.append({
            "url": url,
            "text": res.text
        })
    
    with open('results.json', 'w') as f:
        json.dump(decks, f, indent=4)



if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    print(f'Execution time: {round(end_time-start_time, 3)} seconds')