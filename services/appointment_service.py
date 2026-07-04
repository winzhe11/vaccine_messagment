from models.appointment import Appointment
from utils.exceptions import StockError

class Appointment_service:

    def __init__(self, appointment_dao, vaccine_dao):

        self.appointment_dao = appointment_dao
        self.vaccine_dao = vaccine_dao

    def create_appointment(self, users_id, vaccines_id):
        """
        创建预约
        :param user_id: 用户ID
        :param vaccine_id: 疫苗ID
        :return: {"success": True, "data": appointment} 或 {"success": False, "msg": 错误信息}
        """
        vaccine = self.vaccine_dao.find_by_batch_no(vaccines_id)
        if not vaccine:
            return {"success": False, "msg": "疫苗不存在"}

        stock = vaccine["stock"]
        if stock <= 0:
            return {"success": False, "msg": "库存不足"}
        
        if self.appointment_dao.exists(users_id, vaccines_id):
            return {"success": False, "msg": "你已预约过此疫苗，请勿重复预约"}
        
        appointment = Appointment(None, users_id, vaccines_id, 0, "待确认")

        self.appointment_dao.add_appointment(appointment)

        self.vaccine_dao.update_stock(vaccines_id, stock - 1)

        return {"success": True, "data": appointment}
    
    def confirm_appointment(self, appointment_id):
        """
        确认预约（将状态改为"已确认"）
        :param appointment_id: 预约ID
        :return: {"success": True, "msg": "确认成功"} 或 {"success": False, "msg": 错误信息}
        """
        appointment = self.appointment_dao.find_by_id(appointment_id)
        if appointment is None:
            return {"success": False, "msg": "预约不存在"}
        
        status = appointment[4]

        if status != "待确认":
            return {"success": False, "msg": f"当前状态为{status}:无法确认"}

        self.appointment_dao.update_status(appointment_id, "已确认")

        return {"success": True, "msg": "确认成功"}

    def cancel_appointment(self, appointment_id):

        appointment = self.appointment_dao.find_by_id(appointment_id)
        if appointment is None:
            return {"success": False, "msg": "预约不存在"}

        status = appointment[4]

        if status == "已完成":
            return {"success": False, "msg": "已完成接种无法取消"}

        self.appointment_dao.update_status(appointment_id, "已取消")

        result = self.appointment_dao.find_by_id(appointment_id)
        vaccine_id = result[2]
        result_stock = self.vaccine_dao.find_by_batch_no(vaccine_id)
        stock = result_stock["stock"]
        self.vaccine_dao.update_stock(vaccine_id, stock + 1)

        return {"success": True, "msg": "取消成功"}
    
    def get_appointments_by_hospital(self, hospital_name):
        """
        按医院名称查询预约列表
        :param hospital_name: 医院名称
        :return: 预约列表
        """
        result = self.appointment_dao.get_appointments_by_hospital(hospital_name)
        return [dict(row) for row in result]

    def update_appointment_status(self, appointment_id, new_status):
        """
        修改预约状态（支持任意状态变更，由 controller 层做权限校验）
        :param appointment_id: 预约ID
        :param new_status: 新状态
        :return: {"success": True, "msg": ...} 或 {"success": False, "msg": ...}
        """
        valid_statuses = ("待确认", "已确认", "已完成", "已取消")
        if new_status not in valid_statuses:
            return {"success": False, "msg": f"无效状态：{new_status}"}

        appointment = self.appointment_dao.find_by_id(appointment_id)
        if appointment is None:
            return {"success": False, "msg": "预约不存在"}

        self.appointment_dao.update_status(appointment_id, new_status)
        return {"success": True, "msg": f"预约状态已更新为：{new_status}"}

    def query_appointments(self, users_id):

        result = self.appointment_dao.find_by_user(users_id)

        appointments_list = [dict(row) for row in result]
        
        return appointments_list
    
    def complete_vaccination(self, appointment_id):

        appointment = self.appointment_dao.find_by_id(appointment_id)
        if appointment is None:
            return {"success": False, "msg": "预约不存在"}
        
        status = appointment[4]

        if status != "已确认":
            return {"success": False, "msg": f"当前状态为{status}：无法完成接种"}

        self.appointment_dao.update_status(appointment_id, "已完成")

        return {"success": True, "msg": "接种完成"}
