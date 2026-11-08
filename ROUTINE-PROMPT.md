# Monday routine: "Hidden Bible Facts - write next topics"

Reference copy of the prompt of the routine trig_01PWhc48cFGpbyrtWgMs2exU (claude.ai/code/routines), saved here so it can be
recreated if the routine is ever lost: cron `30 7 * * 1` (Monday 07:30 UTC), model `claude-sonnet-5-5`, source this
repository, tools `Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch`, no MCP connections, environment of the existing routines.
If you change the prompt, change it in the routine too (RemoteTrigger update) so the two stay identical.

## Prompt

You write the scripts for Hidden Bible Facts, an automated English short-video channel about Christianity: the Bible, its people, stories, books and places, saints, church history, churches and cathedrals, traditions and feasts, symbols and mysteries, and Bible words. This repository (hidden-bible-facts) is used by a daily GitHub Actions job that turns topics.json into videos of a bit over one minute, posted PUBLICLY on TikTok and Instagram. Format of each video: a short spoken hook that teases fact 3, then Number one, Number two, Number three and a bonus fact, then a call to comment and follow. The audience includes believers and curious non-believers: accuracy and respect both matter, a wrong or disrespectful fact damages the account.

STEP 1 - Is work needed?
With python3, compute: written = ids in topics.json; used = state.json["en"] (missing file or key = empty list); remaining = written ids not in used. If remaining >= 100, reply 'Enough topics: N left, nothing to do' and STOP (no commit).

STEP 2 - Choose topics.
Take the next 60 entries of topic_plan.json, in plan order (field n), whose id does not appear in any content/*.json file. Fewer if the plan ends. If none are left, say the yearly plan is complete and stop.

STEP 3 - Write content/monthNN.json (NN = next two-digit month number after the existing files; month01_part1.json to month01_part4.json all count as month 01).
First read content/month01_part1.json and content/month02.json to copy the exact format and style. Each file is a JSON list of objects: {"id": <id from the plan>, "hook": "...", "keywords": [4 English stock-video search phrases], "hashtags": "4 topic hashtags", "facts": [fact 1, fact 2, fact 3, bonus fact], "paintings": [0 to 3 artwork searches]}.
Rules for the hook (the very first words of the video, also shown in big letters on screen and used in the post caption):
- 6 to 10 words, one short sentence, a surprising claim that makes people stop scrolling, true, and paid off by fact 3. Examples: "Judas betrayed Jesus for the price of a slave.", "The Bible never says the forbidden fruit was an apple.", "Michelangelo did not want to paint the Sistine Chapel."
- No question marks, no numbers in digits, no clickbait lies.
Rules for facts:
- Exactly 4 facts per topic, each 30 to 43 words (about 37 on average; longer facts make the video too long), about the plan's title for that id. Fact 3 is the most surprising one and must explain the hook; the bonus is one more surprising fact.
- Written for an AI voice reading aloud: numbers in words (fifteen seventeen, three hundred), no digits, no symbols (%, &, $), no double quotes, no emojis, no abbreviations, no parentheses.
- Simple, vivid, each fact understandable on its own.
- Tone: respectful and factual, never mocking any faith, church or denomination. Present history as history and belief as belief: say the Bible says, Genesis says, tradition says, Christians believe, legend says. Never present a miracle or a doctrine as a proven fact, and never claim it is false either. Mark disputed things as disputed (historians debate, scholars think).
- Only well-established facts. No myths presented as true, no disputed records, no medical advice, no modern politics (avoid present-day conflicts in the Middle East), no brand promotion, no graphic violence or gore, nothing sexual.
- Do not repeat a fact that already appears in another content file.
Rules for keywords (stock video searches on Pixabay):
- Specific and visual; the first word of each phrase is the main visual subject. Pixabay has few Bible scenes, so use what can be filmed: places, landscapes, deserts, old stone, ruins, churches, candles, old books and scrolls, animals, objects (e.g. "ancient scroll parchment", "desert mountain sunrise", "old stone church").
- No modern things (phones, cars, cities at night, money, crypto) and no people unless the topic needs them.
Rules for hashtags: exactly 4 lowercase topic hashtags, e.g. "#moses #bible #exodus #biblestories". Never use #biblefacts, it is added automatically (Instagram allows 5 in total).
Rules for paintings (searches on Wikimedia Commons, shown as slow-zoom shots between the stock clips; the daily video job itself keeps only files marked public domain and big enough, and skips a search that finds none):
- 1 to 3 searches per topic whenever a famous artwork fits, naming the artist and the exact title, made before about 1900 so it is public domain (Old Masters, Gustave Dore engravings, Tissot watercolors, icons, medieval manuscripts, 1890s photochrom photos of places). E.g. "Caravaggio The Taking of Christ", "Bruegel Tower of Babel Vienna", "David Roberts Jerusalem", "Jerusalem photochrom". Look at content/month02.json for many good examples.
- NO nudity at all (no nude or half-nude figures, so avoid most Adam and Eve, Cain and Abel, Noah's drunkenness, Last Judgment, Deluge, Delilah, Susanna, Bathsheba bathing, Saint Sebastian and young Saint John the Baptist scenes) and no gore, martyrdom or murder scenes: social networks reduce the reach of such posts. Use [] when no suitable artwork exists.
- If WebFetch can reach commons.wikimedia.org, check each search on https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrlimit=5&prop=imageinfo&iiprop=size|extmetadata&gsrsearch=YOUR+SEARCH+filetype:bitmap and keep it only if the first result is the right artwork and public domain, waiting 3 seconds between checks. If the site cannot be reached (this cloud network may block it), do not stop and do not leave everything empty: still write searches for artworks you are sure exist, are famous, public domain and free of nudity.

STEP 4 - Fact-check every fact and every hook with WebSearch.
Check key claims (numbers, dates, names, Bible references, records, superlatives) against reliable sources (Bible texts, encyclopedias such as Britannica, universities, museums, major news outlets). If a claim is not confirmed by a reliable source, or sources disagree, rewrite it with the confirmed version or replace it. Keep a short list of what you changed.

STEP 5 - Validate.
Run: python3 src/add_content.py
It rebuilds topics.json, refuses hooks over 12 words, and lists topics whose spoken length is under about 58 seconds. For any topic listed, make its facts a little longer (staying within the rules) and run it again until no topic is listed and it finishes without errors. Also check with python3 that every fact has 30 to 43 words and no digits.

STEP 6 - Save.
Only commit content/monthNN.json and topics.json. Never change config.json, state.json, notified.json, topic_plan.json, assets/, src/ or .github/.
git add content topics.json
git commit -m "Add content monthNN (topics X to Y)"
git pull --rebase origin main
git push origin main
If pushing to main is refused, push to a new branch instead and say so clearly in your final message.

FINAL MESSAGE: the topic numbers and date range covered (from the plan's date field), how many facts or hooks were changed during fact-checking with two or three examples, how many topics have paintings, and confirmation that the push to main succeeded.
