#!/bin/bash
# Re-run the whole WoW Forever client extraction from this MacBook.
#
#   tools/wowf/run_all.sh            # pull from the Mac mini, dump, mine
#   SKIP_PULL=1 tools/wowf/run_all.sh  # only re-dump and re-mine what is already in .wowf-extract/raw
#
# What it does:
#   1. downloads the community listfile, WoWDBDefs and TACTKeys into .wowf-extract/_vendor (free, GitHub)
#   2. copies casc.py and the key list to ~/thalassian-scratch on the host that has the game,
#      extracts every DBFilesClient/*.db2 named by the listfile plus a root listing there,
#      rsyncs the results and the client caches/logs back, then deletes the remote scratch folder
#   3. runs export_all.py, history_tokens.py, mine_tokens.py and vo_list.py locally
# It never writes inside the game folder and never starts the game.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$REPO/.wowf-extract"
HOST="${WOWF_HOST:-mini}"
INSTALL="${WOWF_INSTALL:-/Applications/World of Warcraft}"
PRODUCT="${WOWF_PRODUCT:-wowf}"
FLAVOR="${WOWF_FLAVOR:-_forever_}"
BUILD="${WOWF_BUILD:-}"
PY="${PYTHON:-python3}"
mkdir -p "$OUT/_vendor" "$OUT/raw/cache" "$OUT/raw/logs" "$OUT/analysis"

if [ -z "${SKIP_VENDOR:-}" ]; then
  cd "$OUT/_vendor"
  curl -sSL -o community-listfile.csv https://github.com/wowdev/wow-listfile/releases/latest/download/community-listfile.csv
  if [ -d WoWDBDefs/.git ]; then git -C WoWDBDefs pull -q --ff-only; else git clone --depth 1 -q https://github.com/wowdev/WoWDBDefs.git; fi
  curl -sSL -o TACTKeys-WoW.txt https://raw.githubusercontent.com/wowdev/TACTKeys/master/WoW.txt
fi

if [ -z "${SKIP_PULL:-}" ]; then
  # the listfile has CRLF line endings
  tr -d '\r' < "$OUT/_vendor/community-listfile.csv" > "$OUT/raw/listfile-lf.csv"
  grep -i ';dbfilesclient/.*\.db2$' "$OUT/raw/listfile-lf.csv" > "$OUT/raw/db2list.txt"
  # Skyborne voice lines: player emotes and the NPC greeting/farewell sets (audio, for transcription)
  grep -E ';sound/(character/skyborne_elf_(male|female)/vo_skyborne_elf_(male|female)_(hello|bye|thank|welcome|yw|no|nod|apologize|congratulate|flirt|joke|cheer|charge|follow|flee|healme|helpme|incoming|openfire|attackmytarget|wait|train|beg|threaten|taunt|whoa|oops|oom|rasp|violin|bored)_|creature/(7478487|7478494)/[0-9]+_(greetings|farewell|pissed)_)' \
    "$OUT/raw/listfile-lf.csv" > "$OUT/raw/vo_list.txt"
  rm -f "$OUT/raw/listfile-lf.csv"
  ssh "$HOST" 'mkdir -p ~/thalassian-scratch'
  scp -q "$REPO/tools/wowf/casc.py" "$OUT/_vendor/TACTKeys-WoW.txt" "$OUT/raw/db2list.txt" "$OUT/raw/vo_list.txt" \
    "$HOST:thalassian-scratch/"
  ssh "$HOST" "cd ~/thalassian-scratch && python3 casc.py info --install '$INSTALL' --product $PRODUCT > info.txt \
    && python3 casc.py extract --install '$INSTALL' --product $PRODUCT --keys TACTKeys-WoW.txt --list db2list.txt --out out > extract.log \
    && python3 casc.py cdnfetch --install '$INSTALL' --product $PRODUCT --keys TACTKeys-WoW.txt --list vo_list.txt --out vo > vo.log \
    && python3 casc.py rootcsv --install '$INSTALL' --product $PRODUCT --out root.csv"
  rsync -a "$HOST:thalassian-scratch/out/" "$OUT/raw/casc/"
  rsync -a "$HOST:thalassian-scratch/vo/" "$OUT/skyborne_vo/"
  rsync -a "$HOST:thalassian-scratch/vo.log" "$OUT/raw/"
  rsync -a "$HOST:thalassian-scratch/root.csv" "$HOST:thalassian-scratch/extract.log" "$HOST:thalassian-scratch/info.txt" "$OUT/raw/"
  Q="${INSTALL// /\\ }/$FLAVOR"
  rsync -a "$HOST:$Q/Cache/ADB/enUS/DBCache.bin" "$HOST:$Q/Cache/WDB/enUS/" "$OUT/raw/cache/"
  rsync -a "$HOST:$Q/Logs/Hotfix.log" "$HOST:$Q/Logs/Sound.log" "$HOST:$Q/Logs/QuestCache.log" "$HOST:$Q/Logs/Tact.log" "$OUT/raw/logs/"
  ssh "$HOST" 'rm -rf ~/thalassian-scratch'
fi

if [ -z "$BUILD" ]; then
  BUILD="$(grep -m1 '^product' "$OUT/raw/info.txt" | awk '{print $4}')"
fi
echo "build $BUILD"
cd "$REPO"
"$PY" -I tools/wowf/export_all.py --base .wowf-extract --build "$BUILD"
"$PY" -I tools/wowf/history_tokens.py --repo . --out .wowf-extract/analysis/history_tokens.csv
"$PY" -I tools/wowf/mine_tokens.py --base .wowf-extract --lexicon src/thalassian/data/lexicon.json \
  --out .wowf-extract/analysis/client_tokens.csv
"$PY" -I tools/wowf/vo_list.py --base .wowf-extract \
  --path-regex 'sound/character/skyborne|sound/creature/(7478487|7478494)/' --out .wowf-extract/skyborne_vo_files.csv
