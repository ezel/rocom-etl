# rocom-etl
extract data for roco offline dex

## data source
the three folders have 3 different ways of data source
1. folder fetch: data from https://github.com/aoe-top/rocom.aoe.top
2. folder crawl: data from bilibili wiki

### Way 1: fetch data source
1. run the `init_gsc.sh` to get .json data from rocom.aoe.top
2. `uv run main.py` will etl the .json data, and generate a rocom.db file

### Way 2: crawl from wiki
because of the wiki structure change, deprecated since S2

## schemas in db file
```
CREATE TABLE pet_handbook (id INTEGER NOT NULL PRIMARY KEY,name TEXT NOT NULL,forms_count INTEGER, pid_raw TEXT);
CREATE TABLE season_handbook (id INTEGER NOT NULL,name TEXT,pid INTEGER NOT NULL PRIMARY KEY);
CREATE TABLE pet_base (id INTEGER NOT NULL PRIMARY KEY,hid INTEGER NOT NULL,name TEXT NOT NULL,feature INTEGER NOT NULL,type1 INTEGER NOT NULL,type2 INTEGER,stage INTEGER NOT NULL,form TEXT,form_type INTEGER, bid INTEGER, race_hp INTEGER NOT NULL,race_patk INTEGER NOT NULL,race_satk INTEGER NOT NULL,race_pdef INTEGER NOT NULL,race_sdef INTEGER NOT NULL,race_spe INTEGER NOT NULL,race_sum INTEGER NOT NULL, wish INTEGER NOT NULL, egg1 INTEGER, egg2 INTEGER,evolution TEXT, res TEXT NOT NULL, version_id INTEGER);
CREATE TABLE pet_evolution (root INTEGER NOT NULL, path TEXT NOT NULL, stage1 TEXT NOT NULL, stage2 TEXT, stage3 TEXT, version_id INTEGER, PRIMARY KEY(root, path));
CREATE TABLE pets_skills (pid INTEGER NOT NULL,skid INTEGER NOT NULL,type INTEGER NOT NULL, info INTEGER, version_id INTEGER, PRIMARY KEY(pid, skid, type));
CREATE TABLE skill (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,desc TEXT NOT NULL,skill_type INTEGER NOT NULL, damage_type INTEGER NOT NULL, energy INTEGER NOT NULL,damage INTEGER,target_type INTEGER, res TEXT NOT NULL, version_id INTEGER);
CREATE TABLE ability (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,desc TEXT NOT NULL,target_type INTEGER, res TEXT NOT NULL, version_id INTEGER);
CREATE TABLE skill_descs (id INTEGER NOT NULL PRIMARY KEY,name TEXT NOT NULL, desc TEXT, version_id INTEGER);
```

## COPYRIGHT NOTICE
This repository is for academic research only.
No game resources, decryption keys or copyrighted data are included in this project.
Using this tool to extract or disseminate game content without the copyright owner’s written consent is strictly forbidden.
The developer is not responsible for any improper use of this program by end users.
All applicable laws and the game’s EULA must be observed.
