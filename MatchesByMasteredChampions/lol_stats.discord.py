import argparse
import lol_matches
import discord

parser = argparse.ArgumentParser(description='Program descriptiom.')
parser.add_argument('--key', help="Riot api key")
parser.add_argument('--token', help="Discord Bot's token")

args = parser.parse_args()
client = discord.Client()


def get_embedded_content(lol_stat):
    author = '%s last matches'
    field_body = "Champion level: %(level)s\n"\
                 "Champion points: %(points)s\n"\
                 "Matches with champion: %(matches)d\n"

    embed = discord.Embed(
        title="Stats",
        description="League of legends stats",
        color=0xf90000)
    embed.set_author(
        name=author % lol_stat['summoner'])
    embed.add_field(
        name="Matches played since %s" % lol_stat['date'],
        value=len(lol_stat['matches']),
        inline=False)
    for champ in lol_stat['champions']:
        matches = len(
            [m for m in lol_stat['matches']
             if m['champion'] == champ['championId']])
        context = {
            'level': champ['championLevel'],
            'points': champ['championPoints'],
            'matches': matches
        }
        embed.add_field(
            name="%s" % champ['name'],
            value=field_body % (context),
            inline=False)
    return embed


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!lol_stat'):
        summoner = message.content.split(' ')[1]
        lol_stat = lol_matches.run(
            api_key=args.key, summoner_name=summoner)
        embed = get_embedded_content(lol_stat)
        await client.send_message(message.channel, embed=embed)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(args.token)
