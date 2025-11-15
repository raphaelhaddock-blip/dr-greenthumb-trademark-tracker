#!/usr/bin/env python3
"""
Connector to licensing database for territory conflict checking
"""

import json
from datetime import datetime

class LicensingConnector:
    """Check trademark territories against active licensing agreements"""
    
    def __init__(self, trademarks_file="trademarks.json", 
                 licensing_file="licensing_agreements.json"):
        self.trademarks = self.load_json(trademarks_file)
        self.licensing_agreements = self.load_json(licensing_file)
    
    def load_json(self, filename):
        """Load JSON data file"""
        try:
            with open(filename) as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def check_territory_conflicts(self):
        """Check for trademark/licensing territory conflicts"""
        conflicts = []
        
        for tm in self.trademarks:
            if tm['status'] == 'pending' or tm['status'] == 'abandoned':
                # Flag unfiled territories with active licensing
                territory_conflicts = self._check_unfiled_territory(tm)
                if territory_conflicts:
                    conflicts.extend(territory_conflicts)
        
        return conflicts
    
    def _check_unfiled_territory(self, trademark):
        """Check if unfiled trademark conflicts with licensing"""
        conflicts = []
        jurisdiction = trademark['jurisdiction']
        
        for agreement in self.licensing_agreements:
            if jurisdiction.lower() in agreement.get('territories', []):
                if agreement['status'] == 'active':
                    conflicts.append({
                        "trademark": trademark['name'],
                        "jurisdiction": jurisdiction,
                        "issue": "Operating without TM protection",
                        "licensee": agreement['licensee'],
                        "agreement_id": agreement['id'],
                        "risk_level": "HIGH",
                        "cost_to_file": "$3,900",
                        "recommended_action": f"File trademark in {jurisdiction} immediately to protect licensed territory"
                    })
        
        return conflicts
    
    def generate_territory_report(self):
        """Generate comprehensive territory coverage report"""
        print("\n" + "="*80)
        print("TRADEMARK & LICENSING TERRITORY ANALYSIS")
        print("="*80 + "\n")
        
        # Get all territories from licensing
        licensed_territories = set()
        for agreement in self.licensing_agreements:
            if agreement['status'] == 'active':
                for territory in agreement.get('territories', []):
                    licensed_territories.add(territory.lower())
        
        # Get protected territories from trademarks
        protected_territories = set()
        for tm in self.trademarks:
            if tm['status'] == 'active':
                protected_territories.add(tm['jurisdiction'].lower())
        
        # Find gaps
        unprotected = licensed_territories - protected_territories
        
        print(f"TERRITORY COVERAGE:")
        print(f"  Licensed Territories: {len(licensed_territories)}")
        print(f"  Protected by Trademark: {len(protected_territories)}")
        print(f"  🚨 UNPROTECTED: {len(unprotected)}\n")
        
        if unprotected:
            print("CRITICAL: OPERATING WITHOUT TRADEMARK PROTECTION:\n")
            for territory in sorted(unprotected):
                print(f"  - {territory.title()}")
                print(f"    Risk: HIGH - Licensed but no TM protection")
                print(f"    Action: File trademark immediately")
                print(f"    Estimated Cost: $3,900\n")
        
        # Territory conflicts
        conflicts = self.check_territory_conflicts()
        if conflicts:
            print("\nLICENSING CONFLICTS:\n")
            for conflict in conflicts:
                print(f"  Trademark: {conflict['trademark']}")
                print(f"  Territory: {conflict['jurisdiction']}")
                print(f"  Licensee: {conflict['licensee']}")
                print(f"  Issue: {conflict['issue']}")
                print(f"  Action: {conflict['recommended_action']}\n")
        
        print("="*80)
        
        return {
            "licensed": len(licensed_territories),
            "protected": len(protected_territories),
            "unprotected": list(unprotected),
            "conflicts": conflicts
        }

if __name__ == "__main__":
    # Create sample licensing data for demo
    sample_licensing = [
        {
            "id": 1,
            "licensee": "Barney's Farm (California)",
            "brand": "DR. GREENTHUMB",
            "territories": ["california", "arizona", "illinois"],
            "status": "active",
            "start_date": "2024-01-01",
            "royalty_rate": "8%"
        },
        {
            "id": 2,
            "licensee": "Canada Partner",
            "brand": "DR. GREENTHUMB",
            "territories": ["canada"],
            "status": "pending",
            "start_date": "2025-01-01",
            "royalty_rate": "10%"
        }
    ]
    
    with open("licensing_agreements.json", 'w') as f:
        json.dump(sample_licensing, f, indent=2)
    
    connector = LicensingConnector()
    report = connector.generate_territory_report()
    
    print(f"\n💰 ESTIMATED COST TO SECURE UNPROTECTED TERRITORIES:")
    print(f"   ${len(report['unprotected']) * 3900:,}")