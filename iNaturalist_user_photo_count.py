# Alex Abair, 2022-06-02
# This script takes an iNaturalist username as input and generates some stats about their photos.
# It gives a total number of photos uploaded by a user (if they haven't made over 10,000 observations).
# It also gives you the averaage number of photos per observation and the rate of photo uploads over days, weeks, months, and years.

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

# Select and validate an iNaturalist username

url = 'https://api.inaturalist.org/v1/users/'

def validateUsername(urlBase):
        print('\n  Type a username, or type "q" to quit:\n')
        username = input('  ')
        if username == 'q':
                print('\n  Goodbye...\n')
                quit()
        serviceurl = urlBase + username
        controlurl = urlBase + 'alex_abair'
        while str(requests.get(serviceurl)) != str(requests.get(controlurl)):
                print('\n\n  That username was invalid. Try another or type "q" to quit:\n')
                username = input('  ')
                if username == 'q':
                        print('\n  Goodbye...\n')
                        quit()
                else :
                        serviceurl = urlBase + username
        serviceurl = urlBase + username
        uh = urllib.request.urlopen(serviceurl)
        data = uh.read().decode()
        js = json.loads(data)
        totalObs = js['results'][0]['observations_count']
        if totalObs != 0:
                return username
        else:
                print(f'\n  That user has no observations.', end='')
                return 'noObservationsMade'

iNatUser = validateUsername(url)
if iNatUser == 'noObservationsMade':
        validateUsername(url)

print(('\n\n  Collecting infomation about iNaturalist user @' + iNatUser + '.\n  View their profile here: https://www.inaturalist.org/people/' + iNatUser + '\n\n'))

# Get total page number
serviceurl = url + iNatUser
uh =  urllib.request.urlopen(serviceurl)
data = uh.read().decode()
js = json.loads(data)
totalObs = (str(js['results'][0]['observations_count']))
if int(totalObs) > 10000:
        print("  The user @" + iNatUser + " has made over 10,000 observations.\n  Stats will be generated for the first 10,000 observations.")
        totalObs = 9999
totalPageNum = int(totalObs) // 200 + 1

# Get the number of observations on the last page
lastPageObs = int(totalObs) % 200

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

fileName = iNatUser + '_iNat_photo_stats_' + str(date.today()) + '.txt';
with open(fileName, 'w') as f:
    f.write('Infomation about photo upload rate by iNaturalist user @' + iNatUser + '.\nView their profile here: https://www.inaturalist.org/people/' + iNatUser + '\n\nThe user @' + iNatUser + ' submitted ' + str(photoCount) + ' photos to iNaturalist.org as of ' + str(date.today()) + ".\nThey've made " + str(totalObs) + ' observations with an average of ' + str(avePhotosPerObservation) + ' photos per observation.\n@' + iNatUser + ' has uploaded an average of ' + photosPerDay + ' photos per day since ' + userStartDate + '.\n')

print('  Results written to ' + fileName + '.')

results1 = "\n\n  The user @" + iNatUser + " submitted " + str(photoCount) + " photos to iNaturalist.org as of " + str(date.today()) + "."
results2 = "\n  They've made " + str(totalObs) + " observations with an average of " + str(avePhotosPerObservation) + " photos per observation."
if str(avePhotosPerObservation) == '1.00':
        results2 = "\n  They've made " + str(totalObs) + " observations with an average of one photo per observation."
if totalObs == 10000:
        results2 = "\n  For their last 10,000 observations, they've averaged " + str(avePhotosPerObservation) + " photos per observation."
results3 = "\n  @" + iNatUser + " has uploaded an average of " + photosPerDay + " photos per day since " + userStartDate + ".\n\n\n\n\n"
if int(str(photosPerDay)[0]) == 0:
        results3 = "\n  @" + iNatUser + " has uploaded an average of " + photosPerWeek + " photos per week since " + userStartDate + ".\n\n\n\n\n"
        if int(str(photosPerWeek)[0]) == 0:
                results3 = "\n  @" + iNatUser + " has uploaded an average of " + photosPerMonth + " photos per month since " + userStartDate + ".\n\n\n\n\n"
                if int(str(photosPerMonth)[0]) == 0:
                        results3 = "\n  @" + iNatUser + " has uploaded an average of " + photosPerYear + " photos per year since " + userStartDate + ".\n\n\n\n\n"
                        if int(str(photosPerYear)[0]) == 0:
                                results3 = "\n  @" + iNatUser + " has uploaded less than one photo per year since " + userStartDate + ".\n\n\n\n\n"

fileName = iNatUser + '_iNat_photo_stats_' + str(date.today()) + '.txt';
with open(fileName, 'w') as f:
        f.write('Infomation about photo upload rate by iNaturalist user @' + iNatUser + '.\nView their profile here: https://www.inaturalist.org/people/' + iNatUser + '. ' + results1 + results2 + results3 )

print(results1, results2, results3)

