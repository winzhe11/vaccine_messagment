# controllers/admin_controller.py
from services.admin_service import AdminService

class AdminController:
    def __init__(self, user_service):
        self.user_service = user_service

    # 1. 查询所有用户（对齐service的get_all_users方法）
    def query_users(self):
        return self.user_service.get_all_users()

    # 2. 删除用户（对齐service的delete_user方法）
    def delete_user(self, user_id):
        if not user_id:
            return {"success": False, "msg": "用户ID不能为空", "data": None}
        return self.user_service.delete_user(user_id)

    # 3. 数据统计（对齐service的get_statistics方法）
    def statistics(self):
        return self.user_service.get_statistics()

    # [修复闪退] 4. 修改用户角色（对齐service的update_user_role方法）
    def update_user_role(self, user_id, new_role):
        if not user_id:
            return {"success": False, "msg": "用户ID不能为空", "data": None}
        if not new_role:
            return {"success": False, "msg": "角色不能为空", "data": None}
        return self.user_service.update_user_role(user_id, new_role)

    # 5. 修改用户密码（对齐service的update_user_password方法）
    def update_user_password(self, user_id, new_password):
        if not user_id:
            return {"success": False, "msg": "用户ID不能为空", "data": None}
        if not new_password:
            return {"success": False, "msg": "密码不能为空", "data": None}
        return self.user_service.update_user_password(user_id, new_password)