import datetime

from flask import Flask, abort, request, jsonify, render_template
import requests as req
import json
import region
import util
import re
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, set_access_cookies
)
from models import Users, Errors, Transactions, notification
import logging
from setting import app, db

logging.basicConfig(filename='flask_server.log',level=logging.DEBUG)

jwt = JWTManager(app)


#TODO 다른 API보다 로그인 처리단 API가 너무 구현이 빡세다 나중에 OAuth 같은거 하나 만들자..
#TODO Exception 처리 제일중요
#TODO Spotify RestAPI 벤치마크해서 json return 필수!
#TODO API용 toolKit이 있으면... parameter 처리같은거...

def retrieveData(url, data, objectName=None):
    """ try to retrieve and validate data """
    try:
        r = req.post(url, data=data)
        jsonObject = json.loads(r.text)

    # exception handling for requests and json
    except:
        abort(500)

    RESULT_CODE = jsonObject['resultSVO']['rtnRsltCode']

    if RESULT_CODE == 'SUCCESS' and objectName:
        return jsonObject['resultSVO'][objectName]
    elif RESULT_CODE == 'SUCCESS':
        return 'SUCCESS'
    else:
        return 'no data'


    abort(400)

@app.route('/debug-sentry')
def trigger_error():
    division_by_zero = 1 / 0    
    
@app.route('/')
def indexPage():
    return render_template('index.html')

@app.route('/ads.txt')
def adsPage():
    return render_template('ads.txt')

@app.route('/login')
def loginPage():
    return render_template('login.html')

@app.route('/register')
def registerPage():
    return render_template('register.html')

@app.route('/dashboard')
def dashboardPage():
    return render_template('dashboard.html')

@app.route('/privacy')
def privacyPage():
    return render_template('privacy.html')

@app.route('/api/getSchoolName')
def getSchoolName():
    """ retrieve (schulCode) from neis server """
    if not(request.args.get('schoolName') and request.args.get('region')):
        return jsonify(status=400, msg='missing parameters'), 400

    DATA = {
        'schulNm': request.args.get('schoolName')
    }

    url = f'https://eduro.{region.region[request.args.get("region")]}/stv_cvd_co00_003.do'

    r = req.get(url, data=DATA)

    pattern = re.compile('selectSchul?.*?;')
    regex = pattern.findall(r.text)

    pattern = re.compile("'(.*?)'")
    schools = pattern.findall(''.join(regex))

    return_arry = {}

    for school in range(int(len(schools) / 2)):
        return_arry[schools[school * 2 + 1]] = schools[school * 2]

    return json.dumps(return_arry)

@app.route('/api/getToken')
def getToken():
    """ retrieve (qstnCrtfcNoEncpt) from neis servet """
    if not(request.args.get('schoolCode') and request.args.get('name') and request.args.get('birthday')):
        return jsonify(status=400, msg='missing parameters'), 400

    POST_DATA = {
        'schulCode': request.args.get('schoolCode'),
        'pName': request.args.get('name'),
        'frnoRidno': request.args.get('birthday')
    }
    # schulCode: schoolCode, schulNm: name of school, pName: name of user, frnoRidno: birtday of user

    return retrieveData(url=f'https://eduro.{region.region[request.args.get("region")]}/stv_cvd_co00_012.do', data=POST_DATA, objectName='qstnCrtfcNoEncpt')

@app.route('/api/takeSurvey')
def takeSurvey():
    """ take survey with normal condition"""
    if not(request.args.get('token') and request.args.get("region")):
        return jsonify(status=400, msg='missing parameters'), 400

    POST_DATA = {
        'rtnRsltCode': 'SUCCESS',
        'qstnCrtfcNoEncpt': request.args.get('token'),
        'rspns01': '1',
        'rspns02': '1',
        'rspns07': '0',
        'rspsn08': '0',
        'rspsn09': '0'
    }

    return retrieveData(url=f'https://eduro.{region.region[request.args.get("region")]}/stv_cvd_co01_000.do', data=POST_DATA)

#!PAID AREA!
@app.route('/api/sendVerifyCode', methods=['POST'])
def sendVerifyCode():
    if not request.form['phone']:
        return jsonify(status=400, msg='missing parameters'), 400

    try:
        return jsonify(status=200, msg=util.sendVerifyCode(request.form['phone'])), 200
    except:
        return jsonify(status=400, msg='failed to send verification'), 400
#!PAID AREA!

@app.route('/api/login', methods=['POST'])
def login():
    if not(request.form['phone'] and request.form['code']):
        return jsonify(status=400, msg='missing parameters'), 400

    if util.checkVerifyCode(request.form['phone'], request.form['code']) == True:
        expires = datetime.timedelta(days=365)
        access_token = create_access_token(identity=request.form['phone'], expires_delta=expires)
        resp = jsonify({'login': True})
        set_access_cookies(resp, access_token), 200
        return resp
    return jsonify(status=400, msg='wrong code'), 400

@app.route('/api/save', methods=['POST'])
@jwt_required
def save():
    current_user = get_jwt_identity()

    if not(request.form['name'] and request.form['birthDay'] and request.form['region'] and request.form['schoolCode']):
        return jsonify(status=400, msg='missing parameters'), 400

    user = Users.query.filter_by(phone=current_user).first()
    
    if not user:
        user = Users(phone=current_user, name=request.form['name'], schoolCode=request.form['schoolCode'], birthDay=request.form['birthDay'], region=request.form['region'], time=request.form['time']  )
        db.session.add(user)
        db.session.commit()

        return jsonify(status=200, msg='created'), 200

    user = Users.query.filter_by(phone=current_user).first()

    user.name = request.form['name']
    user.schoolCode = request.form['schoolCode']
    user.birthDay = request.form['birthDay']
    user.region = request.form['region']
    user.time = request.form['time']

    db.session.commit()

    return jsonify(status=200, msg='updated'), 200

@app.route('/api/remove', methods=['POST'])
@jwt_required
def remove():
    current_user = get_jwt_identity()

    user = Users.query.filter_by(phone=current_user).first()

    if not user:
        return jsonify(status=400, msg='none data'), 200

    db.session.delete(user)
    db.session.commit()

    return jsonify(status=200, msg='updated'), 200

@app.route('/api/errorreport', methods=['POST'])
def errorReport():
    error = Errors(data=request.form['data'])
    db.session.add(error)
    db.session.commit()

    return jsonify(status=200, msg='updated'), 200

@app.route('/api/gettransactions', methods=['POST'])
@jwt_required
def getTransactions():
    current_user = get_jwt_identity()
    transactions = Transactions.query.filter_by(phone=current_user).all()

    return_arry = []

    for transaction in transactions:
        return_arry.append(transaction.data)

    return jsonify(status=200, msg=return_arry), 200

@app.route('/api/getuserinfo', methods=['POST'])
@jwt_required
def getUserinfo():
    current_user = get_jwt_identity()
    user = Users.query.filter_by(phone=current_user).first()

    if not user:
        return jsonify(status=400, msg='none data'), 200

    return_arry = {}

    return_arry['이름'] = user.name
    return_arry['학교코드'] = user.schoolCode
    return_arry['생일'] = user.birthDay
    return_arry['지역'] = user.region
    return_arry['자가진단 시간'] = user.time

    return json.dumps(return_arry, ensure_ascii = False )

@app.route('/api/getnotification', methods=['GET'])
def getNotifiation():
    notify = notification.query.first()

    if not notify:
        return jsonify(status=200, msg="항상 사용해주셔서 감사합니다!"), 200

    return jsonify(status=200, msg=notify.data), 200

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
