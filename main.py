import csv

import os
import re
from contextlib import AsyncExitStack
from datetime import datetime
from functools import lru_cache
from random import choice, randint

import requests
import gettext

from discord import ChannelType, File, Intents, Embed, DMChannel, Message, Member, Forbidden
from discord.abc import GuildChannel
from discord.ext.commands import Bot
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option
from dotenv import load_dotenv
from emoji import emoji_lis, distinct_emoji_lis

from planet_videos import planet_videos


@lru_cache
def get_translator(lang: str = 'fr_FR'):
    trans = gettext.translation('messages', localedir="locale", languages=(lang,))
    return trans.gettext


load_dotenv()

print_information = False
target_guild_id = int(os.getenv('TARGET_GUILD_ID'))
target_english_guild_id = int(os.getenv('TARGET_ENGLISH_GUILD_ID', default=0))


class MyBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set an arbitrary count for the word apero based on the current date when initializing the bot
        self.apero_count = datetime.today().day * 44
        self.planet_mention_count = 0
        self.search_links_count = 0

    async def on_ready(self):
        print('------')
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

        if print_information:
            # Display categories and channels of the target Discord server
            for guild in bot.guilds:
                if int(guild.id) == target_guild_id:
                    categories = [c for c in guild.channels if c.type == ChannelType.category]
                    text_channels = [c for c in guild.channels if c.type == ChannelType.text]
                    category_to_channel = {}
                    for category in categories:
                        print(f'{category.name} :')
                        category_to_channel[category.name] = []
                        for c in text_channels:
                            if c.category_id == category.id:
                                print(' -', c, repr(c))
                                category_to_channel[category.name].append(c)

    async def on_message(self, message: Message):
        if not message.author.bot:
            # Check if it's a message from DM
            if isinstance(message.channel, DMChannel):
                await message.reply("D??sol??, je n'ai pas encore ??t?? programm?? pour r??pondre au message en priv?? ????")
            else:
                # Switch to english language if from English Server
                if message.guild.id == target_english_guild_id:
                    _ = get_translator('en')
                    apero_regex = r"(drink)|(happy hour)| (HH)|(afterwork)"
                else:
                    _ = get_translator()
                    apero_regex = r"ap[e??]?ro"

                # Prepare and random number to add randomness if the bot replies or not
                random_number = randint(0, 100)

                # Search if message triggers the regex
                if re.search(apero_regex, message.content, re.IGNORECASE):
                    # Reset counter on first day of month
                    if datetime.today().day == 1 and self.apero_count > 50:
                        self.apero_count = 0
                    self.apero_count += 1
                    if self.apero_count % 100 == 0:
                        await message.reply(_('Bravo ! Tu viens de proposer la %s ??me mention '
                                            f'du mot ap??ro ce mois-ci ????????') % self.apero_count)
                    elif random_number < 20:
                        answer_choices = [
                            _("On parle toujours d'ap??ro ici ! ????"),
                            _("J'ai cru entendre parler d'ap??ro ? ????"),
                            _('"Il faut ap??roiser le changement climatique !" ????'),
                            _('Encore un ap??ro ? ????'),
                            _("O?? ??a un ap??ro !? ????"),
                            _("Vivement l'ap??ro du weekend de la Galaxie de l'Action ! ????"),
                            _("Pensez ?? pr??parer 2 mensonges et 1 v??rit?? pour animer l'ap??ro ????"),
                            _('Et... Il y aura du Ricard ?? cet ap??ro ? ????'),
                            _('Tu pr??vois le cidre aussi ? (pour les bretons !)'),
                            _('Ap??ro (nom masculin) : Du latin apertivus qui signifie ouvrir ????'),
                            _('Euh... Vous avez pr??venu <@!696086695283523604> de cet ap??ro ? ????'),
                            _('<@!696086695283523604> a bien donn?? son aval pour cet ap??ro ? ????'),
                            _("C'est chez <@!696086695283523604> l'ap??ro ? ????"),
                            _("Qui s'occupe de pr??parer des mojitos ? ????????"),
                            _("Eh bah alors ! On n'attend pas Patrick ? ????"),
                            _("Un ap??ro? Il doit y avoir un chimiste dans le coin avec une solution, t'inqui??te ???? ????"),
                            _("?? Le tout-venant a ??t?? pirat?? par les m??mes ! Qu'est-ce qu'on fait ? On se risque sur le bizarre ? ??"),
                            _('Vous avez sorti le vitriol ?'),
                            _("Est ce qu'il y aura cette esp??ce de drolerie qu'on buvait dans une petit taule de Bi??n H??a, pas tellement loin de Sa??gon ?"),
                            _("J'lui trouve un go??t de pomme ? Y'en a !"),
                            _('Il y a 2 choses qui gagnent ?? vieillir, le bon vin et les amis.'),
                            _('La gourmandise est le p??ch?? des bonnes ??mes'),
                            _('Quand mes amis me manquent, je fais comme pour les ??chalotes, je les fais revenir avec du vin blanc '),
                            _('Ceux qui disent que le petit d??jeuner est le repas le plus important de la journ??e ne connaissent pas l???ap??ro.'),
                            _("Quel que soit le probl??me ou la question, l'ap??ro est toujours la bonne r??ponse"),
                            _("Comme disait Pierre Desproges : Je ne bois jamais ?? outrance, je ne sais m??me pas o?? c'est."),
                            _('un mojito, et tout est plus beau!'),
                            _("Ceux qui cherchent midi ?? 14h ratent l'heure de l'ap??ro"),
                            _('Ne pas confondre : ivre de bonheur et ivre de bonne heure'),
                            _("Quelqu'un sait ?? quelle page de la bible on trouve la recette pour changer l'eau en vin ? C'est pour un ap??ro ce soir ????"),
                        ]
                        if datetime.now().hour < 10:
                            answer_choices.append(_("Il n'est pas encore un peu t??t pour lancer l'ap??ro ? ????"))
                        await message.reply(choice(answer_choices))

                # Search if message contains "aper'agro"
                elif re.search(r"ap[e??]r'? ?agro", message.content, re.IGNORECASE):
                    answer_choices = [
                        _("Rejoignez les Agros, y'a Ap??r'Agro"),
                        _("Un verre achet??, une baleine sauv??e"),
                        _('Un verre achet??, un ??l??phant sauv??'),
                        _('Un verre achet??, une loutre sauv??e'),
                        _("Un verre achet??, un lama sauv??"),
                        _("Venez ?? l'Ap??r'Agro, les Agros sont aussi chauds que le climat !"),
                        _("Les Agros ne vous connaissent pas mais vous aiment d??j??"),
                        _("Viens planter des baleines autour d'un verre"),
                        _("Viens planter des ??l??phants autour d'un verre"),
                        _("Viens soutenir les fili??res agricoles et viticoles avec les Agros ce soir !"),
                        _('Les Agros, ??a suffit, vous ??tes trop chauds !'),
                    ]
                    await message.reply(choice(answer_choices))

                # Search if message contains beers emoji
                elif '????' in message.content or '????' in message.content and random_number < 40:
                    answer_choices = [
                        _("A la tienne ! ????"),
                        _("Oh je vois des bi??res par ici ????"),
                        _('Tchin ! ????'),
                        _('Ap??ro ? ????')
                    ]
                    await message.reply(choice(answer_choices))

        await self.process_commands(message)

    async def on_member_update(self, before: Member, after: Member):
        if after.nick == before.nick:
            return
        print(f'{after} a chang?? son pseudo : {before.nick} --> {after.nick}')
        emojis_before = set(distinct_emoji_lis(before.nick)) if before.nick else set()
        if after.nick:
            emojis_after = set(distinct_emoji_lis(after.nick))
            new_emojis = emojis_after.difference(emojis_before)
            joined_planet = []
            for emoji in new_emojis:
                # Replace the loupe emoji if it is in the wrong way
                if emoji == '????':
                    emoji = '????'
                    try:
                        await after.edit(nick=after.nick.replace('????', '????'))
                    except Forbidden:
                        print(f'Impossible de modifier le pseudo de {after}')
                if emoji in planet_videos.keys():
                    joined_planet.append(emoji)

            if joined_planet:
                _ = get_translator('en' if after.guild.id == target_english_guild_id else 'fr_FR')

                message = _('Oh, je viens de voir que tu viens de mettre ?? jour '
                            'ton pseudo sur le serveur de Time et que tu as rejoint ')
                if len(joined_planet) == 1:
                    message += _('une nouvelle plan??te !\nVoici donc la vid??o de pr??sentation de cette plan??te ???')
                else:
                    message += _('de nouvelles plan??tes !\nVoici donc les vid??os de pr??sentation de ces plan??tes ???')
                await after.send(message)
                for emoji in joined_planet:
                    await after.send(
                        _('Plan??te %s %s : %s' % (emoji, planet_videos[emoji]["label"], planet_videos[emoji]["url"]))
                    )


