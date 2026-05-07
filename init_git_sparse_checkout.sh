git clone --filter=blob:none --no-checkout https://github.com/aoe-top/rocom.aoe.top/tree/main rat
cd rat
git sparse-checkout init --no-cone
git sparse-checkout set public/data/tables
git checkout main
