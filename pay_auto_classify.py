
# -*- coding: utf-8 -*-
import pandas as pd 
import os
import requests
import json
import openai

rules = {'索迪斯': "午餐", '赛百味': "晚餐", '沃尔玛': "食材",  '滴滴出行': "的士", '医院': "药品医疗", '山姆': "食材"}
detail_rules = {'猫罐头': "宠物", '电影票': "电影", '咖啡豆': "咖啡", '鞋': "鞋子鞋垫", 
                '裤': "裤子内外", '牛奶':  "牛奶乳饮", '奥体中心': "运动健身", '纯净水': '水'}
zfb_account = '交通银行'
wx_account = '微信零钱'
default_expense = '伙食'
expense_types = ["伙食", "饮料", "零食", "食材", "交通出行", "生活缴费", "衣着打扮", "教育培训",  "人情往来", "休闲娱乐", "药品医疗",
                   "数码产品", "日用耗品", "厨房用品", "家具用品", "家具柜子", "家用电器"]

openai.api_key = os.environ.get("AZURE_API_KEY")
openai.api_base = os.environ.get("AZURE_API_BASE")  # your endpoint should look like the following https://YOUR_RESOURCE_NAME.openai.azure.com/
openai.api_type = 'azure'
openai.api_version = "2023-03-15-preview"
deployment_name = 'test35' #This will correspond to the custom name you chose for your deployment when you deployed a model. 


def strip_in_data(data):  # 把列名中和数据中首尾的空格都去掉。
    data = data.rename(columns={column_name: column_name.strip() for column_name in data.columns})
    data = data.applymap(lambda x: x.strip().strip('¥') if isinstance(x, str) else x)
    return data


def classify(df):
    for index, row in df.iterrows():
        hit = False
        for item in rules:
            if item in row['交易对方']:
                df.at[index, '收支项目'] = rules[item]
                hit = True 
                break
        if not hit:
            for item in detail_rules:
                if item in row['备注']:
                    df.at[index, '收支项目'] = detail_rules[item]
                    hit = True 
                    break 
        if not hit:
            response = openai.ChatCompletion.create(
            engine = deployment_name,
            messages=[
            {"role": "system", "content": f"你是一个文本分类器，我将给你两个短文，分别表示交易商家和交易内容，请把这个条目分类到以下支出类目：{' '.join(expense_types)}，不要返回多余的内容和标点符号，只返回支出类目"}, 
            {"role": "user", "content": f"{row['交易对方']} {row['备注']}"}])
            expense_type = response['choices'][0]['message']['content']
            if expense_type in expense_types:
                df.at[index, '收支项目'] = expense_type
    return df 

def read_data_zfb(path):
    d_zfb = pd.read_csv(path, header=4, skipfooter=7, encoding='gbk', engine='python') # 数据获取，支付宝
    d_zfb = d_zfb.iloc[:, [2, 10, 11, 6, 7, 8, 9]]  # 按顺序提取所需列
    d_zfb = strip_in_data(d_zfb)  # 去除列名与数值中的空格。
    d_zfb['交易创建时间'] = d_zfb['交易创建时间'].astype('datetime64').dt.strftime('%Y-%m-%d')  # 数据类型更改
    d_zfb['金额（元）'] = d_zfb['金额（元）'].astype('float64')  # 数据类型更改
    d_zfb = d_zfb[d_zfb['收/支'] == '支出']
    d_zfb.drop(['交易状态', '类型'], axis=1, inplace=True)
    d_zfb.rename(columns={'交易创建时间': '交易日期', '收/支': '收支类型', '商品名称': '备注', '金额（元）': '金额'}, inplace=True)  # 修改列名称
    d_zfb.insert(2, '收支项目', default_expense, allow_duplicates=True)
    money = d_zfb.pop('金额')
    d_zfb.insert(3, '金额', money)
    d_zfb.insert(4, '账户名称', zfb_account, allow_duplicates=True)
    d_zfb.insert(5, '标签', '', allow_duplicates=True)
    d_zfb = classify(d_zfb)  
    d_zfb.drop(['交易对方'], axis=1, inplace=True)
    return d_zfb


def read_data_wx(path):
    d_wx = pd.read_csv(path, header=16, skipfooter=0, encoding='utf-8')  # 数据获取，微信
    d_wx = d_wx.iloc[:, [0, 4, 7, 1, 2, 3, 5]]  # 按顺序提取所需列
    d_wx = strip_in_data(d_wx)  # 去除列名与数值中的空格。
    d_wx['交易时间'] = d_wx['交易时间'].astype('datetime64').dt.strftime('%Y-%m-%d')  # 数据类型更改
    d_wx['金额(元)'] = d_wx['金额(元)'].astype('float64')  # 数据类型更改
    d_wx = d_wx[d_wx['收/支'] == '支出']
    d_wx.drop(['当前状态', '交易类型'], axis=1, inplace=True)
    d_wx.rename(columns={'金额(元)': '金额', '收/支': '收支类型', '商品': '备注', '交易时间': '交易日期'}, inplace=True)  # 修改列名称
    d_wx.insert(2, '收支项目', default_expense, allow_duplicates=True)
    money = d_wx.pop('金额')
    d_wx.insert(3, '金额', money)
    d_wx.insert(4, '账户名称', wx_account, allow_duplicates=True)
    d_wx.insert(5, '标签', '', allow_duplicates=True)
    d_wx = classify(d_wx)
    d_wx.drop(['交易对方'], axis=1, inplace=True)
    return d_wx 


if __name__ == "__main__":
    zfb_path = './alipay.csv'
    wx_path = "./wx.csv"
    zfb_pd = read_data_zfb(zfb_path)
    wx_pd = read_data_wx(wx_path)
    total_pd = pd.concat([zfb_pd, wx_pd])
    total_pd = total_pd.sort_values('交易日期')
    total_pd.to_csv('my_data.csv', index=False)

