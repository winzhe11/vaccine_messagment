from abc import ABC, abstractmethod


# 抽象类
class User(ABC):

    def __init__(self, id_card, username, password, role):

        """
        初始化用户基础信息
        :param id: 用户ID (数据库主键)
        :param username: 登录账号 (唯一)
        :param password: 登录密码 (课设明文即可)
        :param name: 真实姓名
        :param id_card: 身份证号
        :param role: 角色标识 (normal/hospital/admin)
        """
        
        self.username = username
        self.password = password
        self.id_card = id_card
        self.role = role

    @abstractmethod
    def get_role(self):
        pass

class NormalUser(User):

    def __init__(self, id_card, username, password):
        super().__init__(id_card, username, password, "normal")

    def get_role(self):
        return "普通用户"
    
    def make_appointment(self):
        """预约疫苗"""
        pass

    def view_records(self):
        """查看接种记录"""
        pass

class HospitalUser(User):

    def __init__(self, id_card, username, password):
        super().__init__(id_card, username, password,"hospital")

    def get_role(self):
        return "医院用户"

    def publish_vaccine(self):
        """发布疫苗库存"""
        pass

    def confirm_appointment(self):
        """确认预约"""
        pass

class Admin(User):

    def __init__(self, id_card, username, password):
        super().__init__(id_card, username, password, "admin")

    def get_role(self):
        return "管理员"
    
    def manage_users(self):
        """管理用户"""
        pass

