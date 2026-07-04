from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton, QMessageBox,
                             QDialog, QLineEdit, QFormLayout, QDialogButtonBox,
                             QApplication, QLabel, QHeaderView, QGroupBox,
                             QComboBox, QGridLayout, QAbstractItemView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QIcon, QFont
import sys
from datetime import datetime


class VaccinePublishDialog(QDialog):
    """发布新疫苗弹窗"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("发布新疫苗")
        self.setWindowIcon(QIcon("images/app_icon.png"))
        self.resize(400, 350)
        self.setMinimumSize(380, 300)

        layout = QFormLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如：新冠灭活疫苗")
        self.name_edit.setFixedHeight(34)
        self.manufacturer_edit = QLineEdit()
        self.manufacturer_edit.setPlaceholderText("例如：北京生物")
        self.manufacturer_edit.setFixedHeight(34)
        self.batch_edit = QLineEdit()
        self.batch_edit.setPlaceholderText("例如：B202406001")
        self.batch_edit.setFixedHeight(34)
        self.stock_edit = QLineEdit()
        self.stock_edit.setPlaceholderText("例如：100")
        self.stock_edit.setFixedHeight(34)
        self.date_edit = QLineEdit()
        self.date_edit.setPlaceholderText("例如：2024-06-30")
        self.date_edit.setFixedHeight(34)

        layout.addRow("疫苗名称：", self.name_edit)
        layout.addRow("生产企业：", self.manufacturer_edit)
        layout.addRow("疫苗批号：", self.batch_edit)
        layout.addRow("可约数量：", self.stock_edit)
        layout.addRow("接种日期：", self.date_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("确认发布")
        buttons.button(QDialogButtonBox.Ok).setStyleSheet(
            "QPushButton{background-color: #409EFF; color: white; padding: 8px 20px;"
            "border: none; border-radius: 4px; font-size: 14px; font-weight: bold;}"
        )
        buttons.button(QDialogButtonBox.Cancel).setText("取消")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        stock_text = self.stock_edit.text().strip()
        try:
            stock = int(stock_text) if stock_text else 0
        except ValueError:
            stock = 0
        return {
            "vaccinename": self.name_edit.text().strip(),
            "manufacturer": self.manufacturer_edit.text().strip(),
            "batch_no": self.batch_edit.text().strip(),
            "stock": stock,
            "vaccination_date": self.date_edit.text().strip(),
        }


class StatusEditDialog(QDialog):
    """修改预约状态弹窗"""
    def __init__(self, current_status, parent=None):
        super().__init__(parent)
        self.setWindowTitle("修改预约状态")
        self.setWindowIcon(QIcon("images/app_icon.png"))
        self.resize(300, 150)
        self.setMinimumSize(280, 130)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        layout.addWidget(QLabel(f"当前状态：{current_status}"))
        layout.addWidget(QLabel("请选择新状态："))

        self.status_combo = QComboBox()
        self.status_combo.setFixedHeight(34)
        self.status_combo.addItems(["待确认", "已确认", "已完成", "已取消"])
        self.status_combo.setCurrentText(current_status)
        layout.addWidget(self.status_combo)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText("确认修改")
        btns.button(QDialogButtonBox.Ok).setStyleSheet(
            "QPushButton{background-color: #409EFF; color: white; padding: 6px 16px;"
            "border: none; border-radius: 4px; font-size: 13px; font-weight: bold;}"
        )
        btns.button(QDialogButtonBox.Cancel).setText("取消")
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_new_status(self):
        return self.status_combo.currentText()


class HospitalView(QMainWindow):
    def __init__(self, user_info, hospital_controller=None):
        super().__init__()
        self.user_info = user_info
        self.hospital_controller = hospital_controller
        self.hospital_name = user_info.get('hospital_name', '未选择医院')
        self.all_vaccines = []
        self.all_appointments = []

        self.init_ui()
        self.bind_events()

        if hospital_controller:
            self.load_vaccines()
            self.load_appointments()
        else:
            QMessageBox.warning(self, "错误", "控制器未初始化，无法加载数据")

    # ====================== UI 绘制 ======================

    def init_ui(self):
        self.setWindowTitle(f"医院管理端 - {self.user_info.get('username','')} @ {self.hospital_name}")
        self.setWindowIcon(QIcon("images/app_icon.png"))
        self.resize(1920, 1080)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # ========== 顶部信息栏 ==========
        info_group = QGroupBox("医生信息")
        info_group.setStyleSheet(
            "QGroupBox{font-size: 15px; font-weight: bold; color: #303133;"
            "border: 1px solid #dcdfe6; border-radius: 6px; margin-top: 12px; padding-top: 20px;}"
            "QGroupBox::title{subcontrol-origin: margin; left: 16px; padding: 0 8px;}"
        )
        info_layout = QGridLayout()
        info_layout.setSpacing(12)
        info_layout.addWidget(QLabel(f"医生姓名：{self.user_info.get('username', '')}"), 0, 0)
        info_layout.addWidget(QLabel(f"工作单位：{self.hospital_name}"), 0, 1)
        info_layout.addWidget(QLabel(f"角色：医生"), 0, 2)
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)

        # ========== 疫苗管理区域 ==========
        vaccine_group = QGroupBox("💉 疫苗管理")
        vaccine_group.setStyleSheet(
            "QGroupBox{font-size: 16px; font-weight: bold; color: #303133;"
            "border: 2px solid #409EFF; border-radius: 8px; margin-top: 14px; padding-top: 24px;}"
            "QGroupBox::title{subcontrol-origin: margin; left: 16px; padding: 0 8px; color: #409EFF;}"
        )
        vaccine_layout = QVBoxLayout()
        vaccine_layout.setSpacing(10)

        # 疫苗搜索 + 按钮行
        vaccine_toolbar = QHBoxLayout()
        self.vaccine_search_edit = QLineEdit()
        self.vaccine_search_edit.setPlaceholderText("搜索疫苗名称或批号...")
        self.vaccine_search_edit.setFixedHeight(38)
        self.vaccine_search_edit.setStyleSheet(
            "QLineEdit{border: 1px solid #dcdfe6; border-radius: 6px;"
            "padding: 4px 12px; font-size: 14px;}"
            "QLineEdit:focus{border-color: #409EFF;}"
        )

        self.publish_vaccine_btn = QPushButton("➕ 发布新疫苗")
        self.publish_vaccine_btn.setStyleSheet(
            "QPushButton{background-color: #67C23A; color: white; padding: 10px 22px;"
            "border: none; border-radius: 6px; font-size: 15px; font-weight: bold;}"
            "QPushButton:hover{background-color: #85ce61;}"
            "QPushButton:pressed{background-color: #5daf34;}"
        )

        self.refresh_vaccine_btn = QPushButton("🔄 刷新疫苗")
        self.refresh_vaccine_btn.setStyleSheet(
            "QPushButton{background-color: #909399; color: white; padding: 10px 22px;"
            "border: none; border-radius: 6px; font-size: 15px; font-weight: bold;}"
            "QPushButton:hover{background-color: #a6a9ad;}"
            "QPushButton:pressed{background-color: #82848a;}"
        )

        vaccine_toolbar.addWidget(self.vaccine_search_edit)
        vaccine_toolbar.addWidget(self.publish_vaccine_btn)
        vaccine_toolbar.addWidget(self.refresh_vaccine_btn)
        vaccine_layout.addLayout(vaccine_toolbar)

        # 疫苗表格
        self.vaccine_table = QTableWidget()
        self.vaccine_table.setColumnCount(6)
        self.vaccine_table.setHorizontalHeaderLabels([
            "疫苗名称", "生产企业", "批号", "库存", "接种日期", "状态"
        ])
        self.vaccine_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.vaccine_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.vaccine_table.setSelectionMode(QTableWidget.SingleSelection)
        self.vaccine_table.setAlternatingRowColors(True)
        self.vaccine_table.verticalHeader().setVisible(False)
        self.vaccine_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.vaccine_table.setStyleSheet("QTableWidget{font-size: 14px;}")
        vaccine_layout.addWidget(self.vaccine_table)

        vaccine_group.setLayout(vaccine_layout)
        main_layout.addWidget(vaccine_group)

        # ========== 预约管理区域 ==========
        appointment_group = QGroupBox("📋 预约管理")
        appointment_group.setStyleSheet(
            "QGroupBox{font-size: 16px; font-weight: bold; color: #303133;"
            "border: 2px solid #E6A23C; border-radius: 8px; margin-top: 14px; padding-top: 24px;}"
            "QGroupBox::title{subcontrol-origin: margin; left: 16px; padding: 0 8px; color: #E6A23C;}"
        )
        appointment_layout = QVBoxLayout()
        appointment_layout.setSpacing(10)

        # 预约搜索 + 按钮行1
        appoint_toolbar1 = QHBoxLayout()
        self.appoint_search_edit = QLineEdit()
        self.appoint_search_edit.setPlaceholderText("搜索姓名或疫苗名称...")
        self.appoint_search_edit.setFixedHeight(38)
        self.appoint_search_edit.setStyleSheet(
            "QLineEdit{border: 1px solid #dcdfe6; border-radius: 6px;"
            "padding: 4px 12px; font-size: 14px;}"
            "QLineEdit:focus{border-color: #E6A23C;}"
        )

        self.date_filter_edit = QLineEdit()
        self.date_filter_edit.setPlaceholderText("按日期过滤 (如 2024-06-30)...")
        self.date_filter_edit.setFixedHeight(38)
        self.date_filter_edit.setStyleSheet(
            "QLineEdit{border: 1px solid #dcdfe6; border-radius: 6px;"
            "padding: 4px 12px; font-size: 14px;}"
            "QLineEdit:focus{border-color: #E6A23C;}"
        )

        self.refresh_appoint_btn = QPushButton("🔄 刷新预约")
        self.refresh_appoint_btn.setStyleSheet(
            "QPushButton{background-color: #909399; color: white; padding: 10px 22px;"
            "border: none; border-radius: 6px; font-size: 15px; font-weight: bold;}"
            "QPushButton:hover{background-color: #a6a9ad;}"
            "QPushButton:pressed{background-color: #82848a;}"
        )

        appoint_toolbar1.addWidget(self.appoint_search_edit)
        appoint_toolbar1.addWidget(self.date_filter_edit)
        appoint_toolbar1.addWidget(self.refresh_appoint_btn)
        appointment_layout.addLayout(appoint_toolbar1)

        # 操作按钮行2
        appoint_toolbar2 = QHBoxLayout()

        self.confirm_btn = QPushButton("✅ 确认选中预约")
        self.confirm_btn.setStyleSheet(
            "QPushButton{background-color: #409EFF; color: white; padding: 10px 22px;"
            "border: none; border-radius: 6px; font-size: 15px; font-weight: bold;}"
            "QPushButton:hover{background-color: #66b1ff;}"
            "QPushButton:pressed{background-color: #3a8ee6;}"
        )

        self.complete_btn = QPushButton("🏁 完成接种登记")
        self.complete_btn.setStyleSheet(
            "QPushButton{background-color: #67C23A; color: white; padding: 10px 22px;"
            "border: none; border-radius: 6px; font-size: 15px; font-weight: bold;}"
            "QPushButton:hover{background-color: #85ce61;}"
            "QPushButton:pressed{background-color: #5daf34;}"
        )

        self.cancel_appoint_btn = QPushButton("❌ 取消选中预约")
        self.cancel_appoint_btn.setStyleSheet(
            "QPushButton{background-color: #F56C6C; color: white; padding: 10px 22px;"
            "border: none; border-radius: 6px; font-size: 15px; font-weight: bold;}"
            "QPushButton:hover{background-color: #f78989;}"
            "QPushButton:pressed{background-color: #e85b5b;}"
        )

        self.edit_status_btn = QPushButton("✏️ 修改预约状态")
        self.edit_status_btn.setStyleSheet(
            "QPushButton{background-color: #E6A23C; color: white; padding: 10px 22px;"
            "border: none; border-radius: 6px; font-size: 15px; font-weight: bold;}"
            "QPushButton:hover{background-color: #ebb563;}"
            "QPushButton:pressed{background-color: #cf9236;}"
        )

        appoint_toolbar2.addWidget(self.confirm_btn)
        appoint_toolbar2.addWidget(self.complete_btn)
        appoint_toolbar2.addWidget(self.cancel_appoint_btn)
        appoint_toolbar2.addWidget(self.edit_status_btn)
        appointment_layout.addLayout(appoint_toolbar2)

        # 预约表格
        self.appointment_table = QTableWidget()
        self.appointment_table.setColumnCount(6)
        self.appointment_table.setHorizontalHeaderLabels([
            "预约ID", "用户姓名", "疫苗名称", "接种日期", "状态", "批号"
        ])
        self.appointment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.appointment_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.appointment_table.setSelectionMode(QTableWidget.SingleSelection)
        self.appointment_table.setAlternatingRowColors(True)
        self.appointment_table.verticalHeader().setVisible(False)
        self.appointment_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.appointment_table.setStyleSheet("QTableWidget{font-size: 14px;}")
        # 隐藏批号列
        self.appointment_table.setColumnHidden(5, True)
        
        appointment_layout.addWidget(self.appointment_table)

        # 统计标签
        self.appoint_stats_label = QLabel("预约统计：加载中...")
        self.appoint_stats_label.setStyleSheet("color: #909399; font-size: 14px; padding: 6px;")
        appointment_layout.addWidget(self.appoint_stats_label)


        appointment_group.setLayout(appointment_layout)

        main_layout.addWidget(appointment_group)

        # 拉伸比例
        main_layout.setStretch(1, 1)
        main_layout.setStretch(2, 1)

        # ========== 底部状态栏 ==========
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #909399; padding: 5px; font-size: 13px;")
        main_layout.addWidget(self.status_label)

    # ====================== 事件绑定 ======================

    def bind_events(self):
        # 疫苗区
        self.publish_vaccine_btn.clicked.connect(self.publish_vaccine)
        self.refresh_vaccine_btn.clicked.connect(self.load_vaccines)
        self.vaccine_search_edit.textChanged.connect(self.filter_vaccines)

        # 预约区
        self.confirm_btn.clicked.connect(self.confirm_appointment)
        self.complete_btn.clicked.connect(self.complete_vaccination)
        self.cancel_appoint_btn.clicked.connect(self.cancel_appointment)
        self.edit_status_btn.clicked.connect(self.edit_appointment_status)
        self.refresh_appoint_btn.clicked.connect(self.load_appointments)
        self.appoint_search_edit.textChanged.connect(self.filter_appointments)
        self.date_filter_edit.textChanged.connect(self.filter_appointments)

    # ====================== 疫苗管理方法 ======================

    def load_vaccines(self):
        if not self.hospital_controller:
            return
        self.status_label.setText("正在加载疫苗列表...")
        try:
            result = self.hospital_controller.get_hospital_vaccines(self.hospital_name)
            if not result["success"]:
                QMessageBox.warning(self, "错误", result.get("msg", "加载失败"))
                self.status_label.setText("疫苗加载失败")
                return

            self.all_vaccines = result.get("data", [])
            self.fill_vaccine_table(self.all_vaccines)
            self.status_label.setText(f"疫苗加载成功，共 {len(self.all_vaccines)} 种")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载疫苗异常：{str(e)}")
            self.status_label.setText("疫苗加载异常")

    def fill_vaccine_table(self, vaccine_list):
        self.vaccine_table.setRowCount(len(vaccine_list))
        for row, v in enumerate(vaccine_list):
            name = v.get("vaccinename", "")
            manufacturer = v.get("manufacturer", "")
            batch_no = v.get("batch_no", "")
            stock = v.get("stock", 0)
            vdate = v.get("vaccination_date", "")

            self.vaccine_table.setItem(row, 0, QTableWidgetItem(name))
            self.vaccine_table.setItem(row, 1, QTableWidgetItem(manufacturer))
            self.vaccine_table.setItem(row, 2, QTableWidgetItem(batch_no))
            self.vaccine_table.setItem(row, 3, QTableWidgetItem(str(stock)))
            self.vaccine_table.setItem(row, 4, QTableWidgetItem(vdate))

            # 库存状态
            status_item = QTableWidgetItem()
            if stock <= 0:
                status_item.setText("已约满")
                status_item.setBackground(QColor(255, 220, 220))
            elif stock < 10:
                status_item.setText("库存紧张")
                status_item.setBackground(QColor(255, 245, 200))
            else:
                status_item.setText("可预约")
                status_item.setBackground(QColor(200, 245, 200))
            self.vaccine_table.setItem(row, 5, status_item)

    def filter_vaccines(self):
        keyword = self.vaccine_search_edit.text().strip().lower()
        if not keyword:
            self.fill_vaccine_table(self.all_vaccines)
            return
        filtered = [v for v in self.all_vaccines
                    if keyword in v.get("vaccinename", "").lower()
                    or keyword in v.get("batch_no", "").lower()]
        self.fill_vaccine_table(filtered)

    def publish_vaccine(self):
        if not self.hospital_controller:
            QMessageBox.warning(self, "错误", "控制器未初始化")
            return

        dialog = VaccinePublishDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["vaccinename"] or not data["batch_no"]:
                QMessageBox.warning(self, "提示", "疫苗名称和批号不能为空！")
                return

            result = self.hospital_controller.publish_vaccine(
                vaccinename=data["vaccinename"],
                manufacturer=data["manufacturer"],
                batch_no=data["batch_no"],
                stock=data["stock"],
                vaccination_date=data["vaccination_date"],
                hospital_name=self.hospital_name
            )
            if result["success"]:
                QMessageBox.information(self, "成功", "疫苗发布成功！")
                self.load_vaccines()
            else:
                QMessageBox.warning(self, "失败", result["msg"])

    # ====================== 预约管理方法 ======================

    def load_appointments(self):
        if not self.hospital_controller:
            return
        self.status_label.setText("正在加载预约列表...")
        try:
            result = self.hospital_controller.get_hospital_appointments(self.hospital_name)
            if not result["success"]:
                QMessageBox.warning(self, "错误", result.get("msg", "加载失败"))
                self.status_label.setText("预约加载失败")
                return

            self.all_appointments = result.get("data", [])
            self.fill_appointment_table(self.all_appointments)
            self._update_appoint_stats(self.all_appointments)
            self.status_label.setText(f"预约加载成功，共 {len(self.all_appointments)} 条")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载预约异常：{str(e)}")
            self.status_label.setText("预约加载异常")

    def fill_appointment_table(self, appointment_list):
        self.appointment_table.setRowCount(len(appointment_list))
        for row, ap in enumerate(appointment_list):
            self.appointment_table.setItem(row, 0, QTableWidgetItem(str(ap.get("appointments_id", ""))))
            self.appointment_table.setItem(row, 1, QTableWidgetItem(ap.get("user_name", "")))
            self.appointment_table.setItem(row, 2, QTableWidgetItem(ap.get("vaccine_name", "")))
            self.appointment_table.setItem(row, 3, QTableWidgetItem(ap.get("vaccination_date", "")))

            # 状态着色
            status = ap.get("status", "")
            status_item = QTableWidgetItem(status)
            if status == "待确认":
                status_item.setBackground(QColor(255, 245, 200))   # 护眼淡黄
            elif status == "已确认":
                status_item.setBackground(QColor(200, 225, 255))   # 护眼淡蓝
            elif status == "已完成":
                status_item.setBackground(QColor(200, 245, 200))   # 护眼淡绿
            elif status == "已取消":
                status_item.setBackground(QColor(255, 220, 220))   # 护眼淡红
            self.appointment_table.setItem(row, 4, status_item)

            # 隐藏批号
            self.appointment_table.setItem(row, 5, QTableWidgetItem(ap.get("batch_no", "")))

    def _update_appoint_stats(self, appointment_list):
        if not appointment_list:
            self.appoint_stats_label.setText("预约统计：暂无预约记录")
            return

        # 按日期分组统计
        date_counts = {}
        for ap in appointment_list:
            d = ap.get("vaccination_date", "未知日期")
            date_counts[d] = date_counts.get(d, 0) + 1

        total = len(appointment_list)
        stats_parts = [f"总计 {total} 条预约"]
        stats_parts.append(" | ".join([f"{d}: {c}人" for d, c in sorted(date_counts.items())]))
        self.appoint_stats_label.setText("  |  ".join(stats_parts))

    def filter_appointments(self):
        keyword = self.appoint_search_edit.text().strip().lower()
        date_keyword = self.date_filter_edit.text().strip().lower()

        filtered = self.all_appointments
        if keyword:
            filtered = [ap for ap in filtered
                        if keyword in ap.get("user_name", "").lower()
                        or keyword in ap.get("vaccine_name", "").lower()]
        if date_keyword:
            filtered = [ap for ap in filtered
                        if date_keyword in ap.get("vaccination_date", "").lower()]

        self.fill_appointment_table(filtered)
        self._update_appoint_stats(filtered)

    def _get_selected_appointment_id(self):
        row = self.appointment_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "提示", "请先在预约列表中选中一条记录！")
            return None
        return int(self.appointment_table.item(row, 0).text())

    def confirm_appointment(self):
        aid = self._get_selected_appointment_id()
        if aid is None:
            return
        reply = QMessageBox.question(self, "确认操作", f"确定要确认预约 #{aid} 吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        result = self.hospital_controller.confirm_appointment(aid)
        if result["success"]:
            QMessageBox.information(self, "成功", result["msg"])
            self.load_appointments()
        else:
            QMessageBox.warning(self, "失败", result["msg"])

    def complete_vaccination(self):
        aid = self._get_selected_appointment_id()
        if aid is None:
            return
        reply = QMessageBox.question(self, "确认操作", f"确定要完成预约 #{aid} 的接种登记吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        result = self.hospital_controller.complete_vaccination(aid)
        if result["success"]:
            QMessageBox.information(self, "成功", result["msg"])
            self.load_appointments()
        else:
            QMessageBox.warning(self, "失败", result["msg"])

    def cancel_appointment(self):
        aid = self._get_selected_appointment_id()
        if aid is None:
            return
        reply = QMessageBox.question(self, "确认操作", f"确定要取消预约 #{aid} 吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        result = self.hospital_controller.cancel_appointment(aid)
        if result["success"]:
            QMessageBox.information(self, "成功", result["msg"])
            self.load_appointments()
        else:
            QMessageBox.warning(self, "失败", result["msg"])

    def edit_appointment_status(self):
        """自由修改预约状态"""
        row = self.appointment_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "提示", "请先在预约列表中选中一条记录！")
            return

        aid = int(self.appointment_table.item(row, 0).text())
        current_status = self.appointment_table.item(row, 4).text()

        dlg = StatusEditDialog(current_status, self)
        if dlg.exec_() == QDialog.Accepted:
            new_status = dlg.get_new_status()
            if new_status == current_status:
                QMessageBox.information(self, "提示", "状态未发生变更")
                return

            result = self.hospital_controller.update_appointment_status(aid, new_status)
            if result["success"]:
                QMessageBox.information(self, "成功", result["msg"])
            else:
                QMessageBox.warning(self, "失败", result["msg"])
            self.load_appointments()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("images/app_icon.png"))
    test_hospital_info = {
        "id": 2, "username": "张医生", "role": "hospital",
        "hospital_name": "市中心医院", "users_id": "310000199001010001"
    }
    window = HospitalView(user_info=test_hospital_info)
    window.show()
    sys.exit(app.exec_())
