import requests
from bs4 import BeautifulSoup
import sqlite3
import pickle

class BiliCrawler():
    def __init__(self, filename=None):
        self.URL_BASE = "https://wiki.biligame.com"
        self.filename = filename

        self.raw = {}
        self.schema = {}
        self.dic = {'type':{'普通':2,'草':3,'火':4,'水':5,'光':6,'地':8,'冰':9,'龙':10,'电':11,'毒':12,'虫':13,'武':14,'翼':15,'萌':16,'幽':17,'恶':18,'机械':19,'幻':20}, 'stage_type':{'最终形态':10,'Ⅱ阶':2,'Ⅰ阶':1},'form_type':{'原始形态':1,'首领形态':3,'地区形态':2},'category':{'精灵技能':1,'血脉技能':3,'可学技能石':2},'skill_type':{'魔攻':2,'物攻':1,'状态':3,'防御':4}}

    def fetch_data(self, forceFetch=False):
        self.fromFile()
        if forceFetch or self.raw == {}:
            # fetch 2 tables
            self.fetch_skill_table()
            self.fetch_pet_table()

            # fetch pet detail
            self.raw['petskillsList'] = []
            for rawPet in self.raw['petsTable']:
                url = self.URL_BASE+rawPet[15]
                rawKey = rawPet[0]
                if rawKey > 3:
                    break
                self.fetch_pet_detail(url, rawKey)

        self.transform_skill()
        self.transform_pet()
        self.transform_petskill()

    def toFile(self):
        filename = self.filename
        if filename:
            with open(filename, 'wb' ) as f :
                pickle.dump(self.raw, f, protocol=pickle.HIGHEST_PROTOCOL)
                print('pickle self.raw to file:', filename)

    def fromFile(self):
        if self.filename:
            try:
                with open(self.filename, 'rb' ) as f:
                    self.raw = pickle.load(f)
            except FileNotFoundError:
                pass

    def _request(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:151.0) Gecko/20100101 Firefox/151.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,en-US;q=0.9,en;q=0.8',
            # 'Accept-Encoding': 'gzip, deflate, br, zstd',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-GPC': '1',
            'Priority': 'u=4',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        rk = requests.get(url, headers=headers)
        html_doc = rk.text
        print('request len:',len(html_doc))
        soup = BeautifulSoup(html_doc, 'lxml')
        if len(html_doc) < 20000:
            return self._request(url)
        else:
            return soup

    """ Deprecated because of fetch_skill_table """
    def _get_skill_list(self):
        # skills list of
        # ['name', 'param1', 'param2', 'href', 'icon_src']
        url = "https://wiki.biligame.com/rocom/%E6%8A%80%E8%83%BD%E5%9B%BE%E9%89%B4"
        rk = requests.get(url)
        html_doc = rk.text
        soup = BeautifulSoup(html_doc, 'lxml')
        boxSoup = soup.find('div', id='CardSelectTr')
        skillsSoup = boxSoup.find_all('div', class_='divsort')

        skills = []
        for s in skillsSoup:
            sa = s.find('a')
            row = [
                sa.attrs['title'],
                s.attrs['data-param1'],
                s.attrs['data-param2'],
                sa.attrs['href'],
                s.find('img', class_='rocom_skill_bg_img').attrs['src']
            ]
            skills.append(row)

        self.row['skillsList'] = skills

    def fetch_skill_table(self):
        # skills list of
        # ['icon_src', 'name', 'type', 'skill_type'
        #  'damage_type', 'energy, 'damage', 'desp', 'version'
        #  'href']
        url = "https://wiki.biligame.com/rocom/%E6%8A%80%E8%83%BD%E7%AD%9B%E9%80%89"
        print("fetching data of skill table...")
        soup = self._request(url)
        boxSoup = soup.find('table', id='CardSelectTr')
        skillsSoup = boxSoup.find_all('tr')[1:]

        skills = []
        for s in skillsSoup:
            tds = s.find_all('td')
            sa = s.find('a')
            row = [
                s.find('img').attrs['src'],
                tds[1].text.strip(),
                s.attrs['data-param2'],
                s.attrs['data-param1'],
                tds[4].text.strip(),
                tds[5].text.strip(),
                tds[6].text.strip(),
                tds[7].text.strip(),
                s.find('a').attrs['href']
            ]
            skills.append(tuple(row))

        self.raw['skillsTable'] = skills

    def transform_skill(self):
        self.schema['bili_skill'] = {
            'ddl' : "CREATE TABLE IF NOT EXISTS bili_skill (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL, desc TEXT NOT NULL, skill_type INTEGER NOT NULL, damage_type INTEGER NOT NULL, energy INTEGER NOT NULL, damage INTEGER NOT NULL,icon_path TEXT NOT NULL,link TEXT NOT NULL, version TEXT, version_id INTEGER)",
            'dml' : "INSERT INTO bili_skill (icon_path, name, damage_type, skill_type, energy, damage, desc, version, link) VALUES (?,?,?,?,?,?,?,?,?)",
            'clean': "DROP TABLE IF EXISTS bili_skill",
            'data': [(r[0],r[1],self.dic['type'].get(r[2]),self.dic['skill_type'].get(r[3]),
                      r[4],r[5],r[6],r[7],r[8]) for r in self.raw['skillsTable']],
        }


    def fetch_pet_table(self):
        # pets list of
        # ['icon_src', 'name', 'types', 'petid', 'ability',
        # 'race_hp', 'race_spd', 'race_patk', 'race_satk', 'race_pdef', 'race_sdef', 'race_total', 'version',
        # 'href', 'data_region', 'data_rank']
        url = "https://wiki.biligame.com/rocom/%E7%B2%BE%E7%81%B5%E7%AD%9B%E9%80%89"
        print("fetching data of pet table...")
        soup = self._request(url)
        boxSoup = soup.find('table', id='CardSelectTr')
        petsSoup = boxSoup.find_all('tr')[1:]

        pets = []
        for s in petsSoup:
            tds = s.find_all('td')
            if len(tds) < 13:
                continue
            sa = s.find('a')
            types = s.attrs['data-param2'].split(',')
            if len(tds) > 13:
                tmp_ability = ''.join([x.text.strip() for x in tds[4:19]])
                tds[4:19] = [tmp_ability]

            row = [
                s.find('img').attrs['src'],
                tds[1].text.strip(),
                types[0].strip(),
                types[1].strip() if len(types)>1 else None,
                tds[3].text.strip(),
                tds[4].text.strip() if type(tds[4]) != type('text') else tds[4],
                tds[5].text.strip(),
                tds[6].text.strip(),
                tds[7].text.strip(),
                tds[8].text.strip(),
                tds[9].text.strip(),
                tds[10].text.strip(),
                tds[11].text.strip(),
                tds[12].text.strip(),
                s.find('a').attrs['href'],
                s.attrs['data-param3'],
                s.attrs['data-param1']
            ]
            pets.append(row)

        petsWithId = [[i + 1] + row for i, row in enumerate(pets)]
        self.raw['petsTable'] = petsWithId

    def transform_pet(self):
        def extract_name(name):
            ret = name.replace('）','').split('（')
            if len(ret) > 1:
                return ret
            else:
                return [name, None]

        self.schema['bili_pet'] = {
            'ddl' : "CREATE TABLE IF NOT EXISTS bili_pet_base (id INTEGER PRIMARY KEY,hid INTEGER NOT NULL, name TEXT NOT NULL,feature TEXT NOT NULL,type1 INTEGER NOT NULL,type2 INTEGER,stage_type INTEGER NOT NULL,form TEXT, form_type INTEGER,race_hp INTEGER NOT NULL,race_patk INTEGER NOT NULL,race_satk INTEGER NOT NULL,race_pdef INTEGER NOT NULL,race_sdef INTEGER NOT NULL,race_spe INTEGER NOT NULL,race_sum INTEGER NOT NULL, icon_path TEXT NOT NULL, link TEXT NOT NULL, version TEXT, version_id INTEGER)",
            'dml' : "INSERT INTO bili_pet_base (id, icon_path, name, form, type1, type2, hid, feature, race_hp, race_spe, race_patk, race_satk, race_pdef, race_sdef, race_sum, version, link, form_type, stage_type) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            'clean': "DROP TABLE IF EXISTS bili_pet_base",
            'data': [(r[0],r[1],*extract_name(r[2]),
                      self.dic['type'].get(r[3]),self.dic['type'].get(r[4]),
                      r[5],r[6],r[7],r[8],
                      r[9],r[10],r[11],r[12],
                      r[13],r[14],r[15],
                      self.dic['form_type'].get(r[16]),self.dic['stage_type'].get(r[17])) for r in self.raw['petsTable']],
        }

    def fetch_pet_detail(self, url, pkey):
        # pet detail list of

        print("fetching data of pet... :", url)
        soup = self._request(url)
        boxSoup = soup.find('div', class_='rocom_sprite_skill_tabBox')
        petSkillsCategorySoup = boxSoup.find_all('div', class_='tabbertab')

        allPetSkills = []
        for petSkills in petSkillsCategorySoup:
            categoryStr = petSkills.attrs['title']
            skillBox = petSkills.find_all('div', class_='rocom_sprite_skill_box')
            row = [(
                pkey,
                s.find('div', class_='rocom_sprite_skillName').text.strip(),
                categoryStr,
                s.find('div', class_='rocom_sprite_skill_level').text.strip()
            ) for s in skillBox]
            allPetSkills.extend(row)
            self.raw['petskillsList'].extend(allPetSkills)


    def transform_petskill(self):
        # find skid
        # category to type

        self.schema['bili_pets_skills'] = {
            'ddl' : "CREATE TABLE IF NOT EXISTS bili_pets_skills (pid INTEGER NOT NULL,skid INTEGER,skill_name TEXT NOT NULL,type INTEGER, category TEXT NOT NULL, info TEXT, version_id INTEGER)",
            'dml' : "INSERT INTO bili_pets_skills (pid, skill_name, category, info) VALUES (?, ?, ?, ?)",
            'clean': "DROP TABLE IF EXISTS bili_pets_skills",
            'data': tuple(self.raw['petskillsList'])
        }


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
        self.fetch_data()
        print("self.row info:")
        print(self.raw.keys())
        for k in self.raw.keys():
            print(f'{k} has {len(self.raw[k])} rows, first line:')
            if type(self.raw[k]) == type([]):
                print(self.raw[k][1])

        print("self.schema info:")
        print(self.schema.keys())
        # load_to_sqlite
        print('EXPORTED TO DATABASE')
        self.load_sqlite()

        self.toFile()
