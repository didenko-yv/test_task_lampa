import time

from django.contrib.auth.models import User
from django.test import TestCase, Client

from tasks.models import Task


# Create your tests here.
class TaskApiTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

        cls.users = {
            1: {"username": "test", "password": "didenko1"},
            2: {"username": "test2", "password": "didenko2"},
        }
        for id_, user in cls.users.items():
            User.objects.create_user(**user, id=id_)
        tasks = [
            {
                "id_": 1,
                "name": "task1",
                "description": "task 1 desc",
                "status": Task.NEW,
                "authorizer_user_id": None,
            },
            {
                "id_": 2,
                "name": "task2",
                "description": "task 2 desc",
                "status": Task.NEW,
                "authorizer_user_id": None,
            },
            {
                "id_": 3,
                "name": "task3",
                "description": "task 3 desc",
                "status": Task.NEW,
                "authorizer_user_id": 2,
            },
            {
                "id_": 4,
                "name": "task4",
                "description": "task 4 desc",
                "status": Task.NEW,
                "authorizer_user_id": 2,
            },
            {
                "id_": 5,
                "name": "task5",
                "description": "task 5 desc",
                "status": Task.NEW,
                "authorizer_user_id": 1,
            },
        ]

        cls.tasks = []
        for task in tasks:
            task_ = Task(
                id=task["id_"],
                name=task["name"],
                description=task["description"],
                status=task["status"],
                user_id=task["authorizer_user_id"],
            )
            task_.save()
            cls.tasks.append(task_)
            time.sleep(0.1)

    def get_token(self, user_id):
        resp = self.client.post("/api/token/", data=self.users[user_id])
        return resp.data["token"]

    def test_list_unauthorized(self):
        """
        Тест на відповідність відображення лише задач створених неавторизованими користувачами
        для неавторизованого користувача.
        Відповідно відображатимемо лише 2 задачі з 5, оскільки інші 3 створені авторизованими користувачами
        """

        list_response = self.client.get("/api/tasks/")
        self.assertEqual(
            len(list_response.data),
            len(list(filter(lambda x: x.user is None, self.tasks))),
        )

    def test_list_authorized_user(self):
        """
        Тест на відповідність відображення задач створених неавторизованими користувачами та авторизованим користувачем.
        Для користувача з id=1 буде відображатись лише 3 задачі, 1 власна та ще 2 задачі неавторизованих користувачів.
        :return:
        """

        user_id = 1
        list_response = self.client.get(
            "/api/tasks/", headers={"Authorization": f"Token {self.get_token(user_id)}"}
        )

        self.assertEqual(
            len(list_response.data),
            len(
                list(
                    filter(
                        lambda x: (x.user_id == user_id) or x.user_id is None,
                        self.tasks,
                    )
                )
            ),
        )

    def test_filter_task_by_name(self):
        """
        Тест на відповідність фільтрації за назвою задачі
        Взято контекст неавторизованого користувача, тобто лише задачі створені неавторизованими користувачами.
        Спершу протестовано відповідність на 1 конкретному імені та встановлено що повернуто лише 1 запис.
        Друга частина тесту повертає всі назви задач створені неавторизованими користувачами,
        що відповідають загальному шаблону %task%
        """

        task_name = "task2"
        list_response = self.client.get("/api/tasks/", query_params={"name": task_name})

        self.assertEqual(len(list_response.data), 1)
        self.assertEqual(
            list_response.data[0]["description"],
            getattr(
                list(filter(lambda x: x.name == task_name, self.tasks))[0],
                "description",
            ),
        )

        common_unauthorized_task_name = "task"
        list_response = self.client.get(
            "/api/tasks/", query_params={"name": common_unauthorized_task_name}
        )

        self.assertEqual(
            len(list(filter(lambda x: x.user is None, self.tasks))),
            len(list_response.data),
        )

    def test_filter_task_by_status(self):
        """

        Тест на відповідність фільтрації задач за статусом, встановлено статус одній задачі
        та в результаті фільтрації отримано лише її
        """
        task_1 = self.client.get("/api/tasks/1").data
        task_1["status"] = Task.DONE
        self.client.put("/api/tasks/1", data=task_1, content_type="application/json")
        list_response = self.client.get(
            "/api/tasks/", query_params={"status": Task.DONE}
        )

        self.assertEqual(len(list_response.data), 1)

    def test_ordering_unauthorized_task(self):
        """
        Тест на відповідність сортування
        Перша частина тесту перевіряє сортування за замовчуванням 'desc' від останньої створеної задачі до найпершої
        Друга частина тесту перевіряє функціонал сортування обраний користувачем серед доступних 'asc'/'desc'
        """
        list_response = self.client.get("/api/tasks/")
        latest_created_task_from_response = list_response.data[0]
        latest_created_task_instance = max(
            filter(lambda x: x.user is None, self.tasks), key=lambda x: x.created
        )

        self.assertEqual(
            latest_created_task_instance.id, latest_created_task_from_response["id"]
        )

        list_response = self.client.get("/api/tasks/", query_params={"order": "asc"})
        oldest_created_task_from_response = list_response.data[0]
        oldest_created_task_instance = min(
            filter(lambda x: x.user is None, self.tasks), key=lambda x: x.created
        )
        self.assertEqual(
            oldest_created_task_instance.id, oldest_created_task_from_response["id"]
        )
