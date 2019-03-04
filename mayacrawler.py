import requests, re, urllib, time, datetime, MySQLdb, sys
from bs4 import BeautifulSoup
from selenium import webdriver

#core variable needed, obtained from user
idashid = str(sys.argv[1])
bimayid = str(sys.argv[2])
bimayps = str(sys.argv[3])

headers = {
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
	'Content-type': 'application/x-www-form-urlencoded'
	}

url = 'https://binusmaya.binus.ac.id/login/'
url_success = 'https://binusmaya.binus.ac.id/newStudent/'
phantomjs_path = 'E:\Installer\phantomjs-2.1.1-windows\phantomjs.exe'

def writelog(failsegment, account, errfromsystem):
	with open("syncoperation.txt", "w+") as logfile: 
		occur_time_log = time.ctime()
    	logfile.write("[{}] error while fetching {} for {} - [RAW] {}".format(occur_time_log, failsegment, account, errfromsystem))

def flow_todb(sql):
	db = MySQLdb.connect('localhost','root','','webcore')
	cursor = db.cursor()
	try:
		cursor.execute(sql)
		db.commit()
	except:
		db.rollback()
		return

def gradepoint(source):
	soup = BeautifulSoup(source, 'html.parser')
	try:
		gpa = soup.find('div', {'class':'wheel-meter'}).get('data-value')
		query = "UPDATE webcore.userdata SET gpa = '{}' WHERE username = '{}'".format(gpa, idashid)
		flow_todb(query)
	except Exception as e:
		print e
		writelog(bimayid, 'Grade Point', str(e))
		return

def schedule(source):
	soup = BeautifulSoup(source, 'html.parser')
	try:
		course_title = [topic.getText().encode("utf-8") for topic in soup.find_all('span', {'class':'iCourse'})]
		class_campus = [campus.getText().encode("utf-8") for campus in soup.find_all('span', {'class':'iCampus'})]
		class_time = [shift.getText().encode("utf-8") for shift in soup.find_all('div', {'class':'iTimeNextAgenda'})]
		today = datetime.datetime.now().strftime("%A")
		for each in range(len(course_title)):
			query = "INSERT INTO coursedata.{} (day, course, room, shift) VALUE ('{}' , '{}', '{}', '{}')".format(MySQLdb.escape_string(idashid), today, str(course_title[each]), str(class_campus[each]), str(class_time[each]))
			flow_todb(query)
	except Exception as e:
		print e
		writelog(bimayid, 'Upcoming Courses', str(e))
		return
		 
s = requests.Session()
driver = webdriver.PhantomJS(phantomjs_path)
print "aa"
r = s.get(url + 'index.php', headers = headers)
field1 = urllib.unquote(BeautifulSoup(r.content, 'html.parser').find("input", {"class":"input text"}).get('name')) #field for username
field2 = urllib.unquote(BeautifulSoup(r.content, 'html.parser').find("input", {"type":"password"}).get('name')) #field for password
loader = re.search(r'<script src="../login/(loader.php\?serial=[a-zA-Z0-9_%]*)"></script>', r.content) #loader serial url

obtainkey = s.get(url + loader.group(1), headers = headers)
hidden = BeautifulSoup(obtainkey.content, "html.parser").find_all("input", type="hidden")
print "aa"
field3 = [urllib.unquote(secret.get('name')) for secret in hidden] #loader name
field4 = [urllib.unquote(secret.get('value')) for secret in hidden] #loader value

params = {
	str(field1):str(bimayid), #username
	str(field2):str(bimayps), #password
	'ctl00$ContentPlaceHolder1$SubmitButtonBM':'Login',
	str(field3[0]):str(field4[0]),
	str(field3[1]):str(field4[1])
}

r = s.post(url + 'sys_login.php', headers = headers, data = params)
print "aa"
driver.get(url_success)
print "aa"
driver.delete_all_cookies()
print "aa"
driver.execute_script("document.cookie='PHPSESSID={}; path=/';".format(s.cookies.get_dict()['PHPSESSID']))
print "aa"
driver.get(url_success)
print "aa"
time.sleep(5)
print "bb"

source = driver.page_source.encode("utf-8")

#print "Current GPA: ",
#gradepoint(source.encode("utf-8"))
#print "[===] Courses This Semester [===]"
#courses(source.encode("utf-8"))
#print "[===] [===================] [===]"
#print
schedule(source)
gradepoint(source)
#gradepoint(source)
#print BeautifulSoup(r.content, 'html.parser').find("div", {"id":"login_error"}).getText()

