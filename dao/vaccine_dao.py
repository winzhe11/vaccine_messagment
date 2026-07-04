from database.db import DB


class VaccineDAO:

    def __init__(self):
        self.db = DB()
        self.db.connect()

    def add_vaccine(self, name, manufacturer, produce_date, batch_no, stock, location="", doses=1, cost=0):
        sql = """
        INSERT INTO vaccines(vaccinename, manufacturer, vaccination_date, batch_no, stock, location, doses, cost)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.db.cursor.execute(sql, (name, manufacturer, produce_date, batch_no, stock, location, doses, cost))
        self.db.commit()

    def update_stock(self, batch_no, stock):
        sql = "UPDATE vaccines SET stock=? WHERE batch_no=?"
        self.db.cursor.execute(sql, (stock, batch_no))
        self.db.commit()

    def delete_vaccine(self, vaccine_id):
        sql = "DELETE FROM vaccines WHERE batch_no=?"
        self.db.cursor.execute(sql, (vaccine_id,))
        self.db.commit()

    def find_by_id(self, vaccine_id):
        sql = "SELECT * FROM vaccines WHERE batch_no=?"
        self.db.cursor.execute(sql, (vaccine_id,))
        return self.db.cursor.fetchone()

    #在user_view初始显示中按照疫苗名称分组求人数
    def get_all_vaccines(self):
        sql = "SELECT  vaccines.vaccinename, vaccine_info.intro, SUM(vaccines.stock) AS stock FROM vaccines JOIN vaccine_info ON vaccines.vaccinename = vaccine_info.vaccinename " \
        " GROUP BY vaccines.vaccinename, vaccine_info.intro ORDER BY vaccines.vaccinename"
        self.db.cursor.execute(sql)
        return self.db.cursor.fetchall()
    
    def find_by_batch_no(self, batch_no):
        sql = "SELECT * FROM vaccines WHERE batch_no = ?"
        self.db.cursor.execute(sql, (batch_no,))
        return self.db.cursor.fetchone()

    def get_vaccines_by_location(self, location):
        """按接种地点（医院名称）查询疫苗"""
        sql = "SELECT * FROM vaccines WHERE location = ? ORDER BY vaccinename"
        self.db.cursor.execute(sql, (location,))
        return self.db.cursor.fetchall()

    # 以下全为user_view中下拉菜单调用controllers后的调用services后调用数据库 ----------------------------------------
    # 冯彬洲
    # 开始
    def get_by_location(self, vaccine_name, location):
        # 返回时间和厂商
        sql = "SELECT vaccination_date, manufacturer FROM vaccines WHERE vaccinename = ? AND location = ?"
        self.db.cursor.execute(sql, (vaccine_name, location))
        return self.db.cursor.fetchall()

    def get_by_location_time(self, vaccine_name, location, vaccination_date):
        sql = "SELECT manufacturer FROM vaccines WHERE vaccinename = ? AND location = ? AND vaccination_date = ?"
        self.db.cursor.execute(sql, (vaccine_name, location, vaccination_date))
        return self.db.cursor.fetchall()
    
    def get_cost_stock_and_all(self, vaccine_name, location, vaccination_date, manufacturers):
        sql = "SELECT * FROM vaccines WHERE vaccinename = ? AND location = ? AND vaccination_date = ? AND manufacturer = ?"
        self.db.cursor.execute(sql, (vaccine_name, location, vaccination_date, manufacturers))
        return self.db.cursor.fetchone()
    # 结束