"""
Sunona Voice AI - Recruitment Template

Template for HR, hiring, and interview scheduling.

Features:
- Interview scheduling
- Candidate screening
- Application status
- Skill assessment
- Job information
"""

from typing import List

from sunona.templates.base_template import (
    DomainTemplate, 
    ToolDefinition, 
    ExtractionField,
    ToolType,
)


class RecruitmentTemplate(DomainTemplate):
    """
    Recruitment and HR domain template.
    
    Example:
        ```python
        template = RecruitmentTemplate(
            business_name="TechCorp",
            agent_name="HR Assistant"
        )
        ```
    """
    
    def __init__(
        self,
        interview_types: List[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.interview_types = interview_types or ["phone", "video", "in_person"]
    
    @property
    def domain_name(self) -> str:
        return "recruitment"
    
    @property
    def domain_description(self) -> str:
        return "Hiring, interviews, and HR services"
    
    def get_base_prompt(self) -> str:
        return f"""# Recruitment Assistant

You are an HR recruitment assistant for {self.business_name}. Your role is to help with the hiring process.

## Primary Responsibilities
1. **Candidate Screening**: Conduct initial phone screenings
2. **Interview Scheduling**: Schedule interviews with candidates
3. **Job Information**: Provide details about open positions
4. **Application Status**: Update candidates on their application status
5. **Skill Assessment**: Conduct basic skill assessments

## Screening Guidelines
- Be professional but welcoming
- Ask about experience, skills, and availability
- Verify basic qualifications
- Note any concerns or highlights
- Always end with clear next steps

## Interview Process
1. Verify candidate identity and application
2. Explain the interview process
3. Conduct structured screening questions
4. Assess communication and cultural fit
5. Schedule next round if qualified
6. Provide timeline for feedback

## Key Questions to Ask
- Tell me about your relevant experience
- Why are you interested in this role?
- What are your salary expectations?
- When can you start?
- Are you authorized to work in this location?"""
    
    def get_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition(
                name="lookup_candidate",
                description="Look up candidate application and history",
                parameters=[
                    {"name": "email", "type": "string", "description": "Candidate email"},
                    {"name": "phone", "type": "string", "description": "Phone number"},
                    {"name": "application_id", "type": "string", "description": "Application ID"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="lookup_job",
                description="Get details about a job opening",
                parameters=[
                    {"name": "job_id", "type": "string", "description": "Job ID"},
                    {"name": "title", "type": "string", "description": "Job title to search"},
                    {"name": "department", "type": "string", "description": "Department"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="list_open_positions",
                description="List all open job positions",
                parameters=[
                    {"name": "department", "type": "string", "description": "Filter by department"},
                    {"name": "location", "type": "string", "description": "Filter by location"},
                    {"name": "job_type", "type": "string", "description": "Job type", "enum": ["full_time", "part_time", "contract", "internship"]},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="schedule_interview",
                description="Schedule an interview for a candidate",
                parameters=[
                    {"name": "candidate_id", "type": "string", "description": "Candidate ID", "required": True},
                    {"name": "job_id", "type": "string", "description": "Job position", "required": True},
                    {"name": "interview_type", "type": "string", "description": "Type of interview", "enum": ["phone", "video", "in_person"], "required": True},
                    {"name": "date", "type": "string", "description": "Preferred date", "required": True},
                    {"name": "time", "type": "string", "description": "Preferred time", "required": True},
                    {"name": "interviewer", "type": "string", "description": "Interviewer name"},
                ],
                tool_type=ToolType.CALENDAR,
            ),
            ToolDefinition(
                name="check_interviewer_availability",
                description="Check interviewer availability for scheduling",
                parameters=[
                    {"name": "date", "type": "string", "description": "Date to check", "required": True},
                    {"name": "interviewer", "type": "string", "description": "Specific interviewer"},
                    {"name": "department", "type": "string", "description": "Department"},
                ],
                tool_type=ToolType.CALENDAR,
            ),
            ToolDefinition(
                name="update_application_status",
                description="Update candidate application status",
                parameters=[
                    {"name": "application_id", "type": "string", "description": "Application to update", "required": True},
                    {"name": "status", "type": "string", "description": "New status", "enum": ["screening", "interview_scheduled", "interviewed", "offer_pending", "hired", "rejected"], "required": True},
                    {"name": "notes", "type": "string", "description": "Status notes"},
                    {"name": "feedback", "type": "string", "description": "Interview feedback"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="record_screening_notes",
                description="Record notes from candidate screening",
                parameters=[
                    {"name": "candidate_id", "type": "string", "description": "Candidate", "required": True},
                    {"name": "experience_rating", "type": "integer", "description": "Experience rating 1-5"},
                    {"name": "communication_rating", "type": "integer", "description": "Communication rating 1-5"},
                    {"name": "notes", "type": "string", "description": "Screening notes", "required": True},
                    {"name": "recommend_proceed", "type": "boolean", "description": "Recommend to proceed"},
                ],
                tool_type=ToolType.DATABASE,
            ),
            ToolDefinition(
                name="send_interview_invitation",
                description="Send interview invitation to candidate",
                parameters=[
                    {"name": "candidate_id", "type": "string", "description": "Candidate to invite", "required": True},
                    {"name": "interview_details", "type": "string", "description": "Interview details", "required": True},
                    {"name": "calendar_link", "type": "string", "description": "Calendar invite link"},
                ],
                tool_type=ToolType.NOTIFICATION,
            ),
        ]
    
    def get_extraction_fields(self) -> List[ExtractionField]:
        return [
            ExtractionField(
                name="candidate_name",
                description="Candidate's full name",
                field_type="string",
                required=True,
            ),
            ExtractionField(
                name="email",
                description="Candidate email",
                field_type="string",
                required=True,
            ),
            ExtractionField(
                name="phone",
                description="Contact phone number",
                field_type="string",
                required=True,
            ),
            ExtractionField(
                name="job_title",
                description="Position applied for",
                field_type="string",
            ),
            ExtractionField(
                name="years_experience",
                description="Years of relevant experience",
                field_type="integer",
            ),
            ExtractionField(
                name="current_company",
                description="Current or most recent employer",
                field_type="string",
            ),
            ExtractionField(
                name="salary_expectation",
                description="Expected salary or range",
                field_type="string",
            ),
            ExtractionField(
                name="availability",
                description="Availability to start",
                field_type="string",
                examples=["immediately", "2 weeks", "1 month"],
            ),
            ExtractionField(
                name="key_skills",
                description="Key skills mentioned",
                field_type="string",
            ),
            ExtractionField(
                name="preferred_interview_time",
                description="Preferred interview date/time",
                field_type="string",
            ),
        ]
