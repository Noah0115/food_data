# coding=utf-8
import re
import time
import requests
import urllib3
from lxml import etree  # 导入解析库
from utils.Tools import *
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # 取消警告
#  hearder 构造http请求头
header = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 QIHU 360EE',
    # "cookie": 'Hm_lvt_639b8b065d5e3e930071bde74725f06e=1651837246; Hm_lpvt_639b8b065d5e3e930071bde74725f06e=1651837246',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'close',  # 取消keep-alive
    "Content-Type": "application/json"
}
tm = time.strftime("%Y-%m-%d %H-%M")  # 时间戳

def get_url(target_url):
    r = requests.get(target_url, headers=header)  # 向分类页发送请求，携带构造好的请求头
    r.encoding = 'utf-8'  # 以utf-8格式解码
    content = r.text
    html_etree = etree.HTML(content)  # 生成 DOM树对象
    a_list = html_etree.xpath('//div[@id="listtyle1_list"]//a//@href')
    return a_list
def get_single_data(target_url,type_name,food_type):
    r = requests.get(target_url, headers=header)  # 向分类页发送请求，携带构造好的请求头
    r.encoding = 'utf-8'  # 以utf-8格式解码
    content = r.text
    html_etree = etree.HTML(content)  # 生成 DOM树对象
    ingredients = ''
    accessories = ''
    step = ''
    pic_url = ''
    name = html_etree.xpath(f"/html/body/div[@class='main_w clearfix']/article[@id='app']/div[@class='recipe_header']/div[@class='recipe_header_c']/div[@class='recipe_header_info']/h1[@class='recipe_title']")[0].xpath('string(.)')
    if not check_file_exists(f"./data/{type_name}/{name}/{name}.csv"):
        craft = html_etree.xpath(f"/html/body/div[@class='main_w clearfix']/article[@id='app']/div[@class='recipe_header']/div[@class='recipe_header_c']/div[@class='recipe_header_info']/div[@class='info2']/div[@class='info2_item info2_item1']/strong")[0].xpath('string(.)')
        flavour = html_etree.xpath(f"/html/body/div[@class='main_w clearfix']/article[@id='app']/div[@class='recipe_header']/div[@class='recipe_header_c']/div[@class='recipe_header_info']/div[@class='info2']/div[@class='info2_item info2_item2']/strong")[0].xpath('string(.)')
        cost_time = html_etree.xpath(f"/html/body/div[@class='main_w clearfix']/article[@id='app']/div[@class='recipe_header']/div[@class='recipe_header_c']/div[@class='recipe_header_info']/div[@class='info2']/div[@class='info2_item info2_item3']/strong")[0].xpath('string(.)')
        difficult = html_etree.xpath(f"/html/body/div[@class='main_w clearfix']/article[@id='app']/div[@class='recipe_header']/div[@class='recipe_header_c']/div[@class='recipe_header_info']/div[@class='info2']/div[@class='info2_item info2_item4']/strong")[0].xpath('string(.)')
        ingredients_list = html_etree.xpath(f"/html/body/div[@class='main_w clearfix']/article[@id='app']/div[@class='recipe_header']/div[@class='recipe_header_c']/div[@class='recipe_header_info']/div[@class='recipe_ingredientsw']/div[@class='recipe_ingredients']/div[@class='right']/strong")
        for i in ingredients_list:
            ingredients = ingredients + i.xpath('string(.)').replace(' ','') + ','
        ingredients = ingredients.rstrip(',')
        accessories_list = html_etree.xpath(f"/html/body/div[@class='main_w clearfix']/article[@id='app']/div[@class='recipe_header']/div[@class='recipe_header_c']/div[@class='recipe_header_info']/div[@class='recipe_ingredientsw']/div[@class='recipe_ingredients recipe_ingredients1']/div[@class='right']/strong")
        for j in accessories_list:
            accessories = accessories + j.xpath('string(.)').replace(' ','') + ','
        accessories = accessories.rstrip(',')
        step_pic_list = html_etree.xpath(f"/html/body/div[2]/article/div[2]/div[1]/div[2]/div/div[2]/img/@src")
        count = 0
        for k in step_pic_list:
            pic_download = requests.get(url=k,headers=header)
            if 200 == pic_download.status_code:
                if not os.path.exists(f"./data/{type_name}"):
                    os.mkdir(f"./data/{type_name}")
                if not os.path.exists(f"./data/{type_name}/{name}"):
                    os.mkdir(f"./data/{type_name}/{name}")
                # 获取文件扩展名
                file_extension = re.search(r'\.([A-Za-z0-9]+)$', k)
                if file_extension:
                    file_extension = file_extension.group(1)
                else:
                    file_extension = 'jpg'  # 默认扩展名为jpg
                if not os.path.exists(f"./data/{type_name}/{name}"):
                    os.mkdir(f"./data/{type_name}/{name}")
                with open(f"./data/{type_name}/{name}/{count}.{file_extension}", 'wb') as file:
                    file.write(pic_download.content)
                pic_url = pic_url + f"{count}.{file_extension}"+','
            count = count + 1
        pic_url = pic_url.rstrip(',')
        cover = html_etree.xpath(f"/html/body/div[2]/article/div[1]/div/div[1]/img/@src")[0]
        cover_req = requests.get(url=cover,headers=header)
        if 200 == cover_req.status_code:
            # 获取文件扩展名
            file_extension = re.search(r'\.([A-Za-z0-9]+)$', cover)
            if file_extension:
                file_extension = file_extension.group(1)
            else:
                file_extension = 'jpg'  # 默认扩展名为jpg
            with open(f"./data/{type_name}/{name}/cover.{file_extension}", 'wb') as file:
                file.write(cover_req.content)
        step_list = html_etree.xpath(f"/html/body/div[2]/article/div[2]/div[1]/div[2]/div")
        for n in step_list:
            step = step + n.xpath('string(.)').replace(' ', '').replace('\r', '').replace('\n', '') + '\n'
        step = step.rstrip('\n')
        df = pd.DataFrame(
            {'name': [name],'cover': f"./data/{type_name}/{name}/cover.{file_extension}", 'craft': [craft], 'flavour': [flavour], 'cost_time': [cost_time], 'difficult': [difficult],
             'ingredients': [ingredients], 'accessories': [accessories], 'step': [step],'pic_path':[pic_url],'food_type':[food_type]})
        df.to_csv(f"./data/{type_name}/{name}/{name}.csv", index=False)
        print(f"name:{name},cover:{cover},craft:{craft},flavour:{flavour},cost_time:{cost_time},difficult:{difficult},ingredients:{ingredients},accessories:{accessories},step:{step},pic_url:{pic_url},food_type:{food_type}")
    else:
        print(f"{name}已爬取，跳过")
