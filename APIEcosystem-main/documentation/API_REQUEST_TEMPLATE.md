# API Request Template for AI Assistant

## Template Structure

```markdown
I need to create a new API in the APIEcosystem project located at [PROJECT_PATH]. This API should [HIGH_LEVEL_DESCRIPTION].

### Core Functionality
[DESCRIBE_CORE_FUNCTIONALITY_HERE]

Example format:
```python
# Sample code or pseudocode that demonstrates the core logic
def process_something():
    # Key operations
    pass
```

### Required Dependencies
- List any external libraries needed
- Include specific versions if critical

### Data Sources
- Describe any databases, files, or external services needed
- Specify paths or connection details if they are fixed
- Note any environment-specific configurations

### Expected Output
- Describe the expected output format
- Include any specific file paths or naming conventions
- Note any required directory structures

### Integration Requirements
- Note any existing systems this needs to work with
- Specify any specific error handling requirements
- Detail any logging or monitoring needs

As you implement this API, please:
1. Follow the project's existing patterns and conventions
2. Ensure proper error handling and validation
3. Update the configuration appropriately
4. Create necessary templates and documentation
5. Maintain any specific path requirements
```

## Example Usage

Here's how you would use this template for a real API request:

```markdown
I need to create a new API in the APIEcosystem project located at /home/user/APIEcosystem. This API should process document metadata and organize files based on database records.

### Core Functionality
The API needs to:
1. Query a SQLite database for document metadata
2. Create organized directory structures
3. Process and save various file types (text, images)
4. Generate metadata files

Example format:
```python
def process_document(doc_id):
    # Query database
    metadata = get_document_metadata(doc_id)
    
    # Create directory structure
    create_directories(metadata)
    
    # Process files
    process_text_content(metadata)
    process_images(metadata)
    
    # Generate metadata files
    create_metadata_files(metadata)
```

### Required Dependencies
- SQLAlchemy
- Pillow (PIL)
- pydub
- mutagen

### Data Sources
- SQLite database at: C:/Users/user/data/documents.db
- File structure:
  ```
  E:/
  └── ProcessedDocs/
      └── [Document_Title]/
          ├── Metadata/
          ├── Content/
          └── Images/
  ```

### Expected Output
- Organized directory structure
- Processed text files
- Converted images
- Metadata files in JSON format

### Integration Requirements
- Must integrate with existing database schema
- Should handle network path differences
- Need proper logging for batch processing
- Must maintain existing file naming conventions
```

## Key Elements to Include

When using this template, ensure you provide:

1. **Project Context**
   - Full path to the project
   - Any relevant environment details
   - Existing patterns to follow

2. **Functional Requirements**
   - Clear description of what the API should do
   - Any specific business rules
   - Required endpoints

3. **Technical Details**
   - Required dependencies
   - Database schemas
   - File paths and structures
   - Integration points

4. **Special Considerations**
   - Performance requirements
   - Security concerns
   - Error handling needs
   - Logging requirements

## Best Practices for Using This Template

1. **Be Specific**
   - Provide exact paths when they're fixed
   - Include sample data structures
   - Specify exact versions of dependencies if critical

2. **Include Context**
   - Reference existing APIs if similar functionality exists
   - Note any specific patterns to follow
   - Mention any constraints or limitations

3. **Define Success Criteria**
   - What constitutes a successful implementation
   - Required testing scenarios
   - Expected performance metrics

4. **Note Environment Details**
   - Development environment specifics
   - Required configuration changes
   - Any environment variables needed

## Template Customization Guide

Adjust the template based on your specific needs by:

1. **Adding Sections**
   - Security requirements
   - Performance criteria
   - Testing requirements
   - Documentation needs

2. **Removing Sections**
   - Remove unnecessary sections for simpler APIs
   - Skip detailed technical specs for proof-of-concept work
   - Omit environment details for portable solutions

3. **Modifying Content**
   - Add project-specific checklists
   - Include company-specific requirements
   - Reference internal documentation

## Tips for AI Interaction

When using this template with AI:

1. **Be Clear About Priorities**
   - What aspects are most critical
   - Which parts can be simplified
   - What level of documentation is needed

2. **Provide Examples**
   - Include similar existing APIs
   - Show preferred coding styles
   - Reference existing documentation

3. **Specify Constraints**
   - Time limitations
   - Resource constraints
   - Performance requirements

4. **Request Specific Outputs**
   - Documentation formats
   - Code structure
   - Test coverage

Remember to adapt this template based on your specific needs and project requirements. The more detailed and specific you can be, the better the AI can assist in creating your API.