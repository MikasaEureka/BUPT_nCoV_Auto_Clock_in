from datetime import time
import os
import time
import requests
import logging
from lxml import etree
import random

###############################################################################
# 常量设置
###############################################################################

# server bot发送配置
from server_bot import *

# 登陆URL
LOGIN_URL = 'https://auth.bupt.edu.cn/authserver/login'

# 填报URL
FORM_URL = "https://app.bupt.edu.cn/ncov/wap/default/save"

# 重要: CAS认证的跳转地址记录
SERVICE = 'https://app.bupt.edu.cn/a_bupt/api/sso/cas?redirect=https%3A%2F%2Fapp.bupt.edu.cn%2Fncov%2Fwap%2Fdefault%2Findex&from=wap'

# 模拟浏览器信息
USER_AGENT = 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0'

# Execution信息的xpath
EXECUTION_XPATH = '/html/body/div[1]/div/form/div[5]/input[2]/@value'

# 表单信息
DATA = {
	"area":       "北京市 海淀区",                 	# 地区，中间用" "隔开
	"city":       "北京市",							# 城市
	"province":   "北京市",							# 所在省份
	"sfzx":       "1",          					# 是否在校
	"created":    "1608086660", 					# 时间戳

	"xwxgymjzqk": "2",          					# 疫苗接种情况：2针
	"csmjry":     "0",          					# 近14日内本人/共同居住者是否去过疫情发生场所
	"date":       "20201216",   					# 填报日期
	"fjsj":       "20200830",   					# 返京时间
	"fxyy":       "",           					# 返校原因
	"glksrq":     "",           					# 观测开始实际
	"gllx":       "",           					# 观察场所
	"gtjzzfjsj":  "",           					# 共同居住者返京时间
	"gwszdd":     "",           					# 未给出
	"ismoved":    "0",          					# 当前地点是否与上次在同一城市
	"zgfxdq":     "0",          					# 中高风险地区
	"tw":         "2",          					# 体温范围
	"szsqsfybl":  "0",          					# 所在社区是否有确诊病例
	"bztcyy":     "",           					# 不在同城原因（今天为什么和昨天不在一个城市）
	"jcbhlx":     "",           					# 接触人群类型
	"jcbhrq":     "",           					# 接触时间
	"jchbryfs":   "",           					# 接触方式
	"jcjgqr":     "0",          					# 属于正常情况
	"jcjg":       "",           					# 未解释
	"jcqzrq":     "",           					# 未解释
	"jcwhryfs":   "",           					# 接触方式
	"jhfjhbcc":   "",           					# 计划返京航班班次/车次
	"jhfjjtgj":   "",           					# 计划返京交通工具
	"jhfjrq":     "",           					# 计划返京时间
	"jhfjsftjhb": "0",          					# 未给出
	"jhfjsftjwh": "0",          					# 未给出
	"jrsfqzfy":   "",           					# 未给出
	"jrsfqzys":   "",           					# 未给出
	"mjry":       "0",          					# 密切接触人员
	"qksm":       "",           					# 情况说明
	"remark":     "",           					# 其他信息
	"sfcxtz":     "0",          					# 今日是否出现发热，咽痛，干咳，咳痰，乏力，呕吐，腹泻，嗅觉异常，味觉异常
	"sfcxzysx":   "0",          					# 是否有任何与疫情相关的， 值得注意的情况
	"sfcyglq":    "0",          					# 是否处于观察期
	"sfjcbh":     "0",          					# 今日是否接触无症状感染/疑似/确诊人群
	"sfjchbry":   "0",          					# 今日是否接触过近14日内在湖北其他地区（除武汉）活动过的人员
	"sfjcqz":     "",           					# 未解释
	"sfjcwhry":   "0",          					# 是否接触武汉人员
	"sfsfbh":     "0",          					# 未给出
	"sfsqhzjkk":  "0",          					# 未给出
	"sftjhb":     "0",          					# 今日是否到过或者经停湖北其他地区(除武汉)
	"sftjwh":     "0",          					# 今日是否经停武汉
	"sfxk":       "0",          					# 未解释
	"sfygtjzzfj": "0",          					# 家中是否有共同居住者返京
	"sfyqjzgc":   "",           					# 未给出
	"sfyyjc":     "0",          					# 是否到相关医院或门诊检查
	"sqhzjkkys":  "",           					# 未给出
	"szcs":       "",           					# 所在地区
	"szgj":       "",           					# 所在国家	
	"xjzd":       "",           					# 现居住地
	"xkqq":       "",           					# 未解释
	
	"ymjzxgqk":"", #疫苗接种相关情况
	"xwxgymjzqk":"3",  #校外接种情况
	"sfjzxgym":"1", #是否已接种第一针新冠疫苗
	"sfjzdezxgym":"1", #是否已接种第二针新冠疫苗
	
}

