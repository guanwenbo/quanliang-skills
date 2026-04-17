#!/usr/bin/env python3
"""尝试直接调用七鲜API获取商品"""
import requests
import json

# 尝试几种可能的API端点
endpoints = [
    "https://7fresh.m.jd.com/api/activity/acDetail",
    "https://api.m.jd.com/api?functionId=acDetail",
    "https://7fresh.m.jd.com/api/sku/list",
]

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.38",
    "Referer": "https://7fresh.m.jd.com/",
    "Accept": "application/json",
}

params = {
    "activityId": "31574",
    "storeId": "1017261480",
    "tenantId": "1",
    "platformId": "1"
}

for url in endpoints[:1]:
    try:
        print(f"[*] 尝试: {url}")
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"状态码: {resp.status_code}")
        if resp.status_code == 200:
            try:
                data = resp.json()
                print(json.dumps(data, indent=2, ensure_ascii=False)[:3000])
            except:
                print(resp.text[:500])
    except Exception as e:
        print(f"错误: {e}")
    print()
