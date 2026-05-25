# rocom-etl
extract data for roco offline dex

1. use data from https://github.com/aoe-top/rocom.aoe.top

## usage
1. run the `init_gsc.sh` to get .json data from rocom.aoe.top
2. `uv run main.py` will etl the .json data, and generate a rocom.db file

## schemas in db file
```
CREATE TABLE pet_handbook (hid INTEGER PRIMARY KEY,name TEXT NOT NULL,forms_count INTEGER, pid_raw TEXT);
CREATE TABLE pet_base (id INTEGER PRIMARY KEY,hid INTEGER NOT NULL,name TEXT NOT NULL,feature INTEGER NOT NULL,type1 INTEGER NOT NULL,type2 INTEGER,stage INTEGER NOT NULL,form TEXT,form_type INTEGER,race_hp INTEGER,race_patk INTEGER,race_satk INTEGER,race_pdef INTEGER,race_sdef INTEGER,race_spe INTEGER,race_sum INTEGER, egg TEXT,evolution TEXT, res TEXT, version_id INTEGER);
CREATE TABLE pets_skills (pid INTEGER NOT NULL,skid INTEGER NOT NULL,type INTEGER NOT NULL, info INTEGER, version_id INTEGER);
CREATE TABLE skill (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,desc TEXT NOT NULL,skill_type INTEGER NOT NULL, damage_type INTEGER NOT NULL, energy INTEGER NOT NULL,damage INTEGER,target_type INTEGER, res TEXT, version_id INTEGER);
CREATE TABLE ability (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,desc TEXT NOT NULL,target_type INTEGER, res TEXT, version_id INTEGER);
CREATE TABLE dict_type (cid INTEGER PRIMARY KEY,name TEXT NOT NULL,sname TEXT NOT NULL, ebc TEXT, rfc TEXT,scolor TEXT, plc TEXT);
```
