import datetime

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from boomerang.models import Job
from boomerang.tests.tasks import SimpleBoomerangTask


class BoomerangAdminTestCase(TestCase):

    USER_USERNAME = 'jsmith'
    USER_PASSWORD = 'abc123'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=cls.USER_USERNAME,
            password=cls.USER_PASSWORD,
            is_staff=True,
            is_superuser=True
        )
        dt_1_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
        cls.job = Job.objects.create(
            name='Long-running Job',
            start_time=dt_1_hour_ago,
            status=Job.RUNNING,
            progress=100,
            goal=1000,
            executed_by=cls.user
        )

    def setUp(self):
        self.client.login(username=self.USER_USERNAME, password=self.USER_PASSWORD)

    def test_boomerang_job_changelist(self):
        # Verify that the Boomerang Job changelist renders
        response = self.client.get('/admin/boomerang/job/')
        self.assertEqual(response.status_code, 200)

    def test_user_executes_boomerang_job(self):
        # Kick off a Boomerang job within the scope of a request initated by an admin user
        request = RequestFactory().post('/execute')
        request.user = self.user
        SimpleBoomerangTask(range(5), request=request)

        # Verify that the job was marked as being executed by the user that made the request
        job = Job.objects.get(name='Simple')
        self.assertEqual(job.executed_by, self.user)
