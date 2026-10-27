# ═══════════════════════════════════════════════════════════════
# main.py — ENTRY POINT (सिर्फ ये file run करनी है)
# ═══════════════════════════════════════════════════════════════

import asyncio
import time
from cfonts import render

# Auto-import दोनों modules (ये अपने आप load होंगे)
import login_engine
import bot_core

# Globals को share करने के लिए (bot_core में ही हैं, यहाँ reference)
from bot_core import (
    TcPOnLine, TcPChaT,
    build_ob55_online_auth, create_auth_token_chat,
    bot_uid, ToKen, region
)


async def MaiiiinE():
    """Login + TCP start"""
    global bot_uid, ToKen, region

    # ─── यहाँ अपना Guest UID और Password डालें ───
    Uid = '8353495487'
    Pw  = '8EDCA42D6E903016546A0B4A5ED2618B486EA7CE26A8B64E9E4F02B77EDCE6C6'
    REGION_PREF = "DZA"

    # ─── Login ───
    print("[*] Starting login...")
    result = await login_engine.do_login(Uid, Pw, REGION_PREF)
    if not result:
        print("[-] Login failed, retry in 10s...")
        await asyncio.sleep(10)
        return

    # ─── bot_core के globals set करें ───
    bot_core.bot_uid = result["bot_uid"]
    bot_core.ToKen   = result["token"]
    bot_core.region  = result["region"]

    key       = result["key"]
    iv        = result["iv"]
    timestamp = result["timestamp"]
    online_ip = result["online_ip"]
    online_port = result["online_port"]
    chat_ip   = result["chat_ip"]
    chat_port = result["chat_port"]
    acc_name  = result["account_name"]

    print(f"[+] UID: {result['bot_uid']} | Region: {result['region']} | Name: {acc_name}")

    # ─── Auth tokens ───
    ChatAutH = create_auth_token_chat(int(result["bot_uid"]), result["token"], int(timestamp), key, iv)
    OnlineAutH, _ = build_ob55_online_auth(int(result["bot_uid"]), result["token"], int(timestamp), key, iv)

    # ─── TCP tasks start ───
    ready_event = asyncio.Event()
    t1 = asyncio.create_task(
        TcPChaT(chat_ip, chat_port, ChatAutH, key, iv, ready_event, result["region"])
    )
    await ready_event.wait()
    await asyncio.sleep(1)
    t2 = asyncio.create_task(
        TcPOnLine(online_ip, online_port, key, iv, OnlineAutH)
    )

    # ─── Banner ───
    print(render('NORIX TCP', colors=['white', 'green'], align='center'))
    print(f" - Region => {result['region']}")
    print(f" - Bot Online! UID: {result['bot_uid']} | Name: {acc_name}\n")

    # ─── Forever run ───
    await asyncio.gather(t1, t2)


async def StarTinG():
    """Auto-restart loop"""
    while True:
        try:
            await asyncio.wait_for(MaiiiinE(), timeout=7 * 60 * 60)
            print("[!] Login failed or session ended. Retrying in 10s...")
            await asyncio.sleep(10)
        except asyncio.TimeoutError:
            print("[!] Token expired, restarting...")
        except Exception as e:
            print(f"[!] Error: {e} -> Restarting in 5s...")
            await asyncio.sleep(5)

if __name__ == '__main__':
    asyncio.run(StarTinG())
