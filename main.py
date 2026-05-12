from etl import ETLer

#FILE_PATH = 'rat/public/data/tables/'
FILE_PATH = 'rat/public/data/BinData/'

e = ETLer(root=FILE_PATH)

e.test()
