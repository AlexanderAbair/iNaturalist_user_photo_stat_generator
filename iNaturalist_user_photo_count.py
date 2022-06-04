# Importing packages
import os
import urllib.request, urllib.parse, urllib.error
import json
import pandas as pd
from datetime import date
import re
import requests
from dateutil import parser
import time

print('\n\n\n  --COUNTING THE NUMBER OF PHOTOS UPLOADED BY AN INATURALIST USER--')

# Select and validaate the iNaturalist user

url = 'https://api.inaturalist.org/v1/users/'
usernameStatus = 'needsInput'

def validateUsername(username):
        if username == 'q':
                print('\n  Goodbye...\n')
                quit()
        serviceurl = url + username
        controlurl = url + 'alex_abair'
        if str(requests.get(serviceurl)) != str(requests.get(controlurl)):
                print('\n\n  That username was invalid. Try another or type "q" to quit:\n')
                username = input('  ')
                if username == 'q':
                        print('\n  Goodbye...\n')
                        quit()
                else :
                        return 'invalid'
        serviceurl = url + username
        uh = urllib.request.urlopen(serviceurl)
        data = uh.read().decode()
        js = json.loads(data)
        totalObs = js['results'][0]['observations_count']
        if totalObs != 0:
                return 'valid'
        else:
                print(f'\n  That user has no observations.', end='')
                return 'invalid'

if usernameStatus == 'needsInput':
        iNatUser = input('\n  Type a username, or type "q" to quit:\n\n  ')
        usernameStatus = validateUsername(iNatUser)
while usernameStatus == 'invalid':
        iNatUser = input('\n  Type a different username, or type "q" to quit:\n\n  ')
        usernameStatus = validateUsername(iNatUser)

print(('\n\n  Collecting infomation about iNaturalist user @' + iNatUser + '.\n  View their profile here: https://www.inaturalist.org/people/' + iNatUser + '\n\n'))

# Get total page number
serviceurl = url + iNatUser
uh =  urllib.request.urlopen(serviceurl)
data = uh.read().decode()
js = json.loads(data)
totalObs = (str(js['results'][0]['observations_count']))
totalPageNum = int(totalObs) // 200 + 1

# Get the number of observations on the last page
lastPageObs = int(totalObs) % 200

# Account for users with >10k observations. iNat has a request limit
if int(totalObs) >= 10000:
        print("  The user @" + iNatUser + " has made " + str(totalObs) + " observations.\n  Stats will be generated for the first 10,000 observations.")
        totalObs = 10000
        totalPageNum = 50
        lastPageObs = 50
        prolificUserObservationsCount = (str(js['results'][0]['observations_count']))
        promptResponse = input("  This will take a few minutes. Are you sure you sure you want to proceed? (y/n)\n  ")
        while promptResponse != 'clearedToProceed' :
                if promptResponse == 'n':
                        print('\n  Goodbye...\n\n\n\n')
                        quit()
                elif promptResponse == 'y':
                        print('\n  Ok! Be prepared to wait a few minutes.\n')
                        promptResponse = 'clearedToProceed'
                else:
                        promptResponse = input('\n  Invalid entry. Please enter either "y" or "n".\n  ')

# Get user's date of account creation
userStartDate = re.sub(r"T.*", "", js["results"][0]['created_at'])
accountAgeInDays = re.sub(r"\s.*", "", str(parser.parse(str(date.today())) - parser.parse(str(userStartDate))))

# Initialize and populate the photo count dictionary with the number of observations per page
photoCountDict = {k: 200 for k in range(1, int(totalPageNum))}
photoCountDict[totalPageNum] = lastPageObs

# Set up a loop to get counts from any observation with more than one photo. The number of additional photos is added to the page number dictionary

for pageNum in range(1, (int(totalPageNum) + 1)):
        serviceurl = 'https://api.inaturalist.org/v1/observations?user_id=' + iNatUser + '&per_page=200&page='  + str(pageNum)
        uh =  urllib.request.urlopen(serviceurl)
        data = uh.read().decode()
        jsString = json.dumps(json.loads(data))

        pagePhotoCount = 0
        for positionNum in range(1,20):
                photoPositionNum = str('"position": ') + str(positionNum)
                pagePhotoCount = jsString.count(photoPositionNum) + pagePhotoCount

        photoCountDict.update({pageNum : int(pagePhotoCount) + int(photoCountDict[pageNum])})

        # Visualizing search progress
        def completeness(completed, remaining, size=48):
                percentComplete = int(completed) / int(remaining)
                visualizedCompleteness = int(percentComplete * size - 1) * '-' + '>'
                visualizedRemainder = int(size - len(visualizedCompleteness)) * ' '
                ending = '\n' if completed == remaining else '\r'
                print(f'  Pages counted:  [{visualizedCompleteness}{visualizedRemainder}]  {completed}/{remaining}', end=ending)
        completeness(pageNum, totalPageNum)

