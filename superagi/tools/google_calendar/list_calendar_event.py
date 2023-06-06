import os
import datetime
from typing import Type
from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field
from superagi.config.config import get_config
from googleapiclient.discovery import build
from superagi.helper.google_calendar_creds import GoogleCalendarCreds

class ListCalendarEventInput(BaseModel):
    number_of_results: int = Field(..., description="The number of events to get from the calendar, default value is 100.")
    start_date: str = Field(..., description="The start date to return events from the calendar in format 'yyyy-mm-dd'. default value is 'None'")

class ListCalendarEventTool(BaseTool):
    name: str = "Get Calendar Event"
    args_schema: Type[BaseModel] = ListCalendarEventInput
    description: str = "Get the information of all the events from Google Calendar"

    def _execute(self, number_of_results: int, start_date: str):
        credentials_file = get_config('PATH_TO_FILE')
        service = GoogleCalendarCreds().get_credentials(credentials_file)
        if start_date == 'None':
            start_date = datetime.date.today()
        elif isinstance(start_date, str):
            start_date = datetime.date.fromisoformat(start_date)
        
        start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
        start_datetime_utc = start_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        event_results = (
            service.events().list(
            calendarId = "primary",
            timeMin = start_datetime_utc,
            maxResults=number_of_results,
            singleEvents = True,
            orderBy = "startTime"
            ).execute()
        )
        events = event_results.get("items", [])
        print(events)
        return events



    