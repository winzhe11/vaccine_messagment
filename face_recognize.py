import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import time
import base64
import json
import requests
import os
import threading
from dotenv import load_dotenv  # 引入 dotenv

class FaceVerificationSystem:
    def __init__(self, verification_face_path, model_path="blaze_face_short_range.tflite"):

        load_dotenv()
        self.api_key = os.environ.get("API_KEY")
        self.secret_key = os.environ.get("SECRET_KEY")

        if not self.api_key or not self.secret_key:
            raise ValueError("错误：未在环境变量或 .env 文件中找到 API_KEY 或 SECRET_KEY！")

        self.verification_face_path = verification_face_path
        self.model_path = model_path

        self.PASS_SCORE = 80
        self.MAX_SAMPLE = 5
        self.PASS_COUNT = 3
        self.SAMPLE_INTERVAL = 1
        self.NO_FACE_TIMEOUT = 10

        self.sample_count = 0
        self.success_count = 0
        self.scores = []

        self.start_time = None
        self.last_sample_time = 0
        self.no_face_start_time = time.time()

        self.is_comparing = False
        self.should_exit = False
        self.exit_reason = ""

        # ===================== 初始化组件 =====================
        print("获取Token...")
        self.access_token = self._get_token()
        print("Token获取成功")

        self._init_mediapipe()
        self.cap = None

    def _img_to_base64(self, img):
        _, buffer = cv2.imencode(".jpg", img)
        return base64.b64encode(buffer).decode("utf-8")

    def _load_local_image(self, path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _get_token(self):
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        res = requests.post(url, params=params)
        return res.json()["access_token"]

    def _init_mediapipe(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"MediaPipe模型文件未找到: {self.model_path}")

        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.FaceDetectorOptions(base_options=base_options, min_detection_confidence=0.5)
        self.detector = vision.FaceDetector.create_from_options(options)

    # ===================== 异步线程任务 =====================
    def _async_face_compare(self, face_img):
        url = f"https://aip.baidubce.com/rest/2.0/face/v3/match?access_token={self.access_token}"
        body = [
            {"image": self._img_to_base64(face_img), "image_type": "BASE64"},
            {"image": self._load_local_image(self.verification_face_path), "image_type": "BASE64"} # 此处已同步更新
        ]
        headers = {"Content-Type": "application/json"}
        payload = json.dumps(body)

        try:
            response = requests.post(url, headers=headers, data=payload.encode("utf-8"), timeout=5)
            result = response.json()

            if result.get("error_code") == 0:
                score = result["result"]["score"]
            else:
                score = 0
        except Exception as e:
            score = 0

        self.sample_count += 1
        self.scores.append(score)
        print(f"第{self.sample_count}次比对结果：{score:.2f}")

        if score >= self.PASS_SCORE:
            self.success_count += 1
            print("本次成功")
        else:
            print("本次失败")

        if self.success_count >= self.PASS_COUNT:
            self.exit_reason = "SUCCESS"
            self.should_exit = True
        else:
            remain = self.MAX_SAMPLE - self.sample_count
            if self.success_count + remain < self.PASS_COUNT:
                self.exit_reason = "FAILED"
                self.should_exit = True

        self.is_comparing = False

    # ===================== 核心运行逻辑 =====================
    def run(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            print("摄像头打开失败")
            return

        print("系统启动，等待人脸...")

        while True:
            ret, frame = self.cap.read()
            if not ret or self.should_exit:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            detection_result = self.detector.detect(mp_image)

            status_text = "No Face"
            current_time = time.time()

            # -------------------- 检测到人脸 --------------------
            if detection_result.detections:
                status_text = "Face Detected"
                self.no_face_start_time = None

                if self.start_time is None:
                    self.start_time = current_time
                    self.last_sample_time = self.start_time - self.SAMPLE_INTERVAL
                    self.sample_count = 0
                    self.success_count = 0
                    self.scores.clear()
                    print("检测到人脸，开始识别...")

                detection = detection_result.detections[0]
                bbox = detection.bounding_box
                x = max(0, int(bbox.origin_x))
                y = max(0, int(bbox.origin_y))
                w = int(bbox.width)
                h = int(bbox.height)

                x2 = min(frame.shape[1], x + w)
                y2 = min(frame.shape[0], y + h)

                face_img = frame[y:y2, x:x2]
                cv2.rectangle(frame, (x, y), (x2, y2), (0, 255, 0), 2)

                if (
                    self.sample_count < self.MAX_SAMPLE and
                    current_time - self.last_sample_time >= self.SAMPLE_INTERVAL and
                    not self.is_comparing
                ):
                    self.last_sample_time = current_time
                    self.is_comparing = True
                    t = threading.Thread(target=self._async_face_compare, args=(face_img.copy(),))
                    t.daemon = True
                    t.start()

            # -------------------- 没检测到人脸 --------------------
            else:
                if not self.is_comparing:
                    self.start_time = None
                    self.sample_count = 0
                    self.success_count = 0
                    self.scores.clear()

                if self.no_face_start_time is None:
                    self.no_face_start_time = current_time

                elapsed_no_face = current_time - self.no_face_start_time

                if elapsed_no_face >= self.NO_FACE_TIMEOUT and not self.is_comparing:
                    self.exit_reason = "TIMEOUT"
                    break

            # ===================== UI显示 =====================
            cv2.putText(frame, status_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
            cv2.putText(frame, f"Sample : {self.sample_count}/{self.MAX_SAMPLE}", (20,75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
            cv2.putText(frame, f"Success : {self.success_count}/{self.PASS_COUNT}", (20,110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

            if status_text == "No Face" and self.no_face_start_time is not None:
                countdown = max(0, int(self.NO_FACE_TIMEOUT - (current_time - self.no_face_start_time)))
                cv2.putText(frame, f"Timeout in: {countdown}s", (20, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            elif self.is_comparing:
                cv2.putText(frame, "Comparing...", (20, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            cv2.imshow("Face System", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.exit_reason = "MANUAL"
                break

        self.release()
        self._print_result()

    # ===================== 资源释放与结果打印 =====================
    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        if self.detector:
            self.detector.close()
        cv2.destroyAllWindows()

    def _print_result(self):
        print("\n===============================")
        if self.exit_reason == "SUCCESS":
            print(f"认证成功！最终分数: {self.scores}")
        elif self.exit_reason == "FAILED":
            print(f"认证失败！最终分数: {self.scores}")
        elif self.exit_reason == "TIMEOUT":
            print(f"【系统提示】超过 {self.NO_FACE_TIMEOUT} 秒未检测到人脸，程序自动安全退出。")
        elif self.exit_reason == "MANUAL":
            print("用户手动按 'q' 键退出。")
        print("===============================")
