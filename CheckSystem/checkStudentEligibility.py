import json
import re

gradeToIntMap={'C-':1,'C':1.1,'C+':1.2,'B-':1.3,'B':1.4,'B+':1.5,'A-':1.6,'A':1.7,'A+':1.8}

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
    elif(applicationType!='' and applicationType == "Subject Enrollment" and len(requestedSubjects) > 0):
        mapSubRequestedToEligibilityMap,mapEligibleSubToProfMail=checkSubEnrollmentEligibility(lstTranscriptLines,requestedSubjects);
        print "Subject Enrollment eligibility satisfied= ",mapSubRequestedToEligibilityMap
        print "Subject Enrollment eligibile subjects professor details= ",mapEligibleSubToProfMail

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
                var = line.partition('Semester Credits')[2]
                print" var = ", var
                if var.lower().find('gpa') > 0:
                    finalGPA = var.partition('GPA')[2]
                    finalGPA = re.findall(r"(\d+\.\d+)", finalGPA)[0]
                    print '********finalGPA= ', finalGPA
                    finalCredits = var.partition('GPA')[0]
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
                    #print "line= ",line
                    # Check if line contains the subject
                    if line.lower().strip().find(subjectConditions[i]['name'].lower()) > -1:
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
        if line.lower().strip().find(prereqCourseName.lower()) > -1:
            print "prereq found in transcript in line " , line
            #Get the mingrades condition for the prereq from subjectEnrollmentConditions file
            for i in range(0,len(subjectConditions)):
                if(subjectConditions[i]['courseName'].lower() == prereqCourseName.lower()):
                    if(subjectConditions[i]['mingrades']!=''):
                        minGradeInInt=gradeToIntMap.get(subjectConditions[i]['mingrades'].strip())
                        print "minGradeInInt= ", minGradeInInt
                        #Get the grade obtained by student from the current line
                        lst=line.strip().split("\t")
                        print "lst= ", lst
                        gradeObtained = lst[len(lst)-2]
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
    for reqSub in mapSubRequestedToEligibilityMap.keys():
        if(mapSubRequestedToEligibilityMap[reqSub]!='' and mapSubRequestedToEligibilityMap[reqSub]=='true'):
            for infoSub in infoDataSubjects:
                if(infoSub["courseName"].lower() == reqSub.lower() and infoSub["profEmail"]!=''):
                    mapEligibleSubToProfMail[reqSub]=infoSub["profEmail"]

    return mapEligibleSubToProfMail

if __name__ == '__main__':
    #applicationType = "Subject Enrollment"
    applicationType = "Masters"
    #list of subjects requested for Enrollment in case of applicationType "Subject Enrollment"
    #requestedSubjects=["CMPE 273","CMPE 281"]
    requestedSubjects=[]
    checkEligibility(applicationType,requestedSubjects)
