import discord
import y_uno_classes
#the libraries used are above

intents = discord.Intents.default()   #this sets "intents" to its default value 
intents.message_content = True        #intents is a parameter taken by the client class to determine...
                                      #...what commands and events the discord bot will have access to 

client = discord.Client(intents=intents) #defines client as an object from the client class, from the discord library

ONGOING_GAMES = {}


@client.event  #informs the program to look out for this event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))  #outputs this into the shell window for only me to see

@client.event
async def on_message(message): #runs whenever a message is sent
    global ONGOING_GAMES
    
    if message.author == client.user: #if the message is sent by the bot, it ignores it
        return

    if message.content == "y!hello":  #if the message is this, the bot will reply
        await message.channel.send("Hi there!")

    if message.content == "y!register":           #runs if y!register" was messaged
        user_id = str(message.author.id)          #gets the user id of the user who sent the message
        await player_register(user_id, message.channel)  #pauses the on_message event to run the player_register event

    if message.content.startswith("y!inventory"):                           #if the message starts with y!inventory, this is run
        if message.content == "y!inventory":                                #if the message is only y!inventory...
            await view_inventory(str(message.author.id), message.channel)   #...the user that send the message has their inventory returned
        else:
            if len(message.content) <= 32:                                  #checks that the message is long enough to have a user id included...
                await message.channel.send("User is not recognised")        #...if not, an error message is sent
            else:                                                            
                user_id = str(message.content[14:-1])                       #the part including the user id is taken out of the message...
                await view_inventory(user_id, message.channel)              #and sent to the view_inventory function

    if message.content.startswith("y!statistics"):                           #if the message starts with y!statistics, this is run
        if message.content == "y!statistics":                                #if the message is only y!statistics...
            await view_statistics(str(message.author.id), message.channel)   #...the user that send the message has their stats returned
        else:
            if len(message.content) <= 33:                                  #checks that the message is long enough to have a user id included...
                await message.channel.send("User is not recognised")        #...if not, an error message is sent
            else:                                                            
                user_id = str(message.content[15:-1])                       #the part including the user id is taken out of the message...
                await view_statistics(user_id, message.channel)

    if message.content.startswith("y!help"):         #runs when y!help is typed
        await view_help(message.channel)

    if message.content.startswith("y!startgame"):    #runs when a message starts with y!startgame
        if message.channel in ONGOING_GAMES.keys():
            await message.channel.send("There is already a game ongoing")
        else:
            if message.content == "y!startgame":
                await message.channel.send("You need to mention the users you want to play with to use this command")  #if the message is sent by itself, a reminder is sent to the user of how to use this command
            else:
                msg = message.content.split(" ")         #saves the message in a variable, and splits the variable into a list separated by the spaces in the message
                msg = msg[1:]                         #cuts the first item off the list (this stores the y!startgame section of the message)
                for i in range(len(msg)):
                    msg[i] = msg[i][2:-1]             #trims each item in the list to make sure that only the user ID is kept
                msg.append(str(message.author.id))
                if len(msg) <= 4:
                    await player_check(msg, message.channel) #then runs this function, after adding the original users ID
                else:
                    await message.channel.send("Thats too many players \nOnly a maximum of 4 can play, including yourself")

    if message.content == "y!cancel":
        await cancel_game(message.channel)

    


@client.event
async def player_register(user_id, Rchannel):
    registered_users = open("Discord Bot/PLAYER_INFO.txt", "r")     #opens the PLAYER_INFO text file in read mode
    user_list = registered_users.read()                             #stores the contents of the file into a variable
    registered_users.close()                                        #closes the file
    user_list = user_list.split("\n")                               #splits user_list into a list, separated by new lines
    for i in range(len(user_list)):
        info = user_list[i].split(" ")                              #takes only the first item of PLAYER INFO and adds it to player list
        user_list[i] = info[0]
    if user_id in user_list:                                      
        await Rchannel.send("You are already registered")                   #sends a message to the channel the original message was send in
    else:
        registered_users = open("Discord Bot/PLAYER_INFO.txt", "a")         #opens the file in append mode
        registered_users.write("\n" + user_id + " 0 0 0 0 0")               #adds a new line followed by the user's ID [and zeros for their inventory and stats]
        registered_users.close()                                            #closes the file
        await Rchannel.send("You have been registered")                     #sends a confirmation message


