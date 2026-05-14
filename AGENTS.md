# AGENTS.md — IronKeeper Bot Architecture & Guidelines

## Quick Start for AI Agents

**IronKeeper** is a Discord bot for managing PvP game boss spawn timers. It's built with `discord.py` and stores timers in CSV for persistence across restarts.

### Essential Reading Order
1. `main.py` — Bot initialization and cog registration
2. `commands/time_management.py` — Core timer logic and command handlers
3. `features/time_keeper.py` — In-memory timer store and duplicate checks
4. `models/boss_timer.py` / `models/war_timer.py` — Timer data models
5. `utilities/helpers.py` — Helper utilities and validation
6. `config/constants.py` — Boss definitions and enums

---

## Architecture Overview

### Component Boundaries

- **Commands Layer** (`commands/`): Discord command cogs. Each cog is a `commands.Cog` subclass registered in `main.py`.
- **Feature Layer** (`features/`): `TimeKeeper` class manages timer state (in-memory list + CSV persistence).
- **Models** (`models/`): `BossTimer` and `WarTimer` dataclasses with `id`, `name`, `key`, `start_time`, `due_time`, `territory`.
- **Config** (`config/`): Constants (`bosses`, `events`, `Territories` enum) and runtime settings via `BotConfig` cog.
- **Utilities** (`utilities/`): Helpers for boss lookup, parsing, formatting, and owner checks.

### Timer Lifecycle

1. **Create**: User runs `!t <boss-key> [territory] [offset]` in Discord.
2. **Store**: `TimeManagement.handle_boss()` → `TimeKeeper.add_timer()` stores `BossTimer` in memory.
3. **Schedule**: `bot.loop.create_task(dispatch_notification(...))` schedules async sleep until spawn time.
4. **Dispatch**: When sleep completes, `bot.dispatch('timer_expired', channel_id, timer)` fires event.
5. **Notify**: `on_timer_expired()` listener sends Discord message, removes timer from store, saves to CSV.
6. **Persist**: `TimeKeeper.save_timer_state()` writes current timers to `data/timers.csv`.
7. **Reload**: On bot restart, `setup_time_management()` loads timers from CSV in `main.py`.

**Key Detail**: Timers only notify once. If a timer's due time passes before the bot can send the message, it's silently skipped (check in `on_timer_expired` line 181).

### Two Timer Types

- **BossTimer**: Spawns occur at fixed intervals. Offset (minutes early) subtracted from spawn time.
- **WarTimer**: War events scheduled for specific datetime. Notifies 1 hour before start.

---

## Project-Specific Conventions

### Time Handling
- Boss `time` values in `config/constants.py` are **always in minutes**.
- When computing sleeps/respawns, **multiply by 60** to get seconds: `(boss['time'] - offset) * 60`.
- Epoch timestamps use Unix epoch (seconds).

### Territory Logic
- Enum: `Territories.Neutral`, `Territories.BCU`, `Territories.ANI`, `Territories.Both`.
- **Bosses with `Territories.Both`** require explicit `ANI` or `BCU` argument in command.
- Territory stored as uppercase string (`'ANI'` or `'BCU'`): see `BossTimer.__init__` line 10.
- Validation: `validate_input_for_boss()` in `helpers.py` enforces this rule.

### Boss Lookup
- Always use `find_boss(key)` from `utilities.helpers` (case-insensitive on key or name).
- Returns full boss dict: `{'name': '...', 'key': '...', 'time': minutes, 'map': Territories.X}`.
- Return `None` if not found.

### Owner Permissions
- Admin commands use `@require_bot_owner()` decorator (line 14 in `helpers.py`).
- Owner list in `config/constants.py`: `admins = ['xattus']` (Discord username).
- Raises `NotBotOwner` exception; handled in `main.py` `on_command_error`.

### Discord Formatting
- Use Discord timestamp: `<t:{epoch}:R>` (relative time, e.g. "in 2 hours").
- Full datetime: `<t:{epoch}:f>` (e.g. "April 29, 2026 3:45 PM").
- Preserve these formats in outputs; see `output_boss_timer_data()` in `helpers.py`.

### CSV Persistence
- Headers: `config/constants.py` → `CSV_HEADERS_TIMERS`.
- Schema: `['id', 'timer_type', 'key', 'name', 'start_time', 'due_time', 'territory']`.
- Timer models must implement:
  - `to_csv_row()`: return dict matching headers.
  - `from_csv_row(row)` classmethod: reconstruct from CSV dict.
- Atomic write via temp file in `utilities/persistence.py`.
- Expired timers filtered on load (line 65: skip if `due_time < current_time`).

---

## Critical Data Flows

