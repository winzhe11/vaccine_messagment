from models.vaccine import Vaccine
from utils.validator import Validator


class Vaccine_service:
    
    def __init__(self, vaccine_dao):
        """
        初始化疫苗服务
        :param vaccine_dao: 疫苗数据访问对象
        """
        self.vaccine_dao = vaccine_dao

    def add_vaccine(self, name, manufacturer, batch_no, stock, produce_date=None, location="", doses=1, cost=0):

        if Validator.is_empty(name):
            return {"success": False, "msg": "疫苗名称不能为空"}
        if Validator.is_empty(manufacturer):
            return {"success": False, "msg": "生产厂家不能为空"}
        if Validator.is_empty(batch_no):
            return {"success": False, "msg": "批号不能为空"}
        if stock < 0:
            return {"success": False, "msg": "库存不能为负数"}

        existing = self.vaccine_dao.find_by_batch_no(batch_no)
        if existing:
            return {"success": False, "msg": "疫苗批号不能重复"}

        self.vaccine_dao.add_vaccine(name, manufacturer, produce_date, batch_no, stock, location, doses, cost)

        return {"success": True, "msg": "疫苗发布成功"}
    
    def get_all_vaccines(self):
        """
        获取所有疫苗列表
        :return: 所有疫苗记录列表
        """
        result = self.vaccine_dao.get_all_vaccines()
        
        vaccine_list = [dict(row) for row in result]

        return vaccine_list
    
    def update_stock(self, vaccine_id, num):
        """
        更新疫苗库存
        :param vaccine_id: 疫苗ID
        :param num: 变更数量
        :return: {"success": True, "msg": "更新成功"} 或 {"success": False, "msg": 错误信息}
        """

        vaccine = self.vaccine_dao.find_by_id(vaccine_id)
        if vaccine == None:
            return {"success": False, "msg": "疫苗不存在"}
        
        current_stock = vaccine[5]
        new_stock = current_stock + num

        if new_stock < 0:
            return {"success": False, "msg": "库存不能小于0"}
        
        self.vaccine_dao.update_stock(vaccine_id, new_stock)

        return {"success": True, "msg": "更新成功"}
    
    def get_vaccines_by_location(self, location):
        """
        按接种地点（医院名称）查询疫苗列表
        :param location: 医院名称
        :return: 疫苗列表
        """
        result = self.vaccine_dao.get_vaccines_by_location(location)
        return [dict(row) for row in result]

    # 以下全为user_view中下拉菜单调用controllers后的调用 ----------------------------------------
    # 冯彬洲
    # 开始

    def get_by_location(self, vaccine_name, location):
        # 返回时间和厂商
        rows = self.vaccine_dao.get_by_location(vaccine_name, location)
        vaccination_date_list = [row[0] for row in rows]
        manufacturers_list = [row[1] for row in rows]
        return {"vaccination_date" : vaccination_date_list, "manufacturers" : manufacturers_list}
    
    def get_by_location_time(self, vaccine_name, location, vaccination_date):
        
        rows = self.vaccine_dao.get_by_location_time(vaccine_name, location, vaccination_date)
        manufacturers_list = [row[0] for row in rows]
        return {"manufacturers" : manufacturers_list}
    
    def get_cost_stock_and_all(self, vaccine_name, location, vaccination_date, manufacturers):

        data_list = self.vaccine_dao.get_cost_stock_and_all(vaccine_name, location, vaccination_date, manufacturers)

        return {"success": True, "data" : data_list}
    # 结束