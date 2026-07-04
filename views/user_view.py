import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QMessageBox, QHeaderView, QDialog, QLabel,
                             QDialogButtonBox, QGroupBox, QGridLayout, QApplication,
                             QFrame, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QFont



class UserView(QMainWindow):
    def __init__(self, user_info, user_controller=None):
        super().__init__()
        self.user_info = user_info
        self.user_controller = user_controller
        self.current_selected_row = -1  # 记录当前选中的行
        self.vaccine_data_list = []     # 存储所有疫苗数据，供点击注意事项时查找

        self.init_ui()
        self.bind_events()

        # 加载数据
        if self.user_controller:
            self.load_vaccines()
        else:
            QMessageBox.warning(self, "错误", "控制器未初始化，无法加载数据")

    def init_ui(self):
        self.setWindowTitle(f"疫苗预约系统 - 普通用户 ({self.user_info.get('username', '用户')})")
        self.setWindowIcon(QIcon("images/app_icon.png"))
        self.resize(1920, 1080)

        # 屏幕自适应居中
        self.adapt_to_screen()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # ========== 顶部信息栏 ==========
        info_group = QGroupBox("用户信息")
        info_layout = QGridLayout()
        info_layout.addWidget(QLabel(f"姓名：{self.user_info.get('username', '')}"), 0, 0)
        info_layout.addWidget(QLabel(f"证件号：{self.user_info.get('users_id', '')}"), 0, 1)
        info_layout.addWidget(QLabel(f"角色：普通用户"), 0, 2)
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)

        # ========== 按钮区 ==========
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.appointment_btn = QPushButton("📋 预约选中疫苗")
        self.appointment_btn.setStyleSheet("background-color: #67C23A; color: white; padding: 8px;")

        self.cancel_btn = QPushButton("❌ 取消选中预约")
        self.cancel_btn.setStyleSheet("background-color: #F56C6C; color: white; padding: 8px;")

        self.query_btn = QPushButton("📊 查看我的预约记录")
        self.query_btn.setStyleSheet("background-color: #409EFF; color: white; padding: 8px;")

        self.refresh_btn = QPushButton("🔄 刷新疫苗列表")
        self.refresh_btn.setStyleSheet("background-color: #909399; color: white; padding: 8px;")

        btn_layout.addWidget(self.appointment_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.query_btn)
        btn_layout.addWidget(self.refresh_btn)
        main_layout.addLayout(btn_layout)

        # ========== 疫苗表格 ==========
        self.vaccine_table = QTableWidget()
        self.vaccine_table.setColumnCount(4)  # 增加一列用于状态显示
        self.vaccine_table.setHorizontalHeaderLabels([
            "疫苗名称", "可约数量", "疫苗注意事项", "状态"
        ])
        self.vaccine_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.vaccine_table.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选中
        self.vaccine_table.setSelectionMode(QTableWidget.SingleSelection)  # 单选
        self.vaccine_table.setAlternatingRowColors(True)  # 交替行颜色

        # 设置列宽
        self.vaccine_table.setColumnWidth(0, 230)  
        self.vaccine_table.setColumnWidth(1, 200)  
        self.vaccine_table.setColumnWidth(2, 250)  
        self.vaccine_table.setColumnWidth(3, 100)  

        main_layout.addWidget(self.vaccine_table)

        # ========== 预约面板（初始隐藏）==========
        self.appointment_panel = QFrame()
        self.appointment_panel.setFrameShape(QFrame.StyledPanel)
        self.appointment_panel.setStyleSheet(
            "QFrame { border: 1px solid #DCDFE6; border-radius: 8px; "
            "background-color: #FAFAFA; padding: 10px; }"
        )
        self.appointment_panel.setVisible(False)

        panel_layout = QHBoxLayout(self.appointment_panel)
        panel_layout.setSpacing(16)
        panel_layout.setContentsMargins(20, 12, 20, 12)

        # 疫苗名称
        panel_layout.addWidget(QLabel("疫苗名称："))
        self.panel_vaccine_name = QLabel("—")
        self.panel_vaccine_name.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        self.panel_vaccine_name.setStyleSheet("color: #303133; border: none;")
        self.panel_vaccine_name.setMinimumWidth(120)
        panel_layout.addWidget(self.panel_vaccine_name)

        panel_layout.addSpacing(10)

        # 医院（下拉）
        panel_layout.addWidget(QLabel("医院："))
        self.panel_location = QComboBox()
        self.panel_location.setMinimumWidth(130)
        self.panel_location.setStyleSheet(self._combo_style())
        panel_layout.addWidget(self.panel_location)

        panel_layout.addSpacing(10)

        # 预约时间（下拉）
        panel_layout.addWidget(QLabel("预约时间："))
        self.panel_time = QComboBox()
        self.panel_time.setMinimumWidth(160)
        self.panel_time.setStyleSheet(self._combo_style())
        panel_layout.addWidget(self.panel_time)

        panel_layout.addSpacing(10)

        # 生产商（下拉）
        panel_layout.addWidget(QLabel("生产商："))
        self.panel_manufacturer = QComboBox()
        self.panel_manufacturer.setMinimumWidth(160)
        self.panel_manufacturer.setStyleSheet(self._combo_style())
        panel_layout.addWidget(self.panel_manufacturer)

        panel_layout.addSpacing(20)

        # 费用
        panel_layout.addWidget(QLabel("费用："))
        self.panel_cost = QLabel("—")
        self.panel_cost.setStyleSheet("color: #E6A23C; font-weight: bold; border: none;")
        panel_layout.addWidget(self.panel_cost)
        
        panel_layout.addSpacing(20)

        # 剩余数量
        panel_layout.addWidget(QLabel("剩余数量："))
        self.panel_stock = QLabel("0")
        self.panel_stock.setStyleSheet("color: #E6A23C; font-weight: bold; border: none;")
        panel_layout.addWidget(self.panel_stock)
        
        panel_layout.addSpacing(20)

        # 确认支付按钮
        self.panel_pay_btn = QPushButton("💳 确认支付")
        self.panel_pay_btn.setMinimumSize(120, 36)
        self.panel_pay_btn.setStyleSheet(
            "QPushButton { background-color: #409EFF; color: white; "
            "border: none; border-radius: 6px; font-size: 14px; font-weight: bold; }"
            "QPushButton:hover { background-color: #66B1FF; }"
        )
        panel_layout.addWidget(self.panel_pay_btn)

        panel_layout.addStretch()
        main_layout.addWidget(self.appointment_panel)

        # ========== 底部状态栏 ==========
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #909399; padding: 5px;")
        main_layout.addWidget(self.status_label)

    def adapt_to_screen(self):
        """根据屏幕分辨率自适应窗口大小并居中"""
        screen = QApplication.primaryScreen().availableGeometry()
        screen_w, screen_h = screen.width(), screen.height()

        # 基准设计分辨率
        base_w, base_h = 1920, 1080

        if screen_w < base_w or screen_h < base_h:
            # 屏幕较小，按比例缩放以适配
            scale = min(screen_w / base_w, screen_h / base_h)
            new_w = int(base_w * scale * 0.92)
            new_h = int(base_h * scale * 0.90)
            self.resize(new_w, new_h)

        # 居中显示
        geo = self.frameGeometry()
        geo.moveCenter(screen.center())
        self.move(geo.topLeft())

    def bind_events(self):
        """绑定事件"""
        self.appointment_btn.clicked.connect(self.show_appointment_panel)
        self.cancel_btn.clicked.connect(self.cancel_appointment)
        self.query_btn.clicked.connect(self.show_records_dialog)
        self.refresh_btn.clicked.connect(self.load_vaccines)

        # 表格点击事件
        self.vaccine_table.itemClicked.connect(self.on_table_item_clicked)

        # 预约下拉菜单触发器
        
        self.panel_location.currentTextChanged.connect(self.on_location_changed)
        self.panel_time.currentTextChanged.connect(self.on_time_changed)
        self.panel_manufacturer.currentTextChanged.connect(self.update_cost)
        self.panel_pay_btn.clicked.connect(self.pay_for)
        
    def _combo_style(self):
        """下拉框统一样式"""
        return (
            "QComboBox { padding: 5px 10px; border: 1px solid #DCDFE6; "
            "border-radius: 4px; font-size: 12px; background: white; }"
            "QComboBox:hover { border-color: #409EFF; }"
            "QComboBox::drop-down { border: none; width: 20px; }"
        )

    def show_appointment_panel(self):
        """显示预约面板"""
        selected_row = self.vaccine_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "提示", "请先选中要预约的疫苗！")
            return


    
        # 填入选中疫苗的名称
        vaccine_name = self.vaccine_table.item(selected_row, 0).text() if self.vaccine_table.item(selected_row, 0) else "未知"
        self.panel_vaccine_name.setText(vaccine_name)

        # 选择的疫苗
        self.selected_vaccine_name = vaccine_name

        # 锁定信号
        self.panel_location.blockSignals(True)
        self.panel_time.blockSignals(True)
        self.panel_manufacturer.blockSignals(True)

        # 清空列表
        self.panel_location.clear()
        self.panel_time.clear()
        self.panel_manufacturer.clear()

        self.panel_location.addItems(['第一人民医院', '第二人民医院', '第三人民医院', '第四人民医院'])
        self.panel_location.setCurrentIndex(-1)   
        
        # 释放信号
        self.panel_location.blockSignals(False)
        self.panel_time.blockSignals(False)
        self.panel_manufacturer.blockSignals(False)

        self.panel_cost.setText("—")    
        self.panel_stock.setText("0")

        #self.panel_location.setCurrentIndex(0)
        #self.on_location_changed()
        

        self.appointment_panel.setVisible(True)
        self.status_label.setText(f"已选择疫苗：{vaccine_name}，请完善预约信息")

    def on_table_item_clicked(self, item):
        """表格点击事件"""
        self.current_selected_row = item.row()
        row = item.row()
        col = item.column()

        # 如果点击的是第 2 列「疫苗注意事项」，弹出详情对话框
        if col == 2:
            self._show_vaccine_info_dialog(row)
            return

        # 普通点击：显示选中的疫苗名称
        vaccine_name = self.vaccine_table.item(row, 0).text() if self.vaccine_table.item(row, 0) else "未知"
        self.status_label.setText(f"选中疫苗：{vaccine_name}")

    def _show_vaccine_info_dialog(self, row):
        """弹出疫苗注意事项详情对话框"""
        # 从存储的数据中获取疫苗信息
        vaccine_data = {}
        if row < len(self.vaccine_data_list):
            vaccine_data = self.vaccine_data_list[row]

        vaccine_name = vaccine_data.get("vaccinename")
        vaccine_info = vaccine_data.get("intro")
        stock = vaccine_data.get("stock", 0)

        status_text = "可预约" if stock > 0 else "已约满"

        # 构建信息文本
        info_lines = [
            f"📋 疫苗名称：{vaccine_name}",
            f"",
            f"⚠️ 注意事项：",
            f"  {vaccine_info}",
            f"",
            f"━━━━━━━━━━━━━━━━━━━━",
            f"📦 剩余库存：{stock}",
            f"📌 预约状态：{status_text}",
        ]
        detail_text = "\n".join(info_lines)

        QMessageBox.information(self, f"疫苗详情 - {vaccine_name}", detail_text)

    # ====================== 核心方法 ======================

    def load_vaccines(self):
        """加载疫苗列表"""
        if not self.user_controller:
            QMessageBox.warning(self, "错误", "控制器未初始化")
            return

        self.status_label.setText("正在加载疫苗列表...")

        try:
            result = self.user_controller.get_vaccines()
            if not result["success"]:
                QMessageBox.warning(self, "错误", result.get("msg", "加载失败"))
                self.status_label.setText("加载失败")
                return

            vaccine_list = result.get("data", [])
            self.vaccine_data_list = vaccine_list  # 保存原始数据供点击注意事项时查找
            self.vaccine_table.setRowCount(len(vaccine_list))

            for row, vaccine in enumerate(vaccine_list):
                self.vaccine_table.setItem(row, 0, QTableWidgetItem(vaccine.get("vaccinename", "")))
                self.vaccine_table.setItem(row, 1, QTableWidgetItem(str(vaccine.get("stock"))))
                self.vaccine_table.setItem(row, 2, QTableWidgetItem("点击查看注意事项"))


                # 状态列：根据库存显示不同状态
                stock = vaccine.get("stock")
                status_item = QTableWidgetItem()
                if stock <= 0:
                    status_item.setText("已约满")
                    status_item.setBackground(QColor(255, 200, 200))  # 浅红色
                elif stock < 10:
                    status_item.setText("库存紧张")
                    status_item.setBackground(QColor(255, 255, 200))  # 浅黄色
                else:
                    status_item.setText("可预约")
                    status_item.setBackground(QColor(200, 255, 200))  # 浅绿色
                self.vaccine_table.setItem(row, 3, status_item)
                """
                v_id = str(vaccine.get("vaccines_id", ""))
                self.vaccine_table.setItem(row, 6, QTableWidgetItem(v_id))
                """
        

            #隐藏第六列
            """
            self.vaccine_table.setColumnHidden(6, True)

            self.status_label.setText(f"加载成功，共 {len(vaccine_list)} 种疫苗")

            """
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载疫苗列表时发生异常：{str(e)}")
            self.status_label.setText("加载失败")

    def make_appointment(self):
        """提交预约"""
        if not self.user_controller:
            QMessageBox.warning(self, "错误", "控制器未初始化")
            return

        selected_row = self.vaccine_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "提示", "请先选中要预约的疫苗！")
            return

        # 检查疫苗状态
        status_item = self.vaccine_table.item(selected_row, 5)
        if status_item and status_item.text() == "已约满":
            QMessageBox.warning(self, "提示", "该疫苗已约满，无法预约！")
            return

        try:
            vaccine_id = int(self.vaccine_table.item(selected_row, 6).text())
            vaccine_name = self.vaccine_table.item(selected_row, 1).text()
            user_id = self.user_info.get("id")
            if not user_id:
                QMessageBox.warning(self, "错误", "用户信息不完整")
                return

            # 确认预约
            reply = QMessageBox.question(
                self, "确认预约",
                f"确认预约疫苗：{vaccine_name}？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

            self.status_label.setText(f"正在预约疫苗：{vaccine_name}...")
            result = self.user_controller.create_appointment(user_id, vaccine_id)

            if result.get("success"):
                QMessageBox.information(self, "预约成功", result.get("msg", "预约已提交"))
                self.status_label.setText(f"预约成功：{vaccine_name}")
                self.load_vaccines()  # 刷新列表
            else:
                QMessageBox.warning(self, "预约失败", result.get("msg", "预约失败，请稍后重试"))
                self.status_label.setText("预约失败")

        except ValueError as e:
            QMessageBox.warning(self, "错误", "数据格式错误")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"预约时发生异常：{str(e)}")

    def cancel_appointment(self):
        """取消预约"""
        if not self.user_controller:
            QMessageBox.warning(self, "错误", "控制器未初始化")
            return

        # 获取当前选中的预约记录（这里简化处理，弹出对话框让用户选择）
        # 实际应该先获取用户的预约列表，然后选择要取消的
        self.show_records_dialog(cancel_mode=True)
    
    def show_records_dialog(self, cancel_mode=False):
        # 显示预约记录对话框
        if not self.user_controller:
            QMessageBox.warning(self, "错误", "控制器未初始化")
            return

        try:
            users_id = self.user_info.get("users_id")
            if not users_id:
                QMessageBox.warning(self, "错误", "用户信息不完整")
                return

            self.status_label.setText("正在加载预约记录...")
            result = self.user_controller.query_records(users_id)

            if not result.get("success"):
                QMessageBox.warning(self, "查询失败", result.get("msg", "查询失败"))
                self.status_label.setText("加载记录失败")
                return

            records = result.get("data", [])
            if not records:
                QMessageBox.information(self, "提示", "暂无预约记录")
                self.status_label.setText("暂无预约记录")
                return

            # 创建记录对话框
            dialog = QDialog(self)
            if cancel_mode:
                dialog.setWindowTitle("选择要取消的预约")
            else:
                dialog.setWindowTitle("我的预约记录")
            dialog.resize(1400, 600)

            layout = QVBoxLayout(dialog)

            # 记录表格
            record_table = QTableWidget()
            ####
            record_table.setColumnCount(8)
            record_table.setHorizontalHeaderLabels(["疫苗名称", "疫苗批号", "疫苗剂次", "已打计次", "接种时间", "接种地点", "状态", "预约ID"])
            record_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            record_table.setSelectionBehavior(QTableWidget.SelectRows)
            record_table.setSelectionMode(QTableWidget.SingleSelection)

            record_table.setRowCount(len(records))
            for row, record in enumerate(records):
                record_table.setItem(row, 0, QTableWidgetItem(record.get("vaccinename", "")))
                record_table.setItem(row, 1, QTableWidgetItem(record.get("batch_no", "")))
                record_table.setItem(row, 2, QTableWidgetItem(str(record.get("doses", ""))))
                record_table.setItem(row, 3, QTableWidgetItem(str(record.get("completed_doses", ""))))
                record_table.setItem(row, 4, QTableWidgetItem((record.get("vaccination_date", ""))))
                record_table.setItem(row, 5, QTableWidgetItem(record.get("location", "")))
                record_table.setItem(row, 6, QTableWidgetItem(record.get("status", "")))
                record_table.setItem(row, 7, QTableWidgetItem(str(record.get("appointments_id", ""))))

            record_table.setColumnHidden(7, True)

            layout.addWidget(record_table)

            # 按钮
            button_box = QDialogButtonBox()
            if cancel_mode:
                cancel_btn = QPushButton("取消选中的预约")
                cancel_btn.setStyleSheet("background-color: #F56C6C; color: white;")
                cancel_btn.clicked.connect(lambda: self.confirm_cancel_record(dialog, record_table))
                button_box.addButton(cancel_btn, QDialogButtonBox.ActionRole)

            close_btn = QPushButton("关闭")
            close_btn.clicked.connect(dialog.accept)
            button_box.addButton(close_btn, QDialogButtonBox.ActionRole)

            layout.addWidget(button_box)
            dialog.exec_()
            self.status_label.setText("查看记录完成")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"查看记录时发生异常：{str(e)}")

    def confirm_cancel_record(self, dialog, record_table):
        # 确认取消预约记录
        selected_row = record_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "提示", "请选中要取消的预约！")
            return

        try:
            record_id = record_table.item(selected_row, 7).text()
            vaccine_name = record_table.item(selected_row, 0).text()

            reply = QMessageBox.question(
                self, "确认取消",
                f"确认取消疫苗 {vaccine_name} 的预约？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

            self.status_label.setText(f"正在取消预约：{vaccine_name}...")
            result = self.user_controller.cancel_appointment(record_id)

            if result.get("success"):
                QMessageBox.information(self, "取消成功", result.get("msg", "预约已取消"))
                self.status_label.setText(f"取消成功：{vaccine_name}")
                dialog.accept()
                self.load_vaccines()  # 刷新疫苗列表
            else:
                QMessageBox.warning(self, "取消失败", result.get("msg", "取消失败，请稍后重试"))
                self.status_label.setText("取消失败")

        except ValueError as e:
            QMessageBox.warning(self, "错误", "数据格式错误")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"取消失败：{str(e)}")

    
    # 选择医院
    def on_location_changed(self):
        location = self.panel_location.currentText()
        if not location:
            return
        # 查询数据库
        data = self.user_controller.get_by_location(self.selected_vaccine_name, location)  
        # 返回 {vaccination_date: [...], manufacturers: [...]}

        dates = list(dict.fromkeys(data["vaccination_date"]))
        # 填充时间 —— 阻塞信号，防止触发 on_time_changed
        self.panel_time.blockSignals(True)
        self.panel_time.clear()
        self.panel_time.addItems(dates)
        self.panel_time.blockSignals(False)
        
        self.on_time_changed()
        """
        # 填充生产商
        self.panel_manufacturer.blockSignals(True)
        self.panel_manufacturer.clear()
        self.panel_manufacturer.addItems(data["manufacturers"])
        self.panel_manufacturer.blockSignals(False)
        """

    # 选择时间
    def on_time_changed(self):
        location = self.panel_location.currentText()
        vaccination_date = self.panel_time.currentText()
        if not location or not vaccination_date:
            return
        data = self.user_controller.get_by_location_time(self.selected_vaccine_name, location, vaccination_date)

        self.panel_manufacturer.blockSignals(True)
        self.panel_manufacturer.clear()
        self.panel_manufacturer.addItems(data["manufacturers"])
        self.panel_manufacturer.blockSignals(False)

        self.update_cost()

    def update_cost(self):
        location = self.panel_location.currentText()
        vaccination_date = self.panel_time.currentText()
        manufacturers = self.panel_manufacturer.currentText()
        if not location or not vaccination_date or not manufacturers:
            return 
        result = self.user_controller.get_cost_stock_and_all(self.selected_vaccine_name, location, vaccination_date, manufacturers)

        if result.get("success"):
            self.panel_cost.setText(f"¥{result['data']['cost']}")
            self.panel_stock.setText(f"{result['data']['stock']}")

    # 支付并加入预约
    def pay_for(self):
        from views.pay_view import PayWindow 
        location = self.panel_location.currentText()
        vaccination_date = self.panel_time.currentText()
        manufacturers = self.panel_manufacturer.currentText()
        result = self.user_controller.get_cost_stock_and_all(self.selected_vaccine_name, location, vaccination_date, manufacturers)

        pay_win = PayWindow(result['data']['cost'])
        pay_win.exec_()

        users_id = self.user_info["users_id"]
        vaccines_id = result["data"]["batch_no"]

        result = self.user_controller.create_appointment(users_id, vaccines_id)

        if result["success"]:
            self.load_vaccines()       # 刷新主表格
            self.update_cost() 
            QMessageBox.information(
            self,
            "预约成功",
            f'<span style="font-size:14pt;">感谢您的支持🌹🌹🌹<br>请您在{vaccination_date}携带身份证前往{location}接种批次为{vaccines_id}的{self.selected_vaccine_name}</span>'
        )


    def closeEvent(self, event):
        # 窗口关闭事件
        # 可以在这里添加清理逻辑
        self.status_label.setText("正在退出...")
        event.accept()