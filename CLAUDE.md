# CLAUDE.md – Competitive Intelligence Routine NetZero Academy

## Zweck
Wöchentliche Competitive-Intelligence-Analyse für netzeroacademy.de.
Ausführung: automatisch (Scheduled Routine), ohne manuelles Zutun.

---

## Technische Verbesserungen (aus vorherigen Läufen)

### Airtable
- `list_tables_for_base` liefert >250.000 Zeichen → **immer per Agent-Subagent delegieren**, nie direkt in Hauptkontext laden.
- `list_records_for_table` mit `pageSize=50` ebenfalls zu groß → **immer per Agent-Subagent delegieren**.
- `fieldIds` akzeptiert Feldnamen ODER Feld-IDs (case-sensitive). Den `sort`-Parameter bei der ersten Abfrage weglassen, da Feldnamen im Sort zu Validierungsfehlern führen können.
- Airtable-Base ID: `app4R2qm7WvWIFspd` (NetZero Academy Courses), Courses-Table: `tblH4U1AWOEVTkoNE`.
- Erster Airtable-Subagent soll: totalRecordCount, alle Felder + Feldnamen, und kompakte Kursliste (Titel, Kategorie, Start, Ende, Status, Preis) zurückgeben.

### WebFetch – bekannte 403-Seiten (Fallback: WebSearch)
Diese Seiten blockieren direkte Fetches – stattdessen WebSearch nutzen:
- geb-info.de, energie-experten.org, senercon.de, energie-fachberater.de
- netzeroacademy.de (eigene Seite), deneff.org, gih.de
- Für alle Verbands- und Wettbewerberseiten gilt: erst WebSearch, dann WebFetch nur wenn nötig.

### Discord
- Webhook (nur POST, kein Read): `https://discord.com/api/webhooks/1517499845256937597/...?thread_id=1517499777624047688`
- Für **2-Way-Interaktion** (User-Rückfragen aus Discord lesen): Requires Discord Bot Token (GET messages). Details → siehe Abschnitt "Offene Aufgaben".
- Bei HTTP 204: Erfolg. Bei 4xx: Fehlermeldung ausgeben und Notification trotzdem als PushNotification senden.

---

## Discord 2-Way-Interaktion – Implementierungsplan

**Ziel:** User kann in Discord-Thread auf Berichte antworten; nächste Routine-Ausführung liest diese Antworten und berücksichtigt sie.

**Was fehlt:** Discord Bot Token mit READ-Berechtigung für den Thread.

**Implementierungsschritte (sobald Bot Token vorhanden):**
1. Zu Beginn jedes Laufs: Discord-Thread-Messages der letzten 7 Tage per GET abrufen.
   ```
   GET https://discord.com/api/v10/channels/{thread_id}/messages?limit=20
   Authorization: Bot {BOT_TOKEN}
   ```
2. Nachrichten von Nicht-Bots filtern → das ist User-Feedback.
3. Feedback in den Analyse-Prompt als Kontext einbauen: „User-Feedback letzte Woche: [...]".
4. BOT_TOKEN als Umgebungsvariable `DISCORD_BOT_TOKEN` hinterlegen (in Routine-Settings).

**Bis dahin:** Rückfragen per E-Mail (info@netzeroacademy.de) oder als neuer Prompt-Start.

---

## Selbst-Verbesserungs-Protokoll

### KW 25 – 2026-06-19
**Gefundene Probleme:**
- Airtable-Abfragen zu groß für Hauptkontext → Subagent-Pattern etabliert.
- Viele Fachmedien-Seiten (geb-info.de etc.) geben 403 zurück → WebSearch-Fallback-Liste dokumentiert.
- `get_table_schema` erfordert mind. 1 fieldId im Array (nicht leer).
- `list_records_for_table` mit `sort` + Feldnamen schlug fehl → sort weglassen.

**Empfehlungen aus KW 25 (zum Tracking nächste Woche):**
1. 🔴 GModG-Update-Seminar entwickeln (4–6 UE, bis Aug 2026)
2. 🔴 Quereinsteiger Landing-Page: Flexibilitäts-Argument vs. Handwerks Schule
3. 🟡 Landing-Page: Preis-Benchmark vs. Campus EW (€4.080+)
4. 🟡 Energieberater:in Baudenkmale neu terminieren (Q4 2026)
5. 🟡 BEG-unabhängiges Messaging auf Kursseiten

---

## Feste Quellen-Priorität (je Kategorie)

