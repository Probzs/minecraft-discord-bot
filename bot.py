"""
Minecraft Discord Status Bot
Réplique du workflow n8n — met à jour les salons vocaux Discord
avec le statut, les joueurs et la version du serveur Minecraft.
"""

import json
import os
import sys
import urllib.request
import urllib.error

# ──────────────────────────────────────────────
# CONFIGURATION — à adapter à ton serveur
# ──────────────────────────────────────────────

MINECRAFT_SERVER   = "play.cafevanille.com"

DISCORD_BOT_TOKEN  = os.environ["DISCORD_BOT_TOKEN"]   # secret GitHub
GUILD_ID           = "620289546906632193"

# IDs des salons vocaux à renommer
CHANNEL_STATUS     = "1432850727033897112"   # 🟢 Online / 🔴 Offline
CHANNEL_PLAYERS    = "1432850729995079770"   # 👥 Joueurs : X/45
CHANNEL_VERSION    = "1453829805681414226"   # 🎮 Version : X.X.X

STATE_FILE         = "state.json"

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def http_get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "MinecraftDiscordBot/1.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())


def discord_patch(channel_id: str, name: str) -> None:
    url = f"https://discord.com/api/v10/channels/{channel_id}"
    payload = json.dumps({"name": name}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        method="PATCH",
        headers={
            "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            status = r.status
        print(f"  ✅ Salon {channel_id} → « {name} » (HTTP {status})")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ❌ Erreur Discord {e.code} pour le salon {channel_id}: {body}")
        sys.exit(1)


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    # État initial neutre → tout sera mis à jour au premier run
    return {"online": None, "players": None, "version": None}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    print(f"  💾 State sauvegardé : {state}")

# ──────────────────────────────────────────────
# LOGIQUE PRINCIPALE
# ──────────────────────────────────────────────

def main():
    print(f"🔍 Interrogation de {MINECRAFT_SERVER}…")

    try:
        data = http_get(f"https://api.mcsrvstat.us/3/{MINECRAFT_SERVER}")
    except Exception as e:
        print(f"❌ Impossible de joindre l'API mcsrvstat : {e}")
        sys.exit(1)

    # Données actuelles
    is_online      = bool(data.get("online", False))
    players_online = data.get("players", {}).get("online", 0)
    players_max    = data.get("players", {}).get("max", 45)
    version        = data.get("version", "Inconnue")

    print(f"📡 Serveur : {'🟢 EN LIGNE' if is_online else '🔴 HORS LIGNE'}")
    if is_online:
        print(f"   Joueurs : {players_online}/{players_max}")
        print(f"   Version : {version}")

    # État précédent
    old = load_state()
    print(f"📂 Ancien état : {old}")

    updated = False

    # ── 1. Statut ──────────────────────────────
    if old["online"] != is_online:
        print("🔄 Statut changé → mise à jour du salon…")
        name = "🟢 Online" if is_online else "🔴 Offline"
        discord_patch(CHANNEL_STATUS, name)
        updated = True
    else:
        print("⏭️  Statut inchangé.")

    # ── 2. Joueurs ─────────────────────────────
    if old["players"] != players_online:
        print("🔄 Joueurs changés → mise à jour du salon…")
        discord_patch(CHANNEL_PLAYERS, f"👥 Joueurs : {players_online}/{players_max}")
        updated = True
    else:
        print("⏭️  Joueurs inchangés.")

    # ── 3. Version ─────────────────────────────
    if old["version"] != version:
        print("🔄 Version changée → mise à jour du salon…")
        discord_patch(CHANNEL_VERSION, f"🎮 Version : {version}")
        updated = True
    else:
        print("⏭️  Version inchangée.")

    # ── Sauvegarde du nouvel état ───────────────
    if updated:
        save_state({"online": is_online, "players": players_online, "version": version})
    else:
        print("✅ Aucun changement détecté, rien à mettre à jour.")


if __name__ == "__main__":
    main()
