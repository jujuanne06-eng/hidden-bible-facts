# Channel Blueprint — build another automated short-video channel

**Who this is for:** Claude, in a new conversation, asked by the owner (Waël) to create a new automated
TikTok + Instagram channel like *Fun Facts For Real*, but on a different topic.
**What it is:** the full recipe of a system that already works in production, plus every lesson learned
building it. Read it fully before doing anything. Reuse the reference implementation; do not reinvent it.

---

## 0. The reference implementation (copy it, don't rewrite it)

> **Updated 31 Oct 2026 after building the 2nd channel.** Copy **`C:\Users\wqach\hidden-bible-facts`** (repo
> `jujuanne06-eng/hidden-bible-facts`) rather than Fun Facts: it is newer (configurable style, crossfades,
> public-domain paintings, montage 2x faster, music never repeats, `posts_log.jsonl`, `tools/audit.py`).
> **Read section 9 first**: it lists what changed and the traps met on the 2nd channel.

- **Private GitHub repo:** `proutman123321-creator/fun-facts-shorts` (owner's account, GitHub CLI is installed
  and logged in: `"C:\Program Files\GitHub CLI\gh.exe"`).
- **Local copy:** `C:\Users\wqach\fun-facts-shorts`
- Everything below refers to files in that repo. For a new channel: **copy the repo into a new private repo**,
  then change only what is listed in section 4.

```
src/make_video.py   voice (edge-tts), captions, hook, accents, music mix, render (FFmpeg + Pillow)
src/footage.py      Pixabay search + clip filters + montage (camera moves, slow motion)
src/publish.py      Zernio API: upload, schedule, health, post status (with retries)
src/run_daily.py    daily job: slots, post times, checks, Telegram reminders, state
src/notify.py       Telegram messages + "is the post live?" checks
src/build_plan.py   builds the 1-year topic plan (730 topics, categories mixed)
src/add_content.py  merges content/*.json into topics.json + validates (hook length, video length)
config.json         mode, times, accounts, voice, hook/outro/caption templates, hashtags, Telegram chat id
topic_plan.json     730 planned topics (2/day for one year)
content/*.json      written topics: hook + 4 facts (3 + bonus) + keywords + 4 hashtags
assets/music/       royalty-free tracks + moods.json (mood per category)
assets/fonts/       Archivo Black (SIL OFL) — needed on Linux runners
.github/workflows/daily.yml   daily build+publish (04:00 UTC + 06:30 backup)
.github/workflows/notify.yml  post checks + Telegram, every 30 min around posting times
README.md           owner's user guide (keep it updated)
```

---

## 1. How the system works (architecture)

```
Monday 07:00 UTC   Claude cloud routine (owner's subscription) writes the next 60 topics
                   (hook + 4 facts, fact-checked with web search) -> commits content/ + topics.json
Daily 04:00 UTC    GitHub Actions: for each post time -> make video -> upload to Zernio -> schedule
(+06:30 backup)    -> Telegram "🎬 Scheduled" -> check accounts health + earlier posts -> save state.json
~18:00 / ~23:30    Zernio publishes on TikTok + Instagram (same video, same caption)
every 30 min       GitHub Actions notify.yml: asks Zernio if posts are live -> Telegram "✅ Published"
around post times  (with links) or "❌ problem"; reminders "🔔" before a connection expires
```