### Adding a Boss Timer
```python
# User: !t hq ANI 30
boss = find_boss('hq')                           # Look up in constants.bosses
parsed = parse_timer_args(boss, ('ANI', '30'))   # Extract territory, offset
validate_input_for_boss(boss, 'ANI')             # Verify required for Territories.Both
timer = BossTimer(boss, time.time(), 'ANI', 30)  # Create with offset
time_keeper.add_timer(timer)                     # Store in-memory; auto-assign ID
bot.loop.create_task(dispatch_notification(...)) # Schedule asyncio sleep
time_keeper.save_timer_state()                   # Write to CSV
```

### Restarting Timers
- Command: `!restart_timers` (TimeManagement cog).
- For each in-memory `BossTimer`, derive original offset from `(due_time - start_time) / 60`, then recreate with current time.
- Removes old timer (so stale scheduled tasks are ignored), adds new one, reschedules notification.
- **Gotcha**: Offset derived from elapsed time; rounding errors possible.

### Duplicate Prevention
- `TimeKeeper.check_duplicate(boss_or_event, territory)` called before adding timer.
- For `Territories.Both` bosses: checks if same boss + territory combo exists.
- For other bosses: checks if any timer with same key exists (ignores territory).
- Returns `True` if duplicate found; command rejects and tells user.

### War Event Auto-Rescheduling
  
  When a war timer expires for configured recurring events (Akron, Rakion, Castle Corona), 
  the bot automatically creates a new timer scheduled for exactly 5 days in the future.
  
  - **Config**: `BotConfig.auto_reschedule_wars` (boolean toggle)
  - **Recurring events**: Defined in `RECURRING_WAR_EVENTS` constant
  - **Admin commands**: `!toggle_war_reschedule` to enable/disable, `!show_recurring_wars` to view
  - **Discord notifications**: Both expiration and rescheduling messages sent to war channel

---

## Stats Management System

### Overview
The stats system fetches player and brigade rankings from an external game API (oldschoolrivals.com), calculates week-over-week fame changes, and posts formatted leaderboards to Discord. **`BrigStats` cog is active; `NationStats` is a stub (not implemented).**

### Architecture

**Components:**
- `web_requests.py`: Fetches live rankings data via HTTP from oldschoolrivals.com API.
- `models/brig_member.py`: Represents a player with `name`, `level`, `gear` (letter-coded), `fame`, and `fame_diff`.
- `commands/brig_stats.py`: Cog that schedules weekly updates, compares stats, formats output, and saves to CSV.
- `commands/nation_stats.py`: Stub for future nation-wide stat tracking (not functional).

### Stats Lifecycle

1. **Load**: On cog initialization, `cog_load()` calls `load_members_from_csv()` and `load_brig_stats_from_csv()` to restore previous stats from CSV files via factory functions.
2. **Schedule**: `@tasks.loop(time=datetime.time(hour=12, minute=0))` in `BrigStats.__init__` starts scheduler at noon UTC every Monday.
3. **Fetch**: `request_rankings_data(brigade_name)` calls oldschoolrivals.com API with `limit=10` for members across 4 categories (b, i, a, m) and brigade rankings. Individual request times and total API time are printed to console.
4. **Filter**: API responses filtered client-side by brigade name; top 10 brigade results stored.
5. **Compare**: `calculate_member_fame_diff()` and `calculate_brig_fame_diff()` compute `fame_diff = current - previous` (case-insensitive name matching for members).
6. **Format**: `create_members_table()` and `create_brigs_table()` generate monospace tables with columns: Name | Level | Gear | Fame | Diff.
7. **Post**: Tables sent to Discord channel (channel ID from `BotConfig.stat_channel_id`).
8. **Persist**: Current stats saved to CSV via `save_data_to_csv()` for manual inspection; becomes `previous_stats` for next run.

**Data Models:**

**BrigMember:**
```python
BrigMember(name, level, gear, fame)  # gear is numeric (1=B, 16=M, 256=A, 4096=I); converted on setter
member.fame_diff = 0                 # Set during comparison phase
member.to_csv_row()                  # Returns dict for CSV row
member.from_csv_row(row)             # Classmethod to reconstruct from CSV
```

**Brigade:**
```python
Brigade(name, monthly_fame, nation=0, total_fame=0)
brigade.fame_diff = 0                # Set during comparison phase
brigade.to_csv_row()                 # Returns dict for CSV row
brigade.from_csv_row(row)            # Classmethod to reconstruct from CSV
```

**Rankings API Response (filtered to brigade):**
```json
{
  "ranking": {
    "players": [
      {"Name": "PlayerName", "Level": 100, "Gear": 256, "Fame": 5000, "Guild": "BrigadeName"},
      ...
    ],
    "brig": [
      {"Name": "BrigadeName", "TotalFame": 50000, "MonthlyFame": 10000, "Nation": 2},
      ...
    ]
  }
}
```

