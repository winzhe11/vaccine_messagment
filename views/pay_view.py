from PyQt5.QtWidgets import QDialog, QApplication, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QCursor
import sys

class PayWindow(QDialog):

    def __init__(self, cost):
        super().__init__()
        self.cost = cost 
        self.total_seconds = 180 
        
        
        self.turn = 0  
        
        
        self.pay_configs = [
            {
                "window_title": "微信支付",
                "logo_path": "images\\weixin_icon.png",
                "title_text": "微信扫码支付",
                "qr_path": "images\\pay_weixin.png",
                "primary_color": "#09bb07",       
                "hover_color": "#08a606",
                "switch_text": "切换到 支付宝支付"
            },
            {
                "window_title": "支付宝支付",
                "logo_path": "images\\zhifubao_icon.png",  
                "title_text": "支付宝扫码支付",
                "qr_path": "images\\pay_zhifubao.png",    
                "primary_color": "#108ee9", 
                "hover_color": "#0e7bd4",      
                "switch_text": " 切换到 微信支付"
            }
        ]
        # -----------------------------------------------------------
        
        # 定时器初始化
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)
        
        self.initUI()
        # 初始刷新一次界面，让数据注入视图
        self.refresh_ui()

    def initUI(self):
        self.resize(500, 720) # 稍微加高，容纳最底部的切换文字

        self.setStyleSheet("background-color: #f5f5f5;")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 30)
        main_layout.setSpacing(15)

        # 顶方标题栏
        title_layout = QHBoxLayout()
        title_layout.setAlignment(Qt.AlignCenter)

        self.logo_label = QLabel(self) 
        self.logo_label.setStyleSheet("background-color: transparent; border: none;")

        self.title_text = QLabel(self) 
        self.title_text.setStyleSheet("color: #333333; background-color: transparent;")
        font_title = self.title_text.font()
        font_title.setPointSize(14)
        font_title.setBold(True)
        self.title_text.setFont(font_title)

        title_layout.addWidget(self.logo_label)
        title_layout.addSpacing(8)
        title_layout.addWidget(self.title_text)
        main_layout.addLayout(title_layout)
        
        # 卡牌
        card = QFrame(self)
        card.setObjectName("my_white_card")
        card.setStyleSheet("QFrame#my_white_card { background-color: #ffffff; }")
        card.setFrameShape(QFrame.NoFrame)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 40, 30, 40)
        card_layout.setSpacing(15)

        # 金额
        price_label = QLabel(f'¥ {self.cost}', card)
        price_label.setAlignment(Qt.AlignCenter)
        price_label.setStyleSheet("color: #1a1a1a; border: none; background-color: transparent;")
        font_price = price_label.font()
        font_price.setFamily("Segoe UI")
        font_price.setPointSize(36)
        font_price.setBold(True)
        font_price.setWeight(95)
        price_label.setFont(font_price)

        # 文字提示
        text_label = QLabel('请使用手机扫码进行支付', card) 
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet("color: #333333; border: none; background-color: transparent;")
        font = text_label.font()
        font.setPointSize(14)
        font.setBold(True)
        text_label.setFont(font)

        # 二维码图片
        self.img_label = QLabel(card) 
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setStyleSheet("border: none; background-color: transparent;")

        # 倒计时栏
        countdown_container = QHBoxLayout() 
        countdown_container.setAlignment(Qt.AlignCenter) 

        prefix_label = QLabel("距离二维码过期还剩", card)
        prefix_label.setStyleSheet("color: #666666; border: none; background: transparent;")
        prefix_label.setFont(font) 
        
        self.min_label = QLabel("03", card)
        self.min_label.setFixedSize(32, 32) 
        self.min_label.setAlignment(Qt.AlignCenter) 
        self.min_label.setStyleSheet("color: #722ed1; background-color: #f9f0ff; border: none; border-radius: 6px; font-weight: bold;")
        
        unit_min_label = QLabel("分", card)
        unit_min_label.setStyleSheet("color: #666666; border: none; background: transparent;")
        
        self.sec_label = QLabel("00", card)
        self.sec_label.setFixedSize(32, 32)
        self.sec_label.setAlignment(Qt.AlignCenter)
        self.sec_label.setStyleSheet("color: #722ed1; background-color: #f9f0ff; border: none; border-radius: 6px; font-weight: bold;")
        
        unit_sec_label = QLabel("秒", card)
        unit_sec_label.setStyleSheet("color: #666666; border: none; background: transparent;")

        countdown_container.addWidget(prefix_label)
        countdown_container.addSpacing(5)
        countdown_container.addWidget(self.min_label)
        countdown_container.addWidget(unit_min_label)
        countdown_container.addSpacing(2)
        countdown_container.addWidget(self.sec_label)
        countdown_container.addWidget(unit_sec_label)

        
        btn_layout = QHBoxLayout() 
        btn_layout.setSpacing(20)  

        fail_btn = QPushButton("支付失败", card)
        fail_btn.setStyleSheet("""
            QPushButton {
                color: #666666;
                background-color: #f5f5f5;
                border: 1px solid #d9d9d9;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #e8e8e8; }
        """)

        self.success_btn = QPushButton("支付成功", card) 
        self.success_btn.clicked.connect(self.accept) 

        btn_layout.addWidget(fail_btn)
        btn_layout.addWidget(self.success_btn)

        # 组装到卡片里
        card_layout.addWidget(price_label)
        card_layout.addWidget(text_label)
        card_layout.addWidget(self.img_label)
        card_layout.addLayout(countdown_container) 
        card_layout.addSpacing(10) 
        card_layout.addLayout(btn_layout) 
        card_layout.addStretch()
        
        main_layout.addWidget(card)
        
        
        self.switch_label = QLabel(self)
        self.switch_label.setAlignment(Qt.AlignCenter)

        self.switch_label.setStyleSheet("""
            QLabel {
                color: #555555;
                font-size: 13px;
                background: transparent;
            }
            QLabel:hover {
                color: #108ee9;
                text-decoration: underline; /* 鼠标悬停加下划线 */
            }
        """)
         
        
        
        self.switch_label.mousePressEvent = self.on_switch_clicked
        
        main_layout.addWidget(self.switch_label)
        # -------------------------------------------------------------------------
        
        self.setLayout(main_layout)

    
    def refresh_ui(self):
        cfg = self.pay_configs[self.turn]
        
       
        self.setWindowTitle(cfg["window_title"])
        self.title_text.setText(cfg["title_text"])
        
        
        lpixmap = QPixmap(cfg["logo_path"])
        self.logo_label.setPixmap(lpixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
        
        qpixmap = QPixmap(cfg["qr_path"])
        self.img_label.setPixmap(qpixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        
        self.switch_label.setText(cfg["switch_text"])
        
        
        self.success_btn.setStyleSheet(f"""
            QPushButton {{
                color: #ffffff;
                background-color: {cfg['primary_color']};
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {cfg['hover_color']};
            }}
        """)
        
        
        self.success_btn.setFixedHeight(38)

    
    def on_switch_clicked(self, event):
        if event.button() == Qt.LeftButton: 
            self.turn = 1 - self.turn   
            self.total_seconds = 180    
            self.refresh_ui()               

    
    def update_countdown(self):
        if self.total_seconds > 0:
            self.total_seconds -= 1 
            minutes = self.total_seconds // 60
            seconds = self.total_seconds % 60
            self.min_label.setText(f"{minutes:02d}")
            self.sec_label.setText(f"{seconds:02d}")
        else:
            self.timer.stop()
            self.min_label.setText("00")
            self.sec_label.setText("00")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pf = PayWindow(cost="9.73") 
    pf.show()
    sys.exit(app.exec_())