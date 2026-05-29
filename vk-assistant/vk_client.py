import time
import vk_api
from vk_api.exceptions import ApiError
from typing import List, Dict, Optional


class VkAssistant:
    """Личный VK-ассистент для работы с группами, сообщениями и комментариями."""

    def __init__(self, token: str, api_version: str = "5.199"):
        self.token = token
        self.api_version = api_version
        self.vk_session = vk_api.VkApi(token=token, api_version=api_version)
        self.vk = self.vk_session.get_api()
        self.tools = vk_api.VkTools(self.vk_session)

    # ───────────────────────── ГРУППЫ ─────────────────────────

    def get_my_groups(self, extended: bool = True, count: int = 100) -> List[Dict]:
        """Возвращает список групп текущего пользователя."""
        try:
            response = self.vk.groups.get(
                extended=1 if extended else 0,
                count=count,
                fields="members_count,activity,description,site"
            )
            return response.get("items", [])
        except ApiError as e:
            print(f"[Ошибка groups.get] {e}")
            return []

    def get_group_info(self, group_id: str or int) -> Optional[Dict]:
        """Информация о группе по ID или короткому имени."""
        try:
            gid = str(group_id).strip()
            if gid.startswith("-"):
                gid = gid[1:]
            resp = self.vk.groups.getById(
                group_id=gid,
                fields="members_count,activity,status,description,contacts"
            )
            return resp[0] if resp else None
        except ApiError as e:
            print(f"[Ошибка groups.getById] {e}")
            return None

    def search_groups(self, query: str, count: int = 20) -> List[Dict]:
        """Поиск групп по запросу."""
        try:
            resp = self.vk.groups.search(q=query, count=count)
            return resp.get("items", [])
        except ApiError as e:
            print(f"[Ошибка groups.search] {e}")
            return []

    # ───────────────────────── СООБЩЕНИЯ ─────────────────────────

    def get_conversations(self, count: int = 20) -> List[Dict]:
        """Возвращает список диалогов (чатов)."""
        try:
            resp = self.vk.messages.getConversations(count=count)
            return resp.get("items", [])
        except ApiError as e:
            print(f"[Ошибка getConversations] {e}")
            return []

    def get_history(self, user_id: int, count: int = 20) -> List[Dict]:
        """История сообщений с конкретным пользователем."""
        try:
            resp = self.vk.messages.getHistory(user_id=user_id, count=count)
            return resp.get("items", [])
        except ApiError as e:
            print(f"[Ошибка getHistory] {e}")
            return []

    def send_message(self, user_id: int, message: str, attachment: str = "") -> Optional[int]:
        """Отправляет сообщение пользователю. Возвращает message_id."""
        try:
            params = {
                "user_id": user_id,
                "message": message,
                "random_id": int(time.time() * 1000)
            }
            if attachment:
                params["attachment"] = attachment
            resp = self.vk.messages.send(**params)
            print(f"[OK] Сообщение отправлено (id={resp})")
            return resp
        except ApiError as e:
            print(f"[Ошибка send] {e}")
            return None

    # ───────────────────────── КОММЕНТАРИИ ─────────────────────────

    def get_comments(self, owner_id: int, post_id: int, count: int = 20) -> List[Dict]:
        """Комментарии к посту. owner_id: если группа, то со знаком минуса."""
        try:
            resp = self.vk.wall.getComments(
                owner_id=owner_id,
                post_id=post_id,
                count=count,
                extended=1,
                fields="first_name,last_name"
            )
            return resp.get("items", [])
        except ApiError as e:
            print(f"[Ошибка getComments] {e}")
            return []

    def create_comment(self, owner_id: int, post_id: int, message: str) -> Optional[int]:
        """Оставляет комментарий под постом."""
        try:
            resp = self.vk.wall.createComment(
                owner_id=owner_id,
                post_id=post_id,
                message=message
            )
            print(f"[OK] Комментарий создан (id={resp})")
            return resp
        except ApiError as e:
            print(f"[Ошибка createComment] {e}")
            return None

    # ───────────────────────── СРАВНЕНИЯ ─────────────────────────

    def compare_groups(self, group_ids: List[str or int]) -> List[Dict]:
        """Сравнивает несколько групп по подписчикам и активности."""
        results = []
        for gid in group_ids:
            info = self.get_group_info(gid)
            if info:
                results.append({
                    "id": info.get("id"),
                    "name": info.get("name"),
                    "screen_name": info.get("screen_name"),
                    "members_count": info.get("members_count", 0),
                    "activity": info.get("activity", "—")
                })
            time.sleep(0.34)  # ~3 запроса/сек
        return results

    def compare_users(self, user_ids: List[int]) -> List[Dict]:
        """Сравнивает пользователей по базовым полям."""
        try:
            resp = self.vk.users.get(
                user_ids=",".join(map(str, user_ids)),
                fields="followers_count,city,education,counters"
            )
            return resp
        except ApiError as e:
            print(f"[Ошибка users.get] {e}")
            return []

    # ───────────────────────── ПОЛЬЗОВАТЕЛЬ ─────────────────────────

    def get_me(self) -> Optional[Dict]:
        """Информация о текущем пользователе."""
        try:
            return self.vk.users.get()[0]
        except ApiError as e:
            print(f"[Ошибка users.get] {e}")
            return None
