import json
import re
from PIL import Image
import os
from uuid import uuid4
from flask import Flask, request, render_template, send_from_directory
import pytesseract
from base64 import decodestring
from pytesseract import image_to_string
import smtplib
import sqlite3

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

app = Flask(__name__)

gradeToIntMap={'C-':1,'C':1.1,'C+':1.2,'B-':1.3,'B':1.4,'B+':1.5,'A-':1.6,'A':1.7,'A+':1.8}

@app.route("/doOCR", methods=["POST"])
def doOCR():
    
    print "----------------Server Invoked-------------------"

    #fetch the base64 image string from the request
    data = dict(request.form)
    #print data
    img_data = data['img_val'][0].split(',')[1]

    courses = data['courses'][0].split('&')
    #print "Selected Courses ", courses

    coursesList = []

    for i in range(len(courses)):
        eachCourse = courses[i]
        eachCourse = eachCourse.split('=')[0]
        eachCourse = str(eachCourse).replace('+',' ')
        print eachCourse
        coursesList.append(eachCourse)

    print "Courses List ", coursesList
    userEmail = data['userEmail'][0]
    print "User Email ", userEmail

  
    #save to image file
    fh = open('imageToSave.png', 'wb')
    fh.write(decodestring(str(img_data)))
    fh.close()

    #do OCR on the saved image
    fh = open('imageToSave.png', 'r')
    result = image_to_string(Image.open(fh), lang='eng')
    file = open('output.txt','w')
    file.write(result) 
    file.close()
    fh.close()
    #return 'Success!'


    # will be fetched from the client
    applicationType = "Subject Enrollment" 
    mastersProgramme = "MSSE"
    #applicationType = "Masters"
    #requestedSubjects=["CMPE 273","CMPE 281"]
    #requestedSubjects=["EE 253"]
    requestedSubjects = coursesList
    #requestedSubjects=[]

    if(applicationType == "Masters"):
        isEligible = checkEligibility(applicationType,requestedSubjects)
        #isEligible = "true"
        if(isEligible):
            
            ##Save the student enrollment details in the db

            masterProgrammeEnrolled =[]
            masterProgrammeEnrolled.append(mastersProgramme)
            stuEmailId = "saumya.bhasin@sjsu.edu"
            enrollmentStatus = 'Active'
            #saveDetailsToDB(masterProgrammeEnrolled, stuEmailId, enrollmentStatus)


            ##student's email id to be fetched from his login session request
            toaddr = userEmail
            #send notification mail to the student from the dept chair
            #sendNotificationMail(stuEmailId,"true",masterProgrammeEnrolled)
            
        else:
            sendNotificationMail(stuEmailId,"false",masterProgrammeEnrolled)

    else:
        mapSubRequestedToEligibilityMap,mapEligibleSubToProfMail = checkEligibility(applicationType,requestedSubjects)
        print "Subject Enrollment eligibility satisfied= ",mapSubRequestedToEligibilityMap
        print "Subject Enrollment eligibile subjects professor details= ",mapEligibleSubToProfMail


        eligibleCoursesList = []
        eligibleCourseProfMailList = []
        #--- WRITE CODE FOR SAVING THE ELEIGIBLE COURSES INFO IN DB AND ALSO SEND MAIL TO RESPECTIVE PROF AND STUDENT

        #Finding eligible courses with true condition
        for courseName,isEleigible in mapSubRequestedToEligibilityMap.items():
            print courseName, 'corresponds to',isEleigible
            if(isEleigible):
                eligibleCoursesList.append(courseName)

        #finding eligible courses' prof details     
        for key in mapEligibleSubToProfMail.keys():
            for eligibleCourse in eligibleCoursesList:
                if(eligibleCourse==key):
                    eligibleCourseProfMailList.append(mapEligibleSubToProfMail[key])
                    
        print eligibleCoursesList
        print eligibleCourseProfMailList

        if(len(eligibleCoursesList)>0):
            if(len(eligibleCourseProfMailList)>0):
                for i in range(len(eligibleCourseProfMailList)):
                    if(eligibleCourseProfMailList[i]=='sithu.aung@sjsu.edu'):
                        #send mail to that prof
                        profEmail = eligibleCourseProfMailList[i]
                        #sendNotificationMail(profEmail,"true", eligibleCoursesList)

            #send mail to the student
            stuEmail = userEmail
            #sendNotificationMail(stuEmail, "true", eligibleCoursesList)             
                        
   


    return 'Success..Please check your mail box for enrollment eligibility!'

