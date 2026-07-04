class AppException(Exception):
    """
    应用异常
    做父类
    """
    pass

class LoginError(AppException):
    '''登录异常'''
    pass

class AppointError(AppException):
    """预约异常"""
    pass

class StockError(AppException):
    """库存异常"""
    pass