### Key Patterns

**Stat Update Flow (same every Monday at noon):**
```python
# 1. Fetch fresh data
fresh_stats = request_rankings_data(brigade_name)  # Returns {"members": [...], "brigs": [...], "full": [...]}

# 2. Compare with previous (calculates fame_diff, sorts by descending fame_diff)
current_members = calculate_member_fame_diff(fresh_stats["members"], previous_members)
current_brigs = calculate_brig_fame_diff(fresh_stats["brigs"], previous_brigs)

# 3. Format for Discord
members_table = create_members_table(current_members)  # Monospace table
brigs_table = create_brigs_table(current_brigs)

# 4. Send to channel
await channel.send(f"```{members_table}```")
await channel.send(f"```{brigs_table}```")

# 5. Save for next week
save_data_to_csv(current_members, CSV_HEADERS_MEMBER_STATS, 'member_stats', path)
```

**Gear Code Conversion:**
- API returns numeric codes: `1 → 'B'`, `16 → 'M'`, `256 → 'A'`, `4096 → 'I'`.
- Conversion happens in `BrigMember.gear` setter; invalid/unknown values set to `None`.

**Manual Trigger:**
- `!stats` command runs `update_stats()` immediately (admin-only via `@require_bot_owner()`).
- Useful for testing or forcing an update outside the Monday noon window.

### CSV Persistence

**Member Stats Headers:** `['name', 'level', 'gear', 'fame', 'fame_diff']`  
**Brigade Stats Headers:** `['name', 'nation', 'total_fame', 'monthly_fame', 'fame_diff']`

Files:
- `data/member_stats.csv`: Loaded on cog init via `load_members_from_csv()` with `BrigMember.from_csv_row()` factory.
- `data/brig_stats.csv`: Loaded on cog init via `load_brig_stats_from_csv()` with `Brigade.from_csv_row()` factory. Same atomic write pattern as timers.

**Loading Pattern (both methods use same factory approach):**
```python
def load_members_from_csv(self):
    """Load brig member stats from CSV file and populate previous_member_stats."""
    def member_factory(row):
        return BrigMember.from_csv_row(row)
    members = load_from_csv(self.member_persistence_path, CSV_HEADERS_MEMBER_STATS, member_factory)
    self.previous_member_stats = members
```

### External API Integration

**Endpoint:** `https://oldschoolrivals.com/action/ranking/`

**Supported Ranking Types:**
- **Players**: `/players/Fame/{faction}` where faction is `b`, `i`, `a`, `m` (4 separate requests).
- **Brigade**: `/brig/MonthlyFame`

**Parameters:**
- `limit`: Number of results (hardcoded to 10 for top-10 fetch).
- `timeout`: 10 seconds per request.
- HTTP method: GET, JSON response expected.

**Performance Monitoring:**
- Individual request times printed to console (e.g., "→ b request completed in 0.45s").
- Total API call time printed after all requests complete (e.g., "Total API call time: 2.09s").
- Uses `time.perf_counter()` for accurate microsecond-precision timing.

**Error Handling:**
- `requests.raise_for_status()` will raise on 4xx/5xx responses; not caught — will crash the update.
- No retry logic or circuit breaker.
- If API is down during Monday noon update, users don't get notified and `previous_stats` remains stale.

### Brigade Filtering

- `brigade_name` passed from `BotConfig.brigade` (set via `!set_brigade` admin command).
- Members filtered by `member["Guild"] == brigade` (case-sensitive on API response).
- Only members in the specified brigade are included in the table.
- **Top 10 brigades always fetched and stored**, regardless of bot's configured brigade.

---

## Integration Points & External Dependencies

### Environment Variables (from `.env`)
- `DISCORD_TOKEN`: Bot token (required).
- `BRIGADE`: Brigade name/ID (optional, used for stats filtering).
- `WAR_CHANNEL_ID`, `BOSS_CHANNEL_ID`, `STAT_CHANNEL_ID`: Discord channel IDs (required for notifications).
- `IT_PVP_ROLE_ID`, `IT_BOSS_HUNTER_ROLE_ID`: Discord role IDs (used for @mentions).

### External Libraries
- `discord.py`: Bot framework, intents, cogs, listeners, events.
- `python-dotenv`: Loads `.env` for environment variables.
- `requests`: Used by `commands/brig_stats.py` and `utilities/web_requests.py` for API calls.

### Key Intents
- `intents.message_content = True`: Required to read command arguments.
- `intents.members = True`: Required for member role management.

---

## Common Tasks & Patterns

### Adding a New Command
1. Create method in existing Cog or new Cog in `commands/`.
2. Decorate with `@commands.command()` and `@require_bot_owner()` if admin-only.
3. Register Cog in `main.py` `main()` function: `await bot.add_cog(YourCog(bot))`.
4. Implement async handler; use `ctx.send()` for responses.