def saveDetailsToDB(masterProgrammeEnrolled, stuEmailId, enrollmentStatus):
    conn = sqlite3.connect('EnrollmentDetailsDB.sqlite')
    c = conn.cursor()
    #c.execute("INSERT INTO EnrollmentDetailsDB (stu_emailID, degree_enrolled, enrollmentStatus) \
    #  VALUES ("stuEmailId", masterProgrammeEnrolled , enrollmentStatus )");

    c.execute('''INSERT INTO EnrollmentDetailsDB(stu_emailID, degree_enrolled, enrollmentStatus)
                  VALUES(?,?,?)''', (stuEmailId,masterProgrammeEnrolled, enrollmentStatus))

    print "Enrollment Data inserted !!"  
    # Committing changes and closing the connection to the database file
    conn.commit()
    conn.close()

def sendNotificationMail(toaddr,isEligible, coursesList):
    # Connecting to the database file
    conn = sqlite3.connect('CheckSyatemDB.sqlite')
    c = conn.cursor()

    c.execute('SELECT * FROM emailDB')
    dbRecordTuple = c.fetchone()
    emailId = dbRecordTuple[0]
    print emailId
    ##check systems email id is fetched from email.properties file
    checkSystemEmailAddr = dbRecordTuple[0]
    checkSystemEmailPwd = dbRecordTuple[1]

    ##student's email id to be fetched from his login session request
    ##toaddr = "shraddha.yeole@sjsu.edu"
    msg = MIMEMultipart()
    msg['From'] = checkSystemEmailAddr
    msg['To'] = toaddr
    msg['Subject'] = "Prerequisite Check System"
    
    ##fetching this flag from DB for that particular student
    if(isEligible):
        if(len(coursesList)>0):
            bodyStr = "You are enrolled successfully for below courses :" ,coursesList
            body = bodyStr
        else:
            body = "You Are Enrolled Successfully for the master's programmes ", coursesList
    else:
        body = "Sorry..You do not match the eligibility criteria!!"
               
    
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(checkSystemEmailAddr, checkSystemEmailPwd)
    text = msg.as_string()
    server.sendmail(checkSystemEmailAddr, toaddr, text)
    server.quit()

    # Committing changes and closing the connection to the database file
    conn.commit()
    conn.close()
    

def checkEligibility(applicationType,requestedSubjects):
    file = open('output.txt', 'r')
    extractedString = file.read()
    extractedString = str(extractedString)
    lstTranscriptLines = extractedString.splitlines()
    #print 'lstTranscriptLines= ', lstTranscriptLines
    #print ' # of lines in transcripts= ', len(lstTranscriptLines)
    if(applicationType!='' and applicationType == "Masters"):
        eligible=checkMastersEligibility(lstTranscriptLines);
        print "MASTERs eligibility satisfied= ",eligible
        return eligible
    elif(applicationType!='' and applicationType == "Subject Enrollment" and len(requestedSubjects) > 0):
        mapSubRequestedToEligibilityMap,mapEligibleSubToProfMail=checkSubEnrollmentEligibility(lstTranscriptLines,requestedSubjects);
        print "Subject Enrollment eligibility satisfied= ",mapSubRequestedToEligibilityMap
        print "Subject Enrollment eligibile subjects professor details= ",mapEligibleSubToProfMail
        return  mapSubRequestedToEligibilityMap,mapEligibleSubToProfMail





