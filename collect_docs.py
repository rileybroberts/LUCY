#!/usr/bin/env python3
"""
Document Collection Helper for LUCY
Helps organize and prepare documents for ingestion
"""
import os
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse
import time

class SpitfireDocCollector:
    """Helper for collecting Spitfire documentation"""
    
    def __init__(self, docs_dir="./data/docs"):
        self.docs_dir = Path(docs_dir)
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create organized subdirectories
        self.subdirs = {
            'manuals': self.docs_dir / 'manuals',
            'forums': self.docs_dir / 'forums', 
            'technical': self.docs_dir / 'technical',
            'parts': self.docs_dir / 'parts',
            'maintenance': self.docs_dir / 'maintenance'
        }
        
        for subdir in self.subdirs.values():
            subdir.mkdir(exist_ok=True)
    
    def download_file(self, url, filename, subdir='manuals'):
        """Download a file to the specified subdirectory"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            filepath = self.subdirs[subdir] / filename
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✓ Downloaded: {filename}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to download {filename}: {e}")
            return False
    
    def create_manual_checklist(self):
        """Create a checklist of essential manuals to find"""
        checklist = """
# LUCY Document Collection Checklist

## 📋 Essential Manuals (Priority 1)
- [ ] 1978 Triumph Spitfire Workshop Manual (Official)
- [ ] Spitfire 1500 Parts Catalog
- [ ] SU Carburettor Manual (HS4 Twin Carbs)
- [ ] Lucas Electrical Manual
- [ ] Triumph Spitfire Owner's Manual (1978)
- [ ] Haynes Manual - Triumph Spitfire (if available)

## 🔧 Technical Documentation (Priority 2)  
- [ ] Engine Rebuild Manual (1.5L inline-4)
- [ ] Transmission Manual (4-speed + overdrive)
- [ ] Brake System Technical Bulletin
- [ ] Suspension & Steering Manual
- [ ] Body Repair Manual
- [ ] Paint & Trim Specifications

## 🌐 Forum Knowledge (Priority 3)
- [ ] SpitfireGT6.com technical articles
- [ ] Common problems & solutions threads
- [ ] Modification guides
- [ ] Restoration diaries
- [ ] Parts supplier recommendations
- [ ] Modern upgrades & improvements

## 📚 Additional Resources
- [ ] Period road tests & reviews
- [ ] Technical Service Bulletins
- [ ] Factory training materials
- [ ] Competition preparation guides

## 🔗 Recommended Sources:
- Victoria British: Free manual downloads
- Moss Motors: Technical resources
- British Motor Heritage: Official reprints
- ClassicZcar.com: Manual archive
- Internet Archive: Historical documents
- SpitfireGT6.com: Community knowledge

## 💡 Collection Tips:
1. Start with official manuals for accuracy
2. Forums provide real-world solutions
3. Save forum posts as text/markdown files
4. Organize by category for better retrieval
5. Include part numbers and specifications
6. Document source and date for each file
        """
        
        checklist_path = self.docs_dir / 'collection_checklist.md'
        with open(checklist_path, 'w') as f:
            f.write(checklist)
        
        print(f"✓ Created collection checklist: {checklist_path}")
    
    def create_forum_scraper_template(self):
        """Create a template for manual forum post collection"""
        template = '''
# Forum Post Collection Template

## Source Information
- **Forum**: [Forum Name]
- **Thread**: [Thread Title]
- **URL**: [Full URL]
- **Date**: [Post Date]
- **Author**: [Username]

## Topic/Problem
[What issue or topic is being discussed]

## Solution/Information
[The actual technical content, instructions, or advice]

## Parts/Tools Mentioned
- Part 1: [Part number/description]
- Tool 1: [Tool name/specification]

## Related Issues
[Any related problems or follow-up information]

## Notes
[Your own notes or observations]

---
*Collected for LUCY - 1978 Triumph Spitfire Knowledge Base*
        '''
        
        template_path = self.docs_dir / 'forum_post_template.md'
        with open(template_path, 'w') as f:
            f.write(template)
        
        print(f"✓ Created forum post template: {template_path}")
    
    def scan_existing_docs(self):
        """Scan and report on existing documents"""
        print("\n📄 Current Document Inventory:")
        
        total_files = 0
        for subdir_name, subdir_path in self.subdirs.items():
            files = list(subdir_path.glob('*'))
            files = [f for f in files if f.is_file()]
            
            print(f"\n{subdir_name.upper()}:")
            if files:
                for file in files:
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"  ✓ {file.name} ({size_mb:.1f} MB)")
                    total_files += 1
            else:
                print(f"  (empty)")
        
        print(f"\n📊 Total Documents: {total_files}")
        
        if total_files == 0:
            print("\n💡 Ready to start collecting! Use the checklist to guide your search.")
    
    def create_sample_content(self):
        """Create sample technical content for testing"""
        sample_content = """
