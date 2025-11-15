#!/usr/bin/env python3
"""
Dr. Greenthumb Trademark Tracker
Automated trademark portfolio management
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

class TrademarkTracker:
    def __init__(self):
        self.data_file = Path("trademarks.json")
        self.trademarks = self.load_data()
    
    def load_data(self):
        if self.data_file.exists():
            with open(self.data_file) as f:
                return json.load(f)
        return []
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.trademarks, f, indent=2)
    
    def add_trademark(self, name, jurisdiction, filing_date, renewal_date):
        tm = {
            "id": len(self.trademarks) + 1,
            "name": name,
            "jurisdiction": jurisdiction,
            "filing_date": filing_date,
            "renewal_date": renewal_date,
            "status": "active",
            "created": datetime.now().isoformat()
        }
        self.trademarks.append(tm)
        self.save_data()
        print(f"✅ Added: {name} ({jurisdiction})")
    
    def get_upcoming(self, days=90):
        today = datetime.now().date()
        threshold = today + timedelta(days=days)
        
        upcoming = []
        for tm in self.trademarks:
            if tm['status'] != 'active':
                continue
            renewal = datetime.fromisoformat(tm['renewal_date']).date()
            if today <= renewal <= threshold:
                days_until = (renewal - today).days
                upcoming.append({**tm, 'days_until': days_until})
        
        return sorted(upcoming, key=lambda x: x['days_until'])
    
    def generate_report(self):
        print("\n" + "="*80)
        print("DR. GREENTHUMB TRADEMARK PORTFOLIO")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*80 + "\n")
        
        active = [tm for tm in self.trademarks if tm['status'] == 'active']
        print(f"Total Active: {len(active)}\n")
        
        upcoming_30 = self.get_upcoming(30)
        upcoming_60 = self.get_upcoming(60)
        upcoming_90 = self.get_upcoming(90)
        
        print("RENEWAL ALERTS:")
        print(f"  🔴 Within 30 days: {len(upcoming_30)}")
        print(f"  🟠 Within 60 days: {len(upcoming_60)}")
        print(f"  🟡 Within 90 days: {len(upcoming_90)}\n")
        
        if upcoming_30:
            print("URGENT RENEWALS (30 days):")
            for tm in upcoming_30:
                print(f"  - {tm['name']} ({tm['jurisdiction']})")
                print(f"    Due: {tm['renewal_date']} ({tm['days_until']} days)")
            print()
        
        print("="*80)

if __name__ == "__main__":
    import sys
    tracker = TrademarkTracker()
    
    if "--report" in sys.argv:
        tracker.generate_report()
    elif "--upcoming" in sys.argv:
        idx = sys.argv.index("--upcoming")
        days = int(sys.argv[idx + 1]) if len(sys.argv) > idx + 1 else 90
        for tm in tracker.get_upcoming(days):
            print(f"{tm['name']} ({tm['jurisdiction']}) - {tm['days_until']} days")
    elif "--add" in sys.argv:
        # Simple add for demo
        tracker.add_trademark(
            "DR. GREENTHUMB",
            "Arizona",
            "2025-11-15",
            "2035-11-15"
        )
    else:
        tracker.generate_report()
