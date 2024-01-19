import discord
import os
import random
from discord.ext import commands, tasks
from keep_alive import keep_alive
import datetime

# UTC-8 for Pacific Standard Time
utc = datetime.timezone.utc
pst = datetime.timezone(datetime.timedelta(hours=-8))

version = discord.__version__
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)


@bot.event
async def on_ready():
  await bot.change_presence(activity=discord.Activity(
    type=discord.ActivityType.playing, name='Guild Wars 2'))

  print(
    f'Logged in as {bot.user.name} ({bot.user.id}), Discord version: {version}'
  )
  AwakeStatus.start()
  if not ScheduledMetaProfit.is_running():
    ScheduledMetaProfit.start()


@bot.event
async def on_message(message):
  if message.author == bot.user:
    return

  if message.content.startswith('hello'):
    await message.channel.send(
      f'Hello, {message.author.mention}! Care to roll some dice?')

  await bot.process_commands(message)


#dice roll functions
@bot.command(name='d20', description='Rolls a twenty-sided die')
async def d20(ctx):
  rolled_num = random.randint(1, 20)
  if rolled_num == 1:
    await ctx.send(f':game_die: You rolled a {rolled_num}... :cry:')
  else:
    await ctx.send(f':game_die: You rolled a {rolled_num}!')


@bot.command(name='d12', description='Rolls a twelve-sided die')
async def d12(ctx):
  rolled_num = random.randint(1, 12)
  if rolled_num == 1:
    await ctx.send(f':game_die: You rolled a {rolled_num}... :cry:')
  else:
    await ctx.send(f':game_die: You rolled a {rolled_num}!')


@bot.command(name='d10', description='Rolls a ten-sided die')
async def d10(ctx):
  rolled_num = random.randint(1, 10)
  if rolled_num == 1:
    await ctx.send(f':game_die: You rolled a {rolled_num}... :cry:')
  else:
    await ctx.send(f':game_die: You rolled a {rolled_num}!')


@bot.command(name='d8', description='Rolls an eight-sided die')
async def d8(ctx):
  rolled_num = random.randint(1, 8)
  if rolled_num == 1:
    await ctx.send(f':game_die: You rolled a {rolled_num}... :cry:')
  else:
    await ctx.send(f':game_die: You rolled a {rolled_num}!')


@bot.command(name='d6', description='Rolls a six-sided die')
async def d6(ctx):
  rolled_num = random.randint(1, 6)
  if rolled_num == 1:
    await ctx.send(f':game_die: You rolled a {rolled_num}... :cry:')
  else:
    await ctx.send(f':game_die: You rolled a {rolled_num}!')


@bot.command(name='d4', description='Rolls a four-sided die')
async def d4(ctx):
  rolled_num = random.randint(1, 4)
  if rolled_num == 1:
    await ctx.send(f':game_die: You rolled a {rolled_num}... :cry:')
  else:
    await ctx.send(f':game_die: You rolled a {rolled_num}!')


@bot.command(name='d100', description='Rolls a hundred-sided die')
async def d100(ctx):
  rolled_num = random.randint(1, 100)
  if rolled_num == 1:
    await ctx.send(f':game_die: You rolled a {rolled_num}... :cry:')
  else:
    await ctx.send(f':game_die: You rolled a {rolled_num}!')


@bot.command(name='coinflip', description='Flips a coin')
async def coinflip(ctx):
  rolled_num = random.randint(1, 2)
  if rolled_num == 1:
    await ctx.send(":coin: It's heads!")
  elif rolled_num == 2:
    await ctx.send(":coin: It's tails!")


#GW2 Joke function
@bot.command(
  name='gw2joke',
  description='tells a joke from GW2, with jokes courtesy of ChatGPT')
async def gw2joke(ctx):
  jokelist = open("GW2Jokes.txt", 'r')
  jokes = jokelist.readlines()
  get_random_joke = random.choice(jokes)
  await ctx.send(get_random_joke)

MetaProfitResults = None

