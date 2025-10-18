"""
document_schemas.py

Schema definitions for structured data document schemas.
These Pydantic models define the structure of data extracted by the analysis system.

================================================================================
SCHEMA PATTERNS - IMPORTANT: Choose the right pattern for your use case
================================================================================

PATTERN 1: FLAT SCHEMA (for single-instance extraction)
--------------------------------------------------------
Use when: Extracting ONE set of information from a document
Example: Document metadata, overall summary, single compliance check

```python
class DocumentMetadata(BaseModel):
    '''Document metadata extraction'''
    title: str = Field(description="Main title of the document")
    author: Optional[str] = Field(description="Author if mentioned")
    summary: str = Field(description="Brief summary of content")
    
# Register directly in AVAILABLE_MODELS:
"document_metadata": DocumentMetadata
```

PATTERN 2: NESTED SCHEMA (for multi-instance extraction)
---------------------------------------------------------
Use when: Extracting MULTIPLE instances from a document
Example: Multiple reports, multiple audit issues, multiple contracts

```python
class ReportItem(BaseModel):
    '''Individual report item'''
    title: str = Field(..., description="Title of the report")
    summary: str = Field(..., description="Summary of the report")

class Report_response(BaseModel):
    '''Response wrapper for multiple report items'''
    item: List[ReportItem]  # MUST be named 'item' and be a List
    model_config = ConfigDict(critical_fields=[])
    
# Register the response wrapper in AVAILABLE_MODELS:
"report_summary": Report_response  # Use the _response class, not the item class
```

================================================================================
NAMING CONVENTIONS
================================================================================
1. Item Classes: YourModelItem (e.g., ReportItem, IssueItem)
2. Response Wrappers: YourModel_response (e.g., Report_response, ITAudit_response)
3. Model Keys: use lowercase with underscores (e.g., "report_summary", "it_audit")

================================================================================
BEST PRACTICES
================================================================================
1. Always add descriptive docstrings to your classes
2. Use Field(..., description="...") for ALL fields - helps AI understand
3. For Optional fields, use Optional[type] and provide None as default
4. For nested schemas, always use: model_config = ConfigDict(critical_fields=[])
5. Consider using OpenAICompatibleBaseModel for better OpenAI compatibility

================================================================================
HOW TO ADD A NEW SCHEMA
================================================================================
1. Decide: Will you extract ONE instance or MULTIPLE instances?
   - ONE → Use flat schema pattern
   - MULTIPLE → Use nested schema pattern

2. Create your model class(es) following the patterns above

3. Register in AVAILABLE_MODELS at the bottom of this file:
   - For flat schemas: "your_key": YourModel
   - For nested schemas: "your_key": YourModel_response

4. The key you use in AVAILABLE_MODELS is what users will see in the UI

================================================================================
"""


from enum import Enum
from typing import Optional, List, Literal, Union
from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict, field_validator, constr


class OpenAICompatibleBaseModel(BaseModel):
    @classmethod
    def model_json_schema(cls, *args, **kwargs):
        def strip_forbidden_keys(schema):
            if isinstance(schema, dict):
                schema.pop("default", None)
                schema.pop("format", None)
                for value in schema.values():
                    strip_forbidden_keys(value)
            elif isinstance(schema, list):
                for item in schema:
                    strip_forbidden_keys(item)

        schema = super().model_json_schema(*args, **kwargs)
        strip_forbidden_keys(schema)
        return schema


class report_item(BaseModel):
    """data model for report item"""

    title: str = Field(..., description="title of the content")
    summary: str = Field(..., description="summary of the content")


class report_response(BaseModel):
    item: List[report_item]
    model_config = ConfigDict(critical_fields=[])


