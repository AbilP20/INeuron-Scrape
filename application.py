from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import pymongo; import mysql.connector as sqltor
from time import sleep; import os; import logging as lg
from fpdf import FPDF
import boto3

application = Flask(__name__)

@application.route("/")
def homepage():
    try:
        return render_template("index.html")
    except Exception as e:
        lg.info("Exception! - {e}")

@application.route("/courses",methods=['GET'])
def list_course():
    try:
        obj = ineuron_scrape()
        obj.List_All_Courses()
        return render_template("course_list.html",dictionary=obj.course_list)
    except Exception as e:
        lg.info("Exception! - {e}")

@application.route('/result',methods=['GET','POST'])
def search_course():
    try:
        c_name = request.form['cname']
        obj = ineuron_scrape()
        obj.Search_Course(c_name)
        return render_template("search_result.html",course=c_name,cname=obj.course_name, cdesc=obj.course_description,
            cfeat=obj.course_feature,cwyl=obj.course_wyl,creq=obj.course_req,ccurr=obj.course_curriculum,cteach=obj.course_teachers)
    except NoSuchCourseError:
        return render_template("search_result_error.html",course=c_name)
    except Exception as e:
        lg.info("Exception! - {e}")
        
class ineuron_scrape:    
    def __init__(self):
        self.course_list = dict()
        self.course_name = ''
        self.course_description = ''
        self.course_feature=[]
        self.course_wyl = []
        self.course_req = []
        self.course_teachers = dict()
        self.course_curriculum = dict()
        lg.basicConfig(filename="INeuronScraper.log", level=lg.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def __close_consult(self,driver):
        """
         Call this to close the 'Consule Us' pop-up that comes up in courses page
         Pass the Selenium WebDriver interface variable as input
        """
        try:
            close_consultation = driver.find_element(By.XPATH,'//*[@id="Modal_enquiry-modal__yC3YI"]/div/div[1]/i')
            lg.info("Finding pop-up close button.")
        except Exception as e:
            lg.info(f"Exception! - {e}")
        else:
            close_consultation.click()
            lg.info("Consult_Us pop-up Closed.")

    def List_All_Courses(self):
        """
        list all the courses available on INeuron site
        """
        try:
            lg.info("Opening Chrome for listing courses.")
            s = Service("chromedriver.exe")
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            
            options.add_argument("--window-size=1051,805")
            driver = webdriver.Chrome(service=s, options=options)
            lg.info("Setting window size.")
            lg.info("Loading 'https://ineuron.ai'")
            driver.get("https://ineuron.ai/")
        except Exception as e:
            lg.info(f"Exception! - {e}")
        try:
            sleep(2)
            print("Getting list of Courses...",end='')
            driver.find_element(By.XPATH,'//*[@id="hamburger"]/img').click()
            lg.info("Clicked sidebar 3 line button")
            sleep(2)
            driver.find_element(By.XPATH,'//*[@id="nav-sidebar"]/div/div/div[2]/ul/li[1]/i').click()
            lg.info("Clicked sidebar Courses.")
            lst = driver.find_element(By.XPATH,'//*[@id="nav-sidebar"]/div/div/div[2]/ul')
            courses = lst.text.split('\n')
            lg.info("Fetched Main-Courses List")
            j=0
            for i in range(1,len(courses)+1):
                elem = driver.find_element(By.XPATH,f'//*[@id="nav-sidebar"]/div/div/div[2]/ul/li[{i}]')
                elem.click()
                sub_course = driver.find_element(By.XPATH,'//*[@id="nav-sidebar"]/div/div/div[2]/ul')
                sub_course_lst = sub_course.text.split('\n')
                self.course_list[courses[j]] = sub_course_lst
                j=j+1
                elem_back = driver.find_element(By.XPATH,'//*[@id="nav-sidebar"]/div/div/div[1]/div[1]/i')
                elem_back.click()
            lg.info("Fetched Sub-Courses List")
            print("Completed")
        except Exception as e:
            lg.info(f"Exception! - {e}")

    def Search_Course(self,search_course):
        """
        pass the course you want to search as a 'string'
        This function will scrape all details available for that course
        """
        try:
            lg.info("Opening Chrome")
            s = Service("chromedriver.exe")
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument("--window-size=1051,805")
            driver = webdriver.Chrome(service=s, options=options)
            lg.info("Setting window size.")
            lg.info("Loading 'https://ineuron.ai'")
            driver.get("https://ineuron.ai/")
        except Exception as e:
            lg.info(f"Exception! - {e}")
        try:
            search_but = driver.find_element(By.XPATH,'//*[@id="search-mobile"]/img')
            search_but.click()
            lg.info("'Search' Clicked")
            type_here = driver.find_element(By.XPATH,'//*[@id="search-bar-mobile"]')
            type_here.click()
            lg.info("'text-box' Clicked.")
            for i in search_course:
                type_here.send_keys(i)
            sleep(2)
            lg.info("2 sec wait for further info to load.")
            course_entered = driver.find_element(By.XPATH,'//*[@id="nav-search"]/div/div[2]/div/ul/a[1]/li/div/span')
            print("Found a Course.")
            lg.info("Found a Course.")
        except Exception as e:
            print(f"No Course({search_course}) Found.")
            lg.info(f"No such course({search_course}) was found.")
            raise NoSuchCourseError()
        else:
            try:
                course_entered.click()
                lg.info("Course Clicked.")
                sleep(7)
                lg.info("FETCHING COURSE DETAILS...")
                print("Getting Course Details...",end='')
                lg.info("7 sec wait for Consult_Us pop-up.")
                self.__close_consult(driver)
                self.course_name = driver.find_element(By.XPATH,'//*[@id="__next"]/section[1]/div/div[1]/h3').text 
                print(self.course_name,end='...')
                lg.info(f"Fetched Course Name - {self.course_name}")
                self.course_description = driver.find_element(By.XPATH,'//*[@id="__next"]/section[1]/div/div[1]/div[2]').text 
                lg.info("Fetched Course Description")
                features = driver.find_elements(By.XPATH,'//*[@id="__next"]/section[2]/div/div/div[2]/div[1]/div[3]/ul/li')
                self.course_feature = [i.text for i in features]
                lg.info("Fetched Course Features")
                wyl = driver.find_elements(By.XPATH,'//*[@id="__next"]/section[2]/div/div/div[1]/div[1]/ul/li')
                self.course_wyl = [i.text for i in wyl]
                lg.info("Fetched Course What You'll Learn")
                req = driver.find_elements(By.XPATH,'//*[@id="__next"]/section[2]/div/div/div[1]/div[2]/ul/li')
                self.course_req = [i.text for i in req]
                lg.info("Fetched Course Requirements")
                teachers = driver.find_elements(By.CLASS_NAME,"InstructorDetails_left__nVSdv")
                j=4
                for i in range(len(teachers)):
                    xpath_name    = f'//*[@id="__next"]/section[2]/div/div/div[1]/div[{j}]/div[1]/h5'
                    xpath_details = f'//*[@id="__next"]/section[2]/div/div/div[1]/div[{j}]/div[1]/p'
                    teacher_name = teachers[i].find_element(By.XPATH,xpath_name).text
                    details = teachers[i].find_element(By.XPATH,xpath_details).text
                    j=j+1
                    self.course_teachers[teacher_name] = details
                lg.info("Fetched Course Teachers")
                lg.info("Fetching Course Curriculum...")
                try:
                    view_more_but = driver.find_element(By.XPATH,'//*[@id="__next"]/section[2]/div/div/div[1]/div[3]/span')
                    view_more_but.click()
                    lg.info("'View More' in Curriculum Clicked")
                except Exception as e:
                    lg.info(f"No 'View More' Button")
                elem1 = driver.find_elements(By.XPATH,'//*[@id="__next"]/section[2]/div/div/div[1]/div[3]/div/div')
                name=[]
                for i in range(1,len(elem1)+1):
                    xpath      = f'//*[@id="__next"]/section[2]/div/div/div[1]/div[3]/div/div[{i}]/div[1]/span'
                    curr_name       = driver.find_element(By.XPATH,xpath).text
                    name.append(curr_name)
                lg.info("Fetched Course Curriculum Main Topics")
                try:
                    for i in range(len(name)):
                        curr_desc = driver.find_elements(By.XPATH,f'//*[@id="curriculumref{i}"]/li')
                        sub_lst=[]
                        for j in range(1,len(curr_desc)+1):
                            sub_curr = driver.find_element(By.XPATH,f'//*[@id="curriculumref{i}"]/li[{j}]').text.split('\n')[0]
                            sub_lst.append(sub_curr)
                        self.course_curriculum[name[i]]=sub_lst
                        try:
                            plus = driver.find_element(By.XPATH,f'//*[@id="__next"]/section[2]/div/div/div[1]/div[3]/div/div[{i+2}]/div[1]')
                            plus.click()
                            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="__next"]/section[2]/div/div/div[1]/div[3]/div/div[{i+2}]/div[1]')))
                        except Exception as e:
                            lg.info(f"Exception! - No 'Plus' button found")
                    lg.info("Fetched Course Curriculum Sub Topics")
                    print("Completed.")
                    lg.info("Fetched Course Curriculum")
                    self.__create_file_pdf()
                    self.__mongo_push()
                    self.__sql_push()
                    print("Storing in S3 bucket...",end='')
                    lg.info("Storing pdf in Amazon S3 Bucket.")
