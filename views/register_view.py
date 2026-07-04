import os
import sys
from face_recognize import FaceVerificationSystem

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QApplication,
    QComboBox, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor


_script_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_script_dir)
IMAGES = os.path.join(_project_root, "images")


class _AnimatedWidget(QWidget):
    """支持高度动画的容器 — 用于医生单位字段的平滑展开/收起"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._anim_height = 0
        self.setMaximumHeight(0)

    def get_anim_height(self):
        return self._anim_height

    def set_anim_height(self, h):
        self._anim_height = h
        self.setMaximumHeight(h)

    anim_height = pyqtProperty(int, get_anim_height, set_anim_height)


class RegisterView(QMainWindow):
    """注册窗口 — 高级版"""

    def __init__(self, auth_controller=None, face_controller=None):
        super().__init__()
        self.auth_controller = auth_controller
        self.face_controller = face_controller
        self.face_verified = False
        self.drag_pos = None
        self._hospital_expanded = False
        self.init_ui()
        self.bind_events()

    # ═══════════════════════════════════════════════════════════
    #  UI 绘制
    # ═══════════════════════════════════════════════════════════
    def init_ui(self):
        self.setWindowTitle("疫苗预约系统 - 注册")
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(560, 760)

        app_icon = os.path.join(IMAGES, "app_icon.png")
        if os.path.exists(app_icon):
            self.setWindowIcon(QIcon(app_icon))

        # ── 透明外层 ──
        central = QWidget()
        self.setCentralWidget(central)
        central.setStyleSheet("background: transparent;")
        outer = QVBoxLayout(central)
        outer.setContentsMargins(14, 14, 14, 14)

        # ═══════════ 卡片阴影 ═══════════
        card = QWidget()
        card.setObjectName("card")
        card.setStyleSheet("""
            QWidget#card {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8FAFB);
                border-radius: 20px;
                border: 1px solid #E8ECF1;
            }
        """)

        # 阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 50))
        card.setGraphicsEffect(shadow)

        form = QVBoxLayout(card)
        form.setContentsMargins(46, 24, 46, 28)
        form.setSpacing(0)

        # ── 关闭按钮 ──
        self._mk_close_btn(card)

        # ── Logo ──
        icon_lbl = QLabel()
        icon_lbl.setAlignment(Qt.AlignCenter)
        if os.path.exists(app_icon):
            pix = QPixmap(app_icon).scaled(
                64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            # 圆角遮罩
            rounded = QPixmap(pix.size())
            rounded.fill(Qt.transparent)
            from PyQt5.QtGui import QPainter, QPainterPath
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addRoundedRect(0, 0, pix.width(), pix.height(), 16, 16)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, pix)
            painter.end()
            icon_lbl.setPixmap(rounded)
        icon_lbl.setStyleSheet("background: transparent;")
        form.addWidget(icon_lbl)

        form.addSpacing(4)

        # ── 标题 ──
        title = QLabel("创建账号")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("微软雅黑", 20, QFont.Bold))
        title.setStyleSheet("color: #1D2129; background: transparent;")
        form.addWidget(title)

        subtitle = QLabel("加入疫苗预约与接种管理系统")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("微软雅黑", 10))
        subtitle.setStyleSheet("color: #86909C; background: transparent; margin-top: 2px;")
        form.addWidget(subtitle)

        form.addSpacing(22)

        # ── 姓名 ──
        self.name_edit = self._mk_field(form, "icon_user.png", "请输入真实姓名")
        form.addSpacing(16)

        # ── 密码 ──
        self.password_edit = self._mk_field(form, "icon_password.png", "请设置登录密码", is_pwd=True)
        form.addSpacing(16)

        # ── 身份证号 ──
        self.id_card_edit = self._mk_field(form, "id_card.png", "请输入身份证号")
        form.addSpacing(16)

        # ═══════════ 角色选择（高级下拉） ═══════════
        role_row = QHBoxLayout()
        role_row.setSpacing(12)

        role_icon = os.path.join(IMAGES, "icon_user.png")
        role_icon_lbl = QLabel()
        if os.path.exists(role_icon):
            role_icon_lbl.setPixmap(
                QPixmap(role_icon).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        role_icon_lbl.setFixedSize(28, 28)
        role_icon_lbl.setAlignment(Qt.AlignCenter)
        role_icon_lbl.setStyleSheet("background: transparent;")
        role_row.addWidget(role_icon_lbl)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["普通用户", "医生", "管理员"])
        self.role_combo.setCurrentIndex(0)
        self.role_combo.setFixedHeight(42)
        self.role_combo.setCursor(Qt.PointingHandCursor)
        self.role_combo.setFont(QFont("微软雅黑", 13))
        self.role_combo.setStyleSheet("""
            QComboBox {
                border: none;
                border-bottom: 2px solid #E0E4EA;
                background: transparent;
                font-size: 14px;
                padding-left: 2px;
                padding-bottom: 4px;
                color: #303133;
            }
            QComboBox:focus { border-bottom: 2px solid #409EFF; }
            QComboBox:hover { border-bottom: 2px solid #66B1FF; }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 28px;
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                border: 1px solid #E4E7ED;
                border-radius: 8px;
                selection-background-color: #ECF5FF;
                selection-color: #409EFF;
                color: #303133;
                font-size: 14px;
                padding: 6px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                height: 36px;
                padding-left: 14px;
                border-radius: 4px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #F5F7FA;
            }
        """)
        role_row.addWidget(self.role_combo)
        form.addLayout(role_row)

        # ── 角色提示标签 ──
        self.role_hint = QLabel("注册后将获得普通用户权限")
        self.role_hint.setFont(QFont("微软雅黑", 9))
        self.role_hint.setStyleSheet(
            "color: #86909C; background: transparent; padding-left: 40px; padding-top: 2px;"
        )
        form.addWidget(self.role_hint)

        form.addSpacing(6)

        # ═══════════ 医生单位字段（可折叠） ═══════════
        self.hospital_container = _AnimatedWidget()
        hospital_inner = QVBoxLayout(self.hospital_container)
        hospital_inner.setContentsMargins(0, 4, 0, 0)
        hospital_inner.setSpacing(0)

        # 分隔线
        sep = QLabel()
        sep.setFixedHeight(1)
        sep.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 transparent, stop:0.2 #E0E4EA, stop:0.8 #E0E4EA, stop:1 transparent);"
        )
        hospital_inner.addWidget(sep)
        hospital_inner.addSpacing(12)

        # 单位标签
        unit_label = QLabel("工作单位")
        unit_label.setFont(QFont("微软雅黑", 10, QFont.Bold))
        unit_label.setStyleSheet("color: #1D2129; background: transparent; padding-left: 40px;")
        hospital_inner.addWidget(unit_label)
        hospital_inner.addSpacing(6)

        # 单位输入框
        self.hospital_edit = self._mk_field(hospital_inner, "id_card.png", "请输入所属医院/单位名称")
        hospital_inner.addSpacing(4)

        form.addWidget(self.hospital_container)

        form.addSpacing(10)

        # ═══════════ 人脸识别 ═══════════
        face_row = QHBoxLayout()
        face_row.setSpacing(10)
        face_row.setContentsMargins(0, 0, 0, 0)

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
        form.addLayout(face_row)

        form.addSpacing(14)

        # ── 注册按钮 ──
        self.register_btn = QPushButton("注  册")
        self.register_btn.setFixedHeight(48)
        self.register_btn.setCursor(Qt.PointingHandCursor)
        self.register_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #409EFF, stop:1 #66B1FF);
                color: #ffffff;
                border: none;
                border-radius: 12px;
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

        # 注册按钮阴影
        btn_shadow = QGraphicsDropShadowEffect()
        btn_shadow.setBlurRadius(18)
        btn_shadow.setOffset(0, 4)
        btn_shadow.setColor(QColor(64, 158, 255, 80))
        self.register_btn.setGraphicsEffect(btn_shadow)

        form.addWidget(self.register_btn)

        outer.addWidget(card)
        self.btn_close.raise_()

        # 初始化动画
        self._hospital_anim = QPropertyAnimation(self.hospital_container, b"anim_height")
        self._hospital_anim.setDuration(300)
        self._hospital_anim.setEasingCurve(QEasingCurve.InOutCubic)

    # ═══════════════════════════════════════════════════════════
    #  辅助构建方法
    # ═══════════════════════════════════════════════════════════

    def _mk_close_btn(self, parent):
        close_icon = os.path.join(IMAGES, "icon_close.png")
        self.btn_close = QPushButton(parent)
        if os.path.exists(close_icon):
            self.btn_close.setIcon(QIcon(close_icon))
            self.btn_close.setIconSize(QSize(28, 28))
        else:
            self.btn_close.setText("✕")
        self.btn_close.setFixedSize(34, 34)
        self.btn_close.move(508, 10)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background: transparent; border: none;
                color: #86909C; font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(0,0,0,8); border-radius: 17px;
            }
        """)

    def _mk_field(self, parent_layout, icon_filename, placeholder, is_pwd=False):
        row = QHBoxLayout()
        row.setSpacing(12)

        icon_path = os.path.join(IMAGES, icon_filename)
        icon_lbl = QLabel()
        if os.path.exists(icon_path):
            s = 28 if ("password" in icon_filename or "id_card" in icon_filename) else 24
            icon_lbl.setPixmap(
                QPixmap(icon_path).scaled(
                    s, s, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )
        icon_lbl.setFixedSize(28, 28)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("background: transparent;")
        row.addWidget(icon_lbl)

        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(42)
        if is_pwd:
            edit.setEchoMode(QLineEdit.Password)
        edit.setFont(QFont("微软雅黑", 13))
        edit.setStyleSheet("""
            QLineEdit {
                border: none;
                border-bottom: 2px solid #E0E4EA;
                background: transparent;
                font-size: 14px;
                padding-left: 2px;
                padding-bottom: 4px;
                color: #1D2129;
            }
            QLineEdit:focus { border-bottom: 2px solid #409EFF; }
            QLineEdit:hover { border-bottom: 2px solid #C0C4CC; }
            QLineEdit::placeholder { color: #C0C4CC; }
        """)
        row.addWidget(edit)
        parent_layout.addLayout(row)
        return edit

    # ═══════════════════════════════════════════════════════════
    #  事件绑定
    # ═══════════════════════════════════════════════════════════
    def bind_events(self):
        self.btn_close.clicked.connect(self.close)
        self.face_btn.clicked.connect(self.do_face_recognize)
        self.register_btn.clicked.connect(self.register)
        self.role_combo.currentIndexChanged.connect(self._on_role_changed)

    # ═══════════════════════════════════════════════════════════
    #  角色切换 — 医生单位字段动画展开/收起
    # ═══════════════════════════════════════════════════════════
    def _on_role_changed(self, index):
        role_map = {0: "normal", 1: "hospital", 2: "admin"}
        role = role_map.get(index, "normal")

        hints = {
            0: "注册后将获得普通用户权限",
            1: "注册后将获得医生/医院用户权限",
            2: "注册后将获得管理员权限",
        }
        self.role_hint.setText(hints.get(index, ""))

        if role == "hospital":
            if not self._hospital_expanded:
                self._hospital_expanded = True
                self._hospital_anim.stop()
                self._hospital_anim.setStartValue(0)
                self._hospital_anim.setEndValue(100)
                self._hospital_anim.start()
        else:
            if self._hospital_expanded:
                self._hospital_expanded = False
                self._hospital_anim.stop()
                self._hospital_anim.setStartValue(self.hospital_container.height())
                self._hospital_anim.setEndValue(0)
                self._hospital_anim.start()

    # ═══════════════════════════════════════════════════════════
    #  人脸识别
    # ═══════════════════════════════════════════════════════════
    def do_face_recognize(self):
        id_card_text = self.id_card_edit.text().strip()
        face_path = self.face_controller.get_images_path(id_card_text)
        verification_face_path = os.path.join("face_images", face_path["images_path"])
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
            self.face_status.setStyleSheet("color: #F56C6C; background: transparent; font-weight: bold;")
            self.face_btn.setText("✕ 验证失败")
# 按钮红色样式
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

    # ═══════════════════════════════════════════════════════════
    #  注册逻辑
    # ═══════════════════════════════════════════════════════════
    def register(self):
        name = self.name_edit.text().strip()
        password = self.password_edit.text().strip()
        id_card = self.id_card_edit.text().strip()

        # 角色映射
        role_map = {0: "normal", 1: "hospital", 2: "admin"}
        role = role_map.get(self.role_combo.currentIndex(), "normal")

        hospital_name = self.hospital_edit.text().strip() if role == "hospital" else None

        if not all([name, password, id_card]):
            QMessageBox.warning(self, "提示", "所有信息都不能为空！")
            return

        if not self.face_verified:
            QMessageBox.warning(self, "提示", "请先通过人脸识别验证！")
            return
        if role == "hospital" and not hospital_name:
            QMessageBox.warning(self, "提示", "医生角色必须填写工作单位！")
            return

        if self.auth_controller is None:
            QMessageBox.warning(self, "提示", "系统未初始化，请从登录界面进入")
            return
        if  self.face_verified is None:
            QMessageBox.warning(self, "提示", "人脸识别未通过")
            return
        try:
            result = self.auth_controller.register(
                name, id_card, password, role, hospital_name
            )
        except Exception as e:
            QMessageBox.critical(self, "错误", f"注册失败：{e}")
            return

        if result["success"]:
            QMessageBox.information(self, "注册成功", result["msg"])
            self.close()
        else:
            QMessageBox.warning(self, "注册失败", result["msg"])

    # ═══════════════════════════════════════════════════════════
    #  无边框窗口拖动
    # ═══════════════════════════════════════════════════════════
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegisterView()
    window.show()
    sys.exit(app.exec_())