# Determine total number of photos uploaded by user
photoCount = sum(photoCountDict.values())

# Calculate the average number of photos per observation
avePhotosPerObservationLongFloat = int(photoCount) / int(totalObs)
avePhotosPerObservation = "{:.2f}".format(avePhotosPerObservationLongFloat)

# Calculate the average number of photos uploaded per day
photosPerDayLongFloat = int(photoCount) / int(accountAgeInDays)
photosPerDay = "{:.2f}".format(photosPerDayLongFloat)
if (int(photoCount) // int(accountAgeInDays)) == 0:
        photosPerWeek = "{:.2f}".format(int(photoCount) / (int(accountAgeInDays) / 7 ))
        if str(photosPerWeek)[0] == '0':
                photosPerMonth = "{:.2f}".format(int(photoCount) / (int(accountAgeInDays) / 30 ))
                if str(photosPerMonth)[0] == '0':
                        photosPerYear = "{:.2f}".format(int(photoCount) / (int(accountAgeInDays) / 365 ))

fileName = iNatUser + '_iNat_photo_stats_' + str(date.today()) + '.txt'
print('  Results written to ' + fileName + '.')

results1 = "\n\n  The user @" + iNatUser + " submitted " + str(photoCount) + " photos to iNaturalist.org as of " + str(date.today()) + "."
if int(totalObs) >= 10000:
        results1 = "\n\n  The user @" + iNatUser + " submitted over " + str(prolificUserObservationsCount) + " observations to iNaturalist.org as of " + str(date.today()) + ".\n This script is not yet ready to handle such large requests but will be soon!"
results2 = "\n  They've made " + str(totalObs) + " observations with an average of " + str(avePhotosPerObservation) + " photos per observation."
if str(avePhotosPerObservation) == '1.00':
        results2 = "\n  They've made " + str(totalObs) + " observations with an average of one photo per observation."
if int(totalObs) >= 10000:
        results2 = "\n  This user uploaded" + str(photoCount) + "for their last 10k observations (" + str(avePhotosPerObservation) + ") per observation."
results3 = "\n  @" + iNatUser + " has uploaded an average of " + photosPerDay + " photos per day since " + userStartDate + ".\n\n\n"
if int(totalObs) >= 10000:
        results3 = "\n\n\n"
elif int(str(photosPerDay)[0]) == 0:
        results3 = "\n  @" + iNatUser + " has uploaded an average of " + photosPerWeek + " photos per week since " + userStartDate + ".\n\n\n"
        if int(str(photosPerWeek)[0]) == 0:
                results3 = "\n  @" + iNatUser + " has uploaded an average of " + photosPerMonth + " photos per month since " + userStartDate + ".\n\n\n"
                if int(str(photosPerMonth)[0]) == 0:
                        results3 = "\n  @" + iNatUser + " has uploaded an average of " + photosPerYear + " photos per year since " + userStartDate + ".\n\n\n"
                        if int(str(photosPerYear)[0]) == 0:
                                results3 = "\n  @" + iNatUser + " has uploaded less than one photo per year since " + userStartDate + ".\n\n\n"

if int(totalObs) >= 10000:
        with open(fileName, 'w') as f:
                f.write('\n  Infomation about photo upload rate by iNaturalist user @' + iNatUser + '.\n  View their profile here: https://www.inaturalist.org/people/' + iNatUser + '\n\n  The user @' + iNatUser + ' submitted ' + str(photoCount) + ' photos to iNaturalist.org as of ' + str(date.today()) + '.\n  This user uploaded' + str(photoCount) + 'photos for their last 10k observations (' + str(avePhotosPerObservation) + ' per observation.)\n\n\n')
else:
        with open(fileName, 'w') as f:
                f.write('\n  Infomation about photo upload rate by iNaturalist user @' + iNatUser + '.\n  View their profile here: https://www.inaturalist.org/people/' + iNatUser + '. ' + results1 + results2 + results3 )

print(results1, results2, results3)