@client.event
async def view_inventory(user_id, Rchannel):
    registered_users = open("Discord Bot/PLAYER_INFO.txt", "r")             #opens the PLAYER_INFO text file in read mode
    user_inv = registered_users.read()                          #stores the contents of the file into a variable
    registered_users.close()                                    #closes the file
    user_inv = user_inv.split("\n")                             #splits user_list into a list, separated by new lines
    for i in range(len(user_inv)):
        user_inv[i] = user_inv[i].split(" ")                    #splits each line in user_inv into the user id and the inventory
    for i in user_inv:
        if user_id == i[0]:
            user_mention = "<@" + user_id + ">"
            embed1 = discord.Embed(title="Inventory", description=(user_mention + "'s Inventory"), color=0x00FFFF)    #creates the embed
            embed1.add_field(name=(str(i[1]) + " tokens"), value="", inline = False)
            await Rchannel.send(embed=embed1)        #checks each registered user and if found send this message
            return
    await Rchannel.send("User not found or is not registered")  #if user is not found then this message is sent instead
        

@client.event
async def view_statistics(user_id, Rchannel):
    registered_users = open("Discord Bot/PLAYER_INFO.txt", "r")             #opens the PLAYER_INFO text file in read mode
    user_sta = registered_users.read()                          #stores the contents of the file into a variable
    registered_users.close()                                    #closes the file
    user_sta = user_sta.split("\n")                             #splits user_sta into a list, separated by new lines
    for i in range(len(user_sta)):
        user_sta[i] = user_sta[i].split(" ")                    #splits each line in user_sta into the user id and the inventory
    for i in user_sta:
        if user_id == i[0]:
            user_mention = "<@" + user_id + ">"                 #creates the user_mention message
            embed1 = discord.Embed(title="Statistics", description=(user_mention + "'s Statistics"), color=0x00FFFF)    #creates the embed
            if i[2] != "0":
                UWinrate = int(i[3]) / int(i[2])            #calculates the Uno game win rate
                UWinrate = round((UWinrate *100), 4)
            else:
                UWinrate = 0
            if i[4] != "0":
                BWinrate = int(i[5]) / int(i[4])            #calculates the Blackjack game win rate
                BWinrate = round((BWinrate*100), 4)
            else:
                BWinrate = 0
            if int(i[2]) + int(i[4]) != 0:                  #calculates the total win rate
                tWinrate = (int(i[3]) + int(i[5])) / (int(i[2]) + int(i[4]))
                tWinrate = round((tWinrate * 100), 4)
            else:
                tWinrate = 0
            Ureply = str(i[2]) + " Uno games played\n" + str(i[3]) + " Uno games won\n" + str(UWinrate) + "% Win rate\n"
            Breply = str(i[4]) + " Blackjack games played\n" + str(i[5]) + " Blackjack games won\n" + str(BWinrate) + "% Win rate\n"
            Treply = str(int(i[2]) + int(i[4])) + " Total games played\n" + str(int(i[3]) + int(i[5])) + " Total games won\n" + str(tWinrate) + "% Total win rate\n"     #creates the reply message over 3 lines and combines them
            embed1.add_field(name="Uno Statistics", value=Ureply, inline = False)
            embed1.add_field(name="Blackjack Statistics", value=Breply, inline = False)
            embed1.add_field(name="Overall stats", value=Treply, inline = False)                     #adds fields to the embed including the statistics
            await Rchannel.send(embed=embed1)                                                       #checks each registered user and if found send this message
            return
    await Rchannel.send("User not found or is not registered")


