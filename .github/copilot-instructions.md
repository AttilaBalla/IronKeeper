## Quick context for AI contributors

This repo is a small Discord bot (Python, discord.py) that manages boss spawn timers for a game. The bot is organized as:

- `main.py` — bootstraps the bot, sets intents and registers cogs (`commands.TimeManagement`, `commands.Admin`).
- `commands/` — discord command cogs. Look at `time_management.py` and `admin.py` for command patterns and permission checks.
- `features/` — core domain logic: `boss_timer.py` (single timer) and `boss_time_keeper.py` (in-memory timer store and duplicate checks).
- `config/` — settings and constant data. `constants.py` contains `bosses` and `Territories` enum.
- `utilities/helpers.py` — shared helpers: boss lookup, parsing CLI-like command args, output formatting, and owner checks.

Read these files in order when you need the big picture: `main.py` -> `commands/time_management.py` -> `features/*` -> `utilities/helpers.py` -> `config/constants.py`.

## Architecture and data flow (short)

- Commands are implemented as discord.py Cogs. `main.py` registers cogs with `bot.add_cog(...)` and then `bot.start(token)`.
- The primary flow for adding a timer:
  1. `!t <key> [territory] [offset]` in `commands/time_management.py`
  2. `utilities.find_boss` (looks up `config.constants.bosses` by key or name)
  3. `features.BossTimer` created and `features.BossTimeKeeper.add_timer` stores it in memory
  4. A delayed notify is scheduled via `asyncio.sleep(...)` and then `bot.dispatch('notify_spawn', ...)`
  5. `on_notify_spawn` listener sends the Discord message and removes the timer from the keeper

All timers live in memory (no DB). IDs are integer counters assigned by `BossTimeKeeper`. Time values in `bosses` are minutes.

## Project-specific conventions to follow

- Time units: `boss['time']` is always minutes. When computing sleeps or respawn timestamps multiply by 60.
- Boss records: each boss in `config/constants.py` has `name`, `key`, `time` (minutes), and `map` (use the `Territories` enum).
- Keys are lowercase short strings (e.g. `hq`, `hk`). Use `find_boss(key)` to locate bosses.
- Territory handling: some bosses have `Territories.Both` — in those cases the command requires an explicit `ANI` or `BCU` territory. See `utilities.validate_input_for_boss`.
- Permissions/owner checks: use `require_bot_owner()` decorator from `utilities.helpers` (Admin commands rely on it).
- Discord formatting: timers output uses Discord timestamp formatting like `<t:{epoch}:R>` — preserve this when changing outputs.

## Important integration points & secrets

- Token currently read from `config/secret.py` as `token`. This file currently contains a literal token in the repo — treat as a secret. Do not hard-code or commit real tokens.
- Recommended runtime pattern: prefer reading the token from an environment variable and keep `config/secret.py` out of source control.


Example (how the bot is started):

```powershell
python main.py
```

Using a local `.env` file:

- A safe example is provided at `.env.example`. Copy it to `.env`, fill `DISCORD_TOKEN`, and the repo includes a `.gitignore` entry to prevent committing `.env`.
- Recommended workflow (PowerShell):

```powershell
copy .env.example .env
#$env:DISCORD_TOKEN = 'your_token_here' # alternative: set in session
python main.py
```

`main.py` uses `asyncio.run(main())` and registers cogs before starting.

## What to edit when adding features

- New command: add a Cog in `commands/`, register it in `main.py` with `await bot.add_cog(YourCog(bot))`.
- Persistent data: there is none. If you add persistence, update `features/boss_time_keeper.py` to store/load state and ensure notifications handle restarts.
- Boss data changes: update `config/constants.py` (follow existing object shape). Keep `key` unique.

## Files to inspect for quick troubleshooting

- `main.py` — start-up, intents, and cog registration
- `commands/time_management.py` — parsing and main timer command `t`
- `utilities/helpers.py` — parsing helpers and owner check decorators
- `features/boss_time_keeper.py` — in-memory storage; duplicates and removal logic
- `config/constants.py` — canonical boss definitions

## Examples to copy from the codebase

- Command decorator pattern:

```py
@commands.command()
async def t(self, ctx, key, *args):
    boss = find_boss(key)
    ...
```

- Scheduling a spawn notification (see `time_management.dispatch_spawn_notification`):

```py
await asyncio.sleep((boss['time'] - offset) * 60)
bot.dispatch('notify_spawn', ctx, timer)
```

## Known limitations / gotchas (discoverable)

- No persistence — all timers are lost on process restart.
- The bot relies on message content intent (`intents.message_content = True`). If permission changes on Discord developer portal, commands may stop working.
- `config/secret.py` currently exposes `token` in plaintext in the repository; rotate it and switch to env vars before sharing the repo publicly.

If anything here is unclear or you'd like examples expanded (more code snippets, how to add persistence, or a safe token pattern), tell me which section to expand and I will iterate.
