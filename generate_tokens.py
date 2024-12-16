import hmac
import json
import time
import requests
import hashlib
import utils as util
"""
This file consist of all functions to authenticate, generate tokens and refresh tokens
"""
def merchant_auth(partner_key):
    timestamp = int(time.time())
    #host = "https://partner.test-stable.shopeemobile.com"
    host = "https://partner.shopeemobile.com"
    path = "/api/v2/shop/auth_partner"
    partner_id = 2009434
    redirect_url = "https://www.google.com"

    sign = generate_sign(partner_key,partner_id,path,timestamp)
    ##generate api
    url = host + path + "?partner_id=%s&timestamp=%s&sign=%s&redirect=%s" % (partner_id, timestamp, sign, redirect_url)
    return url

def get_token_shop_level(code, partner_id, partner_key, shop_id):
    timestamp = int(time.time())
    host = "https://partner.shopeemobile.com"
    path = "/api/v2/auth/token/get"
    body = {"code": code,
            "shop_id": shop_id,
            "partner_id": partner_id}

    sign = generate_sign(partner_key, partner_id,path,timestamp)
    url = host + path + "?partner_id=%s&timestamp=%s&sign=%s" % (partner_id, timestamp, sign)
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=body, headers=headers)
    print("Response Status Code:", resp.status_code)
    print("Response Content:", resp.content)

    if resp.status_code == 200:
        ret = json.loads(resp.content)
        access_token = ret.get("access_token")
        new_refresh_token = ret.get("refresh_token")
        return access_token, new_refresh_token
    else:
        print("Error:", resp.status_code, resp.text)
        return None, None
    #return access_token, new_refresh_token

def get_token_account_level(code, partner_id, partner_key, main_account_id):
    timestamp = int(time.time())
    host = "https://partner.shopeemobile.com"

    path = "/api/v2/auth/token/get"
    body = {"code": code,
            "main_account_id": main_account_id,
            "partner_id": partner_id}

    sign = generate_sign(partner_key,partner_id,path,timestamp)

    url = host + path + "?partner_id=%s&timestamp=%s&sign=%s" % (partner_id, timestamp, sign)
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=body, headers=headers)
    print("Response Status Code:", resp.status_code)
    print("Response Content:", resp.content)

    if resp.status_code == 200:
        ret = json.loads(resp.content)
        access_token = ret.get("access_token")
        new_refresh_token = ret.get("refresh_token")
        return access_token, new_refresh_token
    else:
        print("Error:", resp.status_code, resp.text)
        return None, None

    #return access_token, new_refresh_token


def generate_sign(partner_key, partner_id,path,timestamp):
    tmp_base_string = "%s%s%s" % (partner_id, path, timestamp)
    base_string = tmp_base_string.encode()
    sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
    #print("Your sign is: " , sign)
    return sign


def refresh_account_token(merchant_id, partner_id, partner_key, refresh_token):
    timestamp = int(time.time())
    host = "https://partner.shopeemobile.com"
    path = "/api/v2/auth/access_token/get"
    body = {"merchant_id": merchant_id, "refresh_token": refresh_token, "partner_id": partner_id}
    tmp_base_string = "%s%s%s" % (partner_id, path, timestamp)
    base_string = tmp_base_string.encode()
    sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
    url = host + path + "?partner_id=%s&timestamp=%s&sign=%s" % (partner_id, timestamp, sign)

    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=body, headers=headers)
    #print("Response Status Code:", resp.status_code)
    #print("Response Content:", resp.content)

    if resp.status_code == 200:
        ret = json.loads(resp.content)
        access_token = ret.get("access_token")
        new_refresh_token = ret.get("refresh_token")
        return access_token, new_refresh_token
    else:
        print("Error:", resp.status_code, resp.text)
        return None, None
    #return access_token, new_refresh_token

def refresh_shop_tokens(shop_id, partner_id, partner_key, refresh_token):
    timestamp = int(time.time())
    host = "https://partner.shopeemobile.com"
    path = "/api/v2/auth/access_token/get"
    body = {"shop_id": shop_id, "refresh_token": refresh_token,"partner_id":partner_id}
    tmp_base_string = "%s%s%s" % (partner_id, path, timestamp)
    base_string = tmp_base_string.encode()
    sign = hmac.new(partner_key, base_string, hashlib.sha256).hexdigest()
    url = host + path + "?partner_id=%s&timestamp=%s&sign=%s" % (partner_id, timestamp, sign)

    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=body, headers=headers)
    #print("Response Status Code:", resp.status_code)
    #print("Response Content:", resp.content)

    if resp.status_code == 200:
        ret = json.loads(resp.content)
        access_token = ret.get("access_token")
        new_refresh_token = ret.get("refresh_token")
        print("New tokens acquired for:", shop_id)
        return access_token, new_refresh_token
    else:
        print("Error:", resp.status_code, resp.text)
        return None, None
    #return access_token, new_refresh_token

def check_account_token(ac):
    f = open("account_token.txt")
    refresh_token = f.read()
    f.close()
    access_token, new_refresh_token = refresh_account_token(ac.get_merchant_id(),
                                                                  ac.get_partner_id(),
                                                                  ac.get_partner_key(),
                                                                  refresh_token)
    if access_token is None:
        print("Refresh token ran out, authenticate a new one")
        print(merchant_auth(ac.get_partner_key()))
        ac.set_code(input("Whats the new code: "))

        access_token, new_refresh_token = get_token_account_level(ac.get_code(),
                                                                        ac.get_partner_id(),
                                                                        ac.get_partner_key(),
                                                                        ac.get_main_account_id())
        print("New tokens acquired")
        auth = True
    else:
        auth = False
        print("Valid refresh token found")
    f = open("account_token.txt", "w")
    f.write(new_refresh_token)
    f.close()
    return access_token, new_refresh_token, auth


def get_shop_tokens(ac, shop_ids, new_account_token, auth):
    shop_access_tokens = []
    shop_refresh_tokens = []
    f = open("shopTokens.txt")
    token_list = f.readlines()
    f.close()

    for shop,line in zip(shop_ids,token_list):
        if auth:
            token = new_account_token
        else:
            token  = line.strip()
        new_shop_access_token, new_shop_refresh_token = refresh_shop_tokens(shop,
                                                                            ac.get_partner_id(),
                                                                            ac.get_partner_key(),
                                                                            token)
        shop_access_tokens.append((shop, new_shop_access_token))
        shop_refresh_tokens.append(new_shop_refresh_token)

    util.update_shop_tokens_list(shop_refresh_tokens)
    return shop_access_tokens
