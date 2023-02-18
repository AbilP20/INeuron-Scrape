Git Link - Code works perfectly fine locally
AWS Link - The Index Page Loads, but an issue of Selenium which does not allow Browsers to open on the EC2 instance could not be solved, so we don't get any output on Cloud
Azure Link - Azure does not accept sign-up using debit cards (only credit card accepted), so could not sign-up, but even on Azure same Selenium issue would have occured. 

mySQL DB Table -> desc course_details;
+-------------+---------------+------+-----+---------+-------+
| Field       | Type          | Null | Key | Default | Extra |
+-------------+---------------+------+-----+---------+-------+
| Name        | varchar(200)  | YES  | UNI | NULL    |       |
| Description | varchar(9000) | YES  |     | NULL    |       |
+-------------+---------------+------+-----+---------+-------+

Google Chrome Version should be '110.0.5481.---'

USAGE :
Search - Enter any course name you want to search and wait for approx 20-80 seconds 
       - (based on amount of data to scrape time can increase or decrease)
List All Courses - Click this button and wait for approx 15-20 seconds to get the list of all courses on INeuron site

TESTS SEARCH CASES WERE PERFORMED SUCCESSFULLY:
    Search based on some keywords :
        1. rasa
        2. c language
        3. data science
        4. web dev
    Search Cases based on Actual Course Names :
        1. Build Modern ETL Data Pipeline using Informatica cloud
        2. House Price Prediction
    Search Cases for No Course Found :
        1. twdpisurl
        2. asasasa


Challenge  number 1 : 
    
1 . Got to ineuron website                              - Done
2. you have to scrap list of all the listed course name - Done
3. Got to a specific course one by one and then try to scrap all the curriculam and its respective details      - Done
4. Try to create a seperate seperate PDF file for all the coursed     - Done
5. Strore PDF file in amazong s3 bucket                        - Done
6. Strore all the course related information in mongo DB       - Done
7. Strore all the course name data and its description in MYSQL- Done
8. Deploy this application on beanstack , aws and azure        - Not Done
9. logging is mandatory                   - Done
10. Exception handling is nescessary      - Done
11. modular coding is nescessary          - Done
12. Classs and object is must             - Done
13. Finally submit your 3 hosted URL to me and sunny along with your code base git hub link
