# parser 
import requests
from bs4 import BeautifulSoup
import re
import csv

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

def write_all_questions(bsObj,spamwriter,tag):
    questions = bsObj.findAll("div", {"class":"consult_question"})
    for question in questions:
        #ques_url = ques_name.a['href']
        #print(ques_url)
        question_str = str(question.get_text())
        question_str = cleanhtml(question_str)
        question_str = question_str.replace("'+'","")
        question_str = question_str.replace("-->","")
        question_str = question_str.replace("<!--","") 
        question_str = question_str.replace("document.write('","")
        question_str = question_str.replace("');","")
        question_str = question_str.replace("\n","")
        # print(question_str)
        try:
            spamwriter.writerow([tag,question_str])
        except:
            pass
    return len(questions)

def main():
    with open('questions.csv', 'w', newline='',encoding = 'maccyrillic') as csvfile:
        spamwriter = csv.writer(csvfile,delimiter=';')
        added_questions_count = 0

        index_url = 'https://www.consmed.ru'
        r = requests.get(index_url)
        r.encoding = 'windows-1251'
        bsObj = BeautifulSoup(r.text,"lxml")

        l1_sections_names = bsObj.findAll("div", {"class":"l1_no_sel"}) 
        for l1_name in l1_sections_names[:]:
            l1_url = l1_name.a['href']
            
            r = requests.get(index_url+l1_url)
            r.encoding = 'windows-1251'
            bsObj = BeautifulSoup(r.text,"lxml")
            l2_sections_names = bsObj.findAll("div", {"class":"l2_no_sel"}) 

            for l2_name in l2_sections_names[:]:
                l2_url = l2_name.a['href']
                
                r = requests.get(index_url+l2_url)
                r.encoding = 'windows-1251'
                bsObj = BeautifulSoup(r.text,"lxml")
                    
                page_bar_no_select_page = bsObj.findAll("span", {"class":"page_bar_no_select_page"}) 
                pages = []
                for page in page_bar_no_select_page:
                    # page_url = page.a['href']
                    # print(page_url)
                    text = page.get_text()
                    text = text.replace('[','')
                    text = text.replace(']','')
                    pages.append(int(text))
                
                max_page = max(pages)

                for i in range(max_page+1):
                    r = requests.get(index_url+l2_url+'/'+str(i)+'/')
                    r.encoding = 'windows-1251'
                    bsObj = BeautifulSoup(r.text,"lxml")

                    added_questions_count += write_all_questions(bsObj,spamwriter,tag = l2_name.text)
                    if i % 20 == 0:
                        csvfile.flush()
                        print(str(added_questions_count) + ' questions were added')

    print("Finally: " + str(added_questions_count) + ' questions were added')

if __name__ == '__main__':
    main()