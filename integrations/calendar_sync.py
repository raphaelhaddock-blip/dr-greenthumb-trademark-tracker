#!/usr/bin/env python3
"""
Calendar integration for trademark renewal deadlines
Supports Google Calendar, Outlook, and iCal formats
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import os

class CalendarSync:
    """Sync trademark deadlines to calendar systems"""
    
    def __init__(self, trademarks_file="trademarks.json"):
        self.trademarks = self.load_trademarks(trademarks_file)
    
    def load_trademarks(self, file):
        """Load trademark data"""
        with open(file) as f:
            return json.load(f)
    
    def generate_ical(self, output_file="trademark_deadlines.ics"):
        """Generate iCalendar file for deadlines"""
        ical_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Dr. Greenthumb//Trademark Tracker//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:Trademark Deadlines
X-WR-TIMEZONE:America/Los_Angeles
X-WR-CALDESC:Dr. Greenthumb trademark renewal deadlines
"""
        
        for tm in self.trademarks:
            if tm['status'] != 'active':
                continue
            
            renewal_date = datetime.fromisoformat(tm['renewal_date'])
            
            # Create events at 90, 60, and 30 days before
            for days_before in [90, 60, 30, 7]:
                alert_date = renewal_date - timedelta(days=days_before)
                
                event = self._create_event(
                    tm,
                    alert_date,
                    f"{days_before}-day reminder"
                )
                ical_content += event
            
            # Create event for actual deadline
            deadline_event = self._create_event(
                tm,
                renewal_date,
                "RENEWAL DEADLINE"
            )
            ical_content += deadline_event
        
        ical_content += "END:VCALENDAR"
        
        with open(output_file, 'w') as f:
            f.write(ical_content)
        
        print(f"✅ Calendar file created: {output_file}")
        print(f"   Import this into Google Calendar, Outlook, or Apple Calendar")
        return output_file
    
    def _create_event(self, trademark, event_date, event_type):
        """Create iCalendar event"""
        uid = f"{trademark['id']}-{event_type.replace(' ', '-')}@drgreenthumbtm.com"
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
        event_date_str = event_date.strftime("%Y%m%d")
        
        summary = f"TM: {trademark['name']} - {event_type}"
        description = f"""Trademark: {trademark['name']}
Jurisdiction: {trademark['jurisdiction']}
Renewal Date: {trademark['renewal_date']}
Registration: {trademark.get('registration_number', 'N/A')}

Action: Review renewal requirements and prepare filing

View in tracker: https://github.com/raphaelhaddock-blip/dr-greenthumb-trademark-tracker"""
        
        event = f"""BEGIN:VEVENT
UID:{uid}
DTSTAMP:{timestamp}
DTSTART;VALUE=DATE:{event_date_str}
SUMMARY:{summary}
DESCRIPTION:{description.replace(chr(10), '\\n')}
STATUS:CONFIRMED
SEQUENCE:0
BEGIN:VALARM
TRIGGER:-P1D
ACTION:DISPLAY
DESCRIPTION:Reminder
END:VALARM
END:VEVENT
"""
        return event
    
    def generate_google_calendar_links(self):
        """Generate Google Calendar quick-add links"""
        links = []
        
        for tm in self.trademarks:
            if tm['status'] != 'active':
                continue
            
            renewal_date = datetime.fromisoformat(tm['renewal_date'])
            date_str = renewal_date.strftime("%Y%m%d")
            
            title = f"TM Renewal: {tm['name']} ({tm['jurisdiction']})"
            details = f"Registration: {tm.get('registration_number', 'N/A')}"
            
            # Google Calendar URL format
            base_url = "https://calendar.google.com/calendar/render"
            params = f"action=TEMPLATE&text={title}&dates={date_str}/{date_str}&details={details}"
            link = f"{base_url}?{params.replace(' ', '+')}"
            
            links.append({
                "trademark": tm['name'],
                "jurisdiction": tm['jurisdiction'],
                "date": tm['renewal_date'],
                "link": link
            })
        
        return links
    
    def export_reminders_markdown(self, output_file="CALENDAR_SETUP.md"):
        """Export calendar setup instructions"""
        links = self.generate_google_calendar_links()
        
        content = """# Trademark Deadline Calendar Setup

## Option 1: Import iCal File

1. Generate the calendar file:
   ```bash
   python integrations/calendar_sync.py
   ```

2. Import `trademark_deadlines.ics` into your calendar app:
   - **Google Calendar:** Settings → Import & Export → Import
   - **Outlook:** File → Open & Export → Import/Export
   - **Apple Calendar:** File → Import → Select file

## Option 2: Quick Add to Google Calendar

Click these links to add individual deadlines:

"""
        
        for link_data in links:
            content += f"### {link_data['trademark']} - {link_data['jurisdiction']}\n"
            content += f"**Renewal Date:** {link_data['date']}\n\n"
            content += f"[Add to Google Calendar]({link_data['link']})\n\n"
        
        content += """## Reminder Schedule

For each trademark, you'll receive reminders:
- 📅 90 days before renewal
- 📅 60 days before renewal  
- 📅 30 days before renewal
- 📅 7 days before renewal
- 📅 On renewal deadline

## Automated Updates

The calendar file is automatically regenerated weekly by GitHub Actions.
Re-import the latest file to stay synced.
"""
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Calendar setup guide created: {output_file}")
        return output_file

if __name__ == "__main__":
    sync = CalendarSync()
    
    # Generate iCal file
    sync.generate_ical()
    
    # Generate setup guide
    sync.export_reminders_markdown()
    
    print("\n✅ Calendar integration files created!")
    print("   1. Import trademark_deadlines.ics into your calendar")
    print("   2. Or use links in CALENDAR_SETUP.md for quick add")