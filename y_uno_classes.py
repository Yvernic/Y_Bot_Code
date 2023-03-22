import discord
import random
from PIL import Image, ImageOps
from io import BytesIO
import y_game_class

class UnoGame(y_game_class.Game):                                            #a subclass of Game
    def __init__(self, Rchannel, players, client):                      #initialises a new object from this class
        super().__init__(Rchannel=Rchannel, players=players, client=client)    #starts the same way as the Game class
        self.cards = []
        self.player_info = {}
        self.current_card = ""
        self.turn = -1
        self.skipped = False
        self.reverse = False
        self.cards_added = 0                                    #all variables to be used in this game, with their starting values

    
    async def U_set_up(self, ongoing_games):                                   #sets up the game
        self.cards = self.U_generate_cards()                    #generates the cards
        random.shuffle(self.players)                            #shuffles the order of players
        self.player_info = self.U_generate_player_hands()       #gives each player their hand, and stores them in player_info
        await self.U_send_user_msgs()                           #sends each player their hand
        self.current_card = self.U_generate_first_card()        #creates the first card
        await self.U_send_game_board("", self.channel)                        #sends the board state to the channel
        self.turn += 1                                          #resets the turn to 0
        await self.U_play(ongoing_games)                                     #begins the game
    
    def U_generate_cards(self):                                 #function to create the cards
        Red = []
        Blue = []
        Green = []
        Yellow = []                                             #temporary lists
        COLOURS = ["r", "g", "b", "y"]
        cards = [Red, Green, Blue, Yellow]                      #the list of all cards
        for a in range(0, 4):
            for b in range(0, 14):
                colour = COLOURS[a]
                if b in range(0, 10):
                    card = colour + str(b)                      #generates the number cards (0-9)
                elif b == 10:
                    card = colour + "Reverse"                         #r for reverse
                elif b == 11:
                    card = colour + "Skip"                         #s for skip
                elif b == 12:
                    card = colour + "+2"                        #+2 for a draw 2 card
                else:
                    if a == 1 or a == 2:                        #wild cards are twice as likely to be drawn than other cards.
                        card = "Wild"
                    else:
                        card = "+4"
                if a == 0:
                    Red.append(card)
                elif a == 1:
                    Green.append(card)
                elif a == 2:
                    Blue.append(card)
                else:
                    Yellow.append(card)                         #creates the cards using iteration, and adds them to the list
        return cards
    
    def U_generate_player_hands(self):                          #gives each player their hands
        PLAYER_HANDS = {}
        for i in range(len(self.players)):
            hand = []
            for j in range(7):
                colour = random.randint(0, 3)                   #chooses a random colour...
                action = random.randint(0, 13)                  #...and action for a card 
                card = self.cards[colour][action]               #gets the randomly generated card...
                hand.append(card)                               #...and adds it to the players hand
            PLAYER_HANDS[str(i)] = [self.players[i], hand]      #adds this player hand to the dictionary
        return PLAYER_HANDS                                     #returns the dictionary
    
    def U_generate_first_card(self):
        colour = random.randint(0, 3)
        action = random.randint(0, 9)
        card = self.cards[colour][action]                       #randomly generates the first card
        return card
    
    def U_create_user_msgs(self, hand):
        width = int(len(hand))*534                              #finds out the width the image needs to be
        new = Image.new("RGBA", (width, 800))                   #creates a new coloured but blank image 
        hand2 = []
        for i in range(len(hand)):
            temp = hand[i] + ".png"                             #creates a new list for storing the card images in the hand 
            hand2.append(temp)
        for i in range(len(hand)):
            path = r"Images\Uno cards\\" + hand2[i]
            img = Image.open(path)                              #finds the image of the specific card...
            new.paste(img, (534*i, 0))                          #...and adds it to the new image
        return new
    
    async def U_send_user_msgs(self):
        for i in range(len(self.players)):
            with BytesIO() as image_binary:
                mention = "<@" + self.players[i] + ">"                                                  #creates the player mention message
                self.U_create_user_msgs(self.player_info[str(i)][1]).save(image_binary, "PNG")          #creates an image of a players hand
                image_binary.seek(0)
                reply = (mention + "'s hand: ")                                                         #the reply message
                user = await super().get_user_details(int(self.player_info[str(i)][0]))                      #gets the user to message
                embed4 = discord.Embed(title="Your hand:", description=reply, color=0x00FFFF)
                embed4.set_image(url="attachment://image.png")
                await user.send(file=discord.File(fp=image_binary, filename="image.png"), embed=embed4) #sends the reply with the image attached
    
    def U_create_game_board(self):
        new = Image.new("RGBA", (5535, 3400))
        path = r"Images\Uno cards\\"
        if self.reverse == False:
            r_path = path + "Rd1.png"
        else:
            r_path = path + "Rd2.png"
        cc_path = path + self.current_card + ".png"
        imgb = Image.open(r_path)
        imgbr = imgb.resize((5535, 3400))
        new.paste(imgbr, (0, 0))
        imgc = Image.open(cc_path)
        new.paste(imgc, (2502, 1300))
        for i in range(len(self.player_info)):
            if i % 2 == 0:
                new2 = Image.new("RGBA", (800, 3204))
                rot = 90
            else:
                new2 = Image.new("RGBA", (3204, 800))
                rot = 0
            for j in range(len(self.player_info[str(i)][1])):
                new_path = path + "uno_back.png"
                img = Image.open(new_path)
                if i % 2 == 0:
                    img2 = img.rotate(angle=rot, expand=1)
                separator = 3204/len(self.player_info[str(i)][1])
                if i % 2 == 0:
                    new2.paste(img2, (0,(0+(int(separator)*(j)))))
                else:
                    new2.paste(img, ((0+(int(separator)*(j))),0))
            if i == self.turn:
                if self.skipped == False:
                    colour = "yellow"
                else:
                    colour = "red"
                new2 = ImageOps.expand(new2, border=50, fill=colour)
            if i == 0:
                new.paste(new2, (100, 98))
            elif i == 1:
                new.paste(new2, (1166, 100))
            elif i == 2:
                new.paste(new2, (4635, 98))
            else:
                new.paste(new2, (1166, 2500))

        new_resized = new.resize((1107, 680))
        return new_resized
    
    async def U_send_game_board(self, msg, channel):
        with BytesIO() as image_binary:
            self.U_create_game_board().save(image_binary, "PNG")
            image_binary.seek(0)
            game_board = discord.Embed(title="Uno", color=0x00FFFF) #creats an embed
            game_board.set_image(url=("attachment://image2.png")) #adds the image to the embed
            await channel.send(msg, file=discord.File(fp=image_binary, filename="image2.png"), embed=game_board)
    
    async def U_play(self, ongoing_games):
        msg = "Uno - <@" + str(self.player_info[str(self.turn)][0]) + ">'s turn"
        await self.U_send_game_board(msg, self.channel)
        current_player = self.player_info[str(self.turn)][0]
        with BytesIO() as image_binary:
            mention = "<@" + current_player + ">" #creates the player mention message
            self.U_create_user_msgs(self.player_info[str(self.turn)][1]).save(image_binary, "PNG") #creats an image of a players hand
            image_binary.seek(0)
            reply =("It is your turn now, " + mention) #the reply message
            user = await super().get_user_details(int(current_player))  #gets the user to message
            await self.U_send_game_board("The current Game board", user)
            embed4 = discord.Embed(title="Your current hand:", color=0x00FFFF)
            embed4.set_image(url="attachment://image.png")
            buttons = {}
            for i in range(len(self.player_info[str(self.turn)][1])):
                dis = self.U_check_cards(self.player_info[str(self.turn)][1][i])
                buttons[str(self.player_info[str(self.turn)][1][i])] = U_Card_Button(self, str(self.player_info[str(self.turn)][1][i]), dis, ongoing_games)
            draw_but = U_Draw_Button(self, ongoing_games)
            view = discord.ui.View()
            for j in buttons.values():
                view.add_item(j)
            view.add_item(draw_but)
            await user.send(reply, file=discord.File(fp=image_binary, filename="image.png"), embed=embed4, view=view)
    
    async def U_process_input(self, action, ongoing_games):
        if action == "draw":
            await self.U_draw_played(1)
            reply1 = "<@" + str(self.player_info[str(self.turn)][0]) + "> drew a card!"
            await self.channel.send(reply1)
            await self.U_process_input2(ongoing_games)
        else:
            self.current_card = action
            self.player_info[str(self.turn)][1].remove(action)
            if action[1:] == "Skip":
                self.skipped = True
                await self.U_process_input2(ongoing_games)
            elif action[1:] == "Reverse":
                await self.channel.send("Play has reversed directions!")
                if self.reverse == True:
                    self.reverse = False
                else:
                    self.reverse = True
                await self.U_process_input2(ongoing_games)
            elif action[1:] == "+2":
                self.skipped = True
                self.cards_added += 2
                await self.U_process_input2(ongoing_games)
            elif action == "Wild":
                await self.U_wild_played("Wild", ongoing_games)
            elif action == "+4":
                await self.U_wild_played("+4", ongoing_games)
                self.skipped = True
                self.cards_added += 4
            else:
                await self.U_process_input2(ongoing_games)
        
    async def U_process_input2(self, ongoing_games):    
        if len(self.player_info[str(self.turn)][1]) == 0:
            self.GAME_ONGOING = False
            winner = self.player_info[str(self.turn)][0]
            reply3 = "<@" + str(winner) + "> has won the game!"
            await self.U_send_game_board(reply3, self.channel)
            await super().end_game(winner, ongoing_games, 2)
            return
        
        if len(self.player_info[str(self.turn)][1]) == 1:
            reply2 = "<@" + str(self.player_info[str(self.turn)][0]) + "> is on Uno!"
            await self.channel.send(reply2)

        if self.GAME_ONGOING == True:
            if self.reverse == False:
                ops_key = "0"
            else:
                ops_key = "1"

            if self.skipped == True:
                self.turn = self.ops[ops_key](self.turn, 1)
                self.U_check_turn()
                if self.cards_added > 0:
                    await self.U_draw_played(self.cards_added)
                    reply3 = "<@" + str(self.player_info[str(self.turn)][0]) + "> drew " + str(self.cards_added) + " cards!"
                    self.cards_added = 0
                else:
                    reply3 = "<@" + str(self.player_info[str(self.turn)][0]) + "> has been skipped!"
                await self.U_send_game_board(reply3, self.channel)
                self.skipped = False
                self.turn = self.ops[ops_key](self.turn, 1)
            else:
                if self.cards_added > 0:
                    self.U_draw_played(self.cards_added)
                    self.cards_added = 0
                self.turn = self.ops[ops_key](self.turn, 1)
            self.U_check_turn() 
            
            await self.U_play(ongoing_games)
    
    def U_check_turn(self):
        if self.turn >(len(self.player_info)-1):
            self.turn -= len(self.player_info)
        if self.turn < 0:
            self.turn += len(self.player_info)

    def U_draw(self, hand):
        colour = random.randint(0, 3)
        action = random.randint(0, 13)
        card = self.cards[colour][action]
        hand.append(card)
        return card

    async def U_draw_played(self, num):
        drawn_cards = []
        for i in range(num):
            drawn_card = self.U_draw(self.player_info[str(self.turn)][1])
            drawn_cards.append(drawn_card)
        await self.U_send_draw_msgs(drawn_cards)

    async def U_send_draw_msgs(self, drawn_cards):
        with BytesIO() as image_binary:
            self.U_create_user_msgs(drawn_cards).save(image_binary, "PNG")          #creates an image of a players hand
            image_binary.seek(0)
            reply = ("The cards you drew:")                                                         #the reply message
            user = await super().get_user_details(int(self.player_info[str(self.turn)][0]))                      #gets the user to message
            embed4 = discord.Embed(title=reply, color=0x00FFFF)
            embed4.set_image(url="attachment://image.png")
            await user.send(file=discord.File(fp=image_binary, filename="image.png"), embed=embed4) 
            
    def U_check_cards(self, card):
        if card == "Wild" or card == "+4":
            return False
        else:
            if card[0] == self.current_card[0] or card[1] == self.current_card[1]:
                return False
            else:
                return True
            
    async def U_wild_played(self, mode, ongoing_games):
        current_player = self.player_info[str(self.turn)][0]
        current_user = await super().get_user_details(current_player)
        reply1 = "<@" + current_player + "> is changing the colour!"
        await self.U_send_game_board(reply1, self.channel)
        embed1 = discord.Embed(title="Choose a colour", description="Pick one of the buttons below to change the colour", color=0x00FFFF)
        red_but = U_Colour_Button("r", lambda: self.U_wild_played2(mode, "r", ongoing_games))
        blue_but = U_Colour_Button("b", lambda: self.U_wild_played2(mode, "b", ongoing_games))
        green_but = U_Colour_Button("g", lambda: self.U_wild_played2(mode, "g", ongoing_games))
        yellow_but = U_Colour_Button("y", lambda: self.U_wild_played2(mode, "y", ongoing_games))
        view = discord.ui.View()
        view.add_item(red_but)
        view.add_item(blue_but)
        view.add_item(green_but)
        view.add_item(yellow_but)
        await current_user.send(embed=embed1, view=view)
    
    async def U_wild_played2(self, mode, color, ongoing_games):
        action = str(color) + "_" + str(mode)
        self.current_card = action
        await self.U_process_input2(ongoing_games)



   