### Verbände
| Verband | Primärquelle | Fallback |
|---|---|---|
| GIH | gih.de (oft 403 → WebSearch) | geb-info.de, WebSearch "GIH" |
| DEN | deutsches-energieberaternetzwerk.de | WebSearch "DEN Energieberater" |
| DENEFF | deneff.org (oft 403 → WebSearch) | WebSearch "DENEFF" |

### Wettbewerber Tier 1
| Anbieter | URL | Notiz |
|---|---|---|
| CQ Bildung | cq-bildung.de | Gut fetchbar |
| fup Leipzig | fup-umwelt.de | Gut fetchbar |
| Die Handwerks Schule | handwerksschule.de | Gut fetchbar |
| Campus EW | campus-ew.de | Gut fetchbar |
| ausbildung-zum-energieberater.de | ausbildung-zum-energieberater.de | Gut fetchbar |
| GUTcert | gut-cert.de | Gut fetchbar |

### Wettbewerber Tier 2
| Anbieter | URL |
|---|---|
| TÜV Rheinland | akademie.tuv.com |
| EIPOS | eipos.de |
| TAE Esslingen | tae.de |
| EBZ Akademie | ebz-akademie.de |
| HBC | hbc.de |

### Fachmedien (403-Fallback)
- energie-fachberater.de (403 → WebSearch)
- geb-info.de (403 → WebSearch)
- tga-fachplaner.de
- energie-experten.org (403 → WebSearch)

---

## Output-Format (VERBINDLICH ab KW26)

### Grundprinzip: NUR NEUES melden
- **Zu Beginn jedes Laufs:** das letzte Moves-File aus `intelligence/moves/` lesen (z.B. `KW25_2026.md`), um bekannte Moves zu kennen.
- Im Bericht erscheinen **ausschließlich Moves, die seit dem letzten Lauf NEU oder verändert sind.**
- Bereits gemeldete Moves NICHT wiederholen. Wettbewerber ohne neue Bewegung kommen in eine einzige "Keine Bewegung"-Zeile.

### Zwei-Ebenen-Struktur
**Ebene 1 — MOVES DER WETTBEWERBER (rein beschreibend, keine Farben):**
Pro Competitor die neuen Moves, jeweils mit Move-Typ-Tag:
| Tag | Bedeutung |
|---|---|
| 🆕 | Neuer Kurs / neues Angebot |
| ❌ | Kurs/Angebot eingestellt |
| 🔁 | Frequenz- oder Format-Änderung |
| 💶 | Preisänderung |
| 🤝 | Neue Partnerschaft |
| 📣 | Ankündigung / PR |
| 🌍 | Geografische Ausweitung |

**Ebene 2 — SO WHAT für NetZero (konsolidiert, priorisiert, MIT Handlungsempfehlung):**
- NICHT pro Competitor, sondern die 2–4 strategisch wesentlichen Erkenntnisse.
- Mehrere Moves dürfen zu einer Erkenntnis verdichtet werden (z.B. "zwei Anbieter senken Preise → Preiskampf").
- Hier (und NUR hier) wird mit 🔴/🟡 priorisiert.
- Jede Erkenntnis endet mit konkreter Handlungsempfehlung (→ ...).
- Fußzeile: "Noch offen aus Vorwochen: …" (Einzeiler, kein eigener Block).

### Template
```
📊 Market Intel · KW## · NetZero Academy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MOVES DER WETTBEWERBER

<Competitor>
  <Tag> <kurze Beschreibung des Moves>

Keine Bewegung: <Liste der gescreenten Anbieter ohne News>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SO WHAT — für NetZero

🔴 <Erkenntnis> → <Handlungsempfehlung>
🟡 <Erkenntnis> → <Handlungsempfehlung>

Noch offen aus Vorwochen: <Einzeiler>
```

### Logging (immer, auch in ruhigen Wochen)
- Jeden neuen Move ins Wochenfile `intelligence/moves/KW##_2026.md` schreiben (Taxonomie: NEW_OFFERING, PRODUCT_CHANGE, PRODUCT_END, PARTNERSHIP, MARKET_EXPANSION, PRICING_CHANGE, REGULATORY_RESPONSE).
- `intelligence/competitors.md` aktualisieren ("Letzter Move" + neu erkannte Anbieter).

### Discord / Notification-Regeln
- Discord: Farbe 15548997 (Rot) bei mind. einer 🔴-Erkenntnis im So-What
- Discord: Farbe 16744272 (Orange) bei nur 🟡-Erkenntnissen
- Discord: KEIN Webhook wenn es weder 🔴 noch 🟡 gibt (nur ⚪/keine neuen Moves)
- PushNotification: immer senden wenn es 🔴 oder 🟡 gibt
- Am Ende des Transkripts: Rückfragen-Block + Selbstverbesserungs-Commit
