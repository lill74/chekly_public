from twilio.rest import Client
import redis
import random
import datetime
import json

# DANGER! This is insecure. See http://twil.io/secure
account_sid = ''
auth_token = ''

client = Client(account_sid, auth_token)
r = redis.Redis(host='localhost', port=6379, db=0)

def sendVerifyCode(to):

    if r.get(to):
        return {'status': 'verify cooltime', 'timeout': r.ttl(to)}

    code = random.SystemRandom().randint(100000, 999999)
    authBody = {
        'code': code
    }
    try:
        message = client.messages \
            .create(
            body='자가진단 인증번호 : ' + str(code),
            from_='+',
            to='+82'+str(to)
        )
    except Exception as e:
        return e

    r.set(to, json.dumps(authBody), datetime.timedelta(seconds=180))

    return 'sent'

def checkVerifyCode(to, code):
    try:
        jsonObject = json.loads(r.get(to))
    except:
        return False

    if str(jsonObject['code']) == code:
        return True
    return False
