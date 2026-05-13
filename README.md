# rocom-etl
extract data for roco offline dex

1. use data from https://github.com/aoe-top/rocom.aoe.top

## usage
1. run the `init_git_sparse_checkout.sh` to get .json data from rocom.aoe.top
2. `uv run main.py` will etl the .json data, and generate a rocom.db file

## schemas in db file
```
CREATE TABLE pets_handbook (hid INTEGER PRIMARY KEY,name TEXT NOT NULL,forms_count INTEGER, pid_raw TEXT);
CREATE TABLE pets_base (pid INTEGER PRIMARY KEY,name TEXT NOT NULL,feature INTEGER,type1 INTEGER NOT NULL,type2 INTEGER,stage INTEGER,form TEXT,race_hp INTEGER,race_patk INTEGER,race_satk INTEGER,race_pdef INTEGER,race_sdef INTEGER,race_spe INTEGER,race_sum INTEGER,hid INTEGER, egg TEXT,pei_raw TEXT,epi_raw TEXT);
CREATE TABLE pets_skills (pid INTEGER NOT NULL,skid INTEGER NOT NULL,type INTEGER NOT NULL, info INTEGER);
CREATE TABLE skill (skid INTEGER PRIMARY KEY,name TEXT NOT NULL,desc TEXT NOT NULL,energy INTEGER NOT NULL,dam_para INTEGER,sk_damage_type INTEGER,sk_feature INTEGER,damage_type INTEGER,concat_type INTEGER,skill_priority INTEGER,target_type INTEGER);
CREATE TABLE ability (skid INTEGER PRIMARY KEY,name TEXT NOT NULL,desc TEXT NOT NULL,target_type INTEGER);
CREATE TABLE dict_type (cid INTEGER PRIMARY KEY,name TEXT NOT NULL,sname TEXT NOT NULL, ebc TEXT, rfc TEXT,scolor TEXT, plc TEXT);
```
