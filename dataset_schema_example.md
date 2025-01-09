# Dataset Schema Documentation - Customer Purchase History

## Basic Information
- **Dataset Name**: customer_purchase_history
- **Owner/Maintainer**: Sarah Johnson (Data Analytics Team)
- **Last Updated**: 2025-01-08
- **Update Frequency**: Daily (incremental updates at 2 AM EST)
- **Business Purpose**: Track and analyze customer purchasing patterns to support marketing initiatives and inventory management

## Dataset Overview
This dataset contains detailed purchase transaction records for all customers across our retail channels (online and in-store). It serves as the primary source for customer behavior analysis, sales reporting, and predictive inventory management.

## Data Source
- **Source System**: ERP System (SAP) and E-commerce Platform (Shopify)
- **Data Collection Method**: Real-time API integration with batch reconciliation
- **Source Data Format**: JSON (e-commerce) and CSV (in-store POS)

## Technical Specifications
### Storage Details
- **Location**: /data/warehouse/customer/purchase_history
- **Format**: Parquet files partitioned by date
- **Size**: ~500GB (compressed)
- **Number of Records**: ~100M transactions (as of Jan 2025)

### Schema Details
| Column Name | Data Type | Description | Constraints/Rules | Example Value |
|------------|-----------|-------------|-------------------|---------------|
| transaction_id | string | Unique identifier for each transaction | Primary Key, UUID format | "f47ac10b-58cc-4372-a567-0e02b2c3d479" |
| customer_id | string | Customer identifier | Foreign key to customer_master | "CUST123456" |
| transaction_date | timestamp | Date and time of purchase | Not null, Format: YYYY-MM-DD HH:MM:SS | "2025-01-08 14:30:22" |
| store_id | string | Identifier for physical store or 'ONLINE' | Not null | "STORE_NYC_001" |
| product_id | string | Product identifier | Foreign key to product_master | "PROD789012" |
| quantity | integer | Number of items purchased | > 0 | 2 |
| unit_price | decimal(10,2) | Price per unit at time of purchase | > 0.00 | 29.99 |
| total_amount | decimal(10,2) | Total transaction amount | = quantity * unit_price | 59.98 |
| payment_method | string | Method of payment | One of: CREDIT, DEBIT, CASH, OTHER | "CREDIT" |

## Data Quality
### Validation Rules
- All transactions must have a valid customer_id (except cash transactions in-store)
- Total_amount must equal quantity * unit_price
- Transaction_date cannot be in the future
- Store_id must exist in store_master table
- Product_id must exist in product_master table

### Known Data Quality Issues
- Some historical records (pre-2024) may have missing payment_method data
- Store_id for online transactions may show inconsistent values in legacy data
- Customer_id might be missing for ~5% of in-store cash transactions

## Access and Security
- **Access Method**: Snowflake Data Warehouse
- **Authentication Required**: Yes
- **Authorization Level Required**: Analyst role or higher
- **Sensitive Data Categories**: Payment information (masked)

## Dependencies
### Upstream Dependencies
- SAP ERP System
- Shopify E-commerce Platform
- store_master table
- product_master table
- customer_master table

### Downstream Dependencies
- Daily Sales Dashboard
- Customer Segmentation Model
- Inventory Forecasting System
- Marketing Campaign Performance Reports

## Processing Information
- **ETL/Processing Schedule**: Daily at 2 AM EST
- **Processing Steps**:
  1. Extract from SAP and Shopify APIs
  2. Transform and validate data
  3. Merge with existing dataset
  4. Update aggregated views
- **Critical Timings**: Must complete by 6 AM EST for morning reports

## Usage Guidelines
### Best Practices
- Always filter by transaction_date when querying large date ranges
- Use the aggregated views for reporting when possible
- Join with customer_master for complete customer information
- Consider seasonality when analyzing patterns

### Common Pitfalls
- Don't assume all transactions have customer_id
- Be aware of timezone differences in transaction_date
- Check for duplicates when processing returns/refunds
- Consider price variations across different stores

## Support
- **Primary Contact**: Sarah Johnson (sarah.j@company.com)
- **Secondary Contact**: Data Engineering Team (data-eng-support@company.com)
- **Support Process**: Create ticket in JIRA (DATA-SUPPORT project)

## Change Log
| Date | Change Description | Changed By |
|------|-------------------|------------|
| 2025-01-08 | Added payment_method column | Sarah Johnson |
| 2024-12-15 | Updated data quality rules | Mark Wilson |
| 2024-11-01 | Implemented partitioning by date | Data Engineering Team |

## Additional Notes
- This dataset is part of the Customer 360 initiative
- Quarterly data quality audits are performed by the Data Governance team
- Historical data (>2 years) is archived in cold storage
- Real-time access is available through the streaming API for specific use cases