if __name__ == '__main__':
    intents = Intents.default()
    intents.members = True
    bot = MyBot(command_prefix=os.getenv('COMMAND_PREFIX', '!'), intents=intents)

    slash = SlashCommand(bot, sync_commands=True)

    @slash.slash(name="ping", description='Teste de la connexion avec le Bot', guild_ids=[target_guild_id])
    async def _ping(ctx):  # Defines a new "context" (ctx) command called "ping."
        await ctx.send(f"Pong ! ({round(bot.latency * 1000, 5)} ms)")

    async def mention_planet_members(ctx, emoji=None, channel: GuildChannel = None, salon=None):
        fr = ctx.guild.id != target_english_guild_id

        bot.planet_mention_count += 1

        # salon is an alias for channel
        channel = salon if salon else channel

        print(f'{emoji=}')

        async with ctx.channel.typing() if ctx.channel else AsyncExitStack():
            # Create a list with all emojis found in the emoji parameter
            emojis = [e['emoji'] for e in emoji_lis(emoji)] if emoji else []

            # If no emoji or no channel has been passed, take by default the channel where the command was executed
            if not emojis and not channel:
                channel = ctx.channel

            # Add emoji of the selected channel name if it exists at the beginning of the name
            if channel:
                emoji_list = emoji_lis(str(channel))
                if emoji_list and emoji_list[0]['location'] == 0:
                    emojis.append(emoji_list[0]['emoji'])
                else:
                    await ctx.reply(
                        f"{channel.mention} n'est pas un salon de plan??te ou bien n'a pas d'emoji associ??." if fr
                        else f"{channel.mention} is not a planet channel or it doesn't have an associated emoji."
                    )
                    return

            print('emojis : ', str(emojis))

            # Search the emoji in the nickname of all guild members
            members_to_ping = []
            for member in ctx.guild.members:
                # Use nickname to search the emoji inside (fallback to the name if nickname hasn't been set)
                for emoji in emojis:
                    if emoji in member.display_name:
                        members_to_ping.append(member)
                        break

        # Ping all targeted members if at least one has been found
        if members_to_ping:
            print('Nombre de personnes ?? pinguer : ', len(members_to_ping))
            offset = 80
            for start in range(1 + (len(members_to_ping) - 1) // offset):
                start = start * offset
                await ctx.reply(
                    ' '.join(user.mention for user in members_to_ping[start:start + offset])
                )
        else:
            await ctx.reply(
                'Aucun utilisateur ?? mentionner...' if fr else 'No user to mention...'
            )


    slash.add_slash_command(
        mention_planet_members,
        name='alerte-la-plan??te',
        description="Cr???? une alerte pour toutes les membres d'une plan??te. "
                    "Veuiller saisir un emoji ou choisir un salon.",
        options=[
            create_option(
                name='emoji',
                description="Indiquer l'??moji de la plan??te ?? alerter",
                option_type=3,
                required=False
            ),
            create_option(
                name='salon',
                description="Choisir le salon d'une plan??te ?? alerter",
                option_type=7,
                required=False
            )
        ],
        guild_ids=[target_guild_id]
    )
    if target_english_guild_id:
        slash.add_slash_command(
            mention_planet_members,
            name='notify-the-planet',
            description="Create an alert to every planet members. Please type an emojo or select a channel.",
            options=[
                create_option(
                    name='emoji',
                    description="Indicate the planet emoji",
                    option_type=3,
                    required=False
                ),
                create_option(
                    name='channel',
                    description="Choose a planet channel to alert",
                    option_type=7,
                    required=False
                )
            ],
            guild_ids=[target_english_guild_id]
        )


    @bot.command(name='alerte-la-planete', aliases=['alerte-la-plan??te', 'notify-the-planet'])
    async def old_mention_planet_members(ctx, *args):
        bot.planet_mention_count += 1
        print(ctx.message.content)

        # Create a list with all emojis to search in usernames
        emojis = []
        # Add mentioned channels name in the args list
        for channel in ctx.message.channel_mentions:
            args += (channel.name,)
        # Foreach args, check if it starts with an emoji then add it to the emojis list
        for arg in args:
            emoji_list = emoji_lis(arg)
            if emoji_list and emoji_list[0]['location'] == 0:
                emojis.append(emoji_list[0]['emoji'])

        print('emojis : ', str(emojis))

        # Search the emoji in the nickname of all guild members
        members_to_ping = []
        for member in ctx.guild.members:
            # Use nickname to search the emoji inside (fallback to the name if nickname hasn't been set)
            for emoji in emojis:
                if emoji in member.display_name:
                    members_to_ping.append(member)
                    break

        # Ping all targeted members if at least one has been found
        if members_to_ping:
            print('Nombre de personnes ?? pinguer : ', len(members_to_ping))
            offset = 80
            for start in range(1 + (len(members_to_ping) - 1) // offset):
                start = start * offset
                await ctx.message.reply(
                    ' '.join(user.mention for user in members_to_ping[start:start + offset])
                )
        else:
            await ctx.message.reply('Aucun utilisateur ?? mentionner...')
        await ctx.message.reply("N'h??site pas ?? utiliser la commande slash `/alerte-la-plan??te` la prochaine fois ????")


    @slash.slash(
        name="cherche-des-liens",
        description='Permet de rechercher des liens en rapport avec Time',
        options=[
            create_option(
                name='query',
                description='Pr??ciser les termes de la recherche',
                option_type=3,
                required=True
            )
        ],
        guild_ids=[target_guild_id]
    )
    async def search_links(ctx, query: str):
        async with ctx.channel.typing() if ctx.channel else AsyncExitStack():
            bot.search_links_count += 1
            found_links = []

            # Prepare request to ShortIO app
            url = 'https://api.short.io/api/links'
            querystring = {'domain_id': os.getenv('SHORT_IO_DOMAIN_ID')}
            headers = {
                'Accept': 'application/json',
                'Authorization': os.getenv('SHORT_IO_SECRET_KEY')
            }
            response = requests.get(url, headers=headers, params=querystring)

            # Loop through each links and add it to found_links if one of the args is matching
            for link in response.json()['links']:
                # Ignore archived links
                if link['archived']:
                    continue

                for arg in query.split(' '):
                    # Stop searching if link has been added
                    if link in found_links:
                        break

                    # Check if in one of the fields is matching one of the args
                    for field in ('title', 'originalURL'):
                        if arg.lower() in link[field].lower():
                            found_links.append(link)
                            break

                    # Check in the tags if link is still not in found_links
                    if link not in found_links:
                        for tag in link['tags']:
                            if arg.lower() in tag.lower():
                                found_links.append(link)
                                break

        if found_links:
            await ctx.reply(f'Voici les r??sultats de votre recherche "{query}":')
            for link in found_links:
                embed = Embed()
                embed.title = link['title']
                embed.type = 'link'
                embed.url = link['shortURL']
                embed.add_field(name='Lien', value=link["shortURL"], inline=False)
                if link['icon']:
                    embed.set_thumbnail(url=link['icon'])
                if link['tags']:
                    embed.add_field(name='Tags', value=' | '.join(tag for tag in link['tags']))
                await ctx.send(embed=embed)
        else:
            await ctx.reply(f'Aucun r??sultat pour votre recherche "{query}"...')


    async def quarks_to_welcome(ctx):
        async with ctx.channel.typing() if ctx.channel else AsyncExitStack():
            fr = ctx.guild.id != target_english_guild_id
            filename = 'quarks ?? accueillir.csv' if fr else "quarks to welcome.csv"
            written = False
            with open(filename, 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                headers = ['Nom utilisateur Discord', 'Pseudo serveur Time', 'Date arriv??e sur le serveur']
                if not fr:
                    headers = ['Discord username', 'Time server nickname', 'Joining date']
                writer.writerow(headers)
                for member in ctx.guild.members:
                    if not member.bot and '*' not in member.display_name:
                        writer.writerow([
                            str(member),
                            member.nick or '',
                            member.joined_at.strftime('%d/%m/%Y %H:%M')]
                        )
                        written = True

        if written:
            # Send file to Discord in message
            with open(filename, 'rb') as file:
                message = "Fichier CSV contenant la liste des quarks n'ayant pas d'ast??rique dans leur pseudo :"
                if not fr:
                    message = "CSV file containing the list of quarks who don't have an asterisk in their nickname :"
                await ctx.reply(message, file=File(file, filename))
        else:
            await ctx.reply(
                'Aucun quarks ?? accueillir ????' if fr else "No quarks to welcome ????"
            )
        # Delete file at the end of processing
        os.remove(filename)


    slash.add_slash_command(
        quarks_to_welcome,
        name='quarks-a-accueillir',
        description="G??n??re un fichier CSV contenant la liste des quarks n'ayant pas ??t?? accueillis",
        guild_ids=[target_guild_id]
    )
    if target_english_guild_id:
        slash.add_slash_command(
            quarks_to_welcome,
            name='quarks-to-welcome',
            description="Generate a CSV file containing the list of quarks who had not been welcomed yet",
            guild_ids=[target_english_guild_id]
        )

    @bot.command(name='bot-info')
    async def get_bot_information(ctx):
        await ctx.message.reply(
            f'Compteur du mot "ap??ro" : {bot.apero_count}.\n'
            f'Nombre d\'utilisation de la commande "alerte-la-planete" : {bot.planet_mention_count}.\n'
            f'Nombre d\'utilisation de la commande "search-links" : {bot.search_links_count}.\n'
        )


    @bot.command(name='set-bot-apero-count')
    async def set_bot_apero_count(ctx, *args):
        if ctx.message.author.id != int(os.getenv('CREATOR_ID')):
            await ctx.message.reply(f"D??sol??, cette commande est r??serv?? au cr??ateur du bot ????")
        else:
            try:
                value = int(args[0])
            except IndexError:
                await ctx.message.reply('Il faut sp??cifier une valeur')
            except ValueError:
                await ctx.message.reply(f"{args[0]} n'a pas l'air d'??tre un nombre")
            else:
                if value < 1:
                    await ctx.message.reply(f"Il me faut une valeur sup??rieure ?? 0 ????")
                else:
                    bot.apero_count = value
                    await ctx.message.reply(f"Le compteur du mot ap??ro a bien ??t?? d??fini ?? {value} ????")

    bot.run(os.getenv('TOKEN'))