class U_Card_Button(discord.ui.Button):
    def __init__(self, obj, name, dis, ongoing_games):
        super().__init__(label=name, style=discord.ButtonStyle.blurple, disabled=dis) #inherits this from the supperclass Button from discord library
        self.obj = obj
        self.ong = ongoing_games

    async def callback(self, interaction):                                  #when the button is clicked...
        reply = self.label + " has been chosen"
        await interaction.response.edit_message(content=reply, view=None)   #...the message is edited
        await UnoGame.U_process_input(self.obj, self.label, self.ong)



class U_Draw_Button(discord.ui.Button):
    def __init__(self, obj, ongoing_games):
        super().__init__(label="Draw", style=discord.ButtonStyle.blurple) #inherits this from the supperclass Button from discord library
        self.obj = obj
        self.ong = ongoing_games

    async def callback(self, interaction):                                  #when the button is clicked...
        reply = "You have chosen to draw a card"
        await interaction.response.edit_message(content=reply, view=None)   #...the message is edited
        await UnoGame.U_process_input(self.obj, "draw", self.ong)



class U_Colour_Button(discord.ui.Button):
    def __init__(self, color, func):
        super().__init__(label=color, style=discord.ButtonStyle.blurple)
        self.func = func
    
    async def callback(self, interaction):
        reply = self.label + " was chosen"
        await interaction.response.edit_message(content=reply, view=None)
        await self.func()
