from database.db import DB


class UserDAO:

    def __init__(self):
        self.db = DB()
        self.db.connect()

    def add_user(self, user):
        sql = """
        INSERT INTO users(users_id, username, password, role)
        VALUES (?, ?, ?, ?)
        """
        try:
            self.db.cursor.execute(sql, (user.id_card, user.username, user.password, user.role))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def find_by_username(self, username):
        sql = "SELECT * FROM users WHERE username=?"
        self.db.cursor.execute(sql, (username,))
        return self.db.cursor.fetchone()

    def find_by_users_id(self, user_id):
        sql = "SELECT * FROM users WHERE users_id=?"
        self.db.cursor.execute(sql, (user_id,))
        return self.db.cursor.fetchone()

    def get_all_users(self):
        sql = "SELECT * FROM users"
        self.db.cursor.execute(sql)
        return self.db.cursor.fetchall()

    def delete_user(self, user_id):
        sql = "DELETE FROM users WHERE users_id=?"
        self.db.cursor.execute(sql, (user_id,))
        self.db.commit()

    # [修复闪退] 新增 update_user_role 方法 —— 修改用户角色
    def update_user_role(self, user_id, new_role):
        """更新指定用户的角色字段
        :param user_id: int 用户ID
        :param new_role: str 新角色（admin/hospital/normal）
        """
        sql = "UPDATE users SET role=? WHERE users_id=?"
        try:
            self.db.cursor.execute(sql, (new_role, user_id))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def update_password(self, users_id, new_password):
        """重置密码
        :param users_id: 身份证号
        :param new_password: 新密码
        """
        sql = "UPDATE users SET password=? WHERE users_id=?"
        try:
            self.db.cursor.execute(sql, (new_password, users_id))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e