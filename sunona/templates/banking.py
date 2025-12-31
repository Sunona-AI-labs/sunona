"""
Sunona Voice AI - Banking/Finance Template

Template for banks, financial services, and fintech.

Features:
- Account inquiries
- Balance and transactions
- Bill payments
- Card services
- Loan information
"""

from typing import List

from sunona.templates.base_template import (
    DomainTemplate, 
    ToolDefinition, 
    ExtractionField,
    ToolType,
)


class BankingTemplate(DomainTemplate):
    """
    Banking and financial services domain template.
    
    Example:
        ```python
        template = BankingTemplate(
            business_name="FirstBank",
            agent_name="Banking Assistant"
        )
        ```
    """
    
    def __init__(
        self,
        services: List[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.services = services or [
            "checking", "savings", "credit_card", 
            "loans", "investments", "insurance"
        ]
    
    @property
    def domain_name(self) -> str:
        return "banking"
    
    @property
    def domain_description(self) -> str:
        return "Banking, financial services, and account management"
    
    def get_base_prompt(self) -> str:
        return f"""# Banking Assistant

You are a customer service representative for {self.business_name}. Your role is to help customers with banking inquiries and services.

## Primary Responsibilities
1. **Account Information**: Provide balance, recent transactions, account details
2. **Bill Payments**: Help with bill payments and transfers
3. **Card Services**: Card activation, lost/stolen cards, limit changes
4. **Loan Information**: Provide loan details, payment schedules
5. **General Inquiries**: Branch locations, hours, rates

## Security Requirements
- ALWAYS verify customer identity before providing account information
- Use multi-factor authentication when required
- NEVER share full account numbers or sensitive data verbally
- If verification fails, do not proceed with the request

## Identity Verification
1. Ask for full name on the account
2. Verify date of birth or last 4 of SSN
3. Confirm registered phone number or email
4. For sensitive transactions, require additional security questions

## Services Available
- Checking and Savings Accounts
- Credit Cards
- Personal and Home Loans
- Investment Products
- Online Banking Support

## Important Disclaimers
- Investment advice should be directed to a financial advisor
- Loan approvals are subject to credit review
- This call may be recorded for quality purposes"""
    
    def get_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition(
                name="verify_customer",
                description="Verify customer identity for security",
                parameters=[
                    {"name": "account_number", "type": "string", "description": "Last 4 digits of account"},
                    {"name": "name", "type": "string", "description": "Name on account", "required": True},
                    {"name": "dob", "type": "string", "description": "Date of birth"},
                    {"name": "ssn_last4", "type": "string", "description": "Last 4 of SSN"},
                    {"name": "security_answer", "type": "string", "description": "Security question answer"},
                ],
                tool_type=ToolType.VALIDATION,
            ),
            ToolDefinition(
                name="get_account_balance",
                description="Get account balance",
                parameters=[
                    {"name": "account_id", "type": "string", "description": "Account ID", "required": True},
                    {"name": "account_type", "type": "string", "description": "Account type", "enum": ["checking", "savings", "credit_card", "loan"]},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="get_transactions",
                description="Get recent transactions",
                parameters=[
                    {"name": "account_id", "type": "string", "description": "Account ID", "required": True},
                    {"name": "days", "type": "integer", "description": "Number of days to show"},
                    {"name": "transaction_type", "type": "string", "description": "Filter by type", "enum": ["all", "credits", "debits"]},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="transfer_funds",
                description="Transfer money between accounts",
                parameters=[
                    {"name": "from_account", "type": "string", "description": "Source account", "required": True},
                    {"name": "to_account", "type": "string", "description": "Destination account", "required": True},
                    {"name": "amount", "type": "number", "description": "Transfer amount", "required": True},
                    {"name": "memo", "type": "string", "description": "Transfer memo"},
                ],
                tool_type=ToolType.PAYMENT,
            ),
            ToolDefinition(
                name="pay_bill",
                description="Make a bill payment",
                parameters=[
                    {"name": "from_account", "type": "string", "description": "Account to pay from", "required": True},
                    {"name": "payee", "type": "string", "description": "Bill payee", "required": True},
                    {"name": "amount", "type": "number", "description": "Payment amount", "required": True},
                    {"name": "pay_date", "type": "string", "description": "Payment date"},
                ],
                tool_type=ToolType.PAYMENT,
            ),
            ToolDefinition(
                name="report_lost_card",
                description="Report a lost or stolen card",
                parameters=[
                    {"name": "card_last4", "type": "string", "description": "Last 4 digits of card", "required": True},
                    {"name": "reason", "type": "string", "description": "Reason", "enum": ["lost", "stolen", "damaged"], "required": True},
                    {"name": "replacement_address", "type": "string", "description": "Address for replacement card"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="activate_card",
                description="Activate a new card",
                parameters=[
                    {"name": "card_last4", "type": "string", "description": "Last 4 digits of new card", "required": True},
                    {"name": "cvv", "type": "string", "description": "CVV for verification", "required": True},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="get_loan_details",
                description="Get loan account details",
                parameters=[
                    {"name": "loan_id", "type": "string", "description": "Loan account number", "required": True},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="make_loan_payment",
                description="Make a loan payment",
                parameters=[
                    {"name": "loan_id", "type": "string", "description": "Loan account", "required": True},
                    {"name": "from_account", "type": "string", "description": "Account to pay from", "required": True},
                    {"name": "amount", "type": "number", "description": "Payment amount", "required": True},
                ],
                tool_type=ToolType.PAYMENT,
            ),
            ToolDefinition(
                name="request_credit_limit_increase",
                description="Request credit limit increase",
                parameters=[
                    {"name": "card_id", "type": "string", "description": "Credit card account", "required": True},
                    {"name": "requested_limit", "type": "number", "description": "Requested new limit"},
                    {"name": "annual_income", "type": "number", "description": "Annual income"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="dispute_transaction",
                description="Dispute a transaction",
                parameters=[
                    {"name": "account_id", "type": "string", "description": "Account", "required": True},
                    {"name": "transaction_id", "type": "string", "description": "Transaction to dispute", "required": True},
                    {"name": "reason", "type": "string", "description": "Dispute reason", "required": True},
                    {"name": "amount", "type": "number", "description": "Disputed amount"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="get_branch_info",
                description="Get branch locations and hours",
                parameters=[
                    {"name": "zip_code", "type": "string", "description": "ZIP code to search"},
                    {"name": "city", "type": "string", "description": "City name"},
                ],
                tool_type=ToolType.DATABASE,
            ),
        ]
    
    def get_extraction_fields(self) -> List[ExtractionField]:
        return [
            ExtractionField(
                name="customer_name",
                description="Customer's full name",
                field_type="string",
                required=True,
            ),
            ExtractionField(
                name="account_number",
                description="Account number (last 4 digits only)",
                field_type="string",
            ),
            ExtractionField(
                name="date_of_birth",
                description="Customer date of birth",
                field_type="date",
            ),
            ExtractionField(
                name="phone",
                description="Registered phone number",
                field_type="string",
            ),
            ExtractionField(
                name="email",
                description="Registered email address",
                field_type="string",
            ),
            ExtractionField(
                name="account_type",
                description="Type of account",
                field_type="string",
                examples=["checking", "savings", "credit card"],
            ),
            ExtractionField(
                name="transaction_amount",
                description="Amount for transaction/transfer",
                field_type="number",
            ),
            ExtractionField(
                name="payee_name",
                description="Bill payee or transfer recipient",
                field_type="string",
            ),
            ExtractionField(
                name="card_last4",
                description="Last 4 digits of card",
                field_type="string",
            ),
            ExtractionField(
                name="issue_type",
                description="Type of issue or request",
                field_type="string",
                examples=["balance inquiry", "lost card", "dispute", "payment"],
            ),
        ]
