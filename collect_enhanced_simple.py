#!/usr/bin/env python3
import requests, json, time
from datetime import datetime

SERVICE_ID = "8806b098778b4d6e84cd"
SECURITY_KEY = "5736845d40cf49ec8da5"
AUTH_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/auth/authentication.json"
POP_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/stats/population.json"
AGE_SEX_URL = "https://sgisapi.kostat.go.kr/OpenAPI3/stats/searchpopulation.json"
YEARS = ["2015","2016","2017","2018","2019","2020","2021","2022","2023"]
OUTPUT = "sgis_enhanced_multiyear_stats.json"

def check_net():
    try: requests.get("https://google.com",timeout=10); return True
    except: return False

def wait_net():
    while not check_net(): print(".",end="",flush=True); time.sleep(30)

def get_token():
    for i in range(5):
        try:
            wait_net()
            r = requests.get(AUTH_URL,params={"consumer_key":SERVICE_ID,"consumer_secret":SECURITY_KEY},timeout=10)
            return r.json()['result']['accessToken']
        except: time.sleep(5)
    return None

def collect(token,year,code):
    for i in range(3):
        try:
            wait_net()
            r1=requests.get(POP_URL,params={"accessToken":token,"year":year,"adm_cd":code},timeout=10)
            d1=r1.json()
            if 'result' not in d1 or not d1['result']: return None
            base=d1['result'][0]
            
            r2=requests.get(AGE_SEX_URL,params={"accessToken":token,"year":year,"adm_cd":code,"low_search":"1"},timeout=10)
            d2=r2.json()
            
            ages={}
            if 'result' in d2:
                for item in d2['result']:
                    c=item['adm_cd'][-6:]
                    if int(c[:2])==2:
                        dc=int(c[2:])
                        age_map={1:"0-9세",2:"10-19세",3:"20-29세",4:"30-39세",5:"40-49세",6:"50-59세",7:"60-69세",8:"70-79세",9:"80세 이상"}
                        age_idx=dc//100 if dc>=100 else dc//10
                        is_fem=dc>=100
                        age=age_map.get(age_idx,"기타")
                        if age not in ages: ages[age]={"male":0,"female":0,"total":0}
                        pop=int(item['population'])
                        if is_fem: ages[age]["female"]=pop
                        else: ages[age]["male"]=pop
                        ages[age]["total"]=ages[age]["male"]+ages[age]["female"]
            
            return {"basic":{"total_population":int(base.get('tot_ppltn',0)),"avg_age":float(base.get('avg_age',0)),"population_density":float(base.get('ppltn_dnsty',0)),"oldage_support_ratio":float(base.get('oldage_suprt_per',0)),"youth_support_ratio":float(base.get('juv_suprt_per',0)),"aging_index":float(base.get('aged_child_idx',0))},"age_groups":ages}
        except: 
            if i<2: time.sleep(2)
    return None

print("╔════════════════════════════════════════════════════════════╗")
print("║     SGIS 연령별 상세 통계 수집 (2015~2023)              ║")
print("╚════════════════════════════════════════════════════════════╝\n")

with open('sgis_comprehensive_stats.json','r') as f:
    codes=list(json.load(f).get('regions',{}).keys())
print(f"✅ {len(codes):,}개 읍면동\n")

try:
    with open(OUTPUT,'r') as f: out=json.load(f)
    print(f"✅ 기존 데이터: {len(out.get('regions_by_year',{}))}개 연도")
except:
    out={"metadata":{"collection_date":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"years":YEARS},"regions_by_year":{}}
    print("✅ 신규 수집 시작")

token=get_token()
if not token: print("❌ 토큰 실패"); exit(1)
print(f"✅ 토큰: {token[:20]}...\n")

token_time=time.time()
for year in YEARS:
    if year not in out['regions_by_year']: out['regions_by_year'][year]={}
    yd=out['regions_by_year'][year]
    done=len(yd)
    if done>=len(codes)-5: print(f"⏭️ {year}년 완료"); continue
    
    print(f"\n📅 {year}년 수집 중... (기존:{done}개)")
    cnt=0
    for idx,code in enumerate(codes,1):
        if code in yd: continue
        if time.time()-token_time>3000: token=get_token(); token_time=time.time()
        
        stats=collect(token,year,code)
        if stats: yd[code]=stats; cnt+=1
        if cnt%100==0:
            with open(OUTPUT,'w') as f: json.dump(out,f,ensure_ascii=False,indent=2)
            print(f"   {done+cnt}/{len(codes)} ({(done+cnt)/len(codes)*100:.1f}%)")
        time.sleep(0.3)
    
    with open(OUTPUT,'w') as f: json.dump(out,f,ensure_ascii=False,indent=2)
    print(f"✅ {year}년 완료: {len(yd)}개")

print("\n✅ 전체 수집 완료!")
