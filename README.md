# CMPE273Project-Prerequisite-Check-System

Requirements

Uploading the sample data or template with fields to be extracted.
Capturing with screenshot using a solution like html2canvas
Send the submission confirmation email and store the data into database.


Abstract

We will be building a pre-requisite check system using Python-tesseract tool.
This check systems performs OCR on the transcript image uploaded and extracts required texts from it.
The system performs student eligibilty check of his GPA and store the details in database if he satisfies the enrollment eligibility.
The system then send the email notification if the student is successfully enrolled. 


Tools -

1.pytesseract :
    Python-tesseract is an optical character recognition (OCR) tool for python.
    That is, it will recognize and "read" the text embedded in transcript.
2.HTMLtoCanvas:
    This javascript allows to take "screenshots" of transcript or parts of it, directly on the users browser.    
3.Flask:
    Flask web microframework for building Pre-requisite Check web application with Python.

