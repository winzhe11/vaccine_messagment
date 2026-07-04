from services.face_service import face_library

class FaceController:

    def __init__(self, face_library):

        self.face_library = face_library

    def get_images_path(self, id_card):

        return self.face_library.get_images_path(id_card)