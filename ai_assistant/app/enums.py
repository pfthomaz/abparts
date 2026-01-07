"""
Enums for the AI Assistant service.
"""

import enum


class SessionStatus(enum.Enum):
    """Status of a troubleshooting session."""
    active = "active"
    completed = "completed"
    escalated = "escalated"
    abandoned = "abandoned"


class MessageSender(enum.Enum):
    """Who sent the message."""
    user = "user"
    assistant = "assistant"
    system = "system"


class MessageType(enum.Enum):
    """Type of message content."""
    text = "text"
    voice = "voice"
    image = "image"
    diagnostic_step = "diagnostic_step"
    escalation = "escalation"


class DocumentType(enum.Enum):
    """Type of knowledge document."""
    manual = "manual"
    procedure = "procedure"
    faq = "faq"
    expert_input = "expert_input"
    troubleshooting_guide = "troubleshooting_guide"