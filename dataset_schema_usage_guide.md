# Dataset Schema Documentation Guide

This guide explains how different stakeholders should interact with the dataset schema documentation. The documentation serves as our single source of truth for dataset information and helps maintain data quality and usability across the organization.

## For Subject Matter Experts (SMEs)

### Your Responsibilities
- Create and maintain documentation for datasets you own
- Keep the documentation up-to-date as changes occur
- Review documentation quarterly for accuracy
- Respond to questions and clarification requests from users

### How to Use the Template
1. **Initial Setup**:
   - Make a copy of the template for each dataset you own
   - Name the file following the convention: `dataset_name_schema.md`
   - Fill out all relevant sections based on your knowledge of the dataset

2. **Critical Sections to Focus On**:
   - Basic Information (especially update frequency and business purpose)
   - Dataset Overview (focus on use cases and business context)
   - Data Quality (document known issues and limitations)
   - Usage Guidelines (share your expert knowledge about working with the data)

3. **Maintenance Guidelines**:
   - Update the "Last Updated" date whenever you make changes
   - Document all significant changes in the Change Log
   - Set calendar reminders for quarterly reviews
   - Add new known issues as they are discovered

4. **Best Practices**:
   - Use clear, non-technical language where possible
   - Include business context for technical details
   - Provide specific examples where helpful
   - Document assumptions and unwritten rules about the data

## For Developers

### Your Responsibilities
- Review documentation before integrating new datasets
- Verify technical specifications match actual implementation
- Report any discrepancies found while working with the data
- Update documentation when making technical changes

### How to Use the Documentation
1. **Before Development**:
   - Review the Technical Specifications section thoroughly
   - Verify all listed dependencies
   - Check access requirements and security constraints
   - Note any data quality issues that might affect development

2. **During Development**:
   - Use the schema details as your reference for data structure
   - Follow the documented validation rules
   - Consider known issues when implementing error handling
   - Reference the processing information for integration timing

3. **After Development**:
   - Update technical specifications if changes were made
   - Document any new validation rules implemented
   - Add new dependencies if created
   - Update processing information if workflows changed

4. **Best Practices**:
   - Validate schema details against actual data structure
   - Test all documented constraints and rules
   - Consider impact on downstream dependencies
   - Communicate technical changes to the SME

## For Metrics Team Lead

### Your Responsibilities
- Ensure documentation standards are maintained
- Review documentation for completeness and clarity
- Coordinate between SMEs and developers
- Manage documentation lifecycle
- Ensure metrics requirements are captured

### How to Use the Documentation
1. **Quality Assurance**:
   - Regular review of documentation completeness
   - Verify critical sections are properly maintained
   - Ensure technical accuracy through developer feedback
   - Validate that business requirements are clearly documented

2. **Documentation Management**:
   - Maintain the template and update as needed
   - Track which datasets have current documentation
   - Schedule regular reviews with SMEs
   - Coordinate updates when major changes occur

3. **Metrics Specific Tasks**:
   - Verify that calculation methodologies are documented
   - Ensure business rules affecting metrics are clear
   - Track dependencies between metrics and datasets
   - Document any data transformations needed for metrics

4. **Best Practices**:
   - Keep a master list of all dataset documentation
   - Track documentation review dates
   - Maintain a feedback loop between all stakeholders
   - Document metric-specific requirements in relevant sections

## General Guidelines for All Users

### Documentation Lifecycle
1. **Creation**:
   - SME creates initial documentation
   - Metrics Team Lead reviews for completeness
   - Developers verify technical accuracy
   - All stakeholders approve final version

2. **Maintenance**:
   - Regular quarterly reviews
   - Update as changes occur
   - Version control through Change Log
   - Annual comprehensive review

3. **Communication**:
   - Use the documentation as the primary reference
   - Direct questions to the listed contacts
   - Suggest updates through appropriate channels
   - Share feedback on documentation usability

### Common Pitfalls to Avoid
- Leaving sections blank without explanation
- Using unexplained acronyms or technical jargon
- Forgetting to update the Change Log
- Not documenting assumptions
- Omitting known limitations or issues
- Providing outdated contact information

### Making Updates
1. **Minor Updates** (no impact on data structure or usage):
   - Update directly
   - Note change in Change Log
   - Update Last Updated date

2. **Major Updates** (impacts data structure or usage):
   - Notify all stakeholders before making changes
   - Get approval from Metrics Team Lead
   - Update all affected sections
   - Document in Change Log
   - Consider impact on dependent systems/reports

### Getting Help
- Review this guide first
- Contact the Metrics Team Lead for documentation questions
- Reach out to listed SME contacts for dataset-specific questions
- Submit enhancement requests through established channels
- Participate in quarterly documentation reviews

## Additional Resources
- Link to template repository
- Documentation best practices guide
- Example implementations
- Contact list for key stakeholders
- Schedule of regular review meetings
- Change management process documentation