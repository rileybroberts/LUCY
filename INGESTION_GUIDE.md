# 📚 LUCY Document Ingestion Guide

## 🚀 Quick Start for Document Collection

### Step 1: Run the Collection Helper
```bash
python collect_docs.py
```
This creates organized folders and checklists to guide your document gathering.

### Step 2: Priority Document Sources

#### 🔧 **Essential Manuals (Start Here)**
1. **Official Triumph Workshop Manual (1978 Spitfire 1500)**
   - Source: British Motor Heritage, Moss Motors
   - File: Save as `manuals/triumph_spitfire_1978_workshop_manual.pdf`

2. **SU Carburettor Manual (HS4)**
   - Source: SU Carburettors Ltd, Classic car forums
   - File: Save as `manuals/su_hs4_carburettor_manual.pdf`

3. **Lucas Electrical Manual**
   - Source: Lucas Classic, electrical suppliers
   - File: Save as `manuals/lucas_electrical_spitfire.pdf`

#### 🌐 **Forum Knowledge Collection**
**Best Forums for Technical Content:**
- **SpitfireGT6.com** - Most comprehensive
- **6-Pack.org** - Active community
- **TriumphExperience.com** - Technical focus
- **Reddit r/Triumph** - Modern solutions

**Forum Collection Strategy:**
1. Search for: "1978 Spitfire [problem]" 
2. Look for posts with part numbers and step-by-step solutions
3. Save as markdown files using the provided template
4. Focus on: oil leaks, carb tuning, electrical issues, brake problems

### Step 3: Web Scraping Tools & Techniques

#### Manual Collection from Archives
```bash
# Internet Archive has many automotive manuals
# Search: "Triumph Spitfire manual" 
# Filter by: Year (1970s), Type (PDF)
```

#### Forum Content Collection
```bash
# Use browser extensions for easy saving:
# - SingleFile (saves complete pages as HTML)
# - MarkDownload (converts to markdown)
# - Web Clipper tools
```

## 📁 File Organization Strategy

### Directory Structure
```
data/docs/
├── manuals/          # Official documentation
│   ├── workshop/     # Service manuals
│   ├── parts/        # Parts catalogs  
│   └── electrical/   # Wiring diagrams
├── forums/           # Community knowledge
│   ├── troubleshooting/
│   ├── modifications/
│   └── maintenance/
├── technical/        # Technical bulletins
└── reference/        # Specifications, torque values
```

### File Naming Convention
```
# Manuals
triumph_spitfire_1978_workshop_manual.pdf
su_hs4_carburettor_service_guide.pdf
lucas_electrical_wiring_diagram_1978.pdf

# Forum Posts  
spitfire_oil_leak_rear_main_seal_fix.md
carb_synchronization_step_by_step.md
electrical_troubleshooting_no_start.md

# Technical Content
engine_torque_specifications.txt
brake_system_bleeding_procedure.md
suspension_alignment_settings.txt
```

## 🔍 Specific Content to Prioritize

### 1. **Maintenance Procedures**
- Oil change procedures & specifications
- Carburettor adjustment & tuning
- Brake system maintenance
- Electrical troubleshooting
- Cooling system service

### 2. **Common Problems & Solutions**
- Oil leaks (rear main seal, gearbox)
- Carburettor issues (flooding, poor idle)
- Electrical gremlins (Lucas "Prince of Darkness")
- Cooling problems (overheating)
- Rust prevention & treatment

### 3. **Technical Specifications**
- Engine specifications & tolerances
- Torque values for all fasteners
- Fluid capacities & types
- Electrical specifications
- Tire pressures & alignment specs

### 4. **Parts Information**
- OEM part numbers
- Modern equivalent parts
- Supplier recommendations
- Upgrade options

## 🤖 Automated Collection Scripts

### Forum Post Collector (Advanced)
```python
# Example for collecting from specific forum threads
# Save this as forum_collector.py

import requests
from bs4 import BeautifulSoup
import time

def collect_forum_thread(url, topic_name):
    """Collect a forum thread and save as markdown"""
    # Implementation would go here
    # This is just a template - actual implementation 
    # would need to respect robots.txt and rate limits
    pass
```

### PDF Download Helper
```bash
# Use wget for bulk PDF downloads
wget -r -A.pdf -np -nd -P data/docs/manuals/ [URL_TO_MANUAL_DIRECTORY]
```

## 🔄 Document Ingestion Process

### After Collecting Documents:

1. **Organize Files**
   ```bash
   # Move files to appropriate subdirectories
   mv *.pdf data/docs/manuals/
   mv *.md data/docs/forums/
   ```

2. **Test Ingestion**
   ```bash
   # Start LUCY - she'll automatically detect and ingest new documents
   python chat.py
   # Look for "Loaded: [filename]" messages during startup
   ```

3. **Verify Knowledge**
   ```bash
   # Test LUCY's knowledge with specific questions
   "Tell me about changing your oil"
   "How do I adjust your carburettors?"  
   "What's the torque specification for your head bolts?"
   ```

## 📊 Quality Control

### Document Quality Checklist
- [ ] Files are readable (not corrupted)
- [ ] Text is searchable (OCR if needed)
- [ ] Metadata includes source and date
- [ ] Content is specific to 1978 Spitfire when possible
- [ ] File names are descriptive and consistent

### Testing LUCY's Knowledge
After adding documents, test these key areas:
- Engine maintenance procedures
- Carburettor adjustment steps  
- Electrical troubleshooting
- Common problem solutions
- Part number lookups

## 🎯 Success Metrics

**Phase 1 Complete When:**
- 5+ official manuals ingested
- 20+ forum posts collected  
- LUCY can answer basic maintenance questions
- Memory system tracks your maintenance work

**Phase 2 Complete When:**
- 50+ documents total
- Coverage of all major systems
- LUCY provides part numbers and torque specs
- Community solutions integrated

**Phase 3 Complete When:**
- 100+ documents
- Historical context and modifications covered
- Modern upgrade advice available
- Comprehensive troubleshooting knowledge

## 🆘 Troubleshooting

### Common Issues:
- **PDFs not searchable**: Use OCR tools like Tesseract
- **Large file sizes**: Compress PDFs before ingestion
- **Duplicate content**: LUCY's vector database handles duplicates well
- **Poor document quality**: Manual cleanup may be needed

### Performance Tips:
- Restart LUCY after adding many documents
- Monitor vector database size in `data/vectordb/`
- Use `/status` command to check document count
- Clear conversation memory if responses get slow

---

*Remember: Start with official manuals for accuracy, then add community knowledge for real-world solutions!*