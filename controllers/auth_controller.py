# controllers/auth_controller.py
class AuthController:
    # 初始化：注入AuthService（课件要求的写法）
    def __init__(self, auth_service):
        self.auth_service = auth_service

    # 登录方法：入参来自View界面
    def login(self, username, users_id, password):
        # 1. 基础参数校验（仅非空，复杂校验放Service）
        if not username or not password:
            return {"success": False, "msg": "账号密码不能为空", "data": None}
        if not users_id:
            return {"success": False, "msg": "身份证号不能为空", "data": None}
        # 2. 调用Service层（业务逻辑全在Service）
        result = self.auth_service.login(username, users_id, password)
        # 3. 返回结果给View
        return result

    # 注册方法
    def register(self, username, users_id, password, role="normal", hospital_name=None):
        if not all([username, password, users_id]):
            return {"success": False, "msg": "所有信息不能为空", "data": None}
        if role == "hospital" and not hospital_name:
            return {"success": False, "msg": "医生角色必须填写工作单位", "data": None}
        result = self.auth_service.register(username, users_id, password, role, hospital_name)
        return result

    # 重置密码
    def reset_password(self, name, id_card, new_password):
        if not all([name, id_card, new_password]):
            return {"success": False, "msg": "所有信息不能为空"}
        result = self.auth_service.reset_password(name, id_card, new_password)
        return result