import requests
import pandas as pd
import json
from bs4 import BeautifulSoup as bs
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from multiprocessing import Pool
import random

captcha_base_url = "https://erp.iitkgp.ac.in/StudentPerformanceV2/auth/PassImageServlet/"

def getResult(roll, dob):
    try:
        s = requests.Session()
        s.get('https://erp.iitkgp.ac.in/StudentPerformanceV2/auth/login.htm')
        r = s.post('https://erp.iitkgp.ac.in/StudentPerformanceV2/auth/getCaptchaCode.htm')
        captcha_hash = r.text
        captcha_link = captcha_base_url + captcha_hash
        captcha_req = s.get(captcha_link, stream=True)

        image_name = str(random.randint(1, 500)) + '.jpeg'
        with open(image_name,'wb') as f:
            for chunk in captcha_req.iter_content(1024):
                f.write(chunk)
        captcha_image = Image.open(image_name)

        img = ImageEnhance.Contrast(captcha_image).enhance(100)
        imgMap = img.load()
        for i in range(1, img.size[0]-1):
            for j in range(1, img.size[1]-1):
                if(imgMap[i,j] == (0,0,0)):
                    count = 0
                    if(imgMap[i,j+1] == (0,0,0)):
                        count += 1
                    if(imgMap[i+1,j] == (0,0,0)):
                        count += 1
                    if(imgMap[i-1,j] == (0,0,0)):
                        count += 1
                    if(imgMap[i,j-1] == (0,0,0)):
                        count += 1
                    if(imgMap[i+1,j-1] == (0,0,0)):
                        count += 1
                    if(imgMap[i-1,j-1] == (0,0,0)):
                        count += 1
                    if(imgMap[i-1,j+1] == (0,0,0)):
                        count += 1
                    if(imgMap[i+1,j+1] == (0,0,0)):
                        count += 1
                    if(count <= 3):
                        imgMap[i,j] = (255,255,255)

        captcha_text = pytesseract.image_to_string(img, lang="eng")[:6]
        print("captcha text: {}".format(captcha_text))
        login_data = {
            'rollno': roll,
            'dob': dob,
            'passline': captcha_text
        }
        # print(login_data)
        s.post('https://erp.iitkgp.ac.in/StudentPerformanceV2/auth/authenticate.htm', login_data)
        # with open('login_fail.html', 'wb') as f:
        #     f.write(r.content)
        year = int(roll[:2])
        sem_no = (21 - year)*2+0
        r = s.post('https://erp.iitkgp.ac.in/StudentPerformanceV2/secure/Stud_Performance.htm?rollno={}&semno={}&disp_val=S'.format(roll, sem_no), {"order":"asc"})
        r_cgpa = s.post('https://erp.iitkgp.ac.in/StudentPerformanceV2/secure/StudentPerfDtls.htm?rollno={}'.format(roll), {"order":"asc"})
        # r = s.post('https://erp.iitkgp.ac.in/StudentPerformanceV2/secure/Stud_Performance.htm?rollno=18cs10002&semno=5&disp_val=S'.format(roll, sem_no), {"order":"asc"})
        # print(s.cookies.get_dict())
        temp = json.loads(r_cgpa.text)
        # temp = [{'cgpa':temp[-1]['nccgsg']}]
        temp = [{'cgpa':temp[-1]['nccgsg']}]

        #uncomment for full result
        temp.extend(json.loads(r.text)) 
        # with open('page.html', 'wb') as f:
            # f.write(s.get('https://erp.iitkgp.ac.in/StudentPerformanceV2/secure/showHome.htm').content)
        # print(json.dumps(temp))
        return json.dumps(temp)
    except Exception as ex:
        print(ex)
        return 'html'

def getResultRec(inp, depth=0):
    name, roll, dob = inp
    print("handling for {} - {}".format(name, roll))
    if(depth > 10):
        return {roll : [['NA']]}
    result = getResult(roll,dob)
    if('html' in result):
        return getResultRec(inp, depth+1)
    else:
        return {roll : result}



# data.csv format: name,roll,dob
roll_list = pd.read_csv('data.csv',header=None).values.tolist()
# valid_roll_list = roll_list[3613:]
# valid_roll_list = roll_list[4925:4935] #18 Part
# valid_roll_list = roll_list[3613:4926] #17
# valid_roll_list = roll_list[2305:3614] #16
valid_roll_list = roll_list[4925:6298] #18
# valid_roll_list = roll_list[6298:] #19
# valid_roll_list = roll_list[5913:6060] #ME Dept
# valid_roll_list = roll_list[5913:5920] #ME Dept Part

print(len(valid_roll_list))

p = Pool(50)
full_result = p.map(getResultRec, valid_roll_list)
p.terminate()
p.join()

with open('data_out_18_Aut_2021_new.json','w') as f:
    f.write(json.dumps(full_result))

print('\n\nDone.')