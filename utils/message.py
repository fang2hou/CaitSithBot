import discord


async def send_error_message(ctx, title, text):
    embed = discord.Embed(
        title=title, description=text, color=discord.Colour.red()
    )

    await ctx.send(embed=embed)
