from database.db import DB

db = DB()
db.connect()
cursor = db.cursor

cursor.execute("""
INSERT INTO face_library VALUES('610222000008161099', '冯彬洲', '610222200608121099_冯彬洲.jpg')
""")


db.commit()
db.close()


