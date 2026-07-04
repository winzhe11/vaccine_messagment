from dao.user_dao import UserDAO

class AdminService:
    def __init__(self):
        self.user_dao = UserDAO()

    # ========== 查询所有用户 作者：XXX ==========
    def get_all_users(self):
        """查询系统全部用户完整信息，适配管理员列表页面展示
        return: dict 统一返回体
            success: bool 查询状态
            data: list[dict] 用户信息列表，匹配界面表头
        """
        try:
            rows = self.user_dao.get_all_users()
            user_list = []
            for row in rows:
                r = dict(row)
                # 全部使用数据库真实字段映射，适配界面5列表头
                # [修复闪退] 数据库无real_name/id_card列，用username做姓名，users_id做身份证号
                user_info = {
                    "id": r["users_id"],        # 用户ID
                    "username": r["username"],  # 用户名
                    "name": r["username"],      # [修复] 姓名取username（数据库无real_name列）
                    "role": r["role"],          # 角色
                    "id_card": str(r["users_id"]),  # [修复] 身份证号取users_id（数据库无id_card列）
                    "real_auth": "已实名"       # 默认已实名
                }
                user_list.append(user_info)

            return {
                "success": True,
                "data": user_list,
                "msg": "查询成功" if user_list else "暂无用户数据"
            }
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "msg": f"查询用户失败：{str(e)}"
            }

    # ========== 单条删除用户 作者：XXX ==========
    def delete_user(self, user_id):
        """根据用户ID删除单个用户
        :param user_id: int 用户唯一ID（users_id）
        return: dict 统一返回体
        """
        try:
            self.user_dao.delete_user(user_id)
            return {"success": True, "msg": "删除成功"}
        except Exception as e:
            return {"success": False, "msg": f"删除失败：{str(e)}"}

    # ========== 批量删除选中用户 适配界面批量删除按钮 作者：XXX ==========
    def batch_delete_user(self, id_list):
        """批量删除多个选中用户
        :param id_list: list[int] 待删除users_id数组
        return: dict
        """
        try:
            for uid in id_list:
                self.user_dao.delete_user(uid)
            return {"success": True, "msg": f"成功删除{len(id_list)}位用户"}
        except Exception as e:
            return {"success": False, "msg": f"批量删除失败：{str(e)}"}

    # ========== 修改用户角色 [修复闪退] 作者：XXX ==========
    def update_user_role(self, user_id, new_role):
        """修改指定用户的角色
        :param user_id: int 用户ID
        :param new_role: str 新角色
        return: dict 统一返回体
        """
        try:
            # 校验角色合法性（与 auth_service 保持一致：admin/hospital/normal）
            valid_roles = ("admin", "hospital", "normal")
            if new_role not in valid_roles:
                return {"success": False, "msg": f"无效角色：{new_role}，可选值：{valid_roles}"}
            self.user_dao.update_user_role(user_id, new_role)
            return {"success": True, "msg": "用户角色修改成功"}
        except Exception as e:
            return {"success": False, "msg": f"角色修改失败：{str(e)}"}

    # ========== 修改用户密码 作者：XXX ==========
    def update_user_password(self, user_id, new_password):
        """修改指定用户的密码
        :param user_id: str 用户ID（身份证号）
        :param new_password: str 新密码
        return: dict 统一返回体
        """
        try:
            if len(new_password) < 6:
                return {"success": False, "msg": "密码长度不能少于6位"}
            self.user_dao.update_password(user_id, new_password)
            return {"success": True, "msg": "用户密码修改成功"}
        except Exception as e:
            return {"success": False, "msg": f"密码修改失败：{str(e)}"}

    # ========== 用户数据统计 作者：XXX ==========
    def get_statistics(self):
        """统计用户总数、管理员数量、普通用户数量
        return: dict
        """
        try:
            rows = self.user_dao.get_all_users()
            user_list = [dict(r) for r in rows]
            total = len(user_list)
            admin_count = len([u for u in user_list if u["role"] == "admin"])
            user_count = len([u for u in user_list if u["role"] == "normal"])
            return {
                "success": True,
                "data": {
                    "total": total,
                    "admin": admin_count,
                    "user": user_count,
                },
                "msg": "统计完成"
            }
        except Exception as e:
            return {
                "success": False,
                "data": {"total":0, "admin":0, "user":0},
                "msg": f"统计失败：{str(e)}"
            }