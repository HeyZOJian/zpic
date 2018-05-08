from django.test import TestCase
from utils import date_utils
# Create your tests here.


class DateTests(TestCase):

    def test_date_util_get_this_week(self):
        """
        返回截止到今天的本月所有日期
        :return:
        """
        exp = ['20180423']
        act = date_utils.get_this_week()
        self.assertEqual(act, exp)
