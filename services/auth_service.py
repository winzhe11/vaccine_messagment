from models.user import NormalUser, HospitalUser, Admin
from utils.validator import Validator
from utils.exceptions import LoginError, AppointError

class Auth_service:
    """
    认证服务
    负责登录注册
    """

    def __init__(self, user_dao):
        """
        user_dao为数据库对象
        """
        self.user_dao = user_dao

    def login(self, user_name, users_id, password):

        """
        用户登录
        :param username: 用户名
        :param password: 密码
        :return: {"success": True, "data": user} 或 {"success": False, "msg": 错误信息}
        """
         
        if Validator.is_empty(user_name):
            return {"success": False, "msg": "用户名不能为空"}
        if Validator.is_empty(password):
            return {"success": False, "msg": "密码不能为空"}
        

        user = self.user_dao.find_by_users_id(users_id)

        if user is None:
            return {"success": False, "msg": "用户不存在"}
        
        users_id, db_user_name, db_password, role = user

        if db_user_name != user_name:
            return {"success": False, "msg": "证据与姓名不对应"}

        if db_password != password:
            return {"success": False, "msg": "密码错误"}
        
        if role == "normal":
            user = NormalUser(users_id, user_name, password)
        elif role == "hospital":
            user = HospitalUser(users_id, user_name, password)
        elif role == "admin":
            user = Admin(users_id, user_name, password)
        else:
            return {"success": False, "msg": "未知角色"}
        
        # user为数据库对象,即用户实体对象
        user_data = {
            "users_id": user.id_card,
            "username": user.username,
            "role": user.role
        }

        # 如果是医生/医院角色，查询关联的医院名称
        if role == "hospital":
            from dao.hospital_dao import HospitalDAO
            hospital_dao = HospitalDAO()
            hospitals = hospital_dao.get_hospitals_by_doctor(users_id)
            user_data["hospital_names"] = [h["hospital_name"] for h in hospitals]
            user_data["hospital_name"] = user_data["hospital_names"][0] if user_data["hospital_names"] else "未选择医院"
            hospital_dao.close()

        return {"success": True, "data": user_data}
    
    def register(self, username, id_card, password, role="normal", hospital_name=None):

        """
        用户注册
        :param username: 用户名
        :param password: 密码
        :param id_card: 身份证号
        :param role: 用户角色 (normal/hospital/admin)
        :param hospital_name: 医生所属单位名称（仅role=hospital时使用）
        :return: {"success": True, "data": user} 或 {"success": False, "msg": 错误信息}
        """

        if Validator.is_empty(username):
            return {"success": False, "msg": "姓名不能为空"}
        if Validator.is_empty(password):
            return {"success": False, "msg": "密码不能为空"}
        if Validator.is_empty(id_card):
            return {"success": False, "msg": "身份证号不能为空"}
        if not Validator.validate_id_card(id_card):
            return {"success": False, "msg": "身份证号不合法"}
        if role not in ("normal", "hospital", "admin"):
            return {"success": False, "msg": "无效的角色类型"}
        if role == "hospital" and Validator.is_empty(hospital_name):
            return {"success": False, "msg": "医生角色必须填写工作单位"}

        # 判断是否被占用
        existing = self.user_dao.find_by_users_id(id_card)
        if existing:
            return {"success": False, "msg": "该用户已注册"}

        # 根据角色创建对应的用户实体
        if role == "normal":
            user = NormalUser(id_card, username, password)
        elif role == "hospital":
            user = HospitalUser(id_card, username, password)
        elif role == "admin":
            user = Admin(id_card, username, password)
        else:
            return {"success": False, "msg": "未知角色"}

        # 添加进数据库
        self.user_dao.add_user(user)

        # 如果是医生/医院角色，同时添加医院关联
        if role == "hospital" and hospital_name:
            from dao.hospital_dao import HospitalDAO
            hospital_dao = HospitalDAO()
            hospital_dao.add_doctor_hospital(id_card, hospital_name)
            hospital_dao.close()

        return {"success": True, "msg": "注册成功"}
        
    def verify_identity(self, name, id_card):
        """
        身份验证（模拟实名认证）
        :param name: 姓名
        :param id_card: 身份证号
        :return: {"success": True, "msg": "验证通过"} 或 {"success": False, "msg": 错误信息}
        """
        if Validator.is_empty(name):
            return {"success": False, "msg": "姓名不能为空"}
        if Validator.is_empty(id_card):
            return {"success": False, "msg": "身份证号不能为空"}
        if not Validator.validate_id_card(id_card):
            return {"success": False, "msg": "身份证号不合法"}
        
        return {"success": True, "msg": "身份验证通过"}

    def reset_password(self, name, id_card, new_password):
        """
        重置密码：通过姓名+身份证号定位用户，更新密码
        :param name: 姓名
        :param id_card: 身份证号
        :param new_password: 新密码
        :return: {"success": True, "msg": "密码重置成功"} 或 {"success": False, "msg": 错误信息}
        """
        if Validator.is_empty(name):
            return {"success": False, "msg": "姓名不能为空"}
        if Validator.is_empty(id_card):
            return {"success": False, "msg": "身份证号不能为空"}
        if Validator.is_empty(new_password):
            return {"success": False, "msg": "新密码不能为空"}
        if len(new_password) < 6:
            return {"success": False, "msg": "密码长度不能少于6位"}

        user = self.user_dao.find_by_users_id(id_card)
        if user is None:
            return {"success": False, "msg": "该用户不存在，请先注册"}

        users_id, db_user_name, db_password, role = user
        if db_user_name != name:
            return {"success": False, "msg": "姓名与身份证号不匹配"}

        self.user_dao.update_password(id_card, new_password)
        return {"success": True, "msg": "密码重置成功"}