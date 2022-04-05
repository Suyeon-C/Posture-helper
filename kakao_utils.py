#!/usr/bin/env python 
# coding: utf-8

import json
import os
import datetime
import requests
from sqlparse import tokens

KAKAO_TOKEN_FILENAME = "kakao_message/kakao_token.json"

# 저장하는 함수
def save_tokens(filename, tokens):
    with open(filename, "w") as fp:
        json.dump(tokens, fp)

# 읽어오는 함수
def load_tokens(filename):
    with open(filename) as fp:
        tokens = json.load(fp)

    return tokens

# refresh_token으로 access_token 갱신하는 함수
def update_tokens(app_key, filename) :
    tokens = load_tokens(filename)

    url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type" : "refresh_token",
        "client_id" : app_key,
        "refresh_token" : tokens['refresh_token']
    }
    response = requests.post(url, data=data)

    # 요청에 실패했다면,
    if response.status_code != 200:
        print("error! because ", response.json())
        tokens = None
    else: # 성공했다면,
        print(response.json())
        # 기존 파일 백업
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = filename+"."+ now
        os.rename(filename, backup_filename)
        # 갱신된 토큰 저장
        tokens['access_token'] = response.json()['access_token']
        save_tokens(filename, tokens)
        
    return tokens

url = "https://kauth.kakao.com/oauth/token"

data = {
    "grant_type" : "authorization_code",
    "client_id" : "rest api 적기",
    "redirect_uri" : "https://localhost.com",
    "code" : "적기" # code=xxx, xxx 부분 적기 https://kauth.kakao.com/oauth/authorize?client_id=rest id 적기&response_type=code&redirect_uri=https://localhost.com
}

response = requests.post(url, data=data)

# 요청에 실패한다면,
if response.status_code != 200:
    print("error ! because" , response.json())
else:
    tokens = response.json()
    print(tokens)

    # 토큰 저장
    save_tokens(KAKAO_TOKEN_FILENAME, tokens)

# 메세지 전송 함수 
def send_message(filename, template):
    tokens = load_tokens(filename)

    headers = {
        "Authorization" : "Bearer " + tokens['access_token']
    }    
    #Json 형식 => 문자열
    payload = {
        "template_object" : json.dumps(template)
    }

    #카카오톡 보내기
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    res = requests.post(url, data=payload, headers=headers)

    return res