class ONE_item(OpenAICompatibleBaseModel):
    client_name: str = Field(..., description="Name of the client (e.g., ABC Ltd).")
    meeting_title: str = Field(
        ...,
        description="Title of the meeting (e.g., Walkthrough interview on procurement process).",
    )
    walkthrough_datetime: datetime = Field(
        ...,
        description="Date and time of the walkthrough (e.g., 2025-01-05T12:00:00). Must be in the future.",
    )
    attendees: List[str] = Field(
        ...,
        description="List of attendees and their roles (e.g., Name (Procurement Manager)).",
    )
    business_process: str = Field(
        ...,
        description="The business process being reviewed (e.g., Purchase Order creation and approval).",
    )
    process_summary: str = Field(
        ...,
        min_length=1,
        strip_whitespace=True,
        description="Summary of the process described (e.g., PR raised by xxx on an ad-hoc basis … approved PR converted to PO … approval will be given by xxx).",
    )
    key_controls: str = Field(
        ...,
        min_length=1,
        strip_whitespace=True,
        description="Key controls related to the process (e.g., all POs are approved by independent personnel prior to posting).",
    )
    control_type: str = Field(
        ...,
        min_length=1,
        strip_whitespace=True,
        description="Type of control (e.g., system control in SAP or manual control).",
    )
    preparer_roles: List[str] = Field(
        ...,
        description="Roles involved in preparing/executing the process (e.g., Procurement Executive).",
    )
    reviewer_roles: List[str] = Field(
        ...,
        description="Roles involved in reviewing/approving the process (e.g., CEO, General Manager).",
    )
    walkthrough_documents: List[str] = Field(
        ...,
        description="Key documents reviewed during the walkthrough (e.g., Invoices, Purchase Orders).",
    )


class MeetingSummary_response(BaseModel):
    item: List[ONE_item]
    model_config = ConfigDict(critical_fields=[])


##########################################


class recom(BaseModel):
    Recommendation: str = Field(
        ...,
        description="Detailed recommendation for addressing the audit issue.  This should be a specific, actionable step that the agency can take.  For example, 'Implement stronger access controls to prevent unauthorized data modification.'",
    )
    management_comment: str = Field(
        ...,
        description="Management's response to the recommendation. This should indicate whether they agree with the recommendation and what actions they plan to take. For example, 'Management agrees with the recommendation and will implement the suggested access controls by [date].'",
    )


class Issue(BaseModel):
    Agency: str = Field(
        ...,
        description="The government agency or ministry being audited.  For example, 'Ministry of Finance'.",
    )
    Category: str = Field(
        ...,
        description="The category or type of audit issue. This could be a predefined category from the audit framework or a descriptive label.  For example, 'Procurement', 'Data Security', 'Financial Reporting'.",
    )
    Reference: str = Field(
        ...,
        description="A unique identifier for this specific issue within the audit report. This could be a letter-number combination or a sequential number.  For example, 'A1', 'Finding 2.3'.",
    )
    Description: str = Field(
        ...,
        description="A comprehensive description of the audit finding. This should explain the issue in detail, including what was observed, why it's a concern, and the potential impact. Be specific and provide examples if possible. For example, 'The audit found that user access logs were not reviewed regularly, increasing the risk of undetected unauthorized access.'",
    )
    Title: str = Field(
        ...,
        description="A concise and descriptive title for the audit issue.  This should summarize the key problem or area of concern. For example, 'Lack of Access Log Review'.",
    )
    SubTitle: Optional[str] = Field(
        None,
        description="An optional sub-title that provides further context or specificity to the issue title. For example, if the title is 'Procurement Issues', the subtitle might be 'Non-Competitive Bidding Practices'.",
    )
    RiskStatement: str = Field(
        ...,
        description="A statement that clearly articulates the potential negative consequences or risks associated with the identified issue. This should explain what could happen if the issue is not addressed. For example, 'Failure to review access logs could lead to undetected security breaches and data compromise.'",
    )
    RootCause: str = Field(
        ...,
        description="The underlying reason or cause of the audit issue.  This should explain why the issue occurred.  For example, 'Lack of clear procedures for access log review' or 'Insufficient training for staff responsible for log review'.",
    )
    RootCause_category: Literal["People", "Process", "System"] = Field(
        None,
        description="Categorization of the root cause into one of three categories: 'People' (e.g., lack of training, human error), 'Process' (e.g., inadequate procedures, lack of oversight), or 'System' (e.g., software bugs, system limitations).",
    )
    r: List[recom] = Field(
        ...,
        description="A list of recommendations provided by the auditors to address the issue. Each recommendation should be a specific, actionable step, along with management's comment on that recommendation.",
    )


