import json
import random
import time
from os import environ as cred

import discord

import game

# cards is a list of lists in which index 0 is the "guessword" and all subsequent words are "taboo" words
with open('word list.json') as o:
	cards = json.load(o)['table']

TOKEN = cred['DISCORD_TOKEN']
client = discord.Client()
game_channel: discord.TextChannel
prefix = "+"
game_master: discord.User  # can start or stop the game
start_message: discord.Message
game_state = 0  # 0: not started, 1: waiting for players, 2: starting, 3: during round, 4: between rounds
players = []
teams = [[], []]  # A team is teams[0], B team is teams[1]
a_team_score = 0
b_team_score = 0
active_team = 0  # 0: A team, 1: B team
active_player = 0  #
active_word = 0


def during_round():
	global game_state, teams, active_word, start_message

	active_word = random.randrange(len(cards) - 1)

	game_state = 3
	await start_message.channel.send(
		f"The current giver is {teams[active_team][active_player].name}"
		f"You have 30 seconds to guess the word."
	)
	await teams[active_team][active_player].send(
		f'The word is {cards[active_word][0]}'
		f'The taboo words are {", ".join(cards[active_word][1, -1])}, and {cards[active_word][-1]}'
	)

	time.sleep(30)
	if game_state == 3:
		between_rounds(False)


def between_rounds(win_state):
	global game_state, a_team_score, b_team_score, start_message, active_team, active_player

	game_state = 4
	if win_state:
		if active_team == 0:
			a_team_score += 1
			await start_message.channel.send('Team A got a point!')
		elif active_team == 1:
			b_team_score += 1
			await start_message.channel.send('Team B got a point!')
		await start_message.channel.send(
			'Score:\n'
			f'Team A: {a_team_score}\n'
			f'Team B: {b_team_score}'
		)
		if a_team_score >= 10:
			await start_message.channel.send("Team A wins!")
			game_state = 0
			return
		elif b_team_score >= 10:
			await start_message.channel.send("Team B wins!")
			game_state = 0
			return
	else:
		await start_message.channel.send('No points awarded')
	if active_team == 0:
		active_team = 1
	elif active_team == 1:
		active_team = 0
		active_player += 1


@client.event
async def on_message(message):
	global game_channel, prefix, game_master, start_message, game_state, active_word, active_player, a_team_score, \
		b_team_score

	if message.author.id == client.user.id:
		return
	elif message.content == f'{prefix}start':
		# start game
		if game_state == 0:
			game_master = message.author
			start_message = await message.channel.send(embed=game.start_embed(game_master))
			await start_message.add_reaction('➕')
			await start_message.add_reaction('➖')
			await start_message.add_reaction('⏯')
			players.append(game_master)
			game_state = 1
		else:
			await message.channel.send(f'A game is already active in {game_channel.name}')
	elif game_state == 3 and message.channel == game_channel:
		if message.author == teams[active_team][active_player]:
			for w in cards[active_word]:
				if game.has_word(message.content, w):
					between_rounds(False)
		elif message.author in teams[active_team]:
			if game.has_word(message.content, cards[active_word][0]):
				between_rounds(True)


@client.event
async def on_reaction_add(reaction, user):
	global start_message
	global game_master
	global players
	global game_state
	global teams

	if reaction.message == start_message and game_state == 1:
		if str(reaction) == '➕':
			players.append(user)
			await start_message.channel.send(f'{user.name} joined the game')
		elif str(reaction) == '➖' and user in players:
			players.remove(user)
			await start_message.channel.send(f'{user.name} left the game')
		elif str(reaction) == '⏯' and user is game_master:
			if len(players) < 4:
				await start_message.channel.send(f'Game not started: Not enough players.')
			else:
				game_state = 2
				await start_message.channel.send(f'Game starting in 3...')
				time.sleep(1)
				await start_message.channel.send(f'2...')
				time.sleep(1)
				await start_message.channel.send(f'1...')
				time.sleep(1)
				teams = game.starting(players, start_message)
		await start_message.remove_reaction(reaction, user)

client.run(TOKEN)
