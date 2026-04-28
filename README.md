# 🎮 Minecraft Discord Status Bot

Bot Discord qui met à jour automatiquement des salons vocaux avec le statut de ton serveur Minecraft, toutes les 5 minutes via GitHub Actions.

## Salons mis à jour

| Salon | Exemple |
|-------|---------|
| Statut | 🟢 Online / 🔴 Offline |
| Joueurs | 👥 Joueurs : 3/45 |
| Version | 🎮 Version : 1.21.4 |

---

## 🚀 Installation (5 minutes)

### 1. Créer le repo GitHub

- Crée un **nouveau repo public** sur GitHub (ex: `minecraft-discord-bot`)
- Clone-le localement et copie tous les fichiers dedans
- Push sur `main`

### 2. Ajouter le secret Discord

Dans ton repo GitHub :  
**Settings → Secrets and variables → Actions → New repository secret**

| Nom | Valeur |
|-----|--------|
| `DISCORD_BOT_TOKEN` | Le token de ton bot Discord |

### 3. Activer les workflows

Va dans l'onglet **Actions** de ton repo et clique sur **"I understand my workflows, go ahead and enable them"**.

### 4. Premier test manuel

Dans **Actions → Minecraft Status Bot → Run workflow** pour vérifier que tout fonctionne.

---

## ⚙️ Configuration

Tout se passe dans `bot.py`, section `CONFIGURATION` :

```python
MINECRAFT_SERVER = "play.cafevanille.com"   # ton serveur
GUILD_ID         = "620289546906632193"      # ID de ton serveur Discord
CHANNEL_STATUS   = "1432850727033897112"     # ID salon statut
CHANNEL_PLAYERS  = "1432850729995079770"     # ID salon joueurs
CHANNEL_VERSION  = "1453829805681414226"     # ID salon version
```

---

## 🔒 Permissions du bot Discord

Le bot doit avoir la permission **Manage Channels** sur le serveur Discord.

---

## 📁 Structure

```
├── bot.py                              # Script principal
├── state.json                          # État précédent (commité auto)
├── .github/
│   └── workflows/
│       └── minecraft-status.yml        # Cron GitHub Actions
└── .gitignore
```
