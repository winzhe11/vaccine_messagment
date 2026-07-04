# controllers/hospital_controller.py
class HospitalController:
    def __init__(self, vaccine_service, appointment_service):
        self.vaccine_service = vaccine_service
        self.appointment_service = appointment_service

    # 1. 发布疫苗
    def publish_vaccine(self, vaccinename, manufacturer, batch_no, stock,
                        vaccination_date, hospital_name, doses=1, cost=0):
        """发布新疫苗，hospital_name 作为接种地点(location)存储"""
        if not all([vaccinename, manufacturer, batch_no, stock, vaccination_date, hospital_name]):
            return {"success": False, "msg": "所有疫苗信息不能为空", "data": None}
        return self.vaccine_service.add_vaccine(
            vaccinename, manufacturer, batch_no, stock,
            vaccination_date, hospital_name, doses, cost
        )

    # 2. 查询本医院疫苗
    def get_hospital_vaccines(self, hospital_name):
        """获取指定医院的疫苗列表"""
        if not hospital_name:
            return {"success": False, "msg": "医院名称不能为空", "data": []}
        try:
            data = self.vaccine_service.get_vaccines_by_location(hospital_name)
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "msg": f"查询疫苗失败：{str(e)}", "data": []}

    # 3. 查询本医院预约
    def get_hospital_appointments(self, hospital_name):
        """获取指定医院的预约列表"""
        if not hospital_name:
            return {"success": False, "msg": "医院名称不能为空", "data": []}
        try:
            data = self.appointment_service.get_appointments_by_hospital(hospital_name)
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "msg": f"查询预约失败：{str(e)}", "data": []}

    # 4. 确认预约
    def confirm_appointment(self, appointment_id):
        if not appointment_id:
            return {"success": False, "msg": "预约ID不能为空", "data": None}
        return self.appointment_service.confirm_appointment(appointment_id)

    # 5. 完成接种
    def complete_vaccination(self, appointment_id):
        if not appointment_id:
            return {"success": False, "msg": "预约ID不能为空", "data": None}
        return self.appointment_service.complete_vaccination(appointment_id)

    # 6. 取消预约
    def cancel_appointment(self, appointment_id):
        if not appointment_id:
            return {"success": False, "msg": "预约ID不能为空", "data": None}
        return self.appointment_service.cancel_appointment(appointment_id)

    # 7. 修改预约状态（通过 service 层，不走 DAO 直连）
    def update_appointment_status(self, appointment_id, new_status):
        if not appointment_id:
            return {"success": False, "msg": "预约ID不能为空", "data": None}
        if not new_status:
            return {"success": False, "msg": "状态不能为空", "data": None}
        return self.appointment_service.update_appointment_status(appointment_id, new_status)

