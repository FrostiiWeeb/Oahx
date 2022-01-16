from quart import Quart
from discord.ext import ipc
import uvloop


app = Quart(__name__)
ipc_client = ipc.Client(secret_key="my_secret_key")  # secret_key must be the same as your server


@app.route("/guilds")
async def index():
    guild_count = await ipc_client.request(
        "get_guild_count"
    )  # get the member count of server with ID 12345678

    return str(guild_count)  # display member count


if __name__ == "__main__":
    app.run(port=7676)