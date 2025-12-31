"""
Sunona Voice AI - Healthcare Template

Template for medical clinics, hospitals, and healthcare services.

Features:
- Appointment scheduling
- Patient registration
- Prescription refills
- Test results
- Insurance verification
"""

from typing import List

from sunona.templates.base_template import (
    DomainTemplate, 
    ToolDefinition, 
    ExtractionField,
    ToolType,
)


class HealthcareTemplate(DomainTemplate):
    """
    Healthcare domain template.
    
    Example:
        ```python
        template = HealthcareTemplate(
            business_name="City Medical Center",
            facility_type="clinic"
        )
        ```
    """
    
    def __init__(
        self,
        facility_type: str = "clinic",
        departments: List[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.facility_type = facility_type
        self.departments = departments or [
            "General Medicine", "Pediatrics", "Cardiology",
            "Orthopedics", "Dermatology", "Gynecology"
        ]
    
    @property
    def domain_name(self) -> str:
        return "healthcare"
    
    @property
    def domain_description(self) -> str:
        return "Medical appointments, patient services, and healthcare"
    
    def get_base_prompt(self) -> str:
        dept_list = ", ".join(self.departments)
        
        return f"""# Healthcare Assistant

You are a patient services assistant for {self.business_name}. Your role is to help patients with appointments and inquiries.

## Primary Responsibilities
1. **Appointment Scheduling**: Schedule, reschedule, or cancel appointments
2. **Patient Support**: Answer questions about services and procedures
3. **Prescription Refills**: Assist with medication refill requests
4. **Insurance Verification**: Help verify insurance coverage
5. **General Information**: Provide facility hours, locations, directions

## Important Guidelines
- NEVER provide medical advice or diagnoses
- Always recommend consulting with a healthcare provider for medical concerns
- Maintain patient confidentiality (HIPAA compliance)
- Verify patient identity before accessing records

## Available Departments
{dept_list}

## Appointment Process
1. Verify patient identity (name, date of birth)
2. Understand the reason for visit
3. Check doctor/department availability
4. Schedule appointment at convenient time
5. Confirm insurance information
6. Provide appointment details and preparation instructions

## Emergency Protocol
If a patient describes a medical emergency:
- Advise them to call 911 immediately
- Do NOT attempt to provide medical advice
- Offer to connect them with emergency services"""
    
    def get_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition(
                name="lookup_patient",
                description="Look up patient records",
                parameters=[
                    {"name": "patient_id", "type": "string", "description": "Patient ID/MRN"},
                    {"name": "name", "type": "string", "description": "Patient name"},
                    {"name": "date_of_birth", "type": "string", "description": "Date of birth for verification", "required": True},
                    {"name": "phone", "type": "string", "description": "Phone number"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="check_availability",
                description="Check appointment availability",
                parameters=[
                    {"name": "department", "type": "string", "description": "Department or specialty", "required": True},
                    {"name": "doctor", "type": "string", "description": "Specific doctor name"},
                    {"name": "date", "type": "string", "description": "Preferred date"},
                    {"name": "time_preference", "type": "string", "description": "Time preference", "enum": ["morning", "afternoon", "any"]},
                ],
                tool_type=ToolType.CALENDAR,
            ),
            ToolDefinition(
                name="schedule_appointment",
                description="Schedule a new appointment",
                parameters=[
                    {"name": "patient_id", "type": "string", "description": "Patient ID", "required": True},
                    {"name": "department", "type": "string", "description": "Department", "required": True},
                    {"name": "doctor", "type": "string", "description": "Doctor name"},
                    {"name": "date", "type": "string", "description": "Appointment date", "required": True},
                    {"name": "time", "type": "string", "description": "Appointment time", "required": True},
                    {"name": "reason", "type": "string", "description": "Reason for visit", "required": True},
                    {"name": "appointment_type", "type": "string", "description": "Type", "enum": ["new_patient", "follow_up", "consultation", "procedure"]},
                ],
                tool_type=ToolType.CALENDAR,
            ),
            ToolDefinition(
                name="reschedule_appointment",
                description="Reschedule an existing appointment",
                parameters=[
                    {"name": "appointment_id", "type": "string", "description": "Appointment to reschedule", "required": True},
                    {"name": "new_date", "type": "string", "description": "New date", "required": True},
                    {"name": "new_time", "type": "string", "description": "New time", "required": True},
                ],
                tool_type=ToolType.CALENDAR,
            ),
            ToolDefinition(
                name="cancel_appointment",
                description="Cancel an appointment",
                parameters=[
                    {"name": "appointment_id", "type": "string", "description": "Appointment to cancel", "required": True},
                    {"name": "reason", "type": "string", "description": "Cancellation reason"},
                ],
                tool_type=ToolType.CALENDAR,
            ),
            ToolDefinition(
                name="request_prescription_refill",
                description="Request a prescription refill",
                parameters=[
                    {"name": "patient_id", "type": "string", "description": "Patient ID", "required": True},
                    {"name": "medication_name", "type": "string", "description": "Medication name", "required": True},
                    {"name": "pharmacy", "type": "string", "description": "Preferred pharmacy"},
                    {"name": "pharmacy_phone", "type": "string", "description": "Pharmacy phone"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="verify_insurance",
                description="Verify insurance coverage",
                parameters=[
                    {"name": "patient_id", "type": "string", "description": "Patient ID", "required": True},
                    {"name": "insurance_provider", "type": "string", "description": "Insurance company"},
                    {"name": "member_id", "type": "string", "description": "Member/Policy ID"},
                    {"name": "service_type", "type": "string", "description": "Service to verify coverage for"},
                ],
                tool_type=ToolType.VALIDATION,
            ),
            ToolDefinition(
                name="get_appointment_details",
                description="Get details of upcoming appointments",
                parameters=[
                    {"name": "patient_id", "type": "string", "description": "Patient ID", "required": True},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="send_appointment_reminder",
                description="Send appointment reminder to patient",
                parameters=[
                    {"name": "appointment_id", "type": "string", "description": "Appointment", "required": True},
                    {"name": "method", "type": "string", "description": "Reminder method", "enum": ["sms", "email", "call"]},
                ],
                tool_type=ToolType.NOTIFICATION,
            ),
        ]
    
    def get_extraction_fields(self) -> List[ExtractionField]:
        return [
            ExtractionField(
                name="patient_name",
                description="Patient's full name",
                field_type="string",
                required=True,
            ),
            ExtractionField(
                name="date_of_birth",
                description="Patient date of birth for verification",
                field_type="date",
                required=True,
                examples=["1985-03-15", "March 15 1985"],
            ),
            ExtractionField(
                name="phone",
                description="Contact phone number",
                field_type="string",
                required=True,
            ),
            ExtractionField(
                name="patient_id",
                description="Patient ID or medical record number",
                field_type="string",
            ),
            ExtractionField(
                name="reason_for_visit",
                description="Reason for the appointment",
                field_type="string",
                required=True,
            ),
            ExtractionField(
                name="department",
                description="Department or specialty needed",
                field_type="string",
            ),
            ExtractionField(
                name="preferred_doctor",
                description="Preferred doctor name",
                field_type="string",
            ),
            ExtractionField(
                name="preferred_date",
                description="Preferred appointment date",
                field_type="date",
            ),
            ExtractionField(
                name="preferred_time",
                description="Preferred time of day",
                field_type="string",
                examples=["morning", "afternoon", "after 3pm"],
            ),
            ExtractionField(
                name="insurance_provider",
                description="Insurance company name",
                field_type="string",
            ),
            ExtractionField(
                name="insurance_id",
                description="Insurance member ID",
                field_type="string",
            ),
            ExtractionField(
                name="medication_name",
                description="Medication for refill request",
                field_type="string",
            ),
        ]
