import sys
import ctypes

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon


from database.db import DB

from dao.user_dao import UserDAO
from dao.vaccine_dao import VaccineDAO
from dao.appointment_dao import AppointmentDAO
from dao.face_library_dao import FaceLibraryDAO

from services.auth_service import Auth_service
from services.vaccine_service import Vaccine_service
from services.appointment_service import Appointment_service
from services.admin_service import AdminService
from services.face_service import face_library

from controllers.auth_controller import AuthController
from controllers.user_controller import UserController
from controllers.hospital_controller import HospitalController
from controllers.admin_controller import AdminController
from controllers.face_controller import FaceController

from views.login_view import LoginView

def main():
    db = DB()
    db.connect()

    user_dao = UserDAO()
    vaccine_dao = VaccineDAO()
    appointment_dao = AppointmentDAO()
    face_dao = FaceLibraryDAO()

    auth_service = Auth_service(user_dao)

    vaccine_service = Vaccine_service(vaccine_dao)

    appointment_service = Appointment_service(
        appointment_dao,
        vaccine_dao
    )

    hospital_controller = HospitalController(
        vaccine_service, appointment_service
    )

    admin_service = AdminService()

    face_service = face_library(face_dao)

    auth_controller = AuthController(
        auth_service
    )

    user_controller = UserController(
        appointment_service, vaccine_service
    )

    face_controller = FaceController(face_service)

    # admin_controller = AdminController()

    admin_controller = AdminController(admin_service)
    

    
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("vaccine.manage.system")

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("images/app_icon.png"))

    login_view = LoginView(
        auth_controller, user_controller, hospital_controller,admin_controller,
        face_controller
    )

    login_view.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
    