class ITAudit_response(BaseModel):
    item: List[Issue]
    model_config = ConfigDict(extra="forbid")


class Recommendation(BaseModel):
    """
    A specific, actionable recommendation to address the audit issue,
    along with management's response.
    """

    recommendation: str = Field(
        ..., description="Actionable recommendation for addressing the audit issue."
    )
    management_comment: str = Field(
        ..., description="Management's response to the recommendation."
    )


class Issue(BaseModel):
    """
    Represents a single audit issue/risk/finding.
    """

    agency: str = Field(
        ..., description="Agency or ministry where the issue was identified."
    )
    category: str = Field(
        ...,
        description="Category or type of audit issue (e.g., Procurement, Data Security).",
    )
    reference: str = Field(
        ..., description="Unique identifier for the issue (e.g., Finding 1, Finding 2."
    )
    title: str = Field(..., description="Concise, descriptive title of the issue.")
    subtitle: Optional[str] = Field(
        None, description="Optional sub-title for additional context."
    )
    description: str = Field(
        ..., description="Detailed description of the audit finding."
    )
    risk_statement: str = Field(
        ...,
        description="Potential negative consequences if the issue is not addressed.",
    )
    root_cause: str = Field(..., description="Underlying reason or cause of the issue.")
    root_cause_category: Literal["People", "Process", "System"] = Field(
        ..., description="Categorization of the root cause."
    )
    recommendations: List[Recommendation] = Field(
        ...,
        description="List of recommendations and corresponding management comments for this issue.",
    )


class ITAudit_Chris_response(BaseModel):
    """
    The complete structured response, containing all extracted issues.
    """

    item: List[Issue] = Field(
        ...,
        description="List of all individual audit issues extracted from the report.",
    )
    model_config = ConfigDict(extra="forbid")


"""
class Category(BaseModel):
    CategoryName: str = Field(
        ...,
        min_length=1,
        description="The name of the category grouping related issues (e.g., 'Commercial to Receivables', 'Bank and Cash Management')."
    )
    Issues: List[Issue]


class ONE_ITAudit_master(BaseModel):
    ClientName: str = Field(
        ...,
        min_length=1,
        description="The name of the client for whom the audit report is created."
    )
    DateOfReport: str = Field(
        ...,
        description="The date on which the audit report is generated (format: YYYY-MM-DD)."
    )
    BusinessProcess: str = Field(
        ...,
        description="The business process being audited (e.g., 'Order to Cash', 'Procure to Pay')."
    )
    Categories: List[Category]


class ONE_ITAudit_response(BaseModel):
    item: List[ONE_ITAudit_master]

    class Config:
        critical_fields = []
        
        """


