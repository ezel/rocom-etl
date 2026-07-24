import sqlite3
import os
import sys

def insert_filenames_to_db(folder_path, db_name='files.db'):
    # 1. 连接到 SQLite 数据库（如果不存在会自动创建）
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # 2. 创建数据表（如果不存在）
    cursor.execute('''CREATE TABLE IF NOT EXISTS files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT NOT NULL
                      )''')

    # 3. 获取文件夹下所有的文件名
    try:
        filenames = [(name,) for name in os.listdir(folder_path)]
    except Exception as e:
        print(f"读取文件夹失败: {e}")
        return

    # 4. 使用 executemany 进行批量插入（提高性能并防止SQL注入）
    cursor.executemany('INSERT INTO files (filename) VALUES (?)', filenames)

    # 5. 提交事务并关闭连接
    conn.commit()
    print(f"成功插入 {len(filenames)} 个文件名！")
    cursor.close()
    conn.close()

# 调用函数，传入目标文件夹路径
if __name__ == '__main__':
    # 判断是否传入了足够的参数
    if len(sys.argv) < 2:
        print("用法: python scanner.py <目标文件夹路径> [可选: 数据库名称]")
        print("示例: python scanner.py ./my_test_folder val_files.db")
        sys.exit(1)

    # 提取命令行参数
    target_folder = sys.argv[1]
    # 如果用户提供了第二个参数作为数据库名，则使用它；否则默认使用 'files.db'
    database_name = sys.argv[2] if len(sys.argv) >= 3 else 'rocom.db'

    # 执行核心逻辑
    insert_filenames_to_db(target_folder, database_name)