###############################################################################
# 设置Log信息
###############################################################################

# 设置debug等级
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s')

###############################################################################
# 环境变量获取
###############################################################################

AREA     = eval(os.environ['AREA'])       # 使用 ` ` 连接省、市、县
SERVER_KEY = eval(os.environ['SERVER_KEY'])
USERs = eval(os.environ['USERs'])

###############################################################################
# 进行CAS认证, 获取cookie
###############################################################################
Flag_successs,responces,data_ps,USERNAMEs,NAMEs= [],[],[],[],[]

for i in range(len(USERs)):
	if i!=0:
		time.sleep(random.randint(60,300))
		#多用户，随机等待60-300s时间防止ip被禁，具体时间待测试
	# 设置打卡成功flag，默认成功为1
	Flag_success = 1
	USERNAME,PASSWORD,NAME,SFZX=USERs[i]
	logging.info('Start authorize for %s ...', str(NAME))
	
	try:
		# 设置连接
		session = requests.Session()

		# 发送请求，设置cookies
		headers = { "User-Agent": USER_AGENT }
		params = { "service": SERVICE }
		responce = session.get(url=LOGIN_URL, headers=headers, params=params)
		logging.debug('Get: %s %s', LOGIN_URL, responce)

		# 获取execution
		html = etree.HTML(responce.content)
		execution = html.xpath(EXECUTION_XPATH)[0]
		logging.debug('execution: %s', execution)

		# 构造表单数据
		data = {
			'username': USERNAME,
			'password': PASSWORD,
			'submit': "登录",
			'type': 'username_password',
			'execution': execution,
			'_eventId': "submit"
		}
		logging.debug(data)

		# 登录到疫情防控通
		responce = session.post(url=LOGIN_URL, headers=headers, data=data)
		logging.debug('Post %s, responce: %s', LOGIN_URL, responce)


		logging.info('Authorize successed !!!')

	###############################################################################
	# 进行填报
	###############################################################################

		logging.info('Start form ...')
		# 设置表单数据
		data = DATA
		data['created'] = str(round(time.time()))
		data["area"] = AREA[i]
		postion = AREA[i].split()
		if postion[0] in ['北京市','上海市','重庆市','天津市']:
			city = postion[0]
		else:
			city = postion[1]
		data["city"] = city
		data["province"] = postion[0]
		data["sfzx"] = SFZX

		logging.info('Form: is in university: %s', bool(SFZX))
		logging.debug(data)

		# 填报
		responce = session.post(url=FORM_URL, headers=headers, data=data)
		logging.debug('Post %s, responce: %s', FORM_URL, responce)
		logging.info('Result below :')
		logging.info('Responce: %s', responce.json()['m'])

	except Exception as e:
		Flag_success = 0
		logging.error(e)
		raise e
		
	# wechat自动播报机器人-使用server酱
	# 借鉴https://github.com/zzp-seeker/bupt-ncov-auto-report
	data_p = AREA[i]
	Flag_successs+=[Flag_success]
	responces+=[responce.json()['m']]
	data_ps+=[data_p]
	USERNAMEs+=[USERNAME]
	NAMEs+=[NAME]	
	try:
		notifier = ServerJiangNotifier(
			sckey=SERVER_KEY[i], # server酱的发送key
			sess=requests.Session()
		)
		print(f'通过「{notifier.PLATFORM_NAME}」给用户发送通知')
		notifier.notify(
			success=Flag_successs, # 打卡是否成功
			msg=responces, # 服务器返回的响应
			data=data_ps, # 发送的打卡信息
			username=USERNAMEs, # 用户的唯一标识
			name=NAMEs # 消息显示的用户名
		)
	except:
		print(r"可能由于 「SERVER_KEY未设置」 或 「SERVER_KEY不正确」 或 「网络波动」 ，SERVER酱发送失败")