class NTT_item(OpenAICompatibleBaseModel):
    """data model for quotation/service order"""

    transacting_party: str = Field(
        ...,
        description="the transacting party, typically the first company name appeared in the content",
    )
    # rfs_date: date = Field(..., description="RFS date")
    location_of_data_center: str = Field(
        ...,
        description="Provide the location of the data center. The location should be represented in the format 'CBJ [number]'. Example: 'CBJ 1' or 'CBJ 2'.",
    )
    order_date: date = Field(..., description="Date of the order or RFS date")
    currency: str = Field(
        ...,
        description="The currency used in the quotation, represented by its ISO 4217 code. Examples include USD for United States Dollar, EUR for Euro, and MYR for Malaysian Ringgit.",
    )
    description: str = Field(..., description="Detailed description of the service")
    it_load: Optional[str] = Field(
        None,
        description="Total power allocation for each item, specified as '[number] kW'.",
    )
    quantity: Optional[Union[int, str]] = Field(
        ..., description="Quantity/Qty of the item"
    )
    unit_of_measure_uom: Optional[str] = Field(
        None, description="Unit of measure (UoM) for the quantity"
    )
    service_length: Optional[Union[int, str]] = Field(
        None,
        description="Number of months the service will be active. It can be an integer (number of months) or a string (e.g., '12 months'). If not specified, return None.",
    )
    unit_price: Optional[float] = Field(None, description="Price per unit of the item")
    net_price_amount: Optional[float] = Field(
        None, description="Net price amount for the service item"
    )
    one_time_charge: Optional[Union[float, str]] = Field(
        None,
        description="One-time charge of the item or service, sometimes it shows as 'included' or other type of explaination, also record that.",
    )
    monthly_charge: Optional[Union[float, str]] = Field(
        None,
        description="Monthly charge of the item or service, sometimes it shows as 'included' or other type of explaination, also record that.",
    )
    total_price_otc_mrc: Optional[float] = Field(
        None, description="Total price (One-Time Charge + Monthly Recurring Charge)"
    )
    payment_terms: Literal["Monthly", "Quarterly", "Annually"] = Field(
        None,
        description="Whether the payment needs to be made Monthly, Quarterly or Annually",
    )
    credit_terms: Optional[str] = Field(
        None,
        description="Terms of Payment - The number of days by which the payment needs to be made",
    )
    deposit_status: Literal["Applicable", "Not Applicable"] = Field(
        None, description="Whether there is a deposit required for the service"
    )
    deposit_amount: Optional[float] = Field(
        None, description="The amount of the deposit required for the service"
    )
    credit_terms: Optional[str] = Field(
        None,
        description="Terms of Payment - The number of days by which the payment needs to be made and other terms of payment.",
    )


class Contract_response(BaseModel):
    item: List[NTT_item]
    model_config = ConfigDict(critical_fields=[])


class excel_item(BaseModel):
    """data model for excel template"""

    solution_name: str = Field(..., description="the original name of the solution")
    impact_score: int = Field(
        ge=0, le=10, description="give a impact score beteween 1-10"
    )
    feasibility_score: int = Field(
        ge=0, le=10, description="give a impact score beteween 1-10"
    )


class excel_response(BaseModel):
    item: List[excel_item]
    model_config = ConfigDict(critical_fields=[])


class FinancialStatement_item(BaseModel):
    # --- Income Statement Metrics ---
    total_revenues: float = Field(
        ..., description="Total consolidated revenues for the fiscal year."
    )
    operating_income: float = Field(
        ..., description="Consolidated operating income (or loss) for the fiscal year."
    )
    income_before_income_taxes: float = Field(
        ...,
        description="Consolidated income (or loss) before provision for income taxes.",
    )
    net_income: float = Field(
        ...,
        description="Consolidated net income (or loss) attributable to Alphabet Inc.",
    )
    earnings_per_share_diluted: float = Field(
        ...,
        description="Diluted earnings per share (EPS) for Class A, B, and C stock combined.",
    )

    # --- Balance Sheet Metrics (as of fiscal year end) ---
    cash_and_marketable_securities: float = Field(
        ..., description="Total cash, cash equivalents, and marketable securities."
    )
    total_assets: float = Field(..., description="Total consolidated assets.")
    total_liabilities: float = Field(..., description="Total consolidated liabilities.")
    total_stockholders_equity: float = Field(
        ..., description="Total stockholders' equity attributable to Alphabet Inc."
    )  # Equivalent to Net Assets

    # --- Cash Flow Metrics ---
    net_cash_from_operating_activities: float = Field(
        ...,
        description="Net cash provided by (used in) operating activities for the fiscal year.",
    )
    capital_expenditures: float = Field(
        ..., description="Purchases of property and equipment (often labeled as CapEx)."
    )


class FinancialStatement_response(BaseModel):
    item: List[FinancialStatement_item]
    model_config = ConfigDict(critical_fields=[""])


# ---------------------------------------------------------------------------------


class BoardResolutionItem(OpenAICompatibleBaseModel):
    """data model for board resolution"""

    company_name: str = Field(..., description="the name of the company")
    record_date: str = Field(
        ..., description="the date of record, output in YYYY-MM-DD format"
    )
    category: str = Field(..., description="the category of the board resolution")
    summary: str = Field(
        ..., description="the detailed summary of the board resolution"
    )


