from database.db import DB


class AppointmentDAO:

    def __init__(self):
        self.db = DB()
        self.db.connect()

    def add_appointment(self, apd):
        sql = """
        INSERT INTO appointments(users_id, batch_no, completed_doses, status)
        VALUES (?, ?, ?, ?)
        """
        self.db.cursor.execute(sql, (apd.users_id, apd.vaccines_id, apd.completed_doses, apd.status))
        self.db.commit()

    def update_status(self, appointment_id, status):
        sql = "UPDATE appointments SET status=? WHERE appointments_id=?"
        self.db.cursor.execute(sql, (status, appointment_id))
        self.db.commit()

    def find_by_user(self, user_id):
        sql = "SELECT * FROM appointments JOIN users ON users.users_id = appointments.users_id JOIN vaccines ON vaccines.batch_no = appointments.batch_no WHERE appointments.users_id=?"
        self.db.cursor.execute(sql, (user_id,))
        return self.db.cursor.fetchall()

    def find_by_id(self, appointment_id):
        sql = "SELECT * FROM appointments WHERE appointments_id=?"
        self.db.cursor.execute(sql, (appointment_id,))
        return self.db.cursor.fetchone()

    def get_all_appointments(self):
        sql = "SELECT * FROM appointments as ap JOIN users as " \
        "us ON us.users_id = ap.users_id " \
        "JOIN vaccines as va ON va.batch_no = ap.batch_no"
        self.db.cursor.execute(sql)
        return self.db.cursor.fetchall()

    def get_appointments_by_hospital(self, hospital_name):
        """按医院名称（vaccines.location）查询预约"""
        sql = """
        SELECT ap.appointments_id, us.username AS user_name,
               va.vaccinename AS vaccine_name, va.vaccination_date,
               ap.status, va.batch_no
        FROM appointments AS ap
        JOIN users AS us ON us.users_id = ap.users_id
        JOIN vaccines AS va ON va.batch_no = ap.batch_no
        WHERE va.location = ?
        ORDER BY ap.appointments_id
        """
        self.db.cursor.execute(sql, (hospital_name,))
        return self.db.cursor.fetchall()

    def exists(self, users_id, batch_no):
        sql = """
        SELECT 1 FROM appointments
        WHERE users_id = ? AND batch_no=? AND status != '已取消'
        LIMIT 1
        """
        self.db.cursor.execute(sql, (users_id, batch_no))
        row = self.db.cursor.fetchone()
        return row is not None
    
