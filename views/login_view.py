import sys
import ctypes
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox, QApplication,
                             QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPainter, QColor



class _BgWidget(QWidget):
    """背景图层：paintEvent 画缩放背景图"""
    def __init__(self, pixmap_path):
        super().__init__()
        self.bg_pixmap = QPixmap(pixmap_path)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.bg_pixmap)
        super().paintEvent(event)  # 确保子控件正常渲染


class LoginView(QMainWindow):
    """
    登录界面

    【接口 - 绝对不能改】
    - __init__(auth_controller, user_controller, hospital_controller, admin_controller)
    - jump_to_main 中 role 判 "normal"（非 "user"）
    - go_register 不关闭登录窗口
    - 各 View 构造时传入对应的 controller
    """

    def __init__(self, auth_controller=None, user_controller=None,
                 hospital_controller=None, admin_controller=None,face_controller=None):
        super().__init__()
        self.auth_controller = auth_controller
        self.user_controller = user_controller
        self.hospital_controller = hospital_controller
        self.admin_controller = admin_controller
        self.face_controller = face_controller
        self.face_verified = False
        self.drag_pos = None
        self.turn = 0
        self.init_ui()
        self.bind_events()

    # ====================== UI 绘制 ======================
    def init_ui(self):
        # --- 窗口基础设置 ---
        self.setWindowTitle("疫苗预约系统 - 登录")
        self.setWindowIcon(QIcon("images/app_icon.png"))
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1920, 1080)
        

        # --- 核心容器 ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)

        # --- 背景图层 ---
        self.bg_widget = _BgWidget("images/bg_login.png")
        central_layout.addWidget(self.bg_widget)

        # ====================== 关闭按钮（bg_widget 的直接子控件，绝对定位右上角） ======================
        self.btn_close = QPushButton(self.bg_widget)
        self.btn_close.setIcon(QIcon("images/icon_close.png"))
        self.btn_close.setIconSize(QSize(40, 40))
        self.btn_close.setFixedSize(50, 50)
        self.btn_close.move(1855, 15)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,60);
                border-radius: 10px;
            }
        """)
        self.btn_close.clicked.connect(self.close)

        # ====================== 左下角署名（bg_widget 的直接子控件，绝对定位） ======================
        self.footer_label = QLabel(self.bg_widget)
        self.footer_label.setText(
            "<span style='color:#1A5FC7; font-weight:bold;'>"
            "西石油宇宙超级无敌银河联合舰队出品</span>"
            "<span style='color:#8CA8CC; margin-left:12px; margin-right:12px;'>|</span>"
            "<span style='color:#3A5070; font-weight:500;'> 技术顾问:</span>"
            "<span style='color:#1A5FC7; font-weight:bold;'> winzhe11</span>"
            "<span style='color:#3A5070; font-weight:500;'> 联系方式:</span>"
            "<span style='color:#1A5FC7; font-weight:bold;'> 18009193989</span>"
        )
        self.footer_label.setFont(QFont("微软雅黑", 10))
        self.footer_label.setStyleSheet("""
            QLabel {
                background: transparent;
                padding: 6px 0px;
            }
        """)
        # 微光晕增强质感
        self.footer_shadow = QGraphicsDropShadowEffect()
        self.footer_shadow.setBlurRadius(8)
        self.footer_shadow.setColor(QColor(26, 95, 199, 50))
        self.footer_shadow.setOffset(0, 0)
        self.footer_label.setGraphicsEffect(self.footer_shadow)
        self.footer_label.adjustSize()
        # 定位到左下角：距左 30px，距底部 20px
        footer_x = 30
        footer_y = self.height() - self.footer_label.height() - 20
        self.footer_label.move(footer_x, footer_y)

        # --- 背景上的主布局 ---
        bg_layout = QHBoxLayout(self.bg_widget)
        bg_layout.setContentsMargins(0, 0, 0, 0)

        # 左：弹性空间（越大表单越靠右）
        bg_layout.addStretch(5)

        # ====================== 右侧面板 ======================
        right_panel = QWidget()
        right_panel.setFixedWidth(520)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 70, 0, 0)
        right_layout.setSpacing(0)

        # 上方弹性空间（越大表单越靠下）
        

        # ====================== 表单卡片 ======================
        self.form_widget = QWidget()
        self.form_widget.setObjectName("formCard")
        self.form_widget.setStyleSheet("""
            QWidget#formCard {
                border-image: url(images/form_bg.png);
                background-color: rgba(255, 255, 255, 220);
                border-radius: 16px;
            }
        """)

        form_layout = QVBoxLayout(self.form_widget)
        form_layout.setContentsMargins(50, 60, 50, 60)
        form_layout.setSpacing(28)

        # Logo 图标
        logo = QLabel() 
        logo.setAlignment(Qt.AlignCenter)
        logo_pix = QPixmap("images/app_icon.png")
        if not logo_pix.isNull():
            logo.setPixmap(logo_pix.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setStyleSheet("background: transparent; border: none;")
        form_layout.addWidget(logo)

        form_layout.addSpacing(6)

        # 标题
        title_label = QLabel("疫苗预约与接种管理系统")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("微软雅黑", 17, QFont.Bold))
        title_label.setStyleSheet("color: #1D2129; background: transparent;")
        title_label.setWordWrap(True)
        form_layout.addWidget(title_label)

        # 副标题
        subtitle = QLabel("安全 · 便捷 · 高效")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("微软雅黑", 9))
        subtitle.setStyleSheet("color: #86909C; background: transparent; margin-top: 2px;")
        form_layout.addWidget(subtitle)

        form_layout.addSpacing(18)

        # 姓名输入行
        self.name_edit = self._mk_input_row(form_layout, "images/icon_user.png", "请输入姓名")

        # 身份证号输入行
        self.idcard_edit = self._mk_input_row(form_layout, "images/id_card.png", "请输入身份证号")

        # 密码输入行
        self.password_edit = self._mk_input_row(form_layout, "images/icon_password.png", "请输入密码", is_pwd=True)

        form_layout.addSpacing(8)

        # ── 人脸识别 ──
        face_row = QHBoxLayout()
        face_row.setSpacing(10)

        self.face_status = QLabel("● 人脸识别未验证")
        self.face_status.setFont(QFont("微软雅黑", 10))
        self.face_status.setStyleSheet(
            "color: #F56C6C; background: transparent; font-weight: bold;"
        )
        face_row.addWidget(self.face_status)
        face_row.addStretch()

        self.face_btn = QPushButton("📷  开始验证")
        self.face_btn.setFixedSize(110, 32)
        self.face_btn.setCursor(Qt.PointingHandCursor)
        self.face_btn.setStyleSheet("""
            QPushButton {
                background: #ECF5FF;
                color: #409EFF;
                border: 1px solid #B3D8FF;
                border-radius: 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #D9ECFF;
                border-color: #409EFF;
            }
        """)
        face_row.addWidget(self.face_btn)
        form_layout.addLayout(face_row)

        form_layout.addSpacing(14)

        # 登录按钮（渐变 + 阴影）
        self.login_btn = QPushButton("登  录")
        self.login_btn.setFixedHeight(46)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #409EFF, stop:1 #66B1FF);
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-size: 17px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #66B1FF, stop:1 #79BBFF);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3A8EE6, stop:1 #409EFF);
            }
        """)
        btn_shadow = QGraphicsDropShadowEffect()
        btn_shadow.setBlurRadius(16)
        btn_shadow.setOffset(0, 3)
        btn_shadow.setColor(QColor(64, 158, 255, 60))
        self.login_btn.setGraphicsEffect(btn_shadow)
        form_layout.addWidget(self.login_btn)


        self.xiaozi_layout = QHBoxLayout()


        # 跳转注册
        self.register_btn = QPushButton("没有账号？去注册")
        self.register_btn.setCursor(Qt.PointingHandCursor)
        self.register_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                color: #409EFF;
                font-size: 13px;
            }
            QPushButton:hover {
                color: #66b1ff;
                text-decoration: underline;
            }
        """)

        self.forget_btn = QPushButton("忘记密码？去找回")
        self.forget_btn.setCursor(Qt.PointingHandCursor)
        self.forget_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                color: #409EFF;
                font-size: 13px;
            }
            QPushButton:hover {
                color: #66b1ff;
                text-decoration: underline;
            }
        """)

        self.xiaozi_layout.addWidget(self.register_btn)
        self.xiaozi_layout.addWidget(self.forget_btn)

        form_layout.addLayout(self.xiaozi_layout)

        right_layout.addStretch(6)

        right_layout.addWidget(self.form_widget)

        right_layout.addSpacing(16)

        # 分隔文字
        sep_row = QHBoxLayout()
        sep_row.setContentsMargins(0, 0, 0, 0)

        def _mk_sep():
            line = QLabel()
            line.setFixedHeight(1)
            line.setStyleSheet("background: #E0E4EA;")
            return line

        sep_row.addWidget(_mk_sep(), 1)
        sep_label = QLabel("  角色入口  ")
        sep_label.setStyleSheet("color: #86909C; font-size: 12px; background: transparent;")
        sep_row.addWidget(sep_label)
        sep_row.addWidget(_mk_sep(), 1)
        right_layout.addLayout(sep_row)

        right_layout.addSpacing(12)

        # 医生入口按钮
        self.doctor_entry_btn = QPushButton("🏥  医生入口")
        self.doctor_entry_btn.setFixedHeight(42)
        self.doctor_entry_btn.setCursor(Qt.PointingHandCursor)
        self.doctor_entry_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #67C23A;
                border: 1.5px solid #67C23A;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(103, 194, 58, 0.08);
                border-color: #85CE61;
            }
            QPushButton:pressed {
                background-color: rgba(103, 194, 58, 0.15);
            }
        """)
        right_layout.addWidget(self.doctor_entry_btn)

        right_layout.addSpacing(10)

        # 管理员入口按钮
        self.admin_entry_btn = QPushButton("⚙  管理员入口")
        self.admin_entry_btn.setFixedHeight(42)
        self.admin_entry_btn.setCursor(Qt.PointingHandCursor)
        self.admin_entry_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #E6A23C;
                border: 1.5px solid #E6A23C;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(230, 162, 60, 0.08);
                border-color: #EBB563;
            }
            QPushButton:pressed {
                background-color: rgba(230, 162, 60, 0.15);
            }
        """)
        right_layout.addWidget(self.admin_entry_btn)

        # 下方弹性空间
        right_layout.addStretch(3)

        bg_layout.addWidget(right_panel)

        # 右：弹性空间
        bg_layout.addStretch(1)

        # 确保关闭按钮在所有布局控件之上
        self.btn_close.raise_()

    # ====================== 业务逻辑 ======================

    def _mk_input_row(self, parent_layout, icon_path, placeholder, is_pwd=False):
        """构建带图标的输入行，返回 QLineEdit"""
        row = QHBoxLayout()
        row.setSpacing(12)

        icon = QLabel()
        pix = QPixmap(icon_path)
        if not pix.isNull():
            s = 30 if "password" in icon_path else 26
            icon.setPixmap(pix.scaled(s, s, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon.setFixedSize(30, 30)
        icon.setStyleSheet("background: transparent;")
        row.addWidget(icon)

        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(42)
        if is_pwd:
            edit.setEchoMode(QLineEdit.Password)
        edit.setFont(QFont("微软雅黑", 14))
        edit.setStyleSheet("""
            QLineEdit {
                border: none;
                border-bottom: 2px solid #DCDFE6;
                background: transparent;
                font-size: 15px;
                padding-left: 2px;
                padding-bottom: 4px;
                color: #303133;
            }
            QLineEdit:focus { border-bottom: 2px solid #409EFF; }
            QLineEdit::placeholder { color: #C0C4CC; }
        """)
        row.addWidget(edit)
        parent_layout.addLayout(row)
        return edit

    def bind_events(self):
        self.login_btn.clicked.connect(self.login)
        self.register_btn.clicked.connect(self.go_register)
        self.forget_btn.clicked.connect(self.go_forget)
        self.doctor_entry_btn.clicked.connect(self.hospital_turn)
        self.admin_entry_btn.clicked.connect(self.admin_turn)
        self.face_btn.clicked.connect(self.do_face_recognize)

    def login(self):
        username = self.name_edit.text().strip()
        users_id = self.idcard_edit.text().strip()
        password = self.password_edit.text().strip()

        if not username or not users_id or not password:
            QMessageBox.warning(self, "提示", "姓名、身份证号和密码不能为空！")
            return
        
        self.face_verified = True

        if self.face_verified is False:
            QMessageBox.warning(self, '人脸识别未通过', '人脸识别未通过，请重新进行人脸识别')
            return 
        
        result = self.auth_controller.login(username, users_id, password)

        if result["success"]:
            QMessageBox.information(self, "登录成功", f"欢迎您，{result['data']['username']}")
            user_role = result["data"]["role"]
            self.jump_to_main(user_role, result["data"])
            self.close()
        else:
            QMessageBox.warning(self, "登录失败", result["msg"])

    
    def do_face_recognize(self):
        import os
        from face_recognize import FaceVerificationSystem
        id_card = self.idcard_edit.text().strip()
        if not id_card:
            QMessageBox.warning(self, "提示", "请先输入身份证号再进行人脸识别！")
            return

        face_info = self.face_controller.get_images_path(id_card)
        if face_info == None:
            QMessageBox.warning(self, "警告", "无效的身份证号")
            return

        
        verification_face_path = os.path.join("face_images", face_info["images_path"])
        face_sys = FaceVerificationSystem(verification_face_path)
        face_sys.run()

        if face_sys.exit_reason == "SUCCESS":
            self.face_verified = True
            self.face_status.setText("● 人脸识别已验证")
            self.face_status.setStyleSheet(
                "color: #67C23A; background: transparent; font-weight: bold;"
            )
            self.face_btn.setText("✓  已验证")
            self.face_btn.setStyleSheet("""
                QPushButton {
                    background: #F0F9EB;
                    color: #67C23A;
                    border: 1px solid #C2E7B0;
                    border-radius: 16px;
                    font-size: 12px;
                    font-weight: bold;
                }
            """)
        else:
            self.face_verified = False
            self.face_status.setStyleSheet(
                "color: #F56C6C; background: transparent; font-weight: bold;"
            )
            self.face_btn.setText("✕ 重新验证")
            self.face_btn.setStyleSheet("""
                QPushButton {
                    background: #FEF0F0;
                    color: #F56C6C;
                    border: 1px solid #FBC4C4;
                    border-radius: 16px;
                    font-size: 12px;
                    font-weight: bold;
                }
            """)

    def go_register(self):
        from views.register_view import RegisterView
        self.register_window = RegisterView(self.auth_controller, self.face_controller)
        self.register_window.show()

    def go_forget(self):
        from views.forget_view import ForgetView
        self.forget_window = ForgetView(self.auth_controller, self.face_controller)
        self.forget_window.show()

    def jump_to_main(self, role, user_info):
        """根据角色跳转到对应主页 — 医生直接进入，不再弹窗选择单位"""
        if role == "admin" and self.turn == 2:
            from views.admin_view import AdminView
            self.main_window = AdminView(user_info, self.admin_controller)
        elif role == "hospital" and self.turn == 1:
            from views.hospital_view import HospitalView
            self.main_window = HospitalView(user_info, self.hospital_controller)
        else:
            from views.user_view import UserView
            self.main_window = UserView(user_info, self.user_controller)
        self.main_window.show()

    # ====================== 无边框窗口拖动 ======================
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def resizeEvent(self, event):
        """窗口大小变化时，重新定位左下角署名"""
        super().resizeEvent(event)
        if hasattr(self, 'footer_label'):
            self.footer_label.move(30, self.height() - self.footer_label.height() - 20)
    
    # [优化] 点击"医生入口"直接登录跳转，无需再点登录按钮
    def hospital_turn(self):
        self.turn = 1
        self.login()

    # [优化] 点击"管理员入口"直接登录跳转，无需再点登录按钮
    def admin_turn(self):
        self.turn = 2
        self.login()

# ====================== 程序入口 ======================
if __name__ == "__main__":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("vaccine.manage.system")
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("images/app_icon.png"))
    login_window = LoginView()
    login_window.show()
    sys.exit(app.exec_())
