import requests
import json
from dotenv import load_dotenv
import os
from pathlib import Path

# NOTE:
# You need to create a "MALlists.env" file in the same directory as this py script
# the .env should have MAL_USER=yourusername (note the lack of quotes)
dotenv_path = Path('MALlists.env')
load_dotenv(dotenv_path=dotenv_path)
MAL_user = os.getenv('MAL_USER')

CR_URL = f"https://myanimelist.net/mangalist/{MAL_user}/load.json?status=1&offset=0"
COMPL_URL = f"https://myanimelist.net/mangalist/{MAL_user}/load.json?status=2&offset=0"
PTR_URL = f"https://myanimelist.net/mangalist/{MAL_user}/load.json?status=6&offset=0"

#Alternatively, you can uncomment this part and put your username in the MAL_user variable

# MAL_user = "username"
# CR_URL = f"https://myanimelist.net/mangalist/{MAL_user}/load.json?status=1&offset=0"
# COMPL_URL = f"https://myanimelist.net/mangalist/{MAL_user}/load.json?status=2&offset=0"
# PTR_URL = f"https://myanimelist.net/mangalist/{MAL_user}/load.json?status=6&offset=0"

def main():
    print(MAL_user)
    curr_read()
    completed()
    ptr()

def curr_read():
    curr_read = requests.get(CR_URL)
    data = curr_read.json()
    with open("MALlists/curr_read.json","w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def completed():
    completed = requests.get(COMPL_URL)
    data = completed.json()
    with open("MALlists/completed.json","w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def ptr():
    ptr = requests.get(PTR_URL)
    data = ptr.json()
    with open("MALlists/ptr.json","w") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()