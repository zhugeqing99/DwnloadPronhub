import re,json,winreg,requests,os,time,random
from bs4 import BeautifulSoup as bf
from urllib.parse import urlparse


def get_proxy_address():
    try:
        # 打开注册表项
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Software\Microsoft\Windows\CurrentVersion\Internet Settings')
        
        # 读取代理服务器地址
        proxy_address, _ = winreg.QueryValueEx(reg_key, 'ProxyServer')
        
        # 关闭注册表项
        winreg.CloseKey(reg_key)
        
        return proxy_address
    except Exception as e:
        print(f"Error: {e}")
        return None

def find_string_positions(string,sstr):
    #获取指定字符出现的所有位置
    pattern = re.compile(sstr)
    positions = [match.start() for match in re.finditer(pattern, string)]
    return positions

def sort_dict_by_key(dictionary):
    #对字典进行排序
    sorted_dict = dict(sorted(dictionary.items(), key=lambda x: x[0],reverse=True))
    return sorted_dict

def GetMainUrl(url:str):
    parsed_url = urlparse(url)
    main_url = parsed_url.scheme + "://" + parsed_url.netloc
    return main_url

def DownloadOneVideo(url:str):
    heads={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Sec-Ch-Ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'Sec-Ch-Ua-Arch': '"x86"',
        'Sec-Ch-Ua-Full-Version': '"116.0.5845.188"',
        'Sec-Ch-Ua-Full-Version-List': '"Chromium";v="116.0.5845.188", "Not)A;Brand";v="24.0.0.0", "Google Chrome";v="116.0.5845.188"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Model': '""',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Ch-Ua-Platform-Version': '"10.0.0"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        }
    proxies={
    'http':'http://{}'.format(get_proxy_address()),
    'https':'http://{}'.format(get_proxy_address()),
    }

    respone_data=requests.get(url,headers=heads,proxies=proxies)

    pattern = r'var flashvars_\d+ = {.*?var player_mp4_seek = "ms";'
    
    result =  re.findall(pattern, respone_data.text, re.DOTALL)
    if(len(result)==0):
        #print("获取失败，等我重试一下")
        time.sleep(random.randint(0, 5))
        DownloadOneVideo(url)
        return
    result=result[0]
    if(result):

        matched_string=result.replace("\/","/")
        all_a=find_string_positions(matched_string,"=")
        all_b=find_string_positions(matched_string,";")
        matched_string=matched_string[all_a[0]+1:all_b[-2]]
        json_data=json.loads(matched_string)
        title=json_data["video_title"]
        video_list={}
        for item in json_data["mediaDefinitions"]:
            if(item["format"]=="hls"):
                qulity=int(item["quality"][0])
                video_url=item["videoUrl"]
                video_list[qulity]=video_url
        video_list=sort_dict_by_key(video_list)
        best_qulity=list(video_list.keys())[0]
        url=video_list[best_qulity]
        print(title,url)


    else:
        print("No match found.")

def GetUperAllVideo(url:str):
    heads={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Sec-Ch-Ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'Sec-Ch-Ua-Arch': '"x86"',
        'Sec-Ch-Ua-Full-Version': '"116.0.5845.188"',
        'Sec-Ch-Ua-Full-Version-List': '"Chromium";v="116.0.5845.188", "Not)A;Brand";v="24.0.0.0", "Google Chrome";v="116.0.5845.188"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Model': '""',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Ch-Ua-Platform-Version': '"10.0.0"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        }
    proxies={
    'http':'http://{}'.format(get_proxy_address()),
    'https':'http://{}'.format(get_proxy_address()),
    }
    page_index=1
    while True:
        urlIndex=url+"/videos?page="+str(page_index)
        respone_data=requests.get(urlIndex,headers=heads,proxies=proxies)
        if respone_data.status_code==404:
            break
        bf_data=bf(respone_data.text,'html.parser')
        video_list=bf_data.find("div",class_="videoUList clear-both")
        video_list=video_list.find_all("li")
        for item in video_list:
            tmpurl=item.find("a").get("href")
            tmpurl=GetMainUrl(url)+tmpurl
            DownloadOneVideo(tmpurl)
        page_index+=1


if(__name__=="__main__"):
    # url="https://cn.pornhub.com/view_video.php?viewkey=ph61d9caf5b727d&t=397"
    # DownloadOneVideo(url)

    url="https://cn.pornhub.com/model/nezukojapan"
    GetUperAllVideo(url)
    