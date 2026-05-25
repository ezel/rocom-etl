rm -rf res
git clone --filter=blob:none --no-checkout https://github.com/aoe-top/rocom.aoe.top.git res

if [ -d res ]; then
cd res/
git sparse-checkout init --no-cone
git sparse-checkout set ''

sqlite3 ../rocom.db "SELECT res from skill" | xargs -r -I {} git sparse-checkout add "public/assets/webp/items/{}.webp"

sqlite3 ../rocom.db "SELECT res from ability" | xargs -r -I {} git sparse-checkout add "public/assets/webp/items/{}.webp"

sqlite3 ../rocom.db "SELECT DISTINCT res from pet_base" | xargs -r -I {} git sparse-checkout add "public/assets/webp/friends/{}.webp"

git checkout main

else
echo "Project res not cloned, stopped."
exit 1
fi