### Adding a New Boss or Event
- Boss: Add dict to `config/constants.py` → `bosses` list. Keys: `name`, `key`, `time` (minutes), `map` (Territories enum).
- Event: Add dict to `events` list. Keys: `name`, `key`, `datetime` (None until scheduled).
- Ensure `key` is unique and lowercase.

### Modifying Output Format
- Timer lists: Edit `output_boss_timer_data()` and `output_event_timer_data()` in `utilities/helpers.py`.
- Stats tables: Edit `create_members_table()` or `create_brigs_table()`.
- Preserve Discord timestamp format for readability.

### Working with Stats Data

**Fetching fresh rankings:**
```python
from utilities.web_requests import request_rankings_data
fresh_stats = request_rankings_data("YourBrigade")
# Returns: {"members": [BrigMember(...), ...], "brigs": [{dict}, ...], "full": [{dict}, ...]}
```

**Computing fame differences:**
```python
from utilities.helpers import calculate_member_fame_diff, calculate_brig_fame_diff
members_with_diff = calculate_member_fame_diff(current_members, previous_members)
# Sets fame_diff on each member; sorts by fame_diff descending
brigs_with_diff = calculate_brig_fame_diff(current_brigs, previous_brigs)
# Sets 'Diff' key on each brigade dict; sorts by MonthlyFame descending
```

**Saving stats to CSV:**
```python
from utilities.persistence import save_data_to_csv
from config.constants import CSV_HEADERS_MEMBER_STATS
save_data_to_csv(members, CSV_HEADERS_MEMBER_STATS, 'member_stats', 'data/member_stats.csv')
# Calls to_csv_row() on each object; atomic write to temp file then replace
```

**Scheduling recurring tasks:**
```python
from discord.ext import tasks
import datetime

@tasks.loop(time=datetime.time(hour=12, minute=0))
async def my_scheduler(self):
    if datetime.datetime.now().weekday() == 0:  # Monday
        await self.do_something()

def cog_unload(self):
    self.my_scheduler.cancel()  # Must cancel on unload
```

### Handling Restart Edge Cases
- **Lost timers**: All in-memory timers lost if bot crashes without save. CSV is only backup.
- **Stale tasks**: If a timer is removed mid-sleep, the scheduled notification task still fires. Guarded by `exists()` check in `on_timer_expired`.
- **Offset rounding**: `restart_timers` derives offset; may drift if elapsed time doesn't align with multiples of 60.
- **Stale stats**: If API fails during scheduler run, previous stats remain in memory unchanged. Manual `!stats` can retry.

---

## Debugging Checklist

- **Command not recognized?** Check Cog is registered in `main.py` and `message_content` intent is enabled.
- **Timer not notifying?** Verify channel ID is set and valid. Check `dispatch_notification()` print statement in logs.
- **Duplicate error on valid input?** Review `check_duplicate()` logic; territory handling for `Territories.Both` bosses.
- **CSV load fails?** Check `data/` directory exists, file not corrupted, headers match `CSV_HEADERS_TIMERS`.
- **Timestamp formatting wrong?** Ensure epoch is Unix (seconds), not milliseconds. Use `int(time.time())`.
- **Stats not updating on Monday?** Check `stat_channel_id` is set (`!set_stat_channel`). Verify oldschoolrivals.com API is accessible. Check bot's system clock (scheduler uses local timezone from `datetime.datetime.now()`).
- **Empty member table?** Brigade name may be case-sensitive or not found in API. Verify `!set_brigade` was called with exact game guild name.
- **Gear shows as `None`?** API returned unexpected gear code; check `BrigMember.gear` setter mapping.
- **`fame_diff` all zeros?** `previous_stats` is empty (first run). Wait for next Monday's run; `current` becomes `previous` for next comparison.

---

## Known Gotchas & Limitations

- **No DB**: All timers in memory. Restart = loss of unsaved timers.
- **Single-notify**: Timers notify once. No recurring or retrying logic.
- **No persistence of config**: `BotConfig` properties reset on restart; must re-run admin commands to set channel/role IDs.
- **Territory case-sensitivity**: Stored uppercase but input is case-insensitive; always normalize in code.
- **Offset boundary**: Must validate `offset < boss['time']` to avoid negative/nonsensical sleeps.
- **Timezone-agnostic**: Timestamps are Unix epoch; all times UTC. No local timezone handling.
- **Stats API single-point-of-failure**: No retry logic; if API is down during Monday noon, update silently fails and users see nothing.
- **Brigade name case-sensitive**: API filtering on `Guild == brigade` is case-sensitive; mismatch results in empty member list.
- **NationStats incomplete**: Cog loads but `update_stats()` is a no-op; scheduler runs but does nothing.




