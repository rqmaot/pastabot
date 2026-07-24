from discord.ext import commands
import subprocess

class Ftp(commands.Cog):
    def __init__(self, app):
        self.app = app
    @commands.command(help='Get information on using Pastabot\'s FTP')
    async def ftp(self, ctx):
        ip = self.app.get_ip()
        msg = f"""To use Pastabot's FTP server, use this info in your FTP client (e.g., Filezilla):
- Host: {ip}
- Port: 22
- Username: files
- Ask Malapasta for password, or just know it already"""
        await ctx.send(msg)
