import unittest
import requests as req
import secret

#TODO 함수 이름별 자동화

class TestAPI(unittest.TestCase):
    testkit = secret.TESTKIT

    def setUp(self):
        self.host = 'http://localhost:5000'

    def test_getSchoolCode(self):
        r = req.get(self.host + '/api/getSchoolCode', params=self.testkit['getSchoolCode']['request'])

        self.assertEqual(self.testkit['getSchoolCode']['response']['0'], r.text)

    def test_getToken(self):
        r = req.get(self.host + '/api/getToken', params=self.testkit['getToken']['request'])

        self.assertEqual(self.testkit['getToken']['response']['0'], r.text)

    def test_takeSurvey(self):
        r = req.get(self.host + '/api/takeSurvey', params=self.testkit['takeSurvey']['request'])

        self.assertEqual(self.testkit['takeSurvey']['response']['0'], r.text)

    #TEST 전용 툴킷을 만들어야할듯.
    def test_login(self):
        r = req.post(self.host + '/api/login', data=self.testkit['login']['request'])

        self.assertEqual(self.testkit['login']['response']['0'], r.text)

if __name__ == '__main__':
    unittest.main()



