import re

class Validator:
    """
    校验工具类
    """
    @staticmethod
    def is_empty(value):
        """检验是否为空"""
        return value is None or str(value).strip == ""
    
    @staticmethod
    def validate_id_card(id_card):
        '''校验身份号码'''
        pattern = r'^[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dX]$'
        
        if not re.match(pattern, id_card):
            return False
        else:
            return True

    @staticmethod
    def validate_stock(stock):
        return stock >= 0
