import json
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import requests as req
from models import Transactions, Users
import region
import time

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost/selfcheck'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
logging.basicConfig(filename='survey_automation.log',level=logging.DEBUG)

db = SQLAlchemy(app)
db.init_app(app)

def retrieveData(url, data, objectName=None):
    """ try to retrieve and validate data """
    try:
        r = req.post(url, data=data)
        jsonObject = json.loads(r.text)

    # exception handling for requests and json
    except Exception as e:
        return e

    RESULT_CODE = jsonObject['resultSVO']['rtnRsltCode']

    if RESULT_CODE == 'SUCCESS' and objectName:
        return jsonObject['resultSVO'][objectName]
    if RESULT_CODE == 'SUCCESS':
        return 'SUCCESS'

now = time.localtime(time.time())

users = Users.query.filter_by(time=now.tm_hour).all()

if not users:
    print("there is no users in this time")
    exit(0)

count_failed_user = 0

for user in users:
    try:
        POST_DATA = {
            'schulCode': user.schoolCode,
            'pName': user.name,
            'frnoRidno': user.birthDay
        }
        # schulCode: schoolCode, schulNm: name of school, pName: name of user, frnoRidno: birtday of user

        token = retrieveData(url=f'https://eduro.{region.region[user.region]}/stv_cvd_co00_012.do',
                             data=POST_DATA, objectName='qstnCrtfcNoEncpt')

        POST_DATA = {
            'rtnRsltCode': 'SUCCESS',
            'qstnCrtfcNoEncpt': token,
            'rspns01': '1',
            'rspns02': '1',
            'rspns07': '0',
            'rspsn08': '0',
            'rspsn09': '0'
        }

        status = retrieveData(url=f'https://eduro.{region.region[user.region]}/stv_cvd_co01_000.do', data=POST_DATA)

        if status == 'SUCCESS':
            transactions = Transactions(phone=user.phone, data=f"[{time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))}] 자가진단 수행을 성공했습니다.")
            db.session.add(transactions)
            db.session.commit()
        else:
            transactions = Transactions(phone=user.phone, data=f"[{time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))}] 자가진단 수행을 실패했습니다. 정보를 다시 확인하고 수정해주세요.")
            db.session.add(transactions)
            db.session.commit()
            logging.error(user.phone + ' cant take survey')
            count_failed_user += 1

    except Exception as e:
        transactions = Transactions(phone=user.phone, data=f"[{time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))}] 자가진단 수행을 실패했습니다. 정보를 다시 확인하고 수정해주세요.")
        db.session.add(transactions)
        db.session.commit()
        logging.error(user.phone + ' cant take survey')
        count_failed_user += 1
        logging.error('ERROR '+ str(e))
        
count_users = len(users)

print(f"{count_users - count_failed_user} / {count_users}")
print(f"Error rate : {count_failed_user  / count_users * 100}")
