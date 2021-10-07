import os

from dotenv import load_dotenv
from client.TTBot import TTBot

if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("TOKEN")
    TTBot().run(TOKEN)