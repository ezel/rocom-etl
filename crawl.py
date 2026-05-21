import requests
from bs4 import BeautifulSoup
import sqlite3

class BiliCrawler():
    def __init__(self):
        self.URL_BASE = "https://wiki.biligame.com"
        self.raw = {}
        self.schema = {}
        self.fetch_data()

    def fetch_data(self):
        # fetch 2 tables
        #self.fetch_skill_table()
        #self.transform_skill()
        self.fetch_pet_table()
        self.transform_pet()
        
        # fetch pet detail
        #self.fetch_pet_detail()


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
        # ['icon_src', 'name', 'type', 'damage_type'
        #  'damage_type', 'energy, 'damage', 'desp', 'version'
        #  'href']
        url = "https://wiki.biligame.com/rocom/%E6%8A%80%E8%83%BD%E7%AD%9B%E9%80%89"
        rk = requests.get(url)
        html_doc = rk.text
        soup = BeautifulSoup(html_doc, 'lxml')
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
            'ddl' : "CREATE TABLE IF NOT EXISTS bili_skill (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL, desc TEXT NOT NULL, damage_type TEXT NOT NULL, skill_type TEXT NOT NULL, energy INTEGER NOT NULL, damage INTEGER NOT NULL,icon_path TEXT NOT NULL,link TEXT NOT NULL, version TEXT )",
            'dml' : "INSERT INTO bili_skill (icon_path, name, damage_type, skill_type, energy, damage, desc, version, link) VALUES (?,?,?,?,?,?,?,?,?)",
            'clean': "DROP TABLE IF EXISTS bili_skill",
            'data': [(r[0],r[1],r[2],r[3],
                      r[4],r[5],r[6],r[7],r[8]) for r in self.raw['skillsTable']],
        }

        
    def fetch_pet_table(self):
        # pets list of
        # ['icon_src', 'name', 'types', 'petid', 'ability',
        # 'race_hp', 'race_spd', 'race_patk', 'race_satk', 'race_pdef', 'race_sdef', 'race_total', 'version',
        # 'href', 'data_region', 'data_rank']
        url = "https://wiki.biligame.com/rocom/%E7%B2%BE%E7%81%B5%E7%AD%9B%E9%80%89"
        rk = requests.get(url)
        html_doc = rk.text
        soup = BeautifulSoup(html_doc, 'lxml')
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
        
        self.raw['petsTable'] = pets

    def transform_pet(self):
        self.schema['bili_pet'] = {
            'ddl' : "CREATE TABLE IF NOT EXISTS bili_pet_base (id INTEGER PRIMARY KEY,hid INTEGER NOT NULL, name TEXT NOT NULL,ability TEXT NOT NULL,type1 TEXT NOT NULL,type2 TEXT,stage TEXT NOT NULL,form TEXT,race_hp INTEGER NOT NULL,race_patk INTEGER NOT NULL,race_satk INTEGER NOT NULL,race_pdef INTEGER NOT NULL,race_sdef INTEGER NOT NULL,race_spe INTEGER NOT NULL,race_sum INTEGER NOT NULL, icon_path TEXT NOT NULL, link TEXT NOT NULL, version TEXT)",
            'dml' : "INSERT INTO bili_pet_base (icon_path, name, type1, type2, hid, ability, race_hp, race_spe, race_patk, race_satk, race_pdef, race_sdef, race_sum, version, link, form, stage) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            'clean': "DROP TABLE IF EXISTS bili_pet_base",
            'data': [(r[0],r[1],r[2],r[3],r[4],
                      r[5],r[6],r[7],r[8],
                      r[9],r[10],r[11],r[12],
                      r[13],r[14],r[15],r[16]) for r in self.raw['petsTable']],
        }

        
    def fetch_pet_detail(self):
        pass

    
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
        print(self.raw.keys())
        for k in self.raw.keys():
            print(f'{k} has {len(self.raw[k])} rows, first line:')
            if type(self.raw[k]) == type([]):
                print(self.raw[k][:3])

        # load_to_sqlite
        print('EXPORTED TO DATABASE')
        self.load_sqlite()