@client.event
async def view_help(Rchannel):
    help_doc = open("Discord Bot/help.txt", "r")      #opens the help.txt file...
    help_message = help_doc.read()        #...copies the content to a variable...
    help_doc.close()                       #...and closes the file  
    help_message = help_message.split("\n")
    desc = "Below are all commands from Y-Bot, and what they do"
    embed2 = discord.Embed(title="Y-Bot commands", description=desc, color=0x00FFFF)    #creates an embed
    for i in range(0, len(help_message), 2):
        embed2.add_field(name=help_message[i], value=help_message[i+1], inline = False)  #adds a field for every other item in the help_message list...
    await Rchannel.send(embed=embed2)                                                    #with the name being the first item and the description being the second item


@client.event
async def player_check(players, Rchannel):
    registered_users = open("Discord Bot/PLAYER_INFO.txt", "r")   #opens the PLAYER_INFO text file, and checks if...
    user_list = registered_users.read()               #...the user sending the message is registered...
    registered_users.close()                          #taken from the player_register function
    user_list = user_list.split("\n")
    for i in range(len(user_list)):
        info = user_list[i].split(" ")
        user_list[i] = info[0]
    for i in players:
        if i in user_list:      #checks the players are in the list...
            continue
        else:
            message = "<@" + i + "> is not registered, they cannot play yet\nTo register, use y!register"
            await Rchannel.send(message)               #...and sends a message that mentions the unregistered player if there is one...
            return
    await game_choice(players, Rchannel)               #...otherwise this function is run


#defines a view that will give me a select button
class GS_Button(discord.ui.Button):
    def __init__(self, name, func):
        super().__init__(label=name, style=discord.ButtonStyle.blurple, disabled=False) #inherits this from the supperclass Button from discord library
        self.func = func

    async def callback(self, interaction):                                  #when the button is clicked...
        reply = self.label + " has been chosen"
        await interaction.response.edit_message(content=reply, view=None)   #...the message is edited...
        await self.func()                                                   #...and this function is run

    
@client.event
async def game_choice(players, Rchannel):
    embed3 = discord.Embed(title="Game Set-up", description="Click one of the buttons below to select a game to play", color=0x00FFFF) #creates the embed
    embed3.add_field(name="Uno", value="A card game for up to 4 players where you aim to get rid of all your cards by \
by matching their colours or values to the currently face up card", inline = False)                                                    #adds a field describing the uno game
    embed3.add_field(name="Blackjack", value="A card game where you aim to beat the dealer's total. Just \
make sure you don't go above a score of 21 or you will bust", inline = False)                                                          #adds a field describing the blackjack game
    Uno_button = GS_Button("Uno", lambda: Uno(players, Rchannel))                     #creates the Uno button
    Blackjack_button = GS_Button("Blackjack", lambda: Blackjack(players, Rchannel))   #creates the Blackjack button
    view = discord.ui.View()                      #creates a view
    view.add_item(Uno_button)
    view.add_item(Blackjack_button)               #adds the uno and blackjack buttons to the view
    await Rchannel.send(embed=embed3, view=view)  #sends the embedded message with the buttons attached


@client.event
async def cancel_game(Rchannel):
    global ONGOING_GAMES                                            #gets the global variaable
    if Rchannel in ONGOING_GAMES.keys():
        await ONGOING_GAMES[Rchannel].early_end_game(ONGOING_GAMES) 
    else: 
        await Rchannel.send("There is no ongoing game currently")   #if there isn't a game going on, this message is sent...                         


@client.event
async def Uno(players, Rchannel):
    global ONGOING_GAMES
    new_game = y_uno_classes.UnoGame(Rchannel, players, client)
    ONGOING_GAMES[Rchannel] = new_game
    await new_game.U_set_up(ONGOING_GAMES)

@client.event
async def Blackjack(players, Rchannel):
    await Rchannel.send("Blackjack will be coming soon")




client.run("ODM2MjU3OTE2NjI1MDkyNjU4.GyHwGa.PBkSgKznug2cu5wwMU6fLI1pUSVwirkB9Txjg0") #the unique token for the Discord bot user