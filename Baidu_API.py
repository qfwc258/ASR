#!/user/bin/env python
# coding=utf-8
"""
@file: Baidu_API.py
@author: zwt
@time: 2020/9/11 16:31
@desc: 
"""
import json
import base64
import time
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode
import traceback
import logging
logger = logging.getLogger()
timer = time.perf_counter


class BaiduSpeech(object):

    def __init__(self, AUDIO_FILE):
        self.API_KEY = ''
        self.SECRET_KEY = ''
        self.AUDIO_FILE = AUDIO_FILE  # 只支持 pcm/wav/amr 格式，极速版额外支持m4a 格式
        self.FORMAT = AUDIO_FILE[-3:]  # 文件后缀只支持 pcm/wav/amr 格式，极速版额外支持m4a 格式
        self.CUID = '123456PYTHON'
        self.RATE = 16000  # 采样率,固定值
        self.DEV_PID = 1537  # 1537 表示识别普通话，使用输入法模型。根据文档填写PID，选择语言及识别模型
        self.ASR_URL = 'http://vop.baidu.com/server_api'
        self.SCOPE = 'audio_voice_assistant_get'  # 有此scope表示有asr能力，没有请在网页里勾选，非常旧的应用可能没有
        self.TOKEN_URL = 'http://openapi.baidu.com/oauth/2.0/token'

    def get_token(self):
        params = {'grant_type': 'client_credentials',
                  'client_id': self.API_KEY,
                  'client_secret': self.SECRET_KEY}
        post_data = urlencode(params)
        post_data = post_data.encode('utf-8')
        req = Request(self.TOKEN_URL, post_data)
        try:
            f = urlopen(req)
            result_str = f.read()
        except URLError as err:
            traceback.print_exc()
            result_str = str(err)
        result_str = result_str.decode()
        result = json.loads(result_str)

        if 'access_token' in result.keys() and 'scope' in result.keys():
            logger.info(self.SCOPE)

            if self.SCOPE and not self.SCOPE in result['scope'].split(' '):  # SCOPE = False 忽略检查
                raise print('scope is not correct')
            logger.info(
                'SUCCESS WITH TOKEN: %s  EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
            print(result['access_token'])
            return result['access_token']

        else:

            raise print('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')

    def read_data(self):
        with open(self.AUDIO_FILE, 'rb') as speech_file:
            speech_data = speech_file.read()
            length = len(speech_data)
            if length == 0:
                raise print('file %s length read 0 bytes' % self.AUDIO_FILE)

            speech = base64.b64encode(speech_data)
            speech = str(speech, 'utf-8')
        return speech, length

    def get_result(self, speech, token, length):
        params = {'dev_pid': self.DEV_PID,
                  # "lm_id" : LM_ID,    #测试自训练平台开启此项
                  'format': self.FORMAT,
                  'rate': self.RATE,
                  'token': token,
                  'cuid': self.CUID,
                  'channel': 1,
                  'speech': speech,
                  'len': length
                  }
        post_data = json.dumps(params, sort_keys=False)
        req = Request(self.ASR_URL, post_data.encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        try:
            begin = timer()
            f = urlopen(req)
            result_str = f.read()
            print("Request time cost %f" % (timer() - begin))

        except URLError as err:
            traceback.print_exc()
            result_str = str(err)

        result_str = str(result_str, 'utf-8')
        res = json.loads(result_str)
        res = res['result']
        print(''.join(res))


if __name__ == '__main__':
    demo = BaiduSpeech('16k.wav')
    token = demo.get_token()
    start = time.time()
    speech, length = demo.read_data()
    demo.get_result(speech, token, length)
    print(time.time() - start)