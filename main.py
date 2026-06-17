from etl import ETLer
import sqlite3

#FILE_PATH = 'rat/public/data/tables/'
FILE_PATH = 'rat/public/data/BinData/'

def load_sqlite(dml, data, path="rocom.db"):
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()

        cursor.executemany(
            dml,
            data
        )
        conn.commit()

    except sqlite3.Error as e:
        print(f"database error: {e}")

    finally:
        cursor.close()
        conn.close()


e = ETLer(root=FILE_PATH)
#e.export_color_html()
e.load_sqlite()

load_sqlite(
    "INSERT INTO skill_descs (id, name, desc) VALUES (?,?,?)",
    [[3006, '沙暴', '天气为沙暴时，双方的地系技能能耗减半。'],
     [3007, '暴风雪', '天气为暴风雪时，双方每回合结束获得2层冰结。（冰系精灵免疫此效果）'],
     [3009, '离场', '通过主动更换精灵或触发脱离效果的方式下场。（不包括精灵力竭后下场）'],
     [3010, '印记', '精灵下场后印记不会消失，新入场的精灵会继承印记效果。精灵最多同时拥有1种正面印记和1种负面印记。']])

