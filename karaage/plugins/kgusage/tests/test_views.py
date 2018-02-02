import datetime

from django.test import TestCase

from karaage.machines.models import Machine


class MachineTestCase(TestCase):
    fixtures = [
        'test_karaage.json',
        'test_kgusage.json',
    ]

    def setUp(self):
        today = datetime.datetime.now()
        # 10cpus
        mach1 = Machine.objects.get(pk=1)
        mach1.start_date = today - datetime.timedelta(days=80)
        mach1.save()
        # 40 cpus
        mach2 = Machine.objects.get(pk=2)
        mach2.start_date = today - datetime.timedelta(days=100)
        mach2.end_date = today - datetime.timedelta(days=20)
        mach2.save()
        # 8000 cpus
        mach3 = Machine.objects.get(pk=3)
        mach3.start_date = today - datetime.timedelta(days=30)
        mach3.save()

    def do_availablity_test(self, start, end, expected_time, expected_cpu):
        from karaage.plugins.kgusage.usage import get_machine_category_usage
        cache = get_machine_category_usage(start.date(), end.date())
        available_time = cache.available_time
        self.assertEqual(available_time, expected_time)

    def fixme_test_available_time(self):
        day = 60 * 60 * 24
        today = datetime.datetime.now()

        end = today - datetime.timedelta(days=20)
        start = today - datetime.timedelta(days=30)
        self.do_availablity_test(start, end, 8050 * day * 11, 8050)

        start = today - datetime.timedelta(days=99)
        end = today - datetime.timedelta(days=90)
        self.do_availablity_test(start, end, 40 * day * 10, 40)

        start = today - datetime.timedelta(days=85)
        end = today - datetime.timedelta(days=76)
        self.do_availablity_test(start, end, 45 * day * 10, 45)

        start = today - datetime.timedelta(days=35)
        end = today - datetime.timedelta(days=16)
        self.do_availablity_test(start, end, 6042 * day * 20, 6042)

        start = today - datetime.timedelta(days=20)
        end = today - datetime.timedelta(days=20)
        self.do_availablity_test(start, end, 8050 * day, 8050)
