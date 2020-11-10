#!/user/bin/env python
# coding=utf-8
"""
@file: Tencent_API.py
@author: zwt
@time: 2020/11/10 10:25
@desc: 
"""
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.asr.v20190614 import asr_client, models
import json
import base64


class TrencentAsr(object):

    def __init__(self, data, type):
        self.SecretId = ""
        self.SecretKey = ""
        self.AppId = ""
        self.data = data
        self.type = type

    def sentence_asr(self):
        # 本地文件方式请求
        try:
            cred = credential.Credential(self.SecretId, self.SecretKey)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "asr.tencentcloudapi.com"
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            clientProfile.signMethod = "TC3-HMAC-SHA256"
            client = asr_client.AsrClient(cred, "ap-shanghai", clientProfile)
            # 读取文件以及 base64
            # 此处可以下载测试音频 https://asr-audio-1300466766.cos.ap-nanjing.myqcloud.com/test16k.wav
            with open(self.data, "rb") as f:
                content = base64.b64encode(f.read()).decode('utf-8')
            # 发送请求
            req = models.SentenceRecognitionRequest()
            if self.type:
                params = {"ProjectId": 0, "SubServiceType": 2, "SourceType": 1, "UsrAudioKey": "session-123"}
            else:
                params = {"ProjectId": 0, "SubServiceType": 2, "SourceType": 0, "UsrAudioKey": "session-123"}
                req.url = self.data

            req._deserialize(params)
            req.EngSerViceType = "16k_zh"
            req.VoiceFormat = "wav"
            if self.type:
                req.DataLen = len(content)
                req.Data = content

            resp = client.SentenceRecognition(req)
            res = resp.to_json_string()
            res = json.loads(res)['Result']
            res = res.replace('。', '').replace('，', '').replace(',', '')
            return res
        except TencentCloudSDKException as err:
            print('tencent返回错误:%s' % err)