def get_data(tag,food_type,page_num,target_url_prefix):
    """
    :param tag:标签名，用于标识数据所属类型
    :param food_type:美食种类编号
    :param page_num:总页码数+1
    :param target_url_prefix:URL前缀
    :return:
    """
    for i in range(1, page_num):
        target_url = target_url_prefix + str(i)  # 分类主页
        url_list = get_url(target_url)
        for url in url_list:
            print(f"下载:{url}")
            try:
                get_single_data(url,tag,food_type)
            except:
                print("美食链接丢失，已跳过")
def get_all_foodtype(target_url):
    """
    :param target_url:一级总页面
    :return:返回美食种类列表、种类url列表
    """
    type_name_ls = []
    type_a_ls = []
    r = requests.get(target_url, headers=header)  # 向分类页发送请求，携带构造好的请求头
    r.encoding = 'utf-8'  # 以utf-8格式解码
    content = r.text
    html_etree = etree.HTML(content)  # 生成 DOM树对象
    type_div_list = html_etree.xpath(f"/html/body/div[@class='main_w clearfix']/div[@class='main']/div[@id='listnav']/div[@id='listnav_con_c']/dl[@class='listnav_dl_style1 w990 bb1 clearfix']/dd")
    type_a_list = html_etree.xpath(f"/html/body/div[@class='main_w clearfix']/div[@class='main']/div[@id='listnav']/div[@id='listnav_con_c']/dl[@class='listnav_dl_style1 w990 bb1 clearfix']/dd//a/@href")
    page_num_obj = html_etree.xpath(f"/html/body/div[@class='main_w clearfix']/div[@class='main']/div[@class='liststyle1_w clearfix']/div[@id='listtyle1_w']/div[@class='listtyle1_page']/div[@class='listtyle1_page_w']/span[@class='gopage']/form")[0]
    for i,k in zip(type_div_list,type_a_list):
        type_name_ls.append(i.xpath('string(.)'))
        type_a_ls.append(k+"?&page=")
    page_text = page_num_obj.xpath('string(.)')
    # 使用正则表达式提取所有数字
    page_num = int(re.findall(r'\d+', page_text)[0])
    df = pd.DataFrame({'type_name':type_name_ls})
    df.to_csv("./all_types.csv",index=False)
    return type_name_ls,type_a_ls,page_num

def get_all_data():
    count = 1
    type_name_ls,type_a_ls,page_num = get_all_foodtype('https://www.meishij.net/chufang/diy/jiangchangcaipu/?&page=')
    for type_name,type_a in zip(type_name_ls,type_a_ls):
        print(f"正在进行：{type_name}:{type_a}")
        # get_data(type_name,str(count),page_num,type_a)
        get_data(type_name,str(count),3,type_a)
        count += 1
# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    get_all_data()