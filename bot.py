import os
import requests
import discord
from discord import app_commands

# --- 설정 (환경변수로 관리, 코드에 직접 넣지 마세요) ---
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://bw-gnhm.onrender.com")  # 발급 사이트 주소
API_SECRET = os.environ.get("API_SECRET", "change-this-secret")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


def try_redeem(code: str, user: str):
    try:
        res = requests.post(
            f"{WEBAPP_URL}/api/redeem",
            json={"code": code, "secret": API_SECRET, "user": user},
            timeout=5,
        )
        return res.json()
    except Exception as e:
        return {"valid": False, "reason": f"request_error: {e}"}


@client.event
async def on_ready():
    await tree.sync()
    print(f"로그인 완료: {client.user}")


@tree.command(name="redeem", description="발급받은 코드를 입력해 인증합니다")
@app_commands.describe(code="발급받은 12자리 코드")
async def redeem(interaction: discord.Interaction, code: str):
    result = try_redeem(code.strip().upper(), str(interaction.user))

    if result.get("valid"):
        await interaction.response.send_message(
            f"✅ 코드 인증 완료! 환영합니다, {interaction.user.mention}"
        )
        # 여기에 원하는 후속 동작 추가 가능
        # 예: 역할 부여
        # role = discord.utils.get(interaction.guild.roles, name="인증됨")
        # await interaction.user.add_roles(role)
    else:
        reason = result.get("reason", "unknown")
        if reason == "not_found":
            msg = "❓ 존재하지 않는 코드입니다."
        elif reason == "already_used":
            msg = "⚠️ 이미 사용된 코드입니다."
        else:
            msg = "❌ 인증에 실패했습니다."
        await interaction.response.send_message(msg, ephemeral=True)


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise SystemExit("DISCORD_TOKEN 환경변수를 설정하세요.")
    client.run(DISCORD_TOKEN)
