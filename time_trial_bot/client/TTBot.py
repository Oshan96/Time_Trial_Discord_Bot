import discord
from discord.ext import commands
from discord.ext.commands import Bot, MissingPermissions

from albion_service.AlbionService import AlbionService


class TTBot(Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super(TTBot, self).__init__(intents=intents, command_prefix="!")
        self.guild_id = "WInSXrwfSMC1P_P07J3d7g"
        self.disc_server_name = "Time Trial"
        self.disc_gid = None
        self.service = AlbionService(self.guild_id)

        @self.command(
            name="register",
            help="Assign Time Trial role and changes nickname",
            pass_context=True
        )
        async def register(ctx: discord.ext.commands.Context, ign):
            player_data = self.service.check_user_guild(ign)
            if player_data:
                player_guild_id = player_data["guild_id"]

                # if player is already in guild, give "Time Trial" role
                if player_guild_id == self.guild_id:
                    # change server nickname to ign
                    await ctx.author.edit(nick=ign)
                    role = discord.utils.get(ctx.guild.roles, name="Time Trial")
                    await ctx.author.add_roles(role)
                    print("Success!", ign, "added!")
                    await ctx.reply(f'Successfully registered!')
                else:
                    await ctx.reply(f'You need to join Time Trial in-game first!')
            else:
                await ctx.reply(f'Failed to retrieve data. Please try again or contact @alliance-officer')

        @self.command(
            name="check",
            help="Check the users who are not in guild or have no nickname set (who will have roles removed on a purge)",
            pass_context=True
        )
        async def check(ctx):
            purged_members = await self.check_non_guild_members(purge=False)
            embed = discord.Embed(color=discord.Color.blurple(), title="Member Check Report", discription='')
            msg = "No users are to be purged!"
            if len(purged_members) > 0:
                users = ''
                for user in purged_members:
                    users += '\n- ' + user
                msg = f'Following users will have their Time Trial role removed on a purge. {users}'

            embed.description = msg

            await ctx.reply(embed=embed)

        @self.command(
            name="purge",
            help="Remove Time Trial role from the users who are not in guild or have no nickname set",
            pass_context=True
        )
        @commands.has_permissions(manage_roles=True)
        async def purge(ctx):
            purged_members = await self.check_non_guild_members(purge=True)
            embed = discord.Embed(color=discord.Color.blurple(), title="Purge Report", discription='')
            msg = "No users were purged!"
            if len(purged_members) > 0:
                users = ''
                for user in purged_members:
                    users += '\n- ' + user
                msg = f'Following users had their Time Trial role removed. {users}'

            embed.description = msg

            await ctx.reply(embed=embed)

        @purge.error
        async def purge_error(ctx, error):
            print("Error!", error)
            if isinstance(error, MissingPermissions):
                text = "Sorry {}, you do not have permissions to do that!".format(ctx.message.author)
                await ctx.reply(text)

    def set_disc_gid(self):
        guilds = self.guilds
        for guild in guilds:
            # change the guild name if the server name is changed
            if guild.name == self.disc_server_name:
                self.disc_gid = guild.id
                print(self.disc_gid)
                return

    async def check_non_guild_members(self, purge=False):
        guild_members_data = self.service.get_members()
        role_removes = []
        if guild_members_data:
            guild_members = []
            for guild_member_data in guild_members_data:
                guild_members.append(guild_member_data["Name"].lower())
            print(guild_members)
            for guild in self.guilds:
                if guild.id == self.disc_gid:
                    disc_members = await guild.fetch_members(limit=None).flatten()
                    # print(disc_members)
                    role = discord.utils.get(guild.roles, name="Time Trial")
                    for disc_member in disc_members:
                        # remove "Time Trial" role of the user if not in guild in game
                        print(disc_member.name, disc_member.nick)
                        if disc_member.bot or disc_member.system:
                            continue
                        if not disc_member.nick or (disc_member.nick.lower() not in guild_members):
                            # add a check if there's any other checks to be made before role removal
                            if role in disc_member.roles:
                                if purge:
                                    await disc_member.remove_roles(role)
                                if not disc_member.nick:
                                    role_removes.append(disc_member.name)
                                else:
                                    role_removes.append(disc_member.nick)
                    return role_removes
        return None

    async def on_ready(self):
        # set discord gid
        self.set_disc_gid()

