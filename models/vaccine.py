class Vaccine():
    def __init__(self, id, name, manufacturer, produce_date, batch_no, stock):
        """
        初始化疫苗信息
        :param id: 疫苗ID (主键)
        :param name: 疫苗名称 (如：新冠疫苗)
        :param manufacturer: 生产厂家 (如：科兴)
        :param produce_date: 生产日期 (datetime.date 或 str)
        :param batch_no: 批号 (唯一标识)
        :param stock: 库存数量 (必须 >= 0)
        """
        self.id = id
        self.name = name
        self.manufacturer = manufacturer
        self.produce_date = produce_date
        self.batch_no = batch_no
        self.stock = stock if stock >= 0 else 0

    def reduce_stock(self, num):
        if self.stock < num:
            print(f"错误:当前库存不足{num}")
            return False
        else:
            num -= self.stock 
            print(f"成功:库存已减少{num}")
            return True
    
    def is_available(self):
        return self.stock > 0