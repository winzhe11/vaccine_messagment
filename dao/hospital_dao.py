from database.db import DB


class HospitalDAO:

    def __init__(self):
        self.db = DB()
        self.db.connect()

    def get_hospitals_by_doctor(self, users_id):
        """查询某个医生关联的所有医院
        :param users_id: 医生用户ID
        :return: list[dict] 医院列表
        """
        sql = "SELECT id, hospital_name FROM doctor_hospital WHERE users_id=?"
        self.db.cursor.execute(sql, (users_id,))
        rows = self.db.cursor.fetchall()
        return [{"id": r["id"], "hospital_name": r["hospital_name"]} for r in rows]

    def get_all_hospitals(self):
        """查询所有不重复的医院名称（用于医生选择）"""
        sql = "SELECT DISTINCT hospital_name FROM doctor_hospital"
        self.db.cursor.execute(sql)
        rows = self.db.cursor.fetchall()
        return [r["hospital_name"] for r in rows]

    def add_doctor_hospital(self, users_id, hospital_name):
        """添加医生-医院关联
        :param users_id: 医生用户ID
        :param hospital_name: 医院名称
        """
        sql = "INSERT INTO doctor_hospital (users_id, hospital_name) VALUES (?, ?)"
        try:
            self.db.cursor.execute(sql, (users_id, hospital_name))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def close(self):
        """关闭数据库连接"""
        self.db.close()
