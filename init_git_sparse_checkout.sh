rm -rf rat/
git clone --filter=blob:none --no-checkout https://github.com/aoe-top/rocom.aoe.top.git rat
cd rat
git sparse-checkout init --no-cone
#git sparse-checkout set public/data/tables
git sparse-checkout add public/data/BinData/PET_HANDBOOK.json
git sparse-checkout add public/data/BinData/LEVEL_SKILL_CONF.json
git sparse-checkout add public/data/BinData/PETBASE_CONF.json
git sparse-checkout add public/data/BinData/SKILL_CONF.json
git checkout main
