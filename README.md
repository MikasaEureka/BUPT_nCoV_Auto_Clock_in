

<h2 align="center">~~北邮每日填报自动化server酱优化版~~ 可以取消啦</h2>

## 项目参考：
- [北邮自动疫情打卡](https://github.com/xiao-niu-ren/BUPT_nCoV_Auto_Clock_in)
- [北邮疫情自动填报（Python+Github Actions）长期维护](https://github.com/zzp-seeker/bupt-ncov-auto-report)

## 说明
利用Github提供的Actions完成自动运行脚本的过程
在`.github/workflow`中有一个YAML文件，打开后即可查看自动运行的相关细节

## 操作说明
1. 点击右上角的Fork将本仓库拷贝到自己的仓库中

2. 打开自己Fork的仓库，查看`.github/workflows/main.yml`中env的字段，如下

  ``` yaml
  env:
          USERs: ${{ secrets.USERs }}       # (学号,密码,server昵称，是否在校) # 是否在校，填"1"表示在校，"0"表示不在
          AREA: ${{ secrets.AREA }}               # 所在地区，例如例如"北京市 海淀区" 或 "xx省 xx市 xx区"
          SERVER_KEY: ${{ secrets.SERVER_KEY }}   # server酱的发送key
  ```
  
  北京市|上海市|重庆市|天津市 这些地区的所在地区格式是"xx市 xx区"
  
  其他地点为 "xx省 xx市 xx区"

3. 根据2中env的变量，在仓库的Settings-->Secrets中添加对应的值

   ![image-20220109211120815](https://images.xiaoniuren666.com/img/image-20220109211120815.png)

   依次将USERs、AREA、PROVINCE、CITY等环境变量添加进去
   若是单人的格式为
   
  ``` yaml
       USERs: [('20********','key','nickname','0')]
       AREA: ["北京市 海淀区"]
       SERVER_KEY: ['*********']
  ```
   
   若是多人的格式为

  ``` yaml
       USERs: [('20********','key','nickname','0'),(第二个人的信息)]
       AREA: ["北京市 海淀区","**"]
       SERVER_KEY: ['*********',"**"]
  ```
  
  ** 注意：失败的同学注意一下，字段要加中括号的 []
  
  
4. 在添加完毕后，点击Actions，进入自动操作的提示界面，开启Workflows

5. 自动操作的触发条件有二，在`.github/workflows/main.yml`中有说明

   ``` yaml
   on:
     push:
       branches: [ main ]
     schedule:
       - cron: '0 1 * * *'
       - cron: '0 17 * * *'
   #原来设置的时间是UTC时间的每日1:00 AM，即China Time的9:00 AM
   #由于北京时间位于东8区，UTC时间的16:00(China Time次日0:00)以后的时间会出现日期不匹配的情况
   #即utc时间 0401 17：00 打卡应该是北京时间 0402 1：00，但会导致服务器时间为0401，日期出现问题
   #所以，时间设置应该在16：00以前
   #具体配置可以参考https://crontab.guru/#0_1,4_*_*_*
   ```

6. 记得每60天要更新下～

7. 关于server 酱

  有关于多人的server发送已适配，每个人提供自己的server key即可
  
  有关于server酱的自定义只有显示名称 name，可以在程序中的USERs设置，对应nickname

  如果不配置Server酱微信推送，那么Value里对应的serverkey填写0即可，
  若为一个人的serverkey，value填写为['0']
  
  如果想配置的话看下一点

  **（可选）** Value填写Server酱的SendKey（在这里查看 [https://sct.ftqq.com/sendkey](https://sct.ftqq.com/sendkey)），在此之前需要微信注册企业号，并加入Server酱内部应用，具体流程见 [https://sct.ftqq.com/forward](https://sct.ftqq.com/forward)，看起来比较多，但也不是很麻烦，一步步照做即可
