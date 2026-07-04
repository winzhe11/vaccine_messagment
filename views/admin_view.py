# ===================================================================
# 合并说明：
#   UI 布局  → 来源于 路径2: C:\Users\ASUS\Desktop\admin_view.py
#   核心逻辑 → 来源于 路径1: D:\疫苗预约与接种管理系统\views\admin_view.py
#   逻辑不变，变量名不变，两者结合使窗口按路径2的UI正常运行
# ===================================================================

# [来源：路径2] sys 用于命令行参数，ctypes 用于 Windows 任务栏图标
import sys
import ctypes

# [来源：路径2] PyQt5 控件导入（比路径1多了 QLineEdit, QDialog, QDialogButtonBox, QLabel, QComboBox）
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QMessageBox, QLineEdit, QDialog,
                               QDialogButtonBox, QLabel, QComboBox)
# [来源：路径2] QIcon 用于窗口图标（路径1无此导入）
from PyQt5.QtGui import QColor, QIcon


# [来源：路径2] EditRoleDialog 弹窗类 —— 路径1没有此功能
class EditRoleDialog(QDialog):
    """修改角色弹窗"""
    def __init__(self, old_role, parent=None):
        super().__init__(parent)
        self.setWindowTitle("修改用户角色")
        self.resize(300, 120)
        layout = QVBoxLayout()
        self.role_combo = QComboBox()
        # [修复] doctor→hospital，与 auth_service 角色体系保持一致
        self.role_combo.addItems(["admin", "hospital", "normal"])
        self.role_combo.setCurrentText(old_role)
        layout.addWidget(QLabel("请选择新角色："))
        layout.addWidget(self.role_combo)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        self.setLayout(layout)

    def get_new_role(self):
        return self.role_combo.currentText()


