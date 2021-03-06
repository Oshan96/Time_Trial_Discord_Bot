import requests


class AlbionService:

    def __init__(self, guild_id, alliance_id):
        self.base_url = "https://gameinfo.albiononline.com/api/gameinfo/"
        self.guild_id = guild_id
        self.alliance_id = alliance_id

    def get(self, url):
        return requests.get(url)

    def search_query(self, query):
        query_url = self.base_url + "search?q=" + str(query)
        response = self.get(query_url)
        return response

    def check_user_guild(self, username):
        user_response = self.search_query(username)
        if user_response.status_code == 200:
            user_response = user_response.json()
            for player in user_response["players"]:
                if player["Name"].lower() == username.lower():
                    return {
                        "id": player["Id"],
                        "player_name": player["Name"],
                        "guild_id": player["GuildId"],
                        "guild_name": player["GuildName"],
                        "alliance_id": player["AllianceId"]
                    }
        else:
            print("check_user_guild:", username, ": status code:", str(user_response.status_code))

        return None

    def get_members(self):
        url = self.base_url + "guilds/" + self.guild_id + "/members"
        response = self.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("get_members: status code:", str(response.status_code))

        return None