# Triumph Spitfire 1500 - Carburettor Tuning Guide

## SU HS4 Twin Carburettors - Detailed Setup

### Tools Required:
- Carburettor balancer (Colortune or Unisyn)
- 7/16" spanner for throttle adjustments  
- Small flat-blade screwdriver for mixture screws
- Tachometer
- Feeler gauges (0.002" - 0.006")

### Initial Checks:
1. **Throttle Linkage**: Check for smooth operation without binding
2. **Air Filters**: Ensure both K&N or paper filters are clean
3. **Vacuum Hoses**: Inspect for cracks or loose connections
4. **Float Chamber Levels**: Should be 5/8" below rim when measured

### Synchronization Procedure:

#### Step 1: Basic Adjustment
- Engine at normal operating temperature (180°F)
- Remove air cleaners for access
- Disconnect throttle return springs temporarily
- Loosen throttle rod adjustment nuts

#### Step 2: Idle Speed Setting  
- Adjust both throttle stop screws equally
- Target idle speed: 800-900 RPM
- Use tachometer for accuracy

#### Step 3: Carburettor Balance
- Connect carb balancer to both carb intakes
- Adjust throttle stop screws until both carbs show identical readings
- Readings should match within 5% at idle

#### Step 4: Mixture Adjustment
- Locate mixture screws (bottom of float chambers)
- Start with both screws at 1.5 turns out from fully closed
- Adjust for smoothest idle and highest RPM
- Final position usually 1.5-2.5 turns out

#### Step 5: Progressive Adjustment
- Snap throttle open quickly - should be crisp response
- Hold at 2000 RPM - both carbs should read identically
- Fine-tune mixture for smooth acceleration

### Common Issues & Solutions:

**Black Smoke**: 
- Mixture too rich
- Turn mixture screws clockwise (leaner)
- Check float levels

**Popping Back Through Carbs**:
- Mixture too lean  
- Turn mixture screws counter-clockwise (richer)
- Check for air leaks

**Uneven Idle**:
- Poor synchronization
- Re-balance using carb tool
- Check throttle linkage adjustment

**Flat Spots on Acceleration**:
- Accelerator pump diaphragm worn
- Clean or replace pump mechanism
- Check fuel delivery

### Part Numbers:
- SU HS4 Rebuild Kit: AUD431
- Needle Valve Assembly: AZX1307  
- Float Chamber Gasket: AHH5749
- Throttle Spindle: AUD505

### Maintenance Schedule:
- Check synchronization: Every 6,000 miles
- Clean float chambers: Every 12,000 miles
- Rebuild carburettors: Every 50,000 miles or 5 years

*Source: Official Triumph Service Manual & SpitfireGT6.com Community*
        """
        
        sample_path = self.subdirs['technical'] / 'carburettor_tuning_detailed.md'
        with open(sample_path, 'w') as f:
            f.write(sample_content)
        
        print(f"✓ Created sample technical content: {sample_path}")

def main():
    """Main function to set up document collection"""
    print("🚗 LUCY Document Collection Helper 🚗\n")
    
    collector = SpitfireDocCollector()
    
    # Create helpful files
    collector.create_manual_checklist()
    collector.create_forum_scraper_template() 
    collector.create_sample_content()
    
    # Show current status
    collector.scan_existing_docs()
    
    print("\n🎯 Next Steps:")
    print("1. Review collection_checklist.md for manual sources")
    print("2. Download official manuals to data/docs/manuals/")
    print("3. Use forum_post_template.md to save forum knowledge")
    print("4. Run 'python chat.py' to test with sample content")
    print("5. LUCY will automatically index new documents on restart")

if __name__ == "__main__":
    main()