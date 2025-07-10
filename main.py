import datetime as dt
import time
import psutil
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle
import pygetwindow as gw

# --- Google Calendar API Setup ---
SCOPES = ['https://www.googleapis.com/auth/calendar'] # Scope for full calendar access

def get_calendar_service():
    """Shows basic usage of the Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES) # Use your credentials file
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

def create_calendar_event(service, vs_start_time, vc_end_time, summary, description=''):
    """Creates an event in the Google Calendar."""
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': vs_start_time.isoformat(), # Use datetime.datetime.now().isoformat()
            'timeZone': 'America/New_York',  # Replace with your time zone (e.g., 'America/New_York')
        },
        'end': {
            'dateTime': vc_end_time.isoformat(), # Use datetime.datetime.now().isoformat()
            'timeZone': 'America/New_York', # Replace with your time zone
        },
    }

    # event = service.events().insert(calendarId='primary', 
    #                                 body=event).execute()
    # print(f'Event created: {event.get("htmlLink")}') # Print link to the event
    print("Attempting to create event with data:", event)  # Debug output
    try:
        event = service.events().insert(calendarId='95404927e95a53c242ae33f7ee860677380fba1bbc9c82980a9e9452e29388d1@group.calendar.google.com',
                                         body=event).execute()
        print(f'Event created: {event.get("htmlLink")}')
    except Exception as e:
        print(f"Failed to create event: {e}")

# --- Process Tracking Logic ---
def is_vscode_running():
    """Checks if any VS Code-related process is running."""
    for proc in psutil.process_iter(['name']):
        name = proc.info['name']
        if name and 'code' in name.lower():
            print("VS Code process detected:", name)
            return True
    return False

def leetcode_in_use(site_name):
    #active = gw.getActiveWindow()
    for title in gw.getAllTitles():
        if site_name.lower() in title.lower(): #Getting the characters to see if the website matches the parameter
            print(f"LeetCode is seen to be in use in: {title}")
            return True
    return False

def is_arduino_running():
    for proc in psutil.process_iter(['name']):
        name = proc.info['name']
        if name and 'arduino' in name.lower():
            print("Arduino is seen", name)
            return True
    return False


if __name__ == '__main__':
    service = get_calendar_service()  # Get Google Calendar service object

    is_vs_running = False
    vs_start_time = None

    is_lc_running = False
    lc_start_time = None

    is_arduino_IDE_running = False
    arduino_start_time = None


    while True:
        if is_vscode_running():
            if not is_vs_running:  # VS Code started running
                is_vs_running = True
                vs_start_time = dt.datetime.now() # Get current time
                print("VS Code started.")
        else:
            if is_vs_running:  # VS Code stopped running
                is_vs_running = False
                vc_end_time = dt.datetime.now() # Get current time
                print("VS Code stopped.")
                if vs_start_time:
                    create_calendar_event(service, vs_start_time, vc_end_time, 'Code Session') # Create event in Google Calendar
                    vs_start_time = None # Reset start time

        if leetcode_in_use('leetcode'):
            if not is_lc_running: #Checking if LeetCode start running
                is_lc_running = True
                lc_start_time = dt.datetime.now()
                print("LeetCode has been opened")
        else:
            if is_lc_running: #Checked that LeetCode was closed
                is_lc_running = False
                lc_end_time = dt.datetime.now()
                print("LeetCode was closed")
                if lc_start_time:
                    create_calendar_event(service, lc_start_time, lc_end_time, 'LeetCode Practice')
                    lc_start_time = None
        
        if is_arduino_running():
            if not is_arduino_IDE_running:
                is_arduino_IDE_running = True
                arduino_start_time = dt.datetime.now()
                print("Arduino has been opened")
        else:
            if is_arduino_IDE_running:
                is_arduino_IDE_running = False
                arduino_end_time = dt.datetime.now()
                print("Arduino has been closed")
                if arduino_start_time:
                    create_calendar_event(service, arduino_start_time, arduino_end_time, 'Electronics Session')
                    arduino_start_time = None

                

        time.sleep(60) # Check every 60 seconds (adjust as needed)
    
    # service = get_calendar_service()
    # now = dt.datetime.now()
    # later = now + dt.timedelta(minutes=5)
    # create_calendar_event(service, now, later, 'Test Event', 'This is a test event')