class BoardResolution_response(BaseModel):
    item: List[BoardResolutionItem]
    model_config = ConfigDict(critical_fields=["company_name"])


class Comparables(OpenAICompatibleBaseModel):
    comp_name: str = Field(
        description="The name of the comparable property for price comparison."
    )
    comp_price: Optional[float] = Field(
        None,
        description="The price of the comparable property. Express value as full numbers without abbreviations or units. If such value was presented in units, transform it into full number. If price is not available, return None.",
    )


class ValuationReportItem(OpenAICompatibleBaseModel):
    """Data model for Valuation Report extraction"""

    company_name: str = Field(
        None, description="Full Name of the company being valuated"
    )
    valuation_company: str = Field(None, description="Name of the valuation company")
    valuer_appraiser: List[str] = Field(
        None,
        description="List of Name and title of the valuer/appraiser. Please include full detail of each valuer/appraiser including title and certification & certification numbers, and as detailed as possible",
    )
    currency: str = Field(
        ..., description="currency used for this report, output in ISO4217 format"
    )
    valuation_date: str = Field(
        None,
        description="Date of valuation or report date, output in YYYY-MM-DD format",
    )
    property_name: str = Field(
        None,
        description="Name of the property and the description of the property, including postal code if any",
    )
    property_location: str = Field(
        None, description="Location of the property, including postal code if any"
    )
    asset_type: Literal[
        "Logistics",
        "Office",
        "Retail",
        "Warehouse",
        "Industrial",
        "Student Accommodation",
        "Data Centres",
        "Mixed-use",
        "Multi-Family Asset",
        "Serviced Apartment",
        "Corporate Housing",
        "Business Park",
        "Commercial",
        "Residential",
    ] = Field(..., description="define the type of the property/asset.")
    fair_value: float = Field(
        ...,
        description="Fair value/concluded value/value conclusion of the property. Express value as full numbers without abbreviations or units. If such value was presented in units, transform it into full number.",
    )
    discounted_cash_flow_method: float = Field(
        None,
        description="the value details of the Discounted Cash Flow (DCF) method used in the valuation. Extract rounded value if it's provided in the text, if not just extract the original value",
    )
    income_capitalisation_method: float = Field(
        None,
        description="the value details of Income Capitalisation Method. Extract rounded value if it's provided in the text, if not just extract the original value",
    )
    comparable_sales_method: float = Field(
        None,
        description="the value details of Comparable Sales Method. Extract rounded value if it's provided in the text, if not just extract the original value",
    )
    residual_value_method: float = Field(
        None,
        description="the value details of Residual Value Method. Extract rounded value if it's provided in the text, if not just extract the original value",
    )
    cost_method: float = Field(
        None,
        description="the value details of cost Method. Extract rounded value if it's provided in the text, if not just extract the original value",
    )
    gross_development_value: float = Field(
        None,
        description="Gross Development Value (GDV) or Gross Realization Value (GRV) of the property",
    )
    discount_rate_percentage: str = Field(
        "Not Specified", description="Discount Rate in percentage(%)"
    )
    capitalisation_rate_percentage: str = Field(
        "Not Specified", description="Capitalisation Rate in percentage (%)"
    )
    terminal_yield_percentage: str = Field(
        "Not Specified",
        description="Terminal Cap Rate/Terminal Yield in percentage (%)",
    )
    comparable: List[Comparables] = Field(
        default_factory=list,  # ensures it defaults to an empty list instead of None
        description="List of comparable properties used for price comparison. Each comparable should include the property name and its price. Extract all comparable properties mentioned in the valuation report with their respective prices.",
    )

    @field_validator(
        "discount_rate_percentage",
        "capitalisation_rate_percentage",
        "terminal_yield_percentage",
    )
    def validate_percentage_format(cls, v):
        if v is None:
            return "Not Specified"
        v_str = str(v).strip()
        if v_str.lower() in {"not specified", "n/a", ""}:
            return "Not Specified"
        if not v_str.endswith("%"):
            return f"{v_str}%"
        return v_str