#                     s3 = boto3.resource(service_name='s3',aws_access_key_id='',aws_secret_access_key='') #access key hidden to prevent unauthorized access and extra charges
# if you want to access s3 bucket and store your pdf ther, enter the 2 hidden data and then run the program
                    a = os.getcwd()+'\INeuron Course PDFs'+f'\{self.course_name}'+f'\{self.course_name}.pdf'
#                     s3.Bucket('test-pdf-store').upload_file(Filename=a,Key=f'{self.course_name}.pdf')
                    print("Completed.")
                    lg.info("Successfully Stored in S3 Bucket.")
                except Exception as e:
                    lg.info(f"Exception! - {e}")
            except Exception as e:
                lg.info(f"Exception! - {e}")

    def __create_file_pdf(self):
        """
        Create directory for the search function, to store the return data in .txt and .pdf formats
        """
        try:
            directory = os.getcwd()+"/INeuron Course PDFs"+"/"+self.course_name
            if os.path.exists(directory):
                print("Folder Exists.")
                lg.info(f"Directory '{directory}' exists.")
            else:
                print("Creating Folder...",end='')
                os.mkdir(directory)
                lg.info(f"Created Directory : '{directory}'")
                fname = directory+"/"+self.course_name+".txt"
                print("Creating .txt...",end='')            
                with open(fname,'w') as f:
                    f.write(self.course_name.upper()+'\n')
                    a = self.__into_mul_lines(self.course_description)
                    f.writelines('\nDESCRIPTION :\n'+a)
                    f.write('\n\nFEATURES :')
                    for i in range(len(self.course_feature)): 
                        f.write('\n'+self.course_feature[i])
                    f.write('\n\nWHAT YOU\'LL LEARN :')
                    for i in range(len(self.course_wyl)):
                        f.write('\n'+self.course_wyl[i])   
                    f.write('\n\nREQUIREMENTS :')
                    for i in range(len(self.course_req)):
                        f.write('\n'+self.course_req[i])
                    f.write('\n\nTEACHERS :')
                    for i in self.course_teachers:
                        f.write('\n'+i+' :-')
                        a = self.__into_mul_lines(self.course_teachers[i])
                        lg.info("Breaking Single-Line string to Multi-Line")
                        f.write('\n'+a+'\n')
                    f.write('\n\nCURRICULUM :')
                    for i in self.course_curriculum:
                        f.write('\n'+i+' :-')
                        for j in self.course_curriculum[i]:
                            f.write('\n\t          '+j)
                        f.write('\n')
                lg.info(f"{self.course_name}.txt Created.")
                print("Creating .pdf...",end='') 
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Times",size=13)
                f = open(fname,'r')
                for i in f:
                    pdf.cell(200,10,txt=i,ln=1,align='L')
                pdf.output(directory+"/"+self.course_name+'.pdf')
                print("Completed.")
                lg.info(f"{self.course_name}.pdf Created.")
                f.close()
        except Exception as e:
            lg.info(f"Exception! - {e}")

    def __mongo_push(self):
        """
        this function pushes the data retrieved(if available) on the MongoAtlas in the given collection(By default)
        """
        try:
            lg.info(f"PUSHING '{self.course_name}' INTO Mongo DB")
            print("Storing in MongoDB...",end='')
            client = pymongo.MongoClient("mongodb+srv://user:user@cluster0.rbmjvui.mongodb.net/?retryWrites=true&w=majority")
            lg.info("Mongo Atlas Connection Established.")
            db = client['INeuron_DB']
            col = db['Search_Course_Details']
            for document in col.find():
                for key in document:
                    if key == 'Name':
                        if document[key] == self.course_name:
                            print("Course Exists...Completed")
                            lg.info("Course Already Exists.")
                            return
            data=dict()
            data['Name']=self.course_name
            data['Description']= self.course_description
            data['Features'] = self.course_feature
            data['What You\'ll Learn']=self.course_wyl
            data['Course Requirements']=self.course_req
            data['Teachers']=self.course_teachers
            data['Curriculum']=self.course_curriculum
            col.insert_one(data)
            print("Completed.")
            lg.info("Insert Successful.")
            client.close()
            lg.info("Mongo Atlas Connection Terminated.")
        except Exception as e:
            lg.info("Insert Unsuccessful.")
            lg.info(f"Exception! - {e}")

    def __sql_push(self):
        """
        this function pushes the data retrieved(if available) on the local mySQL in the given collection(By default)
        """        
        try:
            lg.info(f"PUSHING '{self.course_name}' INTO MYSQL DB")
            print("Storing in mySQL DB...",end='')
            con = sqltor.connect(host="localhost", user="root", passwd="pass", database='ineuron_db')
            lg.info("mySQL Connection Established.")
            cur = con.cursor()
            try:
                cur.execute(f"insert into course_details values(\"{self.course_name}\",\"{self.course_description}\")")
                con.commit()
            except sqltor.IntegrityError:
                print("Course Exists...Completed")
                lg.info("Course Already Exists.")
            except Exception as e:
                lg.info(f"Exception! - {e}")
            else:
                print("Completed.")
                lg.info("Insert Successful.")                
            con.close()
            lg.info("mySQL Connection Terminated.")
        except Exception as e:
            lg.info("Insert Unsuccessful.")
            lg.info(f"Exception! - {e}")

    def __into_mul_lines(self,lst_of_string,limit=90):
        """
            lst_of_string = list of strings, limit = characters per line you want(by Default = 90 char per line)
            this function splits the multi-line course description and course teachers into single line strings so that they can be
            stored in a better looking way in the .txt and .pdf files
        """
        a=''
        trav=0
        for i in range(len(lst_of_string)):
            if trav>limit:
                a = a+'\n'+lst_of_string[i]
                trav=0
            else:
                a = a+lst_of_string[i]
            trav+=1
        return a
    
class NoSuchCourseError(Exception):
    pass

if __name__=="__main__":
    application.run()