async def run_item_finder():
  from bs4 import BeautifulSoup
  import requests
  import time

  # Creates a session to reuse if performing multiple requests
  session = requests.Session()

  # Dictionary to store item names
  item_names = {}

  def itemfinder(url):
    build_name = url.split('/')[-1].replace('-', ' ')
    build_name = ' '.join(word.capitalize() for word in build_name.split())
    print(f'Getting item info from Build: "{build_name}"')

    html_text = session.get(url).text
    soup = BeautifulSoup(str(html_text), 'lxml')
    gear = soup.find_all(
      'div',
      class_="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 mb-3")

    # Set comprehension to get unique IDs
    unique_ids = {
      armory_div['data-armory-ids']
      for div in gear
      for armory_div in div.find_all('div', {'data-armory-ids': True})
    }

    # Guild Wars 2 API endpoint for items
    base_url = 'https://api.guildwars2.com/v2/items/'

    # Iterates through item IDs and fetch item names
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        for item_id in unique_ids:
          try:
            response = session.get(base_url + item_id)
            if response.status_code == 200:
              item_data = response.json()
              item_names[item_id] = item_data['name']
            else:
              retry_count += 1
              time.sleep(1)
          except:
            item_names[item_id] = 'Item not found'       

  def gw2tpprofit(item_id):
    from bs4 import BeautifulSoup
    import requests

    # Creates a session to reuse if performing multiple requests
    session = requests.Session()

    try:
      html_text = session.get(
        f'https://www.gw2tp.com/recipes?id={item_id}').text
      soup = BeautifulSoup((html_text), 'lxml')
      negative = soup.find(string='-', style='color:red')

      # Check if the element is found
      if negative:
        isnegative = '-'
      else:
        isnegative = ''
      valid_spans = soup.find_all('span', class_=['gold', 'silver', 'copper'])

      if len(valid_spans) > 2:
        if "copper" in str(valid_spans[-1]):
          copper = valid_spans[-1].text.strip()
        else:
          copper = 0
        if "silver" in str(valid_spans[-2]):
          silver = valid_spans[-2].text.strip()
        else:
          silver = 0
        if "gold" in str(valid_spans[-3]):
          gold = valid_spans[-3].text.strip()
        else:
          gold = 0
        profit = f"{isnegative}{gold}g {silver}s {copper}c"
        return profit
      if len(valid_spans) == 2:
        gold = 0
        silver = 0
        copper = valid_spans[-1].text.strip()
        profit = f"{isnegative}{gold}g {silver}s {copper}c"
        return profit
    except:
      return 0

  html_text = session.get('https://snowcrows.com/builds').text
  soup = BeautifulSoup((html_text), 'lxml')
  builds = soup.find_all('div', class_="grid gap-1 mt-4")

  # Create a list to store the item profits
  item_profits = []

  # Iterate through the links and call itemfinder() for each URL
  for build in builds:
    links = build.find_all('a', href=True)
    time.sleep(1)

    for link in links:
      url = 'https://snowcrows.com' + link['href']
      itemfinder(url)
      time.sleep(1)

  sorted_items = sorted(item_names.items(), key=lambda x: x[1])

  #appends item_profit to list
  for item_id, item_name in sorted_items:
    #if any(keyword in item_name.lower() for keyword in ['rune', 'superior sigil', 'relic']):
    item_profit = gw2tpprofit(item_id)
    item_profits.append((item_id, item_name, item_profit))

  #prints ID, name, and TP profit if net positive
  Results = ""
  for item_id, item_name, item_profit in item_profits:
    if '-' in str(item_profit) or item_profit == None:
      pass
    elif 'Error' in str(item_name):
      pass
    elif '0g 0s' in str(item_profit):
      pass
    else:
      print(f'adding {item_name} to list...')
      gw2efficiency = f'<https://gw2efficiency.com/crafting/calculator/a~0!b~1!c~0!d~1-{item_id}>'
      Results += f'[{item_name}]({gw2efficiency}), Profit: **{item_profit}**\n'
  return Results


def split_message(message, lines_per_chunk=10):
  chunks = []
  lines = message.split('\n')
  current_chunk = []

  for line in lines:
    current_chunk.append(line)

    if len(current_chunk) == lines_per_chunk:
      chunks.append('\n'.join(current_chunk))
      current_chunk = []

  if current_chunk:
    chunks.append('\n'.join(current_chunk))

  return chunks


@bot.command()
async def commands(ctx):
  embed = discord.Embed(title="Command Menu",
                        description="List of available commands:",
                        color=discord.Color.blue())

  embed.add_field(
    name="/metaprofit",
    value=
    "Gives you the profit for craftable gear across all Snowcrows metabuilds",
    inline=False)

  embed.add_field(name="/gw2joke",
                  value="Want to hear a really terrible joke?",
                  inline=False)
  embed.add_field(
    name="/dX",
    value=
    "Roll a X-sided dice, replace X in the command with the number of sides (4, 6, 8, 10, 12, 20, or 100)",
    inline=False)
  await ctx.send(embed=embed)


#simple task performed every minute to help keep bot awake
@tasks.loop(minutes=1)
async def AwakeStatus():
  print('Bot is still running...')


@tasks.loop(hours=1)
async def ScheduledMetaProfit():
  global MetaProfitResults
  print('performing metaprofit analysis...')
  MetaProfitResults = await run_item_finder()


@bot.command(
  name='metaprofit',
  description=
  'Gives you the profit for craftable gear across all Snowcrows metabuilds')
async def metaprofit(ctx):
  global MetaProfitResults

  if MetaProfitResults == None:
    await ctx.send('still acquiring data, please wait...')
  else:
    await ctx.send("**Today's current profitable items are the following:**")
    message_chunks = split_message(MetaProfitResults)
    for chunk in message_chunks:
      await ctx.send(chunk)


#run uptimerobot server
keep_alive()

#replace 'bot token' with your own bot token, do not remove quotes
bot_token = 'bot token'
bot.run(bot_token)
