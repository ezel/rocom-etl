import json
import sqlite3

class ETLer():
    def __init__(self, root):
        self.root = root
        self.raw = {}
        self.filterIdx = {}
        self.schema = {}
        self.doETL()

    def doETL(self):
        # extract handbook pets
        # set self.raw['handbook_pets'] with ['id', 'name', 'include_petbase_id[]']
        # set self.filterIdx['handbook_pets_pids'] with pids[]
        self.extract_handbook_pets()
        self.transform_handbook_pets()

        # extract available pets
        self.extract_petbase()
        self.transform_petbase()
        
        # extract available skills
        self.extract_level_skills()
        self.transform_level_skills()

        self.extract_skills()
        self.transform_skills()

        # extract dictionary
        self.extract_type_dict()
        self.transform_type_dict()
        

    def extract_handbook_pets(self, fn='PET_HANDBOOK'):
        with open(self.root+fn+'.json') as f:
            rows = json.loads(f.read())['RocoDataRows']

            # init result variables
            ret = []
            pet_ri = {}
            filter_ret_set = set()

            for k, v in rows.items():
                # check multiple pet form
                multiple_pet = 1
                if len(v['include_petbase_id'])>1:
                    multiple_pet = len(v['include_petbase_id'])

                # generate pet_ids
                fold_pids = [ds['petbase_id'] for ds in v['include_petbase_id']]
                flat_pids = [item for sublist in fold_pids for item in sublist]
                for pid in flat_pids:
                    filter_ret_set.add(pid)
                    pet_ri[pid] = v['id']
                    
                row = [ v['id'], v['name'], multiple_pet,
                        fold_pids
                       ]
                ret.append(row)

            self.raw['handbook_pets'] = ret
            self.raw['pid_ri'] = pet_ri
            self.filterIdx['handbook_pets_pids'] = list(filter_ret_set)
            return len(ret)

    def transform_handbook_pets(self):
        self.schema['pet_handbook'] = {
            'ddl' : "CREATE TABLE IF NOT EXISTS pet_handbook (hid INTEGER PRIMARY KEY,name TEXT NOT NULL,forms_count INTEGER, pid_raw TEXT)",
            'dml' : "INSERT INTO pet_handbook (hid,name,forms_count,pid_raw) VALUES (?, ?, ?, ?)",
            'clean': "DROP TABLE IF EXISTS pet_handbook",
            'data': [(r[0], r[1], r[2], str(r[3])) for r in self.raw['handbook_pets']]
        }
        
    def extract_petbase(self, fn='PETBASE_CONF'):
        with open(self.root+fn+'.json') as f:
            rows = json.loads(f.read())['RocoDataRows']

            ret = []
            filter_ret_set = set()
            
            for k, v in rows.items():
                if v['id'] in self.filterIdx['handbook_pets_pids']:
                    if 'hp_max_race' not in v:
                        continue
                    filter_ret_set.add(v['pet_feature'])
                    row = [ v['id'], v['name'],
                            v["pet_feature"],
                            v["unit_type"],
                            v["stage"],
                            v.get("form", None),
                            #v["stength_stage"],
                            v.get("hp_max_race", 0),
                            v.get("phy_attack_race", 0),
                            v.get("spe_attack_race", 0),
                            v.get("phy_defence_race", 0),
                            v.get("spe_defence_race", 0),
                            v.get("speed_race", 0),
                            v.get("SUM_race", 0),
                            self.raw['pid_ri'][v['id']],
                            v.get("egg_group", None),
                            v.get("evolution_pet_id", None),
                           ]
                    ret.append(row)

            self.raw['petbase'] = ret
            self.filterIdx['abilities'] = list(filter_ret_set)
            return len(ret)

    def transform_petbase(self):
        self.schema['pet_base'] = {
            'ddl' : "CREATE TABLE IF NOT EXISTS pet_base (id INTEGER PRIMARY KEY,hid INTEGER NOT NULL,name TEXT NOT NULL,feature INTEGER NOT NULL,type1 INTEGER NOT NULL,type2 INTEGER,stage INTEGER NOT NULL,form TEXT,form_type INTEGER,race_hp INTEGER,race_patk INTEGER,race_satk INTEGER,race_pdef INTEGER,race_sdef INTEGER,race_spe INTEGER,race_sum INTEGER, egg TEXT,evolution TEXT, version_id INTEGER)",
            'dml' : "INSERT INTO pet_base (id,name,feature,type1,type2,stage,form,race_hp,race_patk,race_satk,race_pdef,race_sdef,race_spe,race_sum,hid, egg,evolution) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            'clean': "DROP TABLE IF EXISTS pet_base",
            'data': [(r[0],r[1],r[2],r[3][0],r[3][1] if len(r[3])>1 else None,
                      r[4],r[5],r[6],str(r[7]),r[8],str(r[9]),
                      r[10],r[11],r[12],r[13], str(r[14]),str(r[15])) for r in self.raw['petbase']],
        }

    def extract_level_skills(self, fn='LEVEL_SKILL_CONF'):
        with open(self.root+fn+'.json') as f:
            rows = json.loads(f.read())['RocoDataRows']

            # init result variables
            ret = []
            pet_ri = {}
            filter_ret_set = set()

            for k, v in rows.items():
                if v['id'] in self.filterIdx['handbook_pets_pids']:
                    if 'level' not in v:
                        continue
                    if len(v['level']) > 0:
                        rLevel = tuple([(r['param'], r['level_point'],) for r in v['level']])
                        [filter_ret_set.add(x[0]) for x in rLevel]
                    if len(v['machine_skill_group']) > 0:
                        rMachine = tuple([(r['machine_skill_id'], r['machine_skill_name'],) for r in v['machine_skill_group']])
                        [filter_ret_set.add(x[0]) for x in rMachine]

                    rBlood = [
                        v["blood_skill_COMMON"], v["blood_skill_GRASS"], v["blood_skill_FIRE"],
                        v["blood_skill_WATER"],  v["blood_skill_LIGHT"], v["blood_skill_STONE"],
                        v["blood_skill_ICE"], v["blood_skill_DRAGON"], v["blood_skill_ELECTRIC"],
                        v["blood_skill_TOXIC"], v["blood_skill_INSECT"], v["blood_skill_FIGHT"],
                        v["blood_skill_WING"], v["blood_skill_MOE"], v["blood_skill_GHOST"],
                        v["blood_skill_DEMON"], v["blood_skill_MECHANIC"], v["blood_skill_PHANTOM"]]

                    [filter_ret_set.add(x) for x in rBlood]

                    row = [v['id'], rLevel, rMachine, rBlood]
                    
                ret.append(row)

            self.raw['level_skill'] = ret
            self.filterIdx['skills'] = list(filter_ret_set)
            return len(ret)

    def transform_level_skills(self):
        data = []
        for r in self.raw['level_skill']:
            id = r[0]
            for x in r[1]:
                data.append([id, x[0], 1, x[1]])
            for x in r[2]:
                data.append([id, x[0], 2, x[1]])
            for i in range(len(r[3])):
                data.append([id, r[3][i], 3, i])
            
        self.schema['pets_skills'] = {
            'ddl' : "CREATE TABLE IF NOT EXISTS pets_skills (pid INTEGER NOT NULL,skid INTEGER NOT NULL,type INTEGER NOT NULL, info INTEGER, version_id INTEGER)",
            'dml' : "INSERT INTO pets_skills (pid, skid, type, info) VALUES (?, ?, ?, ?)",
            'clean': "DROP TABLE IF EXISTS pets_skills",
            'data': tuple(data)
        }
        

    def extract_skills(self, fn='SKILL_CONF'):
        with open(self.root+fn+'.json') as f:
            rows = json.loads(f.read())['RocoDataRows']

            ret1 = []
            ret2 = []
            
            for k, v in rows.items():
                if v['id'] in self.filterIdx['skills']:
                    row = [ v['id'], v['name'], v['desc'],
                            v["energy_cost"][0],
                            v["dam_para"][0],
                            v["skill_dam_type"],
                            v["skill_feature"],
                            v["damage_type"],
                            v["contact_type"],
                            v["skill_priority"],
                            v["target_type"]
                           ]
                    ret1.append(row)

                elif v['id'] in self.filterIdx['abilities']:
                    row = [ v['id'], v['name'], v['desc'],
                            v["target_type"],
                           ]
                    ret2.append(row)

            self.raw['skills'] = ret1
            self.raw['abilities'] = ret2

            return len(ret1) + len(ret2)

    def transform_skills(self):
        self.schema['skill'] = {
            'ddl' : "CREATE TABLE IF NOT EXISTS skill (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,desc TEXT NOT NULL,skill_type INTEGER NOT NULL, damage_type INTEGER NOT NULL, energy INTEGER NOT NULL,damage INTEGER,sk_feature INTEGER,concat_type INTEGER,skill_priority INTEGER,target_type INTEGER, version_id INTEGER)",
            'dml' : "INSERT INTO skill (id,name,desc,energy,damage,damage_type,sk_feature,skill_type,concat_type,skill_priority,target_type) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            'clean': "DROP TABLE IF EXISTS skill",
            'data': [(r[0],r[1],r[2],r[3],
                      r[4],r[5],r[6],r[7],
                      r[8],r[9],r[10]) for r in self.raw['skills']],
        }
        self.schema['ability'] = {
            'ddl' : "CREATE TABLE IF NOT EXISTS ability (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,desc TEXT NOT NULL,target_type INTEGER, version_id INTEGER)",
            'dml' : "INSERT INTO ability (id,name,desc,target_type) VALUES (?,?,?,?)",
            'clean': "DROP TABLE IF EXISTS ability",
            'data': [(r[0],r[1],
                      r[2],r[3]) for r in self.raw['abilities']],
        }

    def extract_type_dict(self, fn1='TYPE_DICTIONARY', fn2='SKILL_COLOR_CONF'):
        ret_kv = {}
        with open(self.root+fn1+'.json') as f:
            rows = json.loads(f.read())['RocoDataRows']

            for k, v in rows.items():
                item = [ v['id'], v['type_name'], v['short_name'],
                         v.get('evo_banding_color', None),
                         v.get("rolecard_favorite_pets_colour", None)
                       ]
                ret_kv[v['id']] = item

        with open(self.root+fn2+'.json') as f:
            rows = json.loads(f.read())['RocoDataRows']

            for k, v in rows.items():
                item = [ v.get('color', None), v.get("perform_light_colour", None)]
                if v['unit_type'] in ret_kv:
                    ret_kv[v['unit_type']].extend(item)

        self.raw['type_dictionary'] = list(ret_kv.values())

        return len(ret_kv)

    def transform_type_dict(self):
        self.schema['dict_type'] = {
            'ddl' : "CREATE TABLE IF NOT EXISTS dict_type (cid INTEGER PRIMARY KEY,name TEXT NOT NULL,sname TEXT NOT NULL, ebc TEXT, rfc TEXT,scolor TEXT, plc TEXT)",
            'dml' : "INSERT INTO dict_type (cid, name, sname, ebc, rfc, scolor, plc) VALUES (?,?,?,?,?,?,?)",
            'clean': "DROP TABLE IF EXISTS dict_type",
            'data': [(r[0],r[1],r[2],r[3],r[4],
                      r[5] if 5 in r else None, r[6] if 6 in r else None)
                     for r in self.raw['type_dictionary']]
        }

    def export_color_html(self, path='type_color.html'):
        tr_rows = []

        for rtype in self.schema['dict_type']['data']:
            #print(rtype)
            tds = [f'<td style="background-color: {x}">{x}</td>' for x in rtype[3:] if x is not None]
            #print(tds)
            tr_rows.append(f'<tr><th>{rtype[1]}</th>{"".join(tds)}</tr>')
            

        with open(path, 'w') as f:
            f.write('<html><body><table>')
            f.write("".join(tr_rows))
            f.write('</table></body></html>')
        

    def load_sqlite(self, path="rocom.db"):
        def batch_create_and_insert(cursor, schema):
            cursor.execute(schema['clean'])
            cursor.execute(schema['ddl'])
            cursor.executemany(
                schema['dml'],
                schema['data']
            )
            
        try:
            conn = sqlite3.connect(path)
            cursor = conn.cursor()

            for k, v in self.schema.items():
                try:
                    batch_create_and_insert(cursor, v)
                    conn.commit()
                    print(f"table {k} exported succeed!")
                    
                except sqlite3.Error as e:
                    print(f"create data table {k} error: {e}")
                    conn.rollback()

        except sqlite3.Error as e:
            print(f"database error: {e}")
            
        finally:
            cursor.close()
            conn.close()
            
        
    def test(self):
        print(self.root)

        print("----display self raw data:----")
        print(self.filterIdx.keys())
        print([f'{len(self.filterIdx[x])} in {x}' for x in self.filterIdx])
        
        print(self.raw.keys())
        for k in self.raw.keys():
            print(f'{k} has {len(self.raw[k])} rows, first line:')
            if type(self.raw[k]) == type([]):
                print(self.raw[k][0])

        print("exporting color.html...")
        self.export_color_html()
        
        print("exporting database...")
        self.load_sqlite()
