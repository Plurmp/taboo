import discord

import random


def has_word(phrase, word):
	phrase = phrase.trim().lower()
	word = word.trim().lower()
	phrase_list = phrase.split(" ")
	return bool(word in phrase_list)


def start_embed(game_master):
	embed = discord.Embed(
		title="Taboo",
		description="Press ➕ to join\n"
					"Press ➖ to leave\n"
					f"{game_master.mention}, press ⏯️ to start!"
	)
	return embed


def starting(players, start_message):
	teams = [[], []]
	num_teams = 2
	num_players = len(players)
	for i in range(2):
		while num_players > 0 and num_teams > 0:
			team = random.sample(players, int(num_players / num_teams))
			for x in team:
				players.remove(x)
			num_players = len(players)
			num_teams -= 1
			teams[i] = team
	await start_message.channel.send(
		f'Team A is {", ".join(teams[0])}\n'
		f'Team B is {", ".join(teams[1])}')
	return teams
