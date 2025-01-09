# Quick API Request Template

```markdown
Create a new API in [PROJECT_PATH] with the following specifications:

## Purpose
[ONE_SENTENCE_DESCRIPTION]

## Core Functionality
```python
# Key functionality in pseudo-code or actual code
[INSERT_CODE_HERE]
```

## Requirements
- Dependencies: [LIST_DEPENDENCIES]
- Data Sources: [LIST_SOURCES]
- Output Paths: [SPECIFY_PATHS]
- Special Requirements: [ANY_SPECIAL_NEEDS]

## Integration Points
- Database: [DATABASE_DETAILS]
- External Systems: [SYSTEM_DETAILS]
- File Locations: [PATH_DETAILS]

Please implement following project standards and create:
1. Routes and endpoints
2. Utility functions
3. Templates
4. Configuration updates
5. Documentation
```

## Example Usage

```markdown
Create a new API in /home/user/APIEcosystem with the following specifications:

## Purpose
Process and organize document metadata from SQLite database into structured directories

## Core Functionality
```python
def process_document(doc_id, volume):
    metadata = get_from_database(doc_id)
    create_directories(f"E:/Documents/{metadata.title}")
    process_files(metadata)
    generate_metadata()
```

## Requirements
- Dependencies: sqlalchemy, pillow, pydub
- Data Sources: SQLite at C:/data/docs.db
- Output Paths: E:/Documents/{title}/{type}/
- Special Requirements: Maintain existing file structure

## Integration Points
- Database: Existing SQLite schema
- External Systems: Local file system
- File Locations: Fixed paths on E: drive

Please implement following project standards and create:
1. Routes and endpoints
2. Utility functions
3. Templates
4. Configuration updates
5. Documentation
```

This template provides a quick way to request new APIs while ensuring all critical information is included.