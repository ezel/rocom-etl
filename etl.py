import json
import re
import regex
import sqlite3

class ETLer():
    def __init__(self, root):
        self.root = root
        self.raw = {}
        self.filterIdx = {}
        self.schema = {}
        #self.doETL()

    def doETL(self, more_pets=[]):
        # extract handbook pets
        # set self.raw['handbook_pets'] with ['id', 'name', 'include_petbase_id[]']
        # set self.filterIdx['handbook_pets_pids'] with pids[]
        self.extract_handbook_pets()
        self.extract_season_handbook_pets()

        if len(more_pets) > 0:
            self.filterIdx['handbook_pets_pids'].extend(more_pets)

        self.transform_handbook_pets()
        # extract available pets
        self.extract_petbase()
        self.transform_petbase()
        self.transform_pet_evolution()
        
        # extract available skills
        self.extract_level_skills()
        self.transform_level_skills()

        self.extract_skills()
        self.transform_skills()

        # extract desc notes
        self.extract_skill_descs()
        self.transform_skill_descs()

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
            #self.raw['pid_ri'] = pet_ri
            self.filterIdx['handbook_pets_pids'] = list(filter_ret_set)
            return len(ret)

    def extract_season_handbook_pets(self, fn='SEASON_HANDBOOK_CONF'):
        with open(self.root+fn+'.json') as f:
            rows = json.loads(f.read())['RocoDataRows']

            # init result variables
            ret = []
            filter_ret_set = set()

            for k, v in rows.items():
                # generate pet_ids
                flat_pids = v['season_new_pet_base_id']
                for pid in flat_pids:
                    filter_ret_set.add(pid)
                    ret.append([pid, v['id']])

            self.filterIdx['handbook_pets_pids'].extend(list(filter_ret_set))
            self.raw['handbook_season'] = ret
            return len(ret)


    def transform_handbook_pets(self):
        self.schema['pet_handbook'] = {
            'ddl' : "CREATE TABLE IF NOT EXISTS pet_handbook (id INTEGER NOT NULL PRIMARY KEY,name TEXT NOT NULL,forms_count INTEGER, pid_raw TEXT)",
            'dml' : "INSERT INTO pet_handbook (id,name,forms_count,pid_raw) VALUES (?, ?, ?, ?)",
            'clean': "DROP TABLE IF EXISTS pet_handbook",
            'data': [(r[0], r[1], r[2], str(r[3])) for r in self.raw['handbook_pets']]
        }

        self.schema['season_handbook'] = {
            'ddl' : "CREATE TABLE IF NOT EXISTS season_handbook (id INTEGER NOT NULL,name TEXT,pid INTEGER NOT NULL UNIQUE)",
            'dml' : "INSERT INTO season_handbook (id,pid) VALUES (?,?)",
            'clean': "DROP TABLE IF EXISTS season_handbook",
            'data': [(r[1], r[0]) for r in self.raw['handbook_season']]
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
                            v.get("pictorial_book_id", None),#self.raw['pid_ri'][v['id']],
                            v.get("egg_group", None),
                            v.get("evolution_pet_id", None),
                            v.get("JL_res", None),
                            v.get("wish_number", 0),
                            v.get("is_boss", 0),
                            v.get("bosspetbase_id", None)
                           ]
                    ret.append(row)

            self.raw['petbase'] = ret
            self.filterIdx['abilities'] = list(filter_ret_set)
            return len(ret)

    def transform_petbase(self):
        def split_array(src):
            if src is None:
                return [None, None]
            elif len(src) == 1:
                return [src[0], None]
            elif len(src) > 1:
                return [src[0], src[1]]
        

        self.schema['pet_base'] = {
            'ddl' : "CREATE TABLE IF NOT EXISTS pet_base (id INTEGER NOT NULL PRIMARY KEY,hid INTEGER NOT NULL,name TEXT NOT NULL,feature INTEGER NOT NULL,type1 INTEGER NOT NULL,type2 INTEGER,stage INTEGER NOT NULL,form TEXT,form_type INTEGER, bid INTEGER, race_hp INTEGER NOT NULL,race_patk INTEGER NOT NULL,race_satk INTEGER NOT NULL,race_pdef INTEGER NOT NULL,race_sdef INTEGER NOT NULL,race_spe INTEGER NOT NULL,race_sum INTEGER NOT NULL, wish INTEGER NOT NULL, egg1 INTEGER, egg2 INTEGER,evolution TEXT, res TEXT NOT NULL, version_id INTEGER)",
            'dml' : "INSERT INTO pet_base (id,name,feature,type1,type2,stage,form,race_hp,race_patk,race_satk,race_pdef,race_sdef,race_spe,race_sum,hid, egg1,egg2,evolution, res, wish, form_type, bid) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            'clean': "DROP TABLE IF EXISTS pet_base",
            'data': [(r[0],r[1],r[2],
                      *split_array(r[3]),
                      r[4],r[5],
                      r[6],r[7],r[8],r[9],r[10],r[11],
                      (r[6]+r[7]+r[8]+r[9]+r[10]+r[11]),
                      r[13],
                      *split_array(r[14]),
                      r[15] if r[15] is None else str(r[15]), #evo
                      r[16][r[16].rfind('.')+1:-1], #res
                      r[17], # wish
                      3 if r[18] else (2 if r[5] else 1),
                      r[19] if (r[15] is None) else None, # boss_id
                      ) for r in self.raw['petbase']],
        }

    def transform_pet_evolution(self):
        adj = {}
        for r in self.raw['petbase']:
            if r[15] is not None:
                adj[r[0]]=r[15]
        #print(adj)

        # dfs
        results = []
        visited = {}
        def dfs(start, result=""):
            if start in visited:
                return
            else:
                result += str(start) + "/"
                visited[start] = True
                if start not in adj:
                    results.append(result.split('/')[:-1])
                else:
                    for end in adj[start]:
                        dfs(end, result)

        for k in adj:
            dfs(k)

        # cut the path
        results.sort()
        data = []
        current_prefix = ""
        combine = []
        for i in range(len(results)):
            r = results[i]
            combine.append(r[-1])
            # compare with next row
            if (i+1<len(results) and str(r[:-1]) == str(results[i+1][:-1])):
                continue
            else:
                fullPath = '/'.join(r[:-1])+'/'+','.join(combine)
                stages = fullPath.split('/')
                data.append((r[0],
                             fullPath,
                             stages[0],
                             stages[1] if 1 < len(stages) else None,
                             stages[2] if 2 < len(stages) else None
                             ))
                combine = []

        #print([(x[1], x[1].count('/'), x[1].count(','),) for x in data])
        
        self.schema['pet_evolution'] = {
            'ddl': "CREATE TABLE IF NOT EXISTS pet_evolution (root INTEGER NOT NULL, path TEXT NOT NULL, stage1 TEXT NOT NULL, stage2 TEXT, stage3 TEXT, version_id INTEGER, PRIMARY KEY(root, path))",
            'dml': "INSERT INTO pet_evolution (root, path, stage1, stage2, stage3) VALUES (?,?,?,?,?)",
            'clean': "DROP TABLE IF EXISTS pet_evolution",
            'data': data
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
        typeMap = [2,3,4,5,6,8,9,10,11,12,13,14,15,16,17,18,19,20]
        for r in self.raw['level_skill']:
            id = r[0]
            for x in r[1]:
                data.append([id, x[0], 1, x[1]])
            for x in r[2]:
                data.append([id, x[0], 2, None])
            for i in range(len(r[3])):
                data.append([id, r[3][i], 3, typeMap[i]])
            
        self.schema['pets_skills'] = {
            'ddl' : "CREATE TABLE IF NOT EXISTS pets_skills (pid INTEGER NOT NULL,skid INTEGER NOT NULL,type INTEGER NOT NULL, info INTEGER, version_id INTEGER, PRIMARY KEY(pid, skid, type))",
            'dml' : "INSERT INTO pets_skills (pid, skid, type, info) VALUES (?, ?, ?, ?)",
            'clean': "DROP TABLE IF EXISTS pets_skills",
            'data': tuple(data)
        }
        

    def extract_skills(self, fn='SKILL_CONF'):
        with open(self.root+fn+'.json') as f:
            rows = json.loads(f.read())['RocoDataRows']

            ret1 = []
            ret2 = []
            
            pattern = regex.compile(r'[\p{Cc}\p{Cf}]')
            for k, v in rows.items():
                if v['id'] in self.filterIdx['skills']:
                    if pattern.search(v['desc']):
                        #print(v['name'], repr(v['desc']))
                        v['desc'] = regex.sub(r'[\p{Cc}\p{Cf}]', '', v['desc'])
                    row = [ v['id'], v['name'], v['desc'],
                            v["energy_cost"][0],
                            v["dam_para"][0],
                            v["skill_dam_type"],
                            v["Skill_Type"], v["damage_type"],
                            v["target_type"],
                            v.get('icon')
                           ]
                    ret1.append(row)

                elif v['id'] in self.filterIdx['abilities']:
                    row = [ v['id'], v['name'], v['desc'],
                            v["target_type"],
                            v.get('icon')
                           ]
                    ret2.append(row)

            self.raw['skills'] = ret1
            self.raw['abilities'] = ret2

            return len(ret1) + len(ret2)

    def transform_skills(self):
        def transform_skilltype(sktype, dmgtype):
            if sktype == 1 and dmgtype == 2:
                return 1
            elif sktype == 1 and dmgtype == 3:
                return 2
            elif sktype == 2 and dmgtype == 1:
                return 3
            elif sktype == 3 and dmgtype == 1:
                return 4
            else:
                return 0

        skill_descs_set = set()
        def transform_desc(desc):

            if desc.find('</>')>0:
                extracted_ids = re.findall(r'<desc_id=(\d+)>(.*?)</>', desc)
                skill_descs_set.update(extracted_ids)
                #return re.sub(r'<desc_id=\d+>','', desc.replace('</>',''))
            return desc

        self.schema['skill'] = {
            'ddl' : "CREATE TABLE IF NOT EXISTS skill (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,desc TEXT NOT NULL,skill_type INTEGER NOT NULL, damage_type INTEGER NOT NULL, energy INTEGER NOT NULL,damage INTEGER,target_type INTEGER, res TEXT NOT NULL, version_id INTEGER)",
            'dml' : "INSERT INTO skill (id,name,desc,energy,damage,damage_type,skill_type,target_type, res) VALUES (?,?,?,?,?,?,?,?,?)",
            'clean': "DROP TABLE IF EXISTS skill",
            'data': [(r[0],r[1],transform_desc(r[2]),r[3],
                      r[4],r[5],transform_skilltype(r[6],r[7]),
                      r[8],r[9][r[9].rfind('.')+1:-1]) for r in self.raw['skills']],
        }
        self.schema['ability'] = {
            'ddl' : "CREATE TABLE IF NOT EXISTS ability (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,desc TEXT NOT NULL,target_type INTEGER, res TEXT NOT NULL, version_id INTEGER)",
            'dml' : "INSERT INTO ability (id,name,desc,target_type, res) VALUES (?,?,?,?,?)",
            'clean': "DROP TABLE IF EXISTS ability",
            'data': [(r[0],r[1],
                      transform_desc(r[2]),r[3],r[4][r[4].rfind('.')+1:-1]) for r in self.raw['abilities']],
        }
        self.filterIdx['descs'] = tuple(skill_descs_set)

    def extract_skill_descs(self, fn='DESC_NOTE_CONF'):
        with open(self.root+fn+'.json') as f:
            rows = json.loads(f.read())['RocoDataRows']

            ret1 = []
            filterDict = dict(self.filterIdx['descs'])
            reverseDict = {v: k for k, v in filterDict.items()}
            missingDesc = {}
            for k, v in rows.items():
                if str(v['id']) in filterDict.keys():
                    if v['note'] == filterDict[str(v['id'])]:
                        row = [ v['id'], v['note'], v['desc']]
                        ret1.append(row)
                    else:
                        missingDesc[filterDict[str(v['id'])]] = v['id']

            # find missing desc
            for k, v in rows.items():
                if v['note'] in missingDesc.keys():
                    print('find missing:', v['note'], "on", v['id'])
                    row = [ reverseDict[v['note']], v['note'], v['desc']]
                    del missingDesc[v['note']]
                    ret1.append(row)

            self.raw['skill_descs'] = ret1
            print(missingDesc)
            return len(ret1)

    def transform_skill_descs(self):
        self.schema['skill_descs'] = {
            'ddl' : "CREATE TABLE IF NOT EXISTS skill_descs (id INTEGER NOT NULL PRIMARY KEY,name TEXT NOT NULL, desc TEXT, version_id INTEGER)",
            'dml' : "INSERT INTO skill_descs (id, name, desc) VALUES (?,?,?)",
            'clean': "DROP TABLE IF EXISTS skill_descs",
            'data': tuple(self.raw['skill_descs'])
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
            'ddl' : "CREATE TABLE IF NOT EXISTS dict_type (cid INTEGER NOT NULL PRIMARY KEY,name TEXT NOT NULL,sname TEXT NOT NULL, ebc TEXT, rfc TEXT,scolor TEXT, plc TEXT)",
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
