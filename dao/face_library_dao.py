from database.db import DB

class FaceLibraryDAO:

    def __init__(self):
        self.db = DB()
        self.db.connect()

    def get_path_by_idCard(self, users_id):
        sql = "SELECT images_path FROM face_library WHERE users_id = ?"
        self.db.cursor.execute(sql,(users_id,))
        return self.db.cursor.fetchone()