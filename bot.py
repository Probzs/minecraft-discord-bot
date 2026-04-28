"""
Minecraft Discord Status Bot
Met à jour les salons Discord avec le statut Minecraft
Version debug + logs améliorés
"""

import json
import os
import urllib.request
import urllib.error
import sys
from datetime import datetime

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────

MINECRAFT_SERVER = "play.cafevanille.com"

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

GUILD_ID = "620289546906632193"

CHANNEL_STATUS  = "1432850727033897112"
CHANNEL_PLAYERS = "1432850729995079770"
CHANNEL_VERSION = "1453829805681414226"

STATE_FILE = "state.json"


# ──────────────────────────────────────────────
# LOG SYSTEM
# ──────────────────────────────────────────────

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


# ──────────────────────────────────────────────
# HTTP
# ──────────────────────────────────────────────

def http_get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "MC-Discord-Bot/1.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())


# ──────────────────────────────────────────────
# DISCORD PATCH (DEBUG VERSION)
# ──────────────────────────────────────────────

def discord_patch(channel_id: str, name: str) -> bool:
    url = f"https://discord.com/api/v10/channels/{channel_id}"

    payload = json.dumps({"name": name}).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        method="PATCH",
        headers={
            "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "MC-Discord-Bot/1.0"
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            log(f"✅ Discord OK | channel={channel_id} → '{name}' | HTTP {r.status}")
            return True

    except urllib.error.HTTPError as e:
        body = e.read().decode()

        log("❌ Discord ERROR")
        log(f"   ├─ Channel : {channel_id}")
        log(f"   ├─ Name    : {name}")
        log(f"   ├─ HTTP    : {e.code}")
        log(f"   ├─ Response: {body}")

        return False

    except Exception as e:
        log("❌ Network ERROR Discord")
        log(f"   └─ {e}")
        return False


# ──────────────────────────────────────────────
# STATE
# ──────────────────────────────────────────────

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"online": None, "players": None, "version": None}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    log(f"💾 State sauvegardé : {state}")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main():
    log(f"🔍 Vérification serveur Minecraft : {MINECRAFT_SERVER}")

    try:
        data = http_get(f"https://api.mcsrvstat.us/3/{MINECRAFT_SERVER}")
    except Exception as e:
        log(f"❌ Erreur API Minecraft : {e}")
        return

    is_online = bool(data.get("online", False))
    players_online = data.get("players", {}).get("online", 0)
    players_max = data.get("players", {}).get("max", 45)
    version = data.get("version", "Inconnue")

    log(f"📡 Serveur : {'🟢 ONLINE' if is_online else '🔴 OFFLINE'}")
    log(f"👥 Joueurs : {players_online}/{players_max}")
    log(f"🎮 Version : {version}")

    old = load_state()
    log(f"📂 Ancien état : {old}")

    updated = False

    # ── STATUS ──
    if old["online"] != is_online:
        log("🔄 Changement STATUS détecté")
        name = "🟢 Online" if is_online else "🔴 Offline"
        updated |= discord_patch(CHANNEL_STATUS, name)
    else:
        log("⏭️ STATUS inchangé")

    # ── PLAYERS ──
    if old["players"] != players_online:
        log("🔄 Changement PLAYERS détecté")
        updated |= discord_patch(
            CHANNEL_PLAYERS,
            f"👥 Joueurs : {players_online}/{players_max}"
        )
    else:
        log("⏭️ PLAYERS inchangé")

    # ── VERSION ──
    if old["version"] != version:
        log("🔄 Changement VERSION détecté")
        updated |= discord_patch(
            CHANNEL_VERSION,
            f"🎮 Version : {version}"
        )
    else:
        log("⏭️ VERSION inchangé")

    # ── SAVE STATE ──
    if updated:
        save_state({
            "online": is_online,
            "players": players_online,
            "version": version
        })
    else:
        log("✅ Aucun changement détecté")


if __name__ == "__main__":
    main()