from dao.face_library_dao import FaceLibraryDAO

class face_library:

    def __init__(self, faceLibrary_dao):

        self.faceLibrary_dao = faceLibrary_dao

    def get_images_path(self, id_cards):

        return self.faceLibrary_dao.get_path_by_idCard(id_cards)