"""
NetZero Academy – Competitive Intelligence Discord Bot
------------------------------------------------------
Antwortet direkt im Discord-Thread auf Fragen zur Wettbewerbssituation.

Voraussetzungen:
    pip install discord.py anthropic

Umgebungsvariablen:
    DISCORD_BOT_TOKEN   – Discord Bot Token (aus Developer Portal)
    ANTHROPIC_API_KEY   – Anthropic API Key

Start:
    python discord_bot.py
"""

import os
import discord
import anthropic
from pathlib import Path

THREAD_ID = 1517499777624047688

SYSTEM_PROMPT = """Du bist Competitive-Intelligence-Analyst für die NetZero Academy (netzeroacademy.de) – ein Online-Fernlehrgang-Anbieter für Energieberater-Qualifizierung (Wohn-, Nichtwohngebäude, Industrie) sowie Fachseminare (Wärmepumpe, PV, Denkmalsanierung).

Deine Aufgaben:
- Wettbewerber beobachten: CQ Bildung, fup Leipzig, Die Handwerks Schule, Campus EW, GUTcert, TÜV Rheinland, EIPOS u.a.
- Verbände verfolgen: GIH, DEN, DENEFF
- Regulierung einordnen: GEG/GModG, BEG, EnEfG, BAFA, KfW
- Empfehlungen formulieren: KOPIEREN / KOOPERATION / NEUES KURSPRODUKT / MARKETING RE-TIMING / BENCHMARKEN / IGNORIEREN

Antworte präzise und auf Deutsch. Wenn du aktuelle Infos brauchst die du nicht kennst, sage das klar.
Halte Antworten kompakt – maximal 400 Wörter, außer bei expliziter Bitte um Details.

Aktueller Stand (aus wöchentlichem Bericht KW 25, 19.06.2026):
- GModG ab ~Juli 2026: neue Energieausweise A-G, NWG-Pflicht zum Bedarfsausweis, Pflichtberatung beim Heizungstausch
- Die Handwerks Schule: Lehrgang auf 17 Wochen verkürzt, neuer Quereinsteiger-Kurs 01.09.2026
- Campus EW: neuer Lehrgangsstart Sep 2026 (WG €4.080, NWG bis €7.470)
- NetZero Portfolio: Basiskurs, WG/NWG-Vertiefung, Wärmepumpe, Professional aktiv buchbar
- Lücken: kein GModG-Update-Seminar, Baudenkmale-Kurs storniert ohne Neutermin
"""

def load_claude_md() -> str:
    path = Path(__file__).parent / "CLAUDE.md"
    if path.exists():
        return f"\n\nAktuelles CLAUDE.md (Verbesserungsprotokoll):\n{path.read_text()}"
    return ""


intents = discord.Intents.default()
intents.message_content = True
client_discord = discord.Client(intents=intents)
client_ai = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

conversation_history: dict[int, list] = {}


@client_discord.event
async def on_ready():
    print(f"Bot eingeloggt als {client_discord.user} (ID: {client_discord.user.id})")
    print(f"Lausche auf Thread-ID: {THREAD_ID}")


@client_discord.event
async def on_message(message: discord.Message):
    print(f"[MSG] author={message.author} bot={message.author.bot} channel_id={message.channel.id} type={type(message.channel).__name__} content={message.content[:30]!r}")
    if message.author.bot:
        return

    channel_id = message.channel.id

    is_target_thread = channel_id == THREAD_ID
    is_dm = isinstance(message.channel, discord.DMChannel)

    if not is_target_thread and not is_dm:
        return

    content = message.content.strip()
    if not content:
        return

    history = conversation_history.get(channel_id, [])
    history.append({"role": "user", "content": content})

    if len(history) > 20:
        history = history[-20:]

    system = SYSTEM_PROMPT + load_claude_md()

    response = client_ai.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system,
        messages=history,
    )

    reply = response.content[0].text

    history.append({"role": "assistant", "content": reply})
    conversation_history[channel_id] = history

    # Discord-Limit: 2000 Zeichen pro Nachricht
    for chunk in [reply[i:i+1900] for i in range(0, len(reply), 1900)]:
        await message.channel.send(chunk)


if __name__ == "__main__":
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        raise SystemExit("Fehler: DISCORD_BOT_TOKEN nicht gesetzt.")
    client_discord.run(token)