class ChangePasswordDialog(QDialog):
    """修改密码弹窗"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("修改用户密码")
        self.resize(320, 180)
        layout = QVBoxLayout()
        layout.setSpacing(10)

        layout.addWidget(QLabel("新密码："))
        self.new_pwd_edit = QLineEdit()
        self.new_pwd_edit.setEchoMode(QLineEdit.Password)
        self.new_pwd_edit.setPlaceholderText("请输入新密码")
        layout.addWidget(self.new_pwd_edit)

        layout.addWidget(QLabel("确认密码："))
        self.confirm_pwd_edit = QLineEdit()
        self.confirm_pwd_edit.setEchoMode(QLineEdit.Password)
        self.confirm_pwd_edit.setPlaceholderText("请再次输入新密码")
        layout.addWidget(self.confirm_pwd_edit)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        self.setLayout(layout)

    def get_new_password(self):
        return self.new_pwd_edit.text(), self.confirm_pwd_edit.text()


class AdminView(QMainWindow):
    # [来源：路径1] __init__ 核心结构：user_info → init_ui → bind_events → 条件加载
    # [来源：路径2] 新增 self.all_user_data = [] 用于搜索缓存
    def __init__(self, user_info, admin_controller=None):
        super().__init__()
        self.user_info = user_info
        self.admin_controller = admin_controller
        self.init_ui()
        self.bind_events()
        # [来源：路径1] 只有控制器存在时，才自动加载用户列表
        if self.admin_controller:
            self.load_users()
        # [来源：路径2] 缓存原始全部用户数据，用于搜索过滤（路径1无此变量）
        self.all_user_data = []

    # [来源：路径2] init_ui —— 搜索区 + 3按钮 + 3列表格 + 图标 + 1920x1080
    def init_ui(self):
        # [修复闪退] user_info的键是'username'而非'name'，用get防止KeyError闪退
        self.setWindowTitle(f"系统管理端 - 管理员 {self.user_info.get('username', '管理员')}")
        # 窗口标题栏图标（使用项目 images 目录下的 app_icon.png）
        self.setWindowIcon(QIcon("images/app_icon.png"))
        # [来源：路径2] 窗口尺寸 1920x1080（路径1为 900x600）
        self.resize(1920, 1080)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # ========== [来源：路径2] 搜索区域 ==========
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入姓名/身份证号搜索用户")
        self.search_btn = QPushButton("搜索")
        self.reset_search_btn = QPushButton("重置")
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.reset_search_btn)
        main_layout.addLayout(search_layout)

        # ========== 按钮区（比路径1多了"更改选中用户角色"按钮） ==========
        btn_layout = QHBoxLayout()
        self.delete_btn = QPushButton("删除选中用户")
        self.delete_btn.setStyleSheet(
            "QPushButton{background-color: #F56C6C; color: white; padding: 12px 28px;"
            "border: none; border-radius: 6px; font-size: 16px; font-weight: bold;}"
            "QPushButton:hover{background-color: #f78989;}"
            "QPushButton:pressed{background-color: #e85b5b;}"
        )
        self.edit_role_btn = QPushButton("更改选中用户角色")
        self.edit_role_btn.setStyleSheet(
            "QPushButton{background-color: #E6A23C; color: white; padding: 12px 28px;"
            "border: none; border-radius: 6px; font-size: 16px; font-weight: bold;}"
            "QPushButton:hover{background-color: #ebb563;}"
            "QPushButton:pressed{background-color: #cf9236;}"
        )
        self.edit_pwd_btn = QPushButton("修改选中用户密码")
        self.edit_pwd_btn.setStyleSheet(
            "QPushButton{background-color: #409EFF; color: white; padding: 12px 28px;"
            "border: none; border-radius: 6px; font-size: 16px; font-weight: bold;}"
            "QPushButton:hover{background-color: #66b1ff;}"
            "QPushButton:pressed{background-color: #3a8ee6;}"
        )
        self.refresh_btn = QPushButton("刷新用户列表")
        self.refresh_btn.setStyleSheet(
            "QPushButton{background-color: #67C23A; color: white; padding: 12px 28px;"
            "border: none; border-radius: 6px; font-size: 16px; font-weight: bold;}"
            "QPushButton:hover{background-color: #85ce61;}"
            "QPushButton:pressed{background-color: #5daf34;}"
        )
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.edit_role_btn)
        btn_layout.addWidget(self.edit_pwd_btn)
        btn_layout.addWidget(self.refresh_btn)
        main_layout.addLayout(btn_layout)

        # ========== [来源：路径2] 用户表格（3列，路径1为5列） ==========
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(3)
        # [来源：路径2] 列标题：身份证号 | 姓名 | 角色（路径1为 用户ID|用户名|姓名|角色|实名认证状态）
        self.user_table.setHorizontalHeaderLabels(["身份证号", "姓名", "角色"])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.user_table.setSelectionBehavior(QTableWidget.SelectRows)
        main_layout.addWidget(self.user_table)

    # [来源：路径2] bind_events —— 5个事件绑定（路径1只有删除和刷新2个）
    def bind_events(self):
        self.delete_btn.clicked.connect(self.delete_user)
        self.refresh_btn.clicked.connect(self.load_users)
        # [来源：路径2] 以下3个事件绑定路径1没有
        self.edit_role_btn.clicked.connect(self.edit_user_role)
        self.edit_pwd_btn.clicked.connect(self.edit_user_password)
        self.search_btn.clicked.connect(self.search_user)
        self.reset_search_btn.clicked.connect(self.reset_search)

    # [来源：路径1] load_users 核心逻辑 —— try/except 防闪退 + result["success"] 检查
    # [来源：路径2] 增加了 all_user_data 缓存和 fill_table 调用
    def load_users(self):
        # [来源：路径2] 控制器空值保护
        if not self.admin_controller:
            return
        # [来源：路径1] try/except 包裹渲染逻辑，防止数据异常导致闪退
        try:
            result = self.admin_controller.query_users()
            if not result["success"]:
                QMessageBox.warning(self, "错误", result["msg"])
                return

            user_list = result["data"]
            # [来源：路径2] 缓存全部用户数据供搜索使用（路径1直接遍历填充，不缓存）
            self.all_user_data = user_list
            # [来源：路径2] 调用独立填充方法
            self.fill_table(user_list)
        except Exception as e:
            # [来源：路径1] 捕获所有渲染异常，弹窗提示错误，防止闪退
            QMessageBox.critical(self, "加载异常", f"用户列表加载失败：{str(e)}")

    # [来源：路径2] fill_table —— 独立的表格填充方法（路径1将此逻辑直接写在 load_users 中）
    def fill_table(self, user_list):
        # [来源：路径1] setRowCount(0) 等价于 setRowCount(len(user_list))
        self.user_table.setRowCount(len(user_list))
        for row, user in enumerate(user_list):
            # [来源：路径2] 3列表格填充：身份证号 | 姓名 | 角色
            id_card = user.get("id_card", "未实名")
            self.user_table.setItem(row, 0, QTableWidgetItem(id_card))
            self.user_table.setItem(row, 1, QTableWidgetItem(user["name"]))
            role_item = QTableWidgetItem(user["role"])
            # 角色颜色区分（护眼柔色）：管理员=淡黄，医生(hospital)=淡蓝，普通用户(normal)=淡绿
            role = user.get("role", "")
            if role == "admin":
                role_item.setBackground(QColor(255, 245, 200))       # 护眼淡黄
            elif role == "hospital":
                role_item.setBackground(QColor(200, 225, 255))       # 护眼淡蓝
            elif role == "normal":
                role_item.setBackground(QColor(200, 245, 200))       # 护眼淡绿
            self.user_table.setItem(row, 2, role_item)
            # [来源：路径2] 在首列隐藏存储 user_id（通过 Qt.UserRole+1000），
            # 供删除和修改角色时读取。路径1通过 int(text()) 直接读首列数字，
            # 但路径2首列是身份证号文本，故采用此方式
            self.user_table.item(row, 0).setData(1000, user["id"])

    # [来源：路径2] 搜索用户 —— 按姓名/身份证号过滤（路径1无此功能）
    def search_user(self):
        keyword = self.search_edit.text().strip().lower()
        if not keyword:
            self.fill_table(self.all_user_data)
            return
        filter_list = []
        for u in self.all_user_data:
            name = u.get("name", "").lower()
            idcard = u.get("id_card", "").lower()
            if keyword in name or keyword in idcard:
                filter_list.append(u)
        self.fill_table(filter_list)

    # [来源：路径2] 重置搜索 —— 清空搜索框，恢复全部数据（路径1无此功能）
    def reset_search(self):
        self.search_edit.clear()
        self.fill_table(self.all_user_data)

    # [来源：路径2] 修改用户角色 —— 弹出 EditRoleDialog，调用 controller.update_user_role（路径1无此功能）
    def edit_user_role(self):
        selected_row = self.user_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "提示", "请先选中要修改的用户！")
            return
        # [来源：路径2] 从隐藏数据中读取 user_id
        user_id = self.user_table.item(selected_row, 0).data(1000)
        old_role = self.user_table.item(selected_row, 2).text()
        dlg = EditRoleDialog(old_role, self)
        if dlg.exec_():
            new_role = dlg.get_new_role()
            if new_role == old_role:
                QMessageBox.information(self, "提示", "角色未发生变更")
                return
            res = self.admin_controller.update_user_role(user_id, new_role)
            if res["success"]:
                QMessageBox.information(self, "成功", "用户角色修改完成")
                self.load_users()
            else:
                QMessageBox.warning(self, "失败", res["msg"])

    # [来源：路径2] 修改用户密码 —— 弹出 ChangePasswordDialog，调用 controller.update_user_password
    def edit_user_password(self):
        selected_row = self.user_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "提示", "请先选中要修改密码的用户！")
            return
        user_id = self.user_table.item(selected_row, 0).data(1000)
        dlg = ChangePasswordDialog(self)
        if dlg.exec_():
            new_pwd, confirm_pwd = dlg.get_new_password()
            if not new_pwd or not confirm_pwd:
                QMessageBox.warning(self, "提示", "密码不能为空！")
                return
            if new_pwd != confirm_pwd:
                QMessageBox.warning(self, "提示", "两次输入的密码不一致！")
                return
            res = self.admin_controller.update_user_password(user_id, new_pwd)
            if res["success"]:
                QMessageBox.information(self, "成功", "用户密码修改完成")
            else:
                QMessageBox.warning(self, "失败", res["msg"])

    # [来源：路径1] delete_user 核心逻辑 —— 二次确认 + 删除 + 刷新
    # [来源：路径2] 获取 user_id 的方式改为 data(1000)，因为路径2表格首列为身份证号文本而非用户ID数字
    def delete_user(self):
        selected_row = self.user_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "提示", "请先选中要删除的用户！")
            return

        # [来源：路径1] 二次确认弹窗
        reply = QMessageBox.question(self, "确认删除", "确定要删除该用户吗？",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        # [来源：路径2] 通过 data(1000) 获取 user_id
        # （路径1原为 int(self.user_table.item(selected_row, 0).text())，
        #   但路径2的UI首列是身份证号文本，不能直接转整数，故改用 data(1000)）
        user_id = self.user_table.item(selected_row, 0).data(1000)
        # [来源：路径1] 调用 controller.delete_user 删除
        result = self.admin_controller.delete_user(user_id)
        if result["success"]:
            QMessageBox.information(self, "成功", "用户删除成功")
            self.load_users()  # [来源：路径1] 删除后刷新列表
        else:
            QMessageBox.warning(self, "失败", result["msg"])


# [来源：路径2] 运行入口 —— 含 Windows 任务栏图标设置（路径1无 myappid 和 app.setWindowIcon）
if __name__ == "__main__":
    # [来源：路径2] 设置 Windows 任务栏 AppUserModelID，确保任务栏图标正确显示
    myappid = 'vaccine_system.admin.001'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # [来源：路径1] 创建 Qt 应用实例
    app = QApplication(sys.argv)
    # [来源：路径2] 设置应用级别窗口图标
    app.setWindowIcon(QIcon("images/app_icon.png"))

    # [来源：路径1] 准备测试用的管理员信息
    test_admin_info = {"id": 0, "name": "系统管理员", "role": "admin"}

    # [来源：路径1] 实例化管理员窗口（测试阶段不传 controller，不触发 load_users）
    window = AdminView(user_info=test_admin_info)

    # [来源：路径1] 显示窗口
    window.show()

    # [来源：路径1] 启动事件循环
    sys.exit(app.exec_())
