class Appointment:
    def __init__(self, id, users_id, vaccines_id, completed_doses,status = "待确认"):
        self.id = id
        self.users_id = users_id
        self.vaccines_id = vaccines_id
        self.completed_doses = completed_doses
        self.status = status

    def confirm(self):
        """确认预约"""
        self.ststus = "已确认"

    def cancel(self):
        """取消预约"""
        self.status = "已取消"

    def finish(self):
        """完成预约"""
        self.status = "已完成"
