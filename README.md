# CMPE273Project-Prerequisite-Check-System

#### Requirements

Uploading the sample data or template with fields to be extracted.
Capturing with screenshot using a solution like html2canvas
Send the submission confirmation email and store the data into database.


#### Abstract

We have built a pre-requisite check system using Python-tesseract tool.
This check systems performs OCR on the transcript uploaded and extracts required fields from it.
The system performs student eligibilty check and stores the details in database if he satisfies the enrollment eligibility.
The system then sends an email notification to the student and professor if he/she is eligible for enrollment. 

#### Use Cases:
Master's Enrollment
Semester Enrollment

#### Tools -

##### 1.Pytesseract :
    Python-tesseract is an optical character recognition (OCR) tool for python.
    That is, it will recognize and "read" the text embedded in transcript.
    
##### 2.HTMLtoCanvas:
    This javascript allows to take "screenshots" of transcript or parts of it, directly on the users browser.   
    
##### 3.Flask:
    Flask web microframework for building Pre-requisite Check web application with Python.
 
##### 4.SQLite Database
