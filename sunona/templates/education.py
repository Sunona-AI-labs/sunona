"""
Sunona Voice AI - Education Template

Template for educational, tutoring, and enrollment services.
"""

from typing import List

from sunona.templates.base_template import (
    DomainTemplate, 
    ToolDefinition, 
    ExtractionField,
    ToolType,
)


class EducationTemplate(DomainTemplate):
    """Education and tutoring domain template."""
    
    def __init__(self, institution_type: str = "school", **kwargs):
        super().__init__(**kwargs)
        self.institution_type = institution_type
    
    @property
    def domain_name(self) -> str:
        return "education"
    
    @property
    def domain_description(self) -> str:
        return "Educational institutions, tutoring, and enrollment services"
    
    def get_base_prompt(self) -> str:
        return f"""# Education Assistant

You are an assistant for {self.business_name}. Help students, parents, and faculty with educational inquiries.

## Responsibilities
1. Course information and enrollment
2. Scheduling classes and tutoring sessions
3. Fee inquiries and payment support
4. Academic advising
5. General campus information"""
    
    def get_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition(name="lookup_student", description="Look up student information", 
                          parameters=[{"name": "student_id", "type": "string", "required": True}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="list_courses", description="List available courses",
                          parameters=[{"name": "subject", "type": "string"}, {"name": "level", "type": "string"}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="check_enrollment", description="Check course enrollment status",
                          parameters=[{"name": "course_id", "type": "string", "required": True}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="enroll_student", description="Enroll student in course",
                          parameters=[{"name": "student_id", "type": "string", "required": True}, {"name": "course_id", "type": "string", "required": True}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="schedule_tutoring", description="Schedule tutoring session",
                          parameters=[{"name": "subject", "type": "string", "required": True}, {"name": "date", "type": "string", "required": True}], tool_type=ToolType.CALENDAR),
            ToolDefinition(name="get_fee_info", description="Get fee and payment information",
                          parameters=[{"name": "student_id", "type": "string"}, {"name": "term", "type": "string"}], tool_type=ToolType.DATABASE),
            ToolDefinition(name="process_payment", description="Process tuition payment",
                          parameters=[{"name": "student_id", "type": "string", "required": True}, {"name": "amount", "type": "number", "required": True}], tool_type=ToolType.PAYMENT),
            ToolDefinition(name="get_schedule", description="Get class schedule",
                          parameters=[{"name": "student_id", "type": "string", "required": True}], tool_type=ToolType.DATABASE),
        ]
    
    def get_extraction_fields(self) -> List[ExtractionField]:
        return [
            ExtractionField(name="student_name", description="Student's full name", field_type="string", required=True),
            ExtractionField(name="student_id", description="Student ID number", field_type="string"),
            ExtractionField(name="parent_name", description="Parent/guardian name", field_type="string"),
            ExtractionField(name="email", description="Email address", field_type="string"),
            ExtractionField(name="phone", description="Phone number", field_type="string"),
            ExtractionField(name="grade_level", description="Grade or year level", field_type="string"),
            ExtractionField(name="subject", description="Subject of interest", field_type="string"),
            ExtractionField(name="course_name", description="Course name", field_type="string"),
        ]
