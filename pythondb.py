import json
import re
import copy

import simpleFileManager as files

from errors import *

def doNothing(*args, **kwargs):
    pass

def createDatabase(name, uniqueFields=[], nonUniqueFields=[], rows=[]):
    # (public)
    # NOT TESTED
    print('Warning! this function has not been tested. Use at your own risk!')

    db = {
        'name' : name,
        'uniqueFields' : copy.deepcopy(uniqueFields),
        'nonUniqueFields' : copy.deepcopy(nonUniqueFields),
        'rows' : []
    }
    # Add the rows here one by one, to use the inbuilt error checker in appendRow()
    for row in rows:
        appendRow(db, copy.deepcopy(row))
    return db

# File stuff
# ----------

def openDatabase(filename):
    # Open and load the database at filename, return it as an object

    # Read the file

    # This try-except-finally is not needed as of now
    # as the only error which is expected doesn't get caught,
    # but it will make for easier modification in future

    stringData = '{}' # safeguard in case there is a case which slips through
    try:
        stringData = files.read(filename)
    # no except block - let whatever error has occured break out of this function
    # a finally block is needed here to make syntax correct
    finally:
        pass
    
    # Parse the file

    try:
        database = json.loads(stringData)
        return database
    except json.decoder.JSONDecodeError as err:
        raise FileCorrupted from err

def saveDatabase(database, filename=None):
    # Save the database to filename
    # If filename is None, then it will be saved to: [the name of the database] + 'json'

    if filename is None:
        filename = database['name'] + '.json'
    try:
        databaseStr = json.dumps(database)
        files.write(filename, databaseStr)
    except json.encoder.JsonEncodeError as err:
        raise DatabaseObjectCorrupted from err

# Get stuff
# ---------

def getDatabaseName(database):
    # (public)
    return database['name']

def fieldPathToDirectoryList(fieldPath):
    # Turn the field path into a list of directions
    # (private)

    return re.split('(?<!\\\)[/]', fieldPath)

def getFieldContents(row, fieldPath=None, directoryList=None):
    # Get the contents of the field at fieldPath in row
    # Pass in either a fieldPath or a directoryList
    # (public)
    try:
        if directoryList is None:
            directoryList = fieldPathToDirectoryList(fieldPath)
        crntDir = row
        for item in directoryList:
            crntDir = crntDir[item]
        return crntDir
    except Exception as err:
        raise InvalidFieldPath from err

def getColumn(database, fieldPath):
    # Get a list of all of the items in the fieldPath column
    # (public)
    if (fieldPath not in database['uniqueFields']) and \
        (fieldPath not in database['nonUniqueFields']):
        raise InvalidFieldPath

    column = []
    for crntRow in database['rows']:
        column.append(getFieldContents(crntRow, fieldPath=fieldPath))
    
    return column

def getRowByUniqueField(database, fieldPath, fieldValue):
    # Find the row which has fieldPath set to fieldValue
    # (public)

    # If the field doesn't exist, exit
    if fieldPath not in database['uniqueFields']:
        raise InvalidFieldPath

    row = None

    for crntRow in database['rows']:
        if getFieldContents(crntRow, fieldPath=fieldPath) == fieldValue:
            row = crntRow
            break
    
    return row

        
def getRowsByField(database, fieldPath, fieldValue):
    # Find all of the fields in which fieldPath is set to fieldValue
    # (public)
    
    # If the field doesn't exist, exit
    if fieldPath not in database['nonUniqueFields']:
        raise InvalidFieldPath

    rows = []
    for crntRow in database['rows']:
        if getFieldContents(crntRow, fieldPath) == fieldValue:
            rows.append(crntRow)
    
    return rows

# Set stuff
# ---------

def setDatabaseName(database, newName):
    # (public)
    database['name'] = newName

def setFieldValue(database, row, fieldPath, fieldValue):
    # (public)
    # set the value of the field at row in database
    if fieldPath in database['uniqueFields']:
        existingValues = getColumn(database, fieldPath)
        if fieldValue in existingValues:
            raise FieldDuplicated
        else:
            # Navigate to the dir containing the field
            directoryList = fieldPathToDirectoryList(fieldPath)
            containingDir = getFieldContents(row, directoryList=directoryList[:-1])
            # Then set the last part (the actual field) to the value
            containingDir[directoryList[-1]] = fieldValue
            
    elif fieldPath in database['nonUniqueFields']:
        directoryList = fieldPathToDirectoryList(fieldPath)
        containingDir = getFieldContents(row, directoryList=directoryList[:-1])
        containingDir[directoryList[-1]] = fieldValue
    else:
        raise InvalidFieldPath

# Add stuff
# ---------

def createRow(database, rowContents):
    # Row contents is in the form:
    # {
    #   fieldPath : value,
    # }
    # eg:
    # {
    #   'username' : 'james',
    #   'password' : 123
    # }
    # Note that this does not add the row to the database, use appendRow() for that
    # (public)

    row = {}
    # Set the keys and values of the row object
    for fieldSet in rowContents:
        fieldPath, value = fieldSet
        print(fieldPath, value)

        # Check if the fieldPath is a valid field
        if fieldPath in database['uniqueFields'] or \
            fieldPath in database['nonUniqueFields']:
            setFieldValue(database, row, fieldPath, value)
        else:
            raise InvalidFieldPath
    
    # Now check if the row has any duplicate unique fields
    if not canAddRow(database, row):
        raise FieldDuplicated
    
    return row

def appendRow(database, row):
    # Append the row to the database
    # (public)
    
    if canAddRow(database, row):
        database['rows'].append(row)
    else:
        raise FieldDuplicated

# Other
# -----

def canAddRow(database, row):
    # Check whether the values any of the row's unique fields are already in the database
    # (private)

    duplicateFieldFound = False
    for fieldPath in database['uniqueFields']:
        column = getColumn(database, fieldPath)
        if getFieldContents(row, fieldPath=fieldPath) in column:
            duplicateFieldFound = True
            break
    
    return duplicateFieldFound
