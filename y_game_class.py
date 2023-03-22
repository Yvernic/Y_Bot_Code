import discord
import operator
import asyncio

class Game():
    def __init__(self, Rchannel, players, client):                  #creates an object
        self.client = client
        self.channel = Rchannel
        self.players = players  
        self.GAME_ONGOING = True
        self.ops = {
            "0": operator.add, 
            "1": operator.sub
            }                                               #assigns these variables
    
    async def end_game(self, winner, ongoing_games, game):
        # played - won
        # Uno - 2
        #Blackjack - 4
        with open("PLAYER_INFO.txt", "r") as file1:
            user_inv = file1.read()
        user_inv = user_inv.split("\n")                             #splits user_list into a list, separated by new lines
        for i in range(len(user_inv)):
            user_inv[i] = user_inv[i].split(" ") 
        for j in range(len(user_inv)):
            if str(user_inv[j][0]) == str(winner):
                k = j
                break
            else:
                continue
        temp = int(user_inv[k][1]) 
        temp += 100
        user_inv[k][1] = str(temp)

        for n in range(len(self.players)):
            for o in range(len(user_inv)):
                if str(user_inv[o][0]) == str(self.players[n]):
                    p = o
                    break
                else:
                    continue
            temp2 = int(user_inv[p][game]) 
            temp2 += 1
            user_inv[p][game] = str(temp2)
        
        temp3 = int(user_inv[k][game+1])
        temp3 += 1
        user_inv[k][game+1] = str(temp3)
        
        for m in range(len(user_inv)):
            user_inv[m] = " ".join(user_inv[m])
        user_inv = "\n".join(user_inv)

        with open("PLAYER_INFO.txt", "w") as file2:
            file2.write(user_inv)
        

        del ongoing_games[self.channel]


    async def early_end_game(self, ongoing_games):
        embed = discord.Embed(title="Game Cancellation", description="Are you sure you want to cancel the previous game?", color=0x00FFFF)
        view = discord.ui.View()
        cancel_button = Cancel_button(self.players, lambda: self.early_end_game2(ongoing_games))
        view.add_item(cancel_button)
        await self.channel.send(embed=embed, view=view)
    
    async def early_end_game2(self, ongoing_games):
        del ongoing_games[self.channel]
        await self.channel.send("This game has been cancelled \nNo rewards have been given out")


    async def get_user_details(self, user):
        new_user = await self.client.fetch_user(user) 
        return new_user 


class Cancel_button(discord.ui.Button):
    def __init__(self, players, func):
        super().__init__(label="Cancel Game", style=discord.ButtonStyle.red) #inherits this from the supperclass Button from discord library
        self.players = players
        self.func = func

    async def callback(self, interaction): 
        if str(interaction.user.id) in self.players:                                 #when the button is clicked...
            reply = "You have chosen to cancel the previous game"
            await interaction.response.edit_message(content=reply, view=None)   #...the message is edited...
            await self.func()
        else:
            await interaction.response.send_message("You are not playing the game, so you cannot cancel it", ephemeral=True)


'''players = [685586045370237004, 785397913882853396, 728150082570027048]
ongoing_games = {"5" : "fun"}
client = 3
new_game = Game("5", players, client)
winner=685586045370237004
newfeature = asyncio.get_event_loop().run_until_complete(new_game.end_game(winner, ongoing_games, 2))'''
