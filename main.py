#install pytrends
#pip install pytrends

#pip install --upgrade google-api-python-client
#pip install --upgrade google-auth-oauthlib google-auth-httplib2
#pip install moviepy
#pip install pytube
#pip install youtube-video-uploader-bot

#import the libraries
import os
import googleapiclient.discovery
import pandas as pd
from pytube import YouTube as ytDwnld
from moviepy.editor import *
from pytrends.request import TrendReq
#from youtube_video_uploader_bot import *

videosList = []
totalVideos=0
maxTrendCount = 5
maxResults = 5
regionList = []
selectedRegions = ["US","IN"]
totalVideos = maxResults*len(regionList)
videoDuration = "short"
true=True
false=False
#youtube.login(username="",password="")
#youtube.login_cookie(cookies=getYoutubeCookies())

# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = ""

youtubeAPI = googleapiclient.discovery.build(
api_service_name, api_version, developerKey = DEVELOPER_KEY)

def setRegions():
    request = youtubeAPI.i18nRegions().list(part="snippet")
    global regionList
    regionList = request.execute()

def getCountryName(countryId):
    for i in regionList['items']:
        if i['id']==countryId:
            return i['snippet']['name'].lower().replace(" ", "_")

def main():
    setRegions()
    for index, row in getGoogleTrends().iterrows():
        print(row[0])
        getYoutubeVideos(row[0],row[1])

def getGoogleTrends():
    #get today's treniding topics
    #trendingtoday = pytrend.today_searches(pn='IN')
    #kw_list=['funny pets']
    #pytrend.build_payload(kw_list=kw_list)
    #get related queries
    #related_queries = pytrend.related_queries()
    #print(related_queries.values())

    pytrend = TrendReq()
    trendingKeywordList = []
    
    for countryId in selectedRegions:
        trending_searches = pytrend.trending_searches(pn=getCountryName(countryId))
        trending_searches[1] = countryId
        trendingKeywordList.append(trending_searches.head(maxTrendCount))
    return pd.concat(trendingKeywordList)
    
def getYoutubeVideos(search,country):
    request = youtubeAPI.search().list(
        part="id,snippet",
        eventType="completed",
        order="date",
        maxResults=maxResults,
        videoDuration=videoDuration,
        q=search,
        regionCode=country,
        type="video",
        videoLicense="creativeCommon"
    )
    response = request.execute()
    vdoInfo = {}
    for res in response['items']:
        vdoInfo['id'] = res['id']['videoId']
        vdoInfo['snippet']= res['snippet']
        videosList.append(vdoInfo)
        yt = ytDwnld('http://youtube.com/watch?v='+res['id']['videoId'],
                     on_complete_callback=complete_func)
        try:
            yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').first().download()
        except:
            print("Download faild." + res['id']['videoId'])

def complete_func(self, file_path):
    print('complete')
    print(self)
    youtubeUpload('test', file_path)
    if len(videosList)==  totalVideos:
        print('fully completed')

#def getYoutubeCookies():
    #return [
        #{
            #"domain": ".youtube.com",
            #"expirationDate": 1700549982,
            #"hostOnly": false,
            #"httpOnly": false,
            #"name": "__Secure-3PAPISID",
            #"path": "/",
            #"sameSite": "no_restriction",
            #"secure": true,
            #"session": false,
            #"storeId": "0",
            #"value": "",
            #"id": 1
        #}]
def youtubeUpload(title,path):
    response=youtube.upload(title=title, video_path=path, kid_type="Yes, it's made for kids", description="I am just testing", type="Public")
    print(response['body']['VideoLink'])
main()