#Master's application pre-requisite check usecase
def checkMastersEligibility(lstTranscriptLines):
    # Read the conditions file
    with open('mastersApplicationConditions.json') as data_file:
        conditionsData = json.load(data_file)
    #print 'conditions data = ', conditionsData

    # Get data from extracted transcript string
    overallConditionSatisfied = 'true'
    for line in lstTranscriptLines:
        if line.lower().strip().find('university') > -1:
            university = line.strip()
            print '******university found ', university

        if(conditionsData['minGPA']!=''):
            overallConditionSatisfied = 'false'
            if line.lower().strip().find('semester credits') > -1:
                #var = line.partition('Semester Credits')[2]
                var = line.lower().partition('semester credits')[2]
                print" var = ", var
                if var.lower().find('gpa') > 0:
                    finalGPA = var.partition('gpa')[2]
                    finalGPA = re.findall(r"(\d+\.\d+)", finalGPA)[0]
                    print '********finalGPA= ', finalGPA
                    finalCredits = var.partition('gpa')[0]
                    finalCredits = finalCredits.strip()
                    finalCredits = re.findall(r"(\d+\.\d+)", finalCredits)[0]
                    print '*****finalCredits= ', finalCredits
                    if(float(finalGPA) >= float(conditionsData['minGPA'])):
                        overallConditionSatisfied = 'true'
                        break
    print "Overall GPA conditions satisfied = ",overallConditionSatisfied

    if(overallConditionSatisfied == "true"):
         # Get the subject conditions for student
        subjectConditions = conditionsData['subjects']
        #print 'conditions data of subjects = ', subjectConditions

        # Check if student satisfies subject conditions
        subjectConditionSatisfied = 'true'
        if subjectConditions != '':
            #subjectConditionSatisfied = 'false'
            for i in range(0, len(subjectConditions)):
                #If subject condition fails for any subject,skip checking conditions for other subjects
                if i != 0 and subjectConditionSatisfied != 'true':
                    break
                #print '***checking conditions for subject=', subjectConditions[i]['name']
                # Reinitialize subjectConditionsSatisfied boolean for each subject
                subjectConditionSatisfied = 'false'

                for line in lstTranscriptLines:
                    print "line= ",line
                    # Check if line contains the subject
                    if line.decode('utf-8').lower().strip().find(subjectConditions[i]['name'].lower()) > -1:
                        # If required, check the credits in this subject
                        if(subjectConditions[i]['mincredits'] != ""):
                            # Find floting number
                            credits = re.findall(r"(\d+\.\d+)", line)[0]
                            #print '****credtis in subject ', \
                            #    subjectConditions[i]['name'], 'are', float(credits)
                            if(float(credits)!='' and float(credits)!='undefined' and float(credits) >= float(subjectConditions[i]['mincredits'])):
                                subjectConditionSatisfied = 'true'
                        else:
                            subjectConditionSatisfied = 'true'
                #print "***Conditions satisfied for subject= ", subjectConditionSatisfied
            print "All Subject conditions satisfied= ", subjectConditionSatisfied
            if(subjectConditionSatisfied == 'true'):
                return "true"
    else: #Overall conditions not satisfied
        return "false"

#Subject Enrollment pre-requisite check usecase
def checkSubEnrollmentEligibility(lstTranscriptLines,requestedSubjects):
    print "subjects requested for Enrollment= ", requestedSubjects
    #Map of subjects requested to eligibility satisfied
    mapSubRequestedToEligibilityMap={}
    for reqSub in requestedSubjects:
        mapSubRequestedToEligibilityMap[reqSub]=''
    #Map of eligible subject and professor email
    mapEligibleSubToProfMail={}

    # Read the subjectEnrollmentConditions file
    with open('subjectEnrollmentConditions.json') as data_file:
        conditionsData = json.load(data_file)
    print 'conditions data = ', conditionsData
    # Get the subject conditions for student
    subjectConditions = conditionsData['subjects']

    #check if subjects requested for Enrollment have pre-requisities
    # Read the info file
    with open('info.json') as data_file:
        infoData = json.load(data_file)
    print 'info data = ', infoData
    if(infoData!='' and len(infoData) > 0):
        for requestedSub in requestedSubjects:
            mapSubRequestedToEligibilityMap[requestedSub]='false'
            print "checking eligibility for requested subject ", requestedSub
            #check if requested sub has pre-requisite
            prereqCourses = checkPrereqRequired(requestedSub,infoData['subjects'])
            print "requested subject %s has pre-requisites %s" %(requestedSub,prereqCourses)
            if(prereqCourses != ""):
                #check if student satisfies conditions for pre-requisite courses
                lstPrereq=prereqCourses.split(",")
                for prereq in lstPrereq:
                    prereqSatisfied = checkIfPrereqSatisfied(lstTranscriptLines,prereq,subjectConditions)
                    print "prereq %s satisfied = %s" %(prereq,prereqSatisfied)
                    mapSubRequestedToEligibilityMap[requestedSub]=prereqSatisfied
            else: #Requested subject has no pre-requisities
                mapSubRequestedToEligibilityMap[requestedSub]='true'
    else: #No pre-requisite data defined in info.json
        for reqSub in mapSubRequestedToEligibilityMap.keys():
            mapSubRequestedToEligibilityMap[reqSub]='true'

    mapEligibleSubToProfMail=getProfDetails(mapSubRequestedToEligibilityMap,infoData['subjects'])
    return mapSubRequestedToEligibilityMap,mapEligibleSubToProfMail