class ValuationReport_response(OpenAICompatibleBaseModel):
    item: List[ValuationReportItem]


class CesCompItem(BaseModel):
    """data model for ces comparison"""

    relationships: str = Field(
        ...,
        description="interpret the following organization charts and output the relationships between entities. Display in a list format with hierarchical order and indentation, including the percentage of ownership.",
    )


class CesComp_response(BaseModel):
    item: List[CesCompItem]
    model_config = ConfigDict(critical_fields=[])


"""
Agreement Extraction Use Case - 5th May 2025
Agenda: Extract latest information from signed contracts, from pdf to scanned images
POC: Bhavesh / Owen
Use Case Personnel: Kah Yee Ang (Assurance)
"""


class AgreementExtractionItem(BaseModel):
    """Data model for Kah Yee Agreement Extraction"""

    contract_title: str = Field(
        ..., description="The official title or name of the contract."
    )
    contract_no: str = Field(
        ...,
        description="The unique contract number or identifier assigned to the contract.",
    )
    counterparty: str = Field(
        ...,
        description="The other party involved in the contract (besides your organization).",
    )
    date_of_contract: str = Field(
        ...,
        description="The date on which the contract was signed, in YYYY-MM-DD format.",
    )
    effective_start_date: str = Field(
        ...,
        description="The effective start date of the contract, in YYYY-MM-DD format.",
    )
    period_of_contract: str = Field(
        ...,
        description="The duration or period of the contract (e.g., '1 year', '2024-2025', or specific end date).",
    )
    consignor: str = Field(
        ...,
        description="The party designated as the consignor (sender/owner of goods or rights).",
    )
    consignee: str = Field(
        ...,
        description="The party designated as the consignee (receiver of goods or rights).",
    )
    remuneration_rates: str = Field(
        ...,
        description="The agreed remuneration, rates, or payment terms specified in the contract (e.g., 'USD 10,000/month', 'rate per ton').",
    )
    nature_of_service: str = Field(
        ...,
        description="A brief description of the nature or type of service provided under the contract.",
    )
    termination: str = Field(
        ...,
        description="Termination conditions, notice period, or summary of how the contract can be terminated.",
    )
    credit_terms: str = Field(
        ...,
        description="The conditions and stipulations regarding credit, including payment schedules, interest rates, and any discounts or penalties associated with late payments.",
    )
    amendments: str = Field(
        ...,
        description="Details of any changes or modifications made to the original contract terms.",
    )


class AgreementExtractionItem_response(BaseModel):
    item: List[AgreementExtractionItem]


class MAS_item(BaseModel):
    """data model for MAS correspondence"""

    # S_N: int = Field(..., description="Ordered number starting from 1, to tag emails belonging to the same email header and its summary under the same S_N, and different email header under a different running S_N. Emails with same email header might come from separate files. For example, emails about header 'A', the same S_N should be the same. Then for email with a different header 'B', the S_N should be a different one.")
    date_received: str = Field(
        ...,
        description="Extract the date of email received in DD/MM/YYYY format, if there are more than one email within the document, to output as separate summary in another row.",
    )
    # title: str = Field(..., description="Output the email header.")
    descriptions: str = Field(
        ...,
        description="Summarize the body within the email. First, provide a one-liner of 'Email from xx to yy'(bolded and underlined) where xx and yy represent the organisation. Then start a new line and provide the summary, include information such as names and dates if they are mentioned. If there is more than one email within the file, output each email's summary separately in a different row.",
    )


class MAS_response(BaseModel):
    item: List[MAS_item]

    class Config:
        critical_fields = []


