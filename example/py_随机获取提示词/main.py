#!/usr/bin/env python3
import sys
import json
import time
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import random

# 导入文件操作工具函数
import json

def file_operation(filename, key=None, value=None):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    
    if value is not None:
        data[key] = value
        with open(filename, 'w') as f:
            json.dump(data, f,indent=2, ensure_ascii=False)
    
    return data.get(key) if key else data
def translate_text(text):
    #接入翻译接口即可
    return text
if __name__ == "__main__":

    
    天气字典 = {
        "晴天": "Sunny",
        "阴天": "Cloudy",
        "雨天": "Rainy",
        "雪天": "Snowy",
        "雷阵雨": "Thunderstorm",
        "多云": "Partly Cloudy",
        "大风": "Windy",
        "雾霾": "Foggy",
        "暴风雨": "Stormy",
        "阵雨": "Showers",
        "小雨": "Light Rain",
        "大雨": "Heavy Rain",
        "暴雪": "Blizzard",
        "寒冷": "Cold",
        "温暖": "Warm",
        "湿润": "Humid",
        "干燥": "Dry",
        "酷热": "Hot",
        "寒潮": "Cold Wave",
        "霜冻": "Frost",
        "霾": "Smog"
    }
    时间字典 = {
    "早": "Morning",
    "中": "Noon",
    "晚": "Evening"
    }


    职业字典 = {
        "医生": "Doctor",
        "教师": "Teacher",
        "工程师": "Engineer",
        "程序员": "Programmer",
        "律师": "Lawyer",
        "护士": "Nurse",
        "警察": "Police Officer",
        "消防员": "Firefighter",
        "科学家": "Scientist",
        "艺术家": "Artist",
        "作家": "Writer",
        "设计师": "Designer",
        "演员": "Actor/Actress",
        "歌手": "Singer",
        "厨师": "Chef",
        "司机": "Driver",
        "建筑师": "Architect",
        "记者": "Journalist",
        "会计": "Accountant",
        "农民": "Farmer",
        "商人": "Businessman/Businesswoman",
        "运动员": "Athlete",
        "摄影师": "Photographer",
        "翻译": "Translator",
        "心理学家": "Psychologist",
        "程序经理": "Project Manager",
        "市场营销经理": "Marketing Manager",
        "销售员": "Salesperson",
        "行政助理": "Administrative Assistant",
        "财务顾问": "Financial Advisor",
        "珠宝设计师": "Jewelry Designer",
        "社工": "Social Worker"
    }
    

    职业随机 = random.choice(list(职业字典.keys()))
    天气随机 = random.choice(list(天气字典.keys()))
    时间随机 = random.choice(list(时间字典.keys()))

    header=""

    allprompt = header+"""

    work,test,mykey








    """.replace("，","").replace(" ","").replace("\n","").strip()



    outallprompt = translate_text(allprompt)
    outallprompt=outallprompt.replace(": ",":").replace(", ",",")


    随机整合=""
    随机整合原始=""

    if 天气随机!="":
        随机整合=随机整合+","+天气字典[天气随机]
        随机整合原始=随机整合原始+",天气:"+天气随机

    if 时间随机!="":
        随机整合=随机整合+","+时间字典[时间随机]
        随机整合原始=随机整合原始+",时间:"+时间随机



    if 随机整合!="":
        outallprompt=outallprompt.replace("mykey",随机整合)

    file_operation('data.json', 'outallprompt', outallprompt)

    file_operation('data.json', '随机整合原始', 随机整合原始)
    result = {
        "allprompt": ""+outallprompt+"",
        "allneoprompt":"3d render,smooth,plastic,blurry,grainy,low-resolution,anime,deep-fried,oversaturated,"
        }
    #3d render,smooth,plastic,blurry,grainy,low-resolution,anime,deep-fried,oversaturated,
    print(json.dumps(result, ensure_ascii=False))
