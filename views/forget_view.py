import os
import sys
from face_recognize import FaceVerificationSystem

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QApplication,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor

_script_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_script_dir)
IMAGES = os.path.join(_project_root, "images")


class ForgetView(QMainWindow):
    """忘记密码窗口 — 人脸验证后重置密码"""

    def __init__(self, auth_controller=None, face_controller=None):
        super().__init__()
        self.auth_controller = auth_controller
        self.face_controller = face_controller
        self.face_verified = False
        self.drag_pos = None
        self.init_ui()
        self.bind_events()

    # ═══════════════════════════════════════════════════════════
    #  UI 绘制
    # ═══════════════════════════════════════════════════════════
    def init_ui(self):
        self.setWindowTitle("疫苗预约系统 - 忘记密码")
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(560, 680)

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
        title = QLabel("重置密码")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("微软雅黑", 20, QFont.Bold))
        title.setStyleSheet("color: #1D2129; background: transparent;")
        form.addWidget(title)

        subtitle = QLabel("请先通过人脸识别验证身份")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("微软雅黑", 10))
        subtitle.setStyleSheet("color: #86909C; background: transparent; margin-top: 2px;")
        form.addWidget(subtitle)

        form.addSpacing(22)

        # ── 姓名 ──
        self.name_edit = self._mk_field(form, "icon_user.png", "请输入真实姓名")
        form.addSpacing(16)

        # ── 身份证号 ──
        self.id_card_edit = self._mk_field(form, "id_card.png", "请输入身份证号")
        form.addSpacing(20)

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

        # ── 分隔线 ──
        sep = QLabel()
        sep.setFixedHeight(1)
        sep.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            "stop:0 transparent, stop:0.2 #E0E4EA, stop:0.8 #E0E4EA, stop:1 transparent);"
        )
        form.addWidget(sep)
        form.addSpacing(14)

        # ── 新密码 ──
        self.new_password_edit = self._mk_field(form, "icon_password.png", "请输入新密码", is_pwd=True)
        form.addSpacing(16)

        # ── 确认密码 ──
        self.confirm_password_edit = self._mk_field(form, "icon_password.png", "请再次输入新密码", is_pwd=True)
        form.addSpacing(20)

        # ── 重置按钮 ──
        self.reset_btn = QPushButton("重 置 密 码")
        self.reset_btn.setFixedHeight(48)
        self.reset_btn.setCursor(Qt.PointingHandCursor)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #E6A23C, stop:1 #EBB563);
                color: #ffffff;
                border: none;
                border-radius: 12px;
                font-size: 17px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #EBB563, stop:1 #F0C78E);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #D08C2E, stop:1 #E6A23C);
            }
        """)

        btn_shadow = QGraphicsDropShadowEffect()
        btn_shadow.setBlurRadius(18)
        btn_shadow.setOffset(0, 4)
        btn_shadow.setColor(QColor(230, 162, 60, 80))
        self.reset_btn.setGraphicsEffect(btn_shadow)

        form.addWidget(self.reset_btn)

        outer.addWidget(card)
        self.btn_close.raise_()

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
            QLineEdit:focus { border-bottom: 2px solid #E6A23C; }
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
        self.reset_btn.clicked.connect(self.reset_password)

    # ═══════════════════════════════════════════════════════════
    #  人脸识别
    # ═══════════════════════════════════════════════════════════
    def do_face_recognize(self):
        id_card = self.id_card_edit.text().strip()
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

    # ═══════════════════════════════════════════════════════════
    #  重置密码逻辑
    # ═══════════════════════════════════════════════════════════
    def reset_password(self):
        name = self.name_edit.text().strip()
        id_card = self.id_card_edit.text().strip()
        new_pwd = self.new_password_edit.text().strip()
        confirm_pwd = self.confirm_password_edit.text().strip()

        if not all([name, id_card, new_pwd, confirm_pwd]):
            QMessageBox.warning(self, "提示", "所有信息都不能为空！")
            return
        """
        if not self.face_verified:
            QMessageBox.warning(self, "提示", "请先通过人脸识别验证！")
            return
        """
        if new_pwd != confirm_pwd:
            QMessageBox.warning(self, "提示", "两次输入的密码不一致！")
            return

        try:
            result = self.auth_controller.reset_password(name, id_card, new_pwd)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"重置失败：{e}")
            return

        if result["success"]:
            QMessageBox.information(self, "成功", result["msg"])
            self.close()
        else:
            QMessageBox.warning(self, "重置失败", result["msg"])

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
    window = ForgetView()
    window.show()
    sys.exit(app.exec_())