- Cost: **$0/month** (Zernio free for 2 accounts, GitHub Actions free minutes ~750/2000, Pixabay free,
  edge-tts free, the weekly routine runs on the owner's Claude subscription).
- The owner's PC is **not** needed. Never re-enable the old Windows scheduled task (`FunFactsShorts`).

---

## 2. Rules of engagement with the owner (important)

- The owner writes English and French, prefers **simple, non-technical explanations**, short and concrete.
- **Ask before installing anything.** Explain what it is and that it is safe (official source).
- **Never handle the owner's keys/passwords.** The owner pastes keys into `.env` (gitignored) and into
  GitHub Secrets himself. Never ask him to paste a key in chat. Never print `.env`.
- **Confirm before anything goes public.** Build and test in `"publish_mode": "draft"` first; switch to
  `"schedule"` only after explicit approval.
- **Show an example video before applying a style change to everything**, then wait for validation.
- When asked for an audit: run a full audit, fix every issue, **restart the audit from zero after each fix**,
  stop only at 0 non-conformity, and run a real test on GitHub (`mode=dry-run`).
- Things the safety classifier blocked before (don't retry, use the alternative):
  - writing GitHub secrets with `gh secret set` → owner adds secrets himself on the website
    (non-secret values like the Telegram chat id go in `config.json`);
  - a live Zernio "test" post → validate requests with `--dry-run` and real drafts instead.

---

## 3. Setting up a new channel — step by step

### 3.1 Ask the owner first (one round of questions)
1. Topic / niche and the angle (e.g. "dark history stories", "space facts", "French fun facts").
2. Language(s) — **one account per language** (owner's choice).
3. Format: keep "3 facts + bonus, just over 1 minute" unless asked otherwise (see 5.1 for why 1 minute).
4. Posts per day and times (current: 2/day, ~18:00 and ~23:30 Europe/Paris, ±35 min random = 12:00 and 17:30 New York,
   for the English-speaking audience).
5. Account names (TikTok + Instagram) and whether the accounts exist yet.

### 3.2 Accounts (owner does these; give him exact click paths)
- **TikTok:** keep a **personal** account (Creator Rewards only pays personal accounts; never enable
  "verified business"). Add a password or passkey. Profile picture + bio (no exact post times in bio).
- **Instagram:** **Creator** account (needed for the API), category Education/Digital creator.
  Do **not** enable "AI-generated profile". Same name/username as TikTok if possible.
- **Zernio** (zernio.com): free for the first **2** connected accounts; accounts 3+ cost **$6/month each**
  → tell the owner before connecting a 3rd/4th account. Connect TikTok + Instagram in Zernio, then list
  account ids with `python src/publish.py accounts` and put them in `config.json` → `languages.xx.accounts`.
- **Pixabay key:** reuse the same key (owner's `.env` / GitHub secret `PIXABAY_API_KEY`). Pexels paused new keys.
- **Telegram:** can reuse bot `@Fun_Facts_alertes_bot` and the same chat id, or create a new bot with @BotFather.
- **Claude GitHub app** must have access to the new repo (github.com/apps/claude → Configure) before
  creating the weekly routine, otherwise routine creation fails with 403.

### 3.3 Repo
1. Create a new **private** repo (`gh repo create <name> --private`), copy the reference files into it
   (not `.env`, `output/`, `state.json`, `notified.json`, `assets/clips/`, `preview/`, `.venv/`).
2. Reset `state.json` to `{"en": []}` (or the language key) and delete `notified.json`.
3. Owner adds GitHub secrets: `ZERNIO_API_KEY`, `PIXABAY_API_KEY`, `TELEGRAM_BOT_TOKEN`
   (Settings → Secrets and variables → Actions).
4. Local dev: `python -m venv .venv` then `pip install -r requirements.txt` (edge-tts, pillow, tzdata).
   FFmpeg on Windows: `winget install Gyan.FFmpeg` (already installed on this PC).

### 3.4 Content
1. Rewrite the categories and topic lists in `src/build_plan.py` for the new niche (730 topics, exact counts
   per category, no duplicates; the script checks it), set `START` date, run it → `topic_plan.json`.
2. Write month 1 yourself (60 topics) in `content/month01.json` with the format in section 4.3, run
   `python src/add_content.py` until it reports no problem.
3. Create the weekly routine (`/schedule` skill → RemoteTrigger) with the prompt in section 6, adapted to
   the niche. Remove unneeded MCP connections from it (`clear_mcp_connections: true`). Run it once to
   produce month 2, then **spot-check facts yourself** (one wrong number slipped through last time).

### 3.5 Test, then go live
1. `python src/run_daily.py --no-publish` locally → watch the videos.
2. GitHub: Actions → "Daily ..." → Run workflow `no-publish`, then `dry-run`, then `run` in **draft** mode
   (TikTok draft lands in the app inbox; max 5 pending drafts).
3. Owner approves → `"publish_mode": "schedule"` → push.
4. Run the full audit (section 7) until 0 non-conformity.

### 3.6 Running several channels (one repo per channel)
- **Zernio:** either one Zernio account per channel (free tier = 2 accounts each) or one Zernio account paying
  for accounts 3+. Zernio's ToS (zernio.com/tos, §3) forbids circumventing usage quotas and §8 allows
  termination "for any reason"; there is no explicit one-account-per-person rule. Ask Zernio support in
  writing before using several free accounts. Each repo has its own `ZERNIO_API_KEY` secret and account ids
  in `config.json`; health checks, post checks and reminders already use that repo's key.
- **Distinct content per channel** (Zernio content guidelines forbid near-identical posts across accounts).
- **GitHub Actions minutes:** 2,000 free min/month are shared by **all private repos** of the account; one
  channel uses ~750 → from the 3rd channel, make channel repos public (secrets stay secret), optimize, or pay.
- **Pixabay key** shared (100 requests/60 s): stagger the daily cron per channel (04:00, 04:20, 04:40 UTC…).
- **Telegram:** one bot/chat can serve all channels; every message must carry the channel name
  (`channel_name` in `config.json`, see below).
- **Stats dashboard** (`C:\Users\wqach\stats-hub`): reads each channel through its own Zernio key
  (`ZERNIO_API_KEY_<CHANNEL>` in its `.env`). Each channel repo keeps a permanent `posts_log.jsonl` and tags
  every Zernio post with `cat:<category>`, `topic:<topic id>`, `channel:<slug>` (lowercase, spaces → dashes)
  so the dashboard can group posts by category. *(Being added to fun-facts-shorts on 30 Oct 2026 if approved —
  check that `src/run_daily.py` writes `posts_log.jsonl` before relying on it.)*

---

## 4. What to change for a new topic

### 4.1 `config.json`
- `languages.<lang>`: `accounts`, `voice` (e.g. `en-US-AndrewNeural`, `fr-FR-HenriNeural`),
  `hook` template (`"{teaser} Wait for number three."`), `fact_labels`, `fact_marks`, `outro`, `badge`
  (`"3 CRAZY FACTS: {title}"`), `end_card`, `caption` (`"{title} facts you didn't know 🤯 {teaser} …"`),
  `hashtags` (account tag, so that topic tags (4) + this = **5 max**).
- `post_times`, `timezone`, `post_time_jitter_minutes` (35), `min_seconds` (61), `telegram_chat_id`.
- Adjust wording of labels/outro/badge to the niche (e.g. "3 dark secrets about {title}").

### 4.2 `assets/music/`
- Owner downloads 5–10 royalty-free tracks from **Pixabay Music** (he chooses by taste), each **longer than
  ~70 s**, no vocals. Map them to moods in `moods.json` and map every category of the plan to a mood.

### 4.3 Content format (`content/monthNN.json`)
```json
{"id": "<plan id>", "hook": "6-10 words, true, teased claim paid off by fact 3",
 "keywords": ["subject first, visual, specific", "...", "...", "..."],
 "hashtags": "#four #lowercase #topic #tags",
 "facts": ["30-43 words, ~37 on average", "30-43 words, ~37 on average", "30-43 words (the most surprising, explains the hook)", "bonus 30-43 words"],
 "paintings": ["Artist + exact artwork title, e.g. Caravaggio The Taking of Christ", "a second famous artwork"]}
```
`paintings` (Hidden Bible Facts): 2-3 Wikimedia Commons searches for famous artworks of the topic, painted
before about 1900 so they are public domain (Old Masters, Dore engravings, icons, 1890s photochroms of places).
Name artist + title, not a vague subject. `[]` when nothing fits (e.g. Advent): the video then uses footage only.
Writing rules for the voice: numbers in words, no digits, no symbols (% & $), no double quotes, no
parentheses, no emojis, no abbreviations. Only well-established facts; say "scientists think" when unsure.

---

## 5. Lessons learned (do not repeat these mistakes)

### 5.1 Platforms & money
- **TikTok Creator Rewards** pays only videos **over 1 minute**, on **personal** accounts, after 10k followers
  and 100k views/30 days → videos are built at **≥ 61 s** (`min_seconds`).
- **Instagram allows max 5 hashtags** per post since Dec 2025 (8 hashtags = risk of rejection). Captions with
  keywords matter more than hashtags for search.
- Don't put exact posting times in bios; times are randomized ±35 min so it doesn't look automated.
- Keep posts **≥ 2 hours apart** (a late run once scheduled two videos 3 minutes apart).
- Self-likes don't help and like-bots risk bans; no like automation. A first comment on Instagram is
  possible via Zernio `platformSpecificData.firstComment` (Reels support unconfirmed) — owner declined it.
- TikTok AI label is required for realistic AI imagery; real stock footage + synthetic voice likely doesn't
  need it (owner's decision).

### 5.2 Video style (validated by the owner after an expert-style critique)
- **Hook in the first 2–3 s**: short claim shown big and whole from frame 1 (not word by word), spoken
  immediately. Never a generic "Here are three crazy facts about…" intro (was 6.7 s, killed retention).
- Tease the most surprising fact (#3) in the hook → people stay for it.
- **Short outro** (~4 s) and a comment prompt before the bonus; no long frozen end card (≤ 3 s).
- Voice speed adapts (−4% to −10%) so the voice fills the minute; if still short, lengthen facts.
- **No whoosh on cuts** (owner found it unpleasant). Accents (flash + zoom punch) only on #1/#2/#3/BONUS.
- Montage: shot lengths 1.5–3.4 s (faster in the hook), 9 camera moves (zoom in/out, punch-in, 4 pans,
  tilt, handheld), ~25% slow motion, a new shot exactly when each fact starts.
- Safe zones: captions max ~820 px wide (right-side buttons), progress bar under the title (bottom is
  covered by the app UI). Long titles wrap on 2 lines in the banner.
- Music: chosen by mood per category, rotated so no track repeats twice in a row, **started after its quiet
  intro** (≥ 8 s, measured with ebur128), each track normalized to −30 LUFS, **ducking** under the voice
  (sidechaincompress), fade in/out, final mix loudnorm **−14 LUFS**. Skip tracks shorter than the video.

### 5.3 Stock footage (Pixabay)
- Use `video_type=film` (animations brought a cartoon pig into a chocolate video).
- Filter by tags: all query words (4-letter roots) or, loosely, the video's subject word; reject off-topic
  tags (carousel/fair/ride/cartoon/makeup/fashion/portrait…), reject clips whose **first tag is a person**
  unless the query asks for people, reject very dark clips (mean luma < 40). Seen failures: "octopus" →
  fairground ride, "cocoa beans" → mung bean sprouts, "melted chocolate" → melting ice/candles.
- Cache search results 24 h (Pixabay terms). Clips cached in `assets/clips` (GitHub Actions cache).

### 5.4 Technical traps
- FFmpeg 9.0.2 (Windows) crashes if `eq` comes **after** a per-frame `scale eval=frame` → put `eq` before.
- In FFmpeg filter expressions, commas must be escaped `\,`.
- Windows has no `seguibl.ttf` on Linux → ship a free font (Archivo Black) in the repo.
- edge-tts (free Microsoft voice) sometimes returns `NoAudioReceived` → retry up to ~8 min, but **never
  retry TypeError/ValueError** (a code bug once burned 7 minutes of retries). Don't name a variable `rate`
  next to the audio sample rate.
- Python on Windows needs `tzdata` for `zoneinfo`.
- GitHub: pin `runs-on: ubuntu-24.04` (ubuntu-latest moved to 26), checkout `ref: main` (backup runs must
  see the state saved by the first run), artifacts retention **3 days** (free storage 500 MB),
  `git pull --rebase` with retries before pushing state (weekly routine pushes too), concurrency groups.
- State: a topic counts as used **only after Zernio accepted it**; each slot ("2026-10-30 08:00") is
  remembered so a backup/manual run never posts twice; save state even if the job fails (`if: always()`).
- Zernio: `POST /v1/media/presign` → PUT file → `POST /v1/posts` with `scheduledFor` + `timezone`,
  `Idempotency-Key` header; TikTok needs `tiktokSettings` (privacy `PUBLIC_TO_EVERYONE`,
  `content_preview_confirmed`, `express_consent_given`); retry 408/409/425/429/5xx and network errors.
  Health: `GET /v1/accounts/{id}/health` (`canPost`, `tokenStatus.expiresIn`). TikTok token
  auto-refreshes; **Instagram token expires ~every 60 days** → reminders.
- The weekly routine runs plain `python3` without the venv: `add_content.py` must only import `common.py`.
- Telegram "✅ Published" can arrive up to ~30 min after posting (check job every 30 min) — expected.

---

## 6. Weekly routine prompt (template — adapt the niche words)

Create with RemoteTrigger: cron `0 7 * * 1` (UTC), model `claude-sonnet-5-5`, repo source the new repo,
tools `Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch`, then `clear_mcp_connections: true`.
Copy the current prompt from the existing routine "Fun facts - write next topics" (RemoteTrigger `get`
`trig_015K6jsrb5fKSc766tFZWhys`) and change only the niche description and examples. Its key steps:
1. If ≥ 100 written-but-unused topics: stop. 2. Take the next 60 plan topics without content.
3. Write `content/monthNN.json` (hook 6–10 words, 4 facts of 30–43 words (~37 avg; 45–60 made 94 s videos), keyword and hashtag rules).
4. Fact-check every fact and hook with WebSearch. 5. Run `python3 src/add_content.py` until clean.
6. Commit only `content/` + `topics.json`, `git pull --rebase`, push to main.

---

## 7. Audit checklist (must be all OK before saying "done")

GitHub: repo private · secrets present · both workflows active · 2 crons (main + backup) · ubuntu-24.04 ·
`ref: main` · state saved on failure · crash alert to Telegram · keys never in git history · `.env` ignored.
Config: public mode only after approval · post times + timezone · accounts set · Telegram chat set.
Code: compiles · PC launchers that could post twice disabled · old Windows task off.
Content: format/characters/no duplicates · every topic has a hook ≤ 12 words · every video ≥ 61 s ·
frozen end card ≤ 3 s · max 5 hashtags · ≥ 30 days of topics ahead · all titles fit the banner.
Music: ≥ 3 tracks longer than a video · moods.json valid for every category · tracks committed ·
no repeat twice in a row · start after intro.
Accounts: Zernio health OK for every account. Reminders configured (7/3/2/1 days, topics 20/10/4).
Then a real GitHub run (`dry-run`) must succeed. A reusable audit script lived in the old session's
scratchpad; rebuild it from this list if needed.

---

## 8. Owner's current setup (for reference)

- Channel: *Fun Facts For Real* — TikTok `fun_fact_for_real`, Instagram `funfact_for_real`, English,
  2 videos/day, public mode, Telegram bot `@Fun_Facts_alertes_bot`.
- French settings exist in `config.json` (`"fr"`, disabled) for a future French account.
- The owner wants to grow toward monetization; next step suggested: review real stats after 2–3 weeks
  (views, watch time, followers) and tune hooks, times and topics.

---

## 9. Lessons from the 2nd channel (Hidden Bible Facts, built 30 Oct 2026, live 31 Oct)

### 9.1 Accounts: one email per channel (owner's rule)
- The owner creates a **new email per channel** and uses it for everything: TikTok, Instagram, **GitHub**, Zernio,
  Pixabay. So a new channel = a **new GitHub account** (its own 2,000 free Actions minutes, no sharing).
- **Zernio support confirmed (30 Oct 2026)** that a 2nd free Zernio account for a separate channel is allowed.
- Steps that worked, in this order: owner creates the empty private repo on github.com (no README) → push with
  the login in the URL (`https://<login>@github.com/<login>/<repo>.git`) so Git Credential Manager asks for the
  right account → owner adds secrets on the website (paste Pixabay, Telegram, Zernio) → owner runs
  `& "C:\Program Files\GitHub CLI\gh.exe" auth login` (PowerShell needs the `&`) to add the account to `gh`
  (both accounts stay; `gh auth switch` changes the active one) → owner installs github.com/apps/claude on the
  new account, only on that repo.
- **Several GitHub accounts on one PC:** pin every local repo's remote to its login (`https://<login>@github.com/...`),
  otherwise Git Credential Manager can't choose and any non-interactive pull fails (it broke the stats-hub pull of
  Fun Facts until its remote was pinned).
- TikTok on a PC: the website has no "add account": use a private window, or the mobile app (username → Add account).
  Instagram: switch to **Creator** (Settings → Account type and tools), category Education.
- A GitHub secret is never shown again after saving: an empty box is normal. If the job says Zernio **401 "Invalid,
  revoked or expired API key"**, the secret was pasted wrong: paste it again from `.env`. The workflow
  `notify.yml` has a mode **`accounts`** (20 s) that checks the Zernio key from GitHub and lists the accounts.
- Brand-new GitHub accounts may run **one job at a time**: tests queue behind each other. Never launch duplicates.
- The owner sometimes renames `.env.example` instead of copying it: restore it with `git checkout -- .env.example`.

### 9.2 Video
- **Fact length: about 37 words (30-43)**, not 45-60: 45-60 gave 94 s videos. Real Fun Facts facts average 37.
- Voice: `en-US-ChristopherNeural` (deep, calm) at **+0%**. It is slower than Andrew: at -8% the video reached 87 s.
- Style is now in `config.json` → `"style"`: highlight color, shot lengths, camera moves, slow motion share,
  accent `glow` (soft) or `flash` (punchy), color `grade`, `crossfade_seconds`, `painting_every`, `painting_grade`.
  A calm channel: warm gold, 2.8-4.2 s shots, no shake/punch-in, 40% slow motion, glow, warm grade + vignette.
- **Paintings:** each topic can list 2-3 `paintings` searches (artist + exact title). The job searches Wikimedia
  Commons, keeps **only public-domain** files ≥ 900 px (no credit needed), retries on HTTP 429. Wide paintings are
  shown whole over a blurred copy (cropping cut out the main scene), tall ones fill the frame. **Exclude nudity and
  gore** (Adam and Eve, Deluge, Delilah, Last Judgment, severed heads, martyrdoms, executions): it cuts reach.
- **Montage 2x faster:** paintings are graded/framed once into a still, intermediate shots use `ultrafast` (a run of
  2 videos takes ~11 min on GitHub instead of 34).
- Block modern things in stock footage for a historical niche (Bitcoin, phones, cars, neon...): `OFF_TOPIC_TAGS`.
- Music: owner downloads Pixabay tracks (> 90 s, no lyrics); a track may sit in several moods; `pick_music` now
  guarantees the same track never plays twice in a row. Tracks shorter than the video are skipped.

### 9.3 Plan and content
- **Align the plan on the real launch day** (`START` in `build_plan.py`) and pin feast days (`SEASONAL`): the job
  posts topics in order, so a different start date shifts Christmas, Easter... Launch-week feasts (here Halloween,
  Reformation Day, All Saints) make a timely start.
- The weekly cloud routine **cannot reach commons.wikimedia.org** (blocked network): its prompt now tells it to
  still propose famous artworks; the daily job filters them. Spot-check its facts and paintings (nudity/gore).
- A respectful tone for a religious niche: history as history, belief as belief ("the Bible says", "tradition says").

### 9.4 Tests and launch
- Draft test: TikTok drafts land only in the **mobile app inbox** (Zernio keeps showing "uploading", normal);
  Instagram drafts stay **on zernio.com** (Instagram has no API drafts). Tell the owner to delete them, not post them.
- **A draft run marks its topics as used:** reset `state.json` to `{"en": []}` before going public.
- `dry-run` and `no-publish` never save state.
- Downloading TikTok videos with yt-dlp needs browser impersonation, which the safety system blocks: ask the owner
  to save reference videos himself; `tools/analyze_reference.py` (yt-dlp, faster-whisper, PySceneDetect in
  `.venv-analysis`) analyzes a local file (script, cuts, frames, loudness).
- **Audit:** `tools/audit.py` runs the whole section 7 checklist (+ timing, paintings, music rotation, accounts);
  fix, then run again until "0 problem(s)", then a GitHub `dry-run`.

### 9.5 Stats dashboard
- Each run appends to **`posts_log.jsonl`** (Zernio post id, topic, category, title, channel), committed with
  `state.json`. Stats Hub (`C:\Users\wqach\stats-hub`) pulls each channel repo before every sync (non-interactive).
- Add a channel in Stats Hub → Settings: name, the channel's Zernio key, the channel's project folder.
- Zernio post tags (`cat:`, `topic:`) are still **not** sent: not verified that the API accepts them.

### 9.6 Owner's channels now
| Channel | TikTok / Instagram | GitHub repo | Weekly routine |
|---|---|---|---|
| Fun Facts For Real | `fun_fact_for_real` / `funfact_for_real` | `proutman123321-creator/fun-facts-shorts` | trig_015K6jsrb5fKSc766tFZWhys (Mon 07:00 UTC) |
| Hidden Bible Facts | `hidden_bible_facts_real` (both) | `jujuanne06-eng/hidden-bible-facts` | trig_01PWhc48cFGpbyrtWgMs2exU (Mon 07:30 UTC) |
Both use the same Telegram bot; messages of the 2nd channel start with `[Hidden Bible Facts]`. Daily jobs are
staggered (04:00 and 04:20 UTC).