class lease_agree_item(BaseModel):
    """data model for lease agreement"""

    asset_name: str = Field(
        ...,
        description="the name of the asset. This should be the address or reference name. Addresses normally contain street name, block number, unit number and postal code. Unit number starts with a # ",
    )
    asset_type: str = Field(
        ...,
        description="the type of the asset. Some keywords to look for might be 'Permitted use of premises'. Limit output options only to the following: Retail, Office, Vehicle, Equipment and Machines. Do not output generic ones like Premises, Property. If they are specific like Medical clinic, categorize it as retail.",
    )
    asset_type_reason: str = Field(
        ...,
        description="Explain why asset_type is output as such. Explain the rationale and reason",
    )
    lessor: str = Field(..., description="the name of the lessor")
    lessee: str = Field(
        ...,
        description="the name of the lessee. Output the organization or company name, which is usually addressed first before any individual's name. if not found then output person name.",
    )
    lease_start_date: str = Field(
        ...,
        description="the date of lease start stated in the agreement. Some keywords that may refer to lease start date are, 'entered into a tenancy agreement on','the term of agreement commencing on' etc. It is NOT the date of renewal agreement was made",
    )
    lease_start_date_reason: str = Field(
        ...,
        description="Explain why lease_start_date is output as such. Explain the rationale and reason",
    )
    lease_duration: str = Field(
        ..., description="the duration of the lease, state unit (month or year)"
    )
    lease_end_date: str = Field(
        ...,
        description="the date of lease end. If not stated, calculate using lease start date and lease duration.",
    )
    lease_extendable: str = Field(
        ...,
        description="whether the lease can be extended or not, or if it is not stated. Some keywords to look for, might be 'Renewal of Tenancy','Option for renewal','option to renew'. Output Yes, No or Not identified. If output is Yes or No, state the section and sentence from the document as reference.",
    )
    lease_extendable_reason: str = Field(
        ...,
        description="Explain why lease_extendable is output as such. Explain the rationale and reason",
    )
    rent_free_period: str = Field(
        ...,
        description="amount of fitting out period or rent free period, state unit (month). If not stated or stated as zero, then put 'not specifically mentioned'.",
    )
    lease_fee: str = Field(
        ...,
        description="payment amount for each month. If there are multiple periods of varying fees, extract all info and output in sample format as follows: '$[xx] monthly for [period one],$[yy] for [period two]'",
    )
    lease_payment_schedule: str = Field(
        ...,
        description="this refers to the timing of lease payments, eg. At the start of month, at the end of month etc., If output is Yes or No, state the section and sentence from the document as reference. If not stated, leave as 'not identified'.",
    )
    reinstatement_clause: str = Field(
        ...,
        description="whether there is reinstatement clause included, or if it is not stated. Output Yes, No or Not identified. If output is Yes or No, state the section and sentence from the document as reference.",
    )
    reinstatement_clause_reason: str = Field(
        ...,
        description="Explain why reinstatement_clause is output as such. Explain the rationale and reason",
    )


class lease_agree_response(BaseModel):
    item: List[lease_agree_item]
    model_config = ConfigDict(critical_fields=[])


class loan_agree_item(BaseModel):
    """data model for loan agreement"""

    principal_amount: str = Field(
        ...,
        description="output the principal amount of loan. If its truncated, like 65M, output the full sum, like 65,000,000",
    )
    currency: str = Field(
        ...,
        description="output its currency if it is identified, otherwise output 'not identified'. Output currency according to its shortform, eg. SGD, USD instead of its long form.",
    )
    maturity_date: str = Field(
        ...,
        description="output the maturity date in format 'dd-mm-yyyy'. If only loan duration is stated, calculate the maturity date if agreement date is stated. Otherwise, output the loan duration",
    )
    interest_rate: str = Field(
        ...,
        description="output the interest rate. If there are various interest rates, output all of them together, separated by comma.",
    )
    interest_rate_reason: str = Field(
        ...,
        description="Explain why interest_rate is output as such. Explain the rationale and reason, can also state the section or clause that the information falls under.",
    )
    dividend_rights: str = Field(
        ...,
        description="Output the dividend rights, look out for clause which contain keywords like 'dividends'. If it is mentioned that there are no rights or any undertaking not to pay dividends, output 'none'. Otherwise if there is no mention, strictly output 'not identified'. Be certain about each output, distinguish between 'none' and 'not identified'.",
    )
    dividend_rights_reason: str = Field(
        ...,
        description="Explain why dividend_rights is output as such. Explain the rationale and reason, can also state the section or clause that the information falls under.",
    )
    redemption_terms: str = Field(
        ...,
        description="State the redemption terms. Also look out for events resulting in immediate redemption, redemption on change of control, Event of Default, Default. Look out for phrases which state something like, 'if XXX occurs, the outstanding amount of loan shall become immediately repayable'. Otherwise, output 'not identified'. Be certain about each output.",
    )
    redemption_terms_reason: str = Field(
        ...,
        description="Explain why redemption_terms is output as such. Explain the rationale and reason, can also state the section or clause that the information falls under.",
    )
    early_repayment_option: str = Field(
        ...,
        description="output the early repayment option if there is any information. Otherwise, output 'not identified' as the early repayment option",
    )
    conversion_ratio: str = Field(
        ...,
        description="output the ratio of conversion or any information regarding conversions, such as conversion price. The conversion ratio can be either in percentage or amount. Keyword to look out for includes 'Conversion Price'. Include any additional information or elaboration regarding the conversion ratio or conversion price. If not identified, output 'not identified'. Be certain about whether it is identified or not.",
    )
    conversion_events: str = Field(
        ...,
        description="output the information on what must happen for conversion to occur. Otherwise, output 'not identified'",
    )
    conversion_events_reason: str = Field(
        ...,
        description="Explain why conversion_events is output as such. Explain the rationale and reason, can also state the section or clause that the information falls under.",
    )
    conversion_ratio_adjustment: str = Field(
        ...,
        description="output the information on adjustments to the conversion ratios. Otherwise, output 'not identified'",
    )


