# controllers/user_controller.py
class UserController:
    def __init__(self, appointment_service, vaccine_service):
        self.appointment_service = appointment_service
        self.vaccine_service = vaccine_service

    # 1. 获取疫苗列表
    def get_vaccines(self):
        return {"success": True, "data" : self.vaccine_service.get_all_vaccines()}

    # 2. 创建预约
    def create_appointment(self, users_id, vaccines_id):
        if not users_id or not vaccines_id:
            return {"success": False, "msg": "用户和疫苗信息不能为空", "data": None}
        return self.appointment_service.create_appointment(users_id, vaccines_id)

    # 3. 取消预约
    def cancel_appointment(self, appointment_id):
        if not appointment_id:
            return {"success": False, "msg": "预约ID不能为空", "data": None}
        return self.appointment_service.cancel_appointment(appointment_id)

    # 4. 查询预约记录
    def query_records(self, users_id):
        if not users_id:
            return {"success": False, "msg": "用户ID不能为空", "data": None}
        data = self.appointment_service.query_appointments(users_id)
        return {"success": True, "data": data}
    
    # 以下全为user_view中下拉菜单的调用 ----------------------------------------
    # 冯彬洲
    # 开始

    def get_by_location(self, vaccine_name, location):
        return self.vaccine_service.get_by_location(vaccine_name, location)
    
    def get_by_location_time(self, vaccine_name, location, vaccination_date):
        return self.vaccine_service.get_by_location_time(vaccine_name, location, vaccination_date)
    
    def get_cost_stock_and_all(self, vaccine_name, location, vaccination_date, manufacturers):
        return self.vaccine_service.get_cost_stock_and_all(vaccine_name, location, vaccination_date, manufacturers)

    # 结束