def checkPrereqRequired(requestedSub,infoDataSubjects):
    for infoSub in infoDataSubjects:
        if(infoSub["courseName"].lower() == requestedSub.lower() and infoSub["prereqCourses"]!=''):
            return infoSub["prereqCourses"]
    return ""

def checkIfPrereqSatisfied(lstTranscriptLines,prereqCourseName,subjectConditions):
    print "checking pre-requisite %s in transcript " %(prereqCourseName)
    for line in lstTranscriptLines:
        # Check if line contains the subject
        if line.decode('utf-8').lower().strip().find(prereqCourseName.lower()) > -1:
            print "prereq found in transcript in line " , line
            #Get the mingrades condition for the prereq from subjectEnrollmentConditions file
            for i in range(0,len(subjectConditions)):
                if(subjectConditions[i]['courseName'].lower() == prereqCourseName.lower()):
                    if(subjectConditions[i]['mingrades']!=''):
                        minGradeInInt=gradeToIntMap.get(subjectConditions[i]['mingrades'].strip())
                        print "minGradeInInt= ", minGradeInInt
                        #Get the grade obtained by student from the current line
                        lst=line.decode('utf-8').strip().split(" ")
                        lst1 = str(lst).encode('utf-8')
                        print "lst= ", lst[len(lst)-2]
                        #if(str(lst1).__contains__('A')):
                            #gradeObtained = 'A'
                        gradeObtained = lst[len(lst)-2]
                        print gradeObtained
                        if(gradeObtained!=''):
                            gradeObtainedInt=gradeToIntMap.get(gradeObtained.strip())
                            print "gradeObtainedInt = ",gradeObtainedInt
                            if(gradeObtainedInt!='' and minGradeInInt!=''):
                                if(gradeObtainedInt >= minGradeInInt):
                                    print "mingrades condition satisfied for prereqCourseName ", prereqCourseName
                                    #mapEligibleSubToProfMail[]=
                                    return 'true'
                                else:
                                    return 'false'
                            else:
                                #some problem in determining grades
                                return 'true'
                    else:
                        return 'true'
            #subjectEnrollmentConditions file does not have record for the pre-requisite subject
            return 'true'

    #pre-req subject not found in students transcript
    return 'false'

def getProfDetails(mapSubRequestedToEligibilityMap,infoDataSubjects):
    mapEligibleSubToProfMail={}
    print "Req sub map" , mapSubRequestedToEligibilityMap
    for reqSub in mapSubRequestedToEligibilityMap.keys():
        print "Req subject ", reqSub
        if(mapSubRequestedToEligibilityMap[reqSub]!='' and mapSubRequestedToEligibilityMap[reqSub]=='true'):
            for infoSub in infoDataSubjects:
                print "Inside info for loop", infoSub["profEmail"]

                if(infoSub["courseName"].lower() == reqSub.lower() and infoSub["profEmail"]!=''):
                    mapEligibleSubToProfMail[reqSub]=infoSub["profEmail"]

    return mapEligibleSubToProfMail

if __name__ == '__main__':
    app.run(port=4557, debug=True)
    

    