# to calculate the interest rate based on current and future, then use present one because actually current and present are the same, and future is irrelevant (and not accurate)
class loan_agree_response(BaseModel):
    item: List[loan_agree_item]
    model_config = ConfigDict(critical_fields=[])



class Category(str, Enum):
    violence = "violence"
    sexual = "sexual" 
    self_harm = "self_harm"


class ContentCompliance_response(BaseModel):
    """Content compliance analysis for policy violations"""
    is_violating: bool = Field(description="Whether content violates policies")
    category: Optional[Category] = Field(description="Violation category if applicable")
    explanation_if_violating: Optional[str] = Field(description="Explanation of violation")


class DocumentMetadata(BaseModel):
    """Document metadata extraction"""
    title: str = Field(description="Main title of the document")
    author: Optional[str] = Field(description="Author if mentioned")
    summary: str = Field(description="Brief summary of content")
    word_count: int = Field(description="Approximate word count", ge=0)
    key_topics: List[str] = Field(description="3-5 main topics", min_length=1, max_length=5)


class TechnicalDocAnalysis(BaseModel):
    """Technical documentation analysis"""
    programming_languages: List[str] = Field(description="Programming languages mentioned")
    code_snippets_count: int = Field(description="Number of code blocks", ge=0)
    has_installation_guide: bool = Field(description="Whether it has installation instructions")
    has_api_reference: bool = Field(description="Whether it contains API documentation")
    complexity_level: str = Field(description="Beginner, Intermediate, or Advanced")
    external_links_count: int = Field(description="Number of external links", ge=0)


# Model registry - just the models
AVAILABLE_MODELS = {
    #"UI displayed name": actual pydantic model name,
    "content_compliance": ContentCompliance_response,   
    "document_metadata": DocumentMetadata,
    "technical_analysis": TechnicalDocAnalysis,
    
    # Report and Meeting Models
    "report_summary": report_response,
    "meeting_summary": MeetingSummary_response,
    
    # Audit Models
    "it_audit": ITAudit_response,
    "it_audit_chris": ITAudit_Chris_response,
    
    # Contract and Agreement Models
    "contract_ntt": Contract_response,
    "agreement_extraction": AgreementExtractionItem_response,
    "lease_agreement": lease_agree_response,
    "loan_agreement": loan_agree_response,
    
    # Financial Models
    "financial_statement": FinancialStatement_response,
    "board_resolution": BoardResolution_response,
    "valuation_report": ValuationReport_response,
    
    # Other Models
    "excel_impact_feasibility": excel_response,
    "ces_comparison": CesComp_response,
    "mas_correspondence": MAS_response,
}
