"""
Escalation Service for AutoBoss AI Assistant.

This service manages escalation workflows, support ticket generation,
and expert knowledge capture systems.
"""

import json
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import text, desc

from ..database import get_db_session
from ..models import (
    SupportTicket, EscalationTrigger, ExpertKnowledge, ExpertFeedback,
    AISession, AIMessage
)
from ..schemas import (
    EscalationReasonEnum, TicketPriorityEnum, TicketStatusEnum,
    FeedbackTypeEnum, CreateSupportTicketRequest, CreateExpertKnowledgeRequest,
    CreateExpertFeedbackRequest, EscalationDecisionRequest
)
from .abparts_integration import abparts_integration
from .troubleshooting_types import ConfidenceLevel

logger = logging.getLogger(__name__)


class EscalationService:
    """Service for managing escalation workflows and expert knowledge."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def evaluate_escalation_need(
        self,
        session_id: str,
        current_confidence: float,
        steps_completed: int,
        user_feedback: Optional[str] = None
    ) -> Tuple[bool, Optional[EscalationReasonEnum], Dict[str, Any]]:
        """
        Evaluate whether a troubleshooting session should be escalated.
        
        Args:
            session_id: ID of the troubleshooting session
            current_confidence: Current confidence level (0.0-1.0)
            steps_completed: Number of troubleshooting steps completed
            user_feedback: Latest user feedback
            
        Returns:
            Tuple of (should_escalate, reason, decision_factors)
        """
        decision_factors = {
            "confidence_score": current_confidence,
            "steps_completed": steps_completed,
            "confidence_threshold": 0.3,
            "max_steps_threshold": 8,
            "user_feedback_analysis": None,
            "safety_concerns": False,
            "expert_required_indicators": []
        }
        
        # Check confidence threshold
        if current_confidence < 0.3:
            self.logger.info(f"Session {session_id}: Low confidence escalation trigger ({current_confidence:.2f})")
            await self._record_escalation_trigger(
                session_id, "confidence_low", current_confidence, "escalate", 
                f"Confidence below threshold: {current_confidence:.2f}"
            )
            return True, EscalationReasonEnum.low_confidence, decision_factors
        
        # Check maximum steps threshold
        if steps_completed >= 8:
            self.logger.info(f"Session {session_id}: Max steps escalation trigger ({steps_completed} steps)")
            await self._record_escalation_trigger(
                session_id, "steps_exceeded", steps_completed, "escalate",
                f"Maximum troubleshooting steps exceeded: {steps_completed}"
            )
            return True, EscalationReasonEnum.steps_exceeded, decision_factors
        
        # Analyze user feedback for escalation indicators
        if user_feedback:
            escalation_indicators = await self._analyze_user_feedback_for_escalation(user_feedback)
            decision_factors["user_feedback_analysis"] = escalation_indicators
            
            if escalation_indicators.get("user_requests_help", False):
                self.logger.info(f"Session {session_id}: User requested escalation")
                await self._record_escalation_trigger(
                    session_id, "user_request", 1.0, "escalate",
                    "User explicitly requested expert help"
                )
                return True, EscalationReasonEnum.user_request, decision_factors
            
            if escalation_indicators.get("safety_concern", False):
                self.logger.info(f"Session {session_id}: Safety concern detected")
                decision_factors["safety_concerns"] = True
                await self._record_escalation_trigger(
                    session_id, "safety_concern", 1.0, "escalate",
                    "Safety concern detected in user feedback"
                )
                return True, EscalationReasonEnum.safety_concern, decision_factors
        
        # Check for expert-required indicators in session metadata
        expert_indicators = await self._check_expert_required_indicators(session_id)
        decision_factors["expert_required_indicators"] = expert_indicators
        
        if expert_indicators:
            self.logger.info(f"Session {session_id}: Expert required indicators found: {expert_indicators}")
            await self._record_escalation_trigger(
                session_id, "expert_required", 1.0, "escalate",
                f"Expert required indicators: {', '.join(expert_indicators)}"
            )
            return True, EscalationReasonEnum.expert_required, decision_factors
        
        # No escalation needed
        await self._record_escalation_trigger(
            session_id, "evaluation", current_confidence, "continue",
            "Escalation evaluation completed - continue troubleshooting"
        )
        return False, None, decision_factors
    
    async def _analyze_user_feedback_for_escalation(self, user_feedback: str) -> Dict[str, Any]:
        """Analyze user feedback for escalation indicators."""
        feedback_lower = user_feedback.lower()
        
        # Keywords that indicate user wants expert help
        help_keywords = [
            "help", "expert", "technician", "support", "call", "contact",
            "stuck", "confused", "don't understand", "need assistance",
            "escalate", "human", "person", "specialist"
        ]
        
        # Keywords that indicate safety concerns
        safety_keywords = [
            "dangerous", "unsafe", "risk", "hazard", "injury", "damage",
            "fire", "electrical", "shock", "leak", "pressure", "emergency"
        ]
        
        # Keywords that indicate frustration or giving up
        frustration_keywords = [
            "frustrated", "give up", "impossible", "doesn't work", "broken",
            "waste of time", "useless", "not working", "failed"
        ]
        
        return {
            "user_requests_help": any(keyword in feedback_lower for keyword in help_keywords),
            "safety_concern": any(keyword in feedback_lower for keyword in safety_keywords),
            "user_frustrated": any(keyword in feedback_lower for keyword in frustration_keywords),
            "feedback_length": len(user_feedback),
            "negative_sentiment": any(word in feedback_lower for word in ["no", "not", "can't", "won't", "doesn't"])
        }
    
    async def _check_expert_required_indicators(self, session_id: str) -> List[str]:
        """Check session metadata for expert-required indicators."""
        try:
            with get_db_session() as db:
                query = text("""
                    SELECT session_metadata FROM ai_sessions 
                    WHERE session_id = :session_id
                """)
                result = db.execute(query, {'session_id': session_id}).fetchone()
                
                if not result or not result.session_metadata:
                    return []
                
                metadata = result.session_metadata
                indicators = []
                
                # Check diagnostic assessment
                diagnostic = metadata.get("diagnostic_assessment", {})
                if diagnostic.get("requires_expert", False):
                    indicators.append("diagnostic_requires_expert")
                
                if diagnostic.get("confidence_level") == "very_low":
                    indicators.append("very_low_diagnostic_confidence")
                
                # Check for complex problem categories
                problem_category = diagnostic.get("problem_category", "")
                complex_categories = ["electrical", "hydraulic", "mechanical"]
                if problem_category in complex_categories:
                    indicators.append(f"complex_category_{problem_category}")
                
                # Check safety warnings
                safety_warnings = diagnostic.get("safety_warnings", [])
                if len(safety_warnings) > 2:
                    indicators.append("multiple_safety_warnings")
                
                return indicators
                
        except Exception as e:
            self.logger.error(f"Error checking expert required indicators: {e}")
            return []
    
    async def _record_escalation_trigger(
        self,
        session_id: str,
        trigger_type: str,
        trigger_value: float,
        decision: str,
        reason: str
    ) -> None:
        """Record escalation trigger in database."""
        try:
            with get_db_session() as db:
                trigger_id = str(uuid.uuid4())
                query = text("""
                    INSERT INTO escalation_triggers 
                    (id, session_id, trigger_type, trigger_value, escalation_decision, decision_reason, triggered_at)
                    VALUES (:id, :session_id, :trigger_type, :trigger_value, :decision, :reason, :triggered_at)
                """)
                db.execute(query, {
                    'id': trigger_id,
                    'session_id': session_id,
                    'trigger_type': trigger_type,
                    'trigger_value': trigger_value,
                    'decision': decision,
                    'reason': reason,
                    'triggered_at': datetime.utcnow()
                })
                
        except Exception as e:
            self.logger.error(f"Failed to record escalation trigger: {e}")
    
    async def create_support_ticket(
        self,
        session_id: str,
        escalation_reason: EscalationReasonEnum,
        priority: TicketPriorityEnum = TicketPriorityEnum.medium,
        additional_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a support ticket for an escalated session.
        
        Args:
            session_id: ID of the troubleshooting session
            escalation_reason: Reason for escalation
            priority: Ticket priority level
            additional_notes: Additional notes from user
            
        Returns:
            Dictionary containing ticket information
        """
        try:
            # Generate unique ticket number
            ticket_number = await self._generate_ticket_number()
            
            # Compile session data
            session_summary = await self._compile_session_summary(session_id)
            machine_context = await self._get_machine_context_for_ticket(session_id)
            expert_contact_info = await self._get_expert_contact_info(escalation_reason, machine_context)
            
            # Create support ticket
            ticket_id = str(uuid.uuid4())
            
            with get_db_session() as db:
                query = text("""
                    INSERT INTO support_tickets 
                    (id, session_id, ticket_number, priority, status, escalation_reason,
                     session_summary, machine_context, expert_contact_info, created_at, updated_at)
                    VALUES (:id, :session_id, :ticket_number, :priority, :status, :escalation_reason,
                            :session_summary, :machine_context, :expert_contact_info, :created_at, :updated_at)
                """)
                db.execute(query, {
                    'id': ticket_id,
                    'session_id': session_id,
                    'ticket_number': ticket_number,
                    'priority': priority.value,
                    'status': TicketStatusEnum.open.value,
                    'escalation_reason': escalation_reason.value,
                    'session_summary': session_summary,
                    'machine_context': json.dumps(machine_context) if machine_context else None,
                    'expert_contact_info': json.dumps(expert_contact_info) if expert_contact_info else None,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                })
            
            # Update session status to escalated
            await self._update_session_status_escalated(session_id, ticket_number)
            
            self.logger.info(f"Created support ticket {ticket_number} for session {session_id}")
            
            return {
                "ticket_id": ticket_id,
                "ticket_number": ticket_number,
                "priority": priority.value,
                "status": TicketStatusEnum.open.value,
                "session_summary": session_summary,
                "machine_context": machine_context,
                "expert_contact_info": expert_contact_info,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create support ticket: {e}")
            raise
    
    async def _generate_ticket_number(self) -> str:
        """Generate unique ticket number."""
        # Format: AB-YYYYMMDD-NNNN (AutoBoss-Date-Sequential)
        date_str = datetime.now().strftime("%Y%m%d")
        
        try:
            with get_db_session() as db:
                # Get count of tickets created today
                query = text("""
                    SELECT COUNT(*) as count FROM support_tickets 
                    WHERE ticket_number LIKE :pattern
                """)
                result = db.execute(query, {'pattern': f'AB-{date_str}-%'}).fetchone()
                count = result.count if result else 0
                
                return f"AB-{date_str}-{count + 1:04d}"
                
        except Exception as e:
            self.logger.error(f"Error generating ticket number: {e}")
            # Fallback to timestamp-based number
            timestamp = int(datetime.now().timestamp())
            return f"AB-{date_str}-{timestamp % 10000:04d}"
    
    async def _compile_session_summary(self, session_id: str) -> str:
        """Compile comprehensive session summary for support ticket."""
        try:
            # Get session data
            with get_db_session() as db:
                # Get session info
                session_query = text("""
                    SELECT user_id, machine_id, status, language, session_metadata, created_at
                    FROM ai_sessions WHERE session_id = :session_id
                """)
                session_result = db.execute(session_query, {'session_id': session_id}).fetchone()
                
                if not session_result:
                    return "Session data not found"
                
                # Get messages
                messages_query = text("""
                    SELECT sender, content, message_type, timestamp
                    FROM ai_messages 
                    WHERE session_id = :session_id 
                    ORDER BY timestamp ASC
                """)
                messages = db.execute(messages_query, {'session_id': session_id}).fetchall()
                
                # Get troubleshooting steps
                steps_query = text("""
                    SELECT step_number, instruction, user_feedback, completed, success
                    FROM troubleshooting_steps 
                    WHERE session_id = :session_id 
                    ORDER BY step_number ASC
                """)
                steps = db.execute(steps_query, {'session_id': session_id}).fetchall()
            
            # Build summary
            summary_parts = []
            
            # Session overview
            metadata = session_result.session_metadata or {}
            diagnostic = metadata.get("diagnostic_assessment", {})
            
            summary_parts.append("=== TROUBLESHOOTING SESSION SUMMARY ===")
            summary_parts.append(f"Session ID: {session_id}")
            summary_parts.append(f"Created: {session_result.created_at}")
            summary_parts.append(f"Language: {session_result.language}")
            summary_parts.append(f"Machine ID: {session_result.machine_id or 'Not specified'}")
            summary_parts.append("")
            
            # Diagnostic assessment
            if diagnostic:
                summary_parts.append("=== INITIAL DIAGNOSTIC ASSESSMENT ===")
                summary_parts.append(f"Problem Category: {diagnostic.get('problem_category', 'Unknown')}")
                summary_parts.append(f"Confidence Level: {diagnostic.get('confidence_level', 'Unknown')}")
                summary_parts.append(f"Likely Causes: {', '.join(diagnostic.get('likely_causes', []))}")
                summary_parts.append(f"Safety Warnings: {', '.join(diagnostic.get('safety_warnings', []))}")
                summary_parts.append(f"Requires Expert: {diagnostic.get('requires_expert', False)}")
                summary_parts.append("")
            
            # Troubleshooting steps
            if steps:
                summary_parts.append("=== TROUBLESHOOTING STEPS ATTEMPTED ===")
                for step in steps:
                    status = "✓ Completed" if step.completed else "⏳ In Progress"
                    success = " (Successful)" if step.success else " (Unsuccessful)" if step.completed else ""
                    summary_parts.append(f"Step {step.step_number}: {step.instruction} - {status}{success}")
                    if step.user_feedback:
                        summary_parts.append(f"  User Feedback: {step.user_feedback}")
                summary_parts.append("")
            
            # Conversation highlights
            if messages:
                summary_parts.append("=== CONVERSATION HIGHLIGHTS ===")
                user_messages = [msg for msg in messages if msg.sender == "user"]
                for i, msg in enumerate(user_messages[-3:], 1):  # Last 3 user messages
                    summary_parts.append(f"User Message {i}: {msg.content[:200]}{'...' if len(msg.content) > 200 else ''}")
                summary_parts.append("")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            self.logger.error(f"Error compiling session summary: {e}")
            return f"Error compiling session summary: {str(e)}"
    
    async def _get_machine_context_for_ticket(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get machine context for support ticket."""
        try:
            with get_db_session() as db:
                query = text("""
                    SELECT machine_id, session_metadata FROM ai_sessions 
                    WHERE session_id = :session_id
                """)
                result = db.execute(query, {'session_id': session_id}).fetchone()
                
                if not result or not result.machine_id:
                    return None
                
                # Get machine details from ABParts integration
                machine_details = await abparts_integration.get_machine_details(result.machine_id)
                if not machine_details:
                    return None
                
                # Get additional context from session metadata
                metadata = result.session_metadata or {}
                machine_context = metadata.get("machine_context", {})
                
                return {
                    "machine_details": machine_details,
                    "maintenance_history": machine_context.get("recent_maintenance", []),
                    "parts_usage": machine_context.get("recent_parts_usage", []),
                    "hours_history": machine_context.get("hours_history", []),
                    "maintenance_suggestions": machine_context.get("maintenance_suggestions", [])
                }
                
        except Exception as e:
            self.logger.error(f"Error getting machine context: {e}")
            return None
    
    async def _get_expert_contact_info(
        self, 
        escalation_reason: EscalationReasonEnum, 
        machine_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get appropriate expert contact information based on escalation reason and machine context."""
        
        # Default expert contact information
        expert_contacts = {
            "general_support": {
                "name": "AutoBoss Technical Support",
                "email": "support@autoboss.com",
                "phone": "+1-800-AUTOBOSS",
                "hours": "Monday-Friday 8AM-6PM EST",
                "specialization": "General troubleshooting and maintenance"
            },
            "electrical_specialist": {
                "name": "AutoBoss Electrical Systems",
                "email": "electrical@autoboss.com", 
                "phone": "+1-800-AUTOBOSS ext. 201",
                "hours": "Monday-Friday 9AM-5PM EST",
                "specialization": "Electrical systems and control panels"
            },
            "hydraulic_specialist": {
                "name": "AutoBoss Hydraulic Systems",
                "email": "hydraulic@autoboss.com",
                "phone": "+1-800-AUTOBOSS ext. 202", 
                "hours": "Monday-Friday 9AM-5PM EST",
                "specialization": "Hydraulic systems and pressure issues"
            },
            "emergency_support": {
                "name": "AutoBoss Emergency Support",
                "email": "emergency@autoboss.com",
                "phone": "+1-800-AUTOBOSS ext. 911",
                "hours": "24/7 Emergency Line",
                "specialization": "Safety concerns and emergency situations"
            }
        }
        
        # Determine appropriate contact based on escalation reason
        if escalation_reason == EscalationReasonEnum.safety_concern:
            primary_contact = expert_contacts["emergency_support"]
        elif machine_context:
            # Check diagnostic assessment for problem category
            diagnostic = machine_context.get("diagnostic_assessment", {})
            problem_category = diagnostic.get("problem_category", "")
            
            if problem_category == "electrical":
                primary_contact = expert_contacts["electrical_specialist"]
            elif problem_category == "hydraulic":
                primary_contact = expert_contacts["hydraulic_specialist"]
            else:
                primary_contact = expert_contacts["general_support"]
        else:
            primary_contact = expert_contacts["general_support"]
        
        return {
            "primary_contact": primary_contact,
            "alternative_contacts": [
                expert_contacts["general_support"],
                expert_contacts["emergency_support"]
            ],
            "escalation_reason": escalation_reason.value,
            "recommended_action": "Contact primary expert for immediate assistance",
            "ticket_reference": "Provide this ticket number when contacting support"
        }
    
    async def _update_session_status_escalated(self, session_id: str, ticket_number: str) -> None:
        """Update session status to escalated."""
        try:
            with get_db_session() as db:
                query = text("""
                    UPDATE ai_sessions 
                    SET status = 'escalated', 
                        resolution_summary = :resolution_summary,
                        updated_at = NOW()
                    WHERE session_id = :session_id
                """)
                db.execute(query, {
                    'session_id': session_id,
                    'resolution_summary': f"Escalated to expert support - Ticket #{ticket_number}"
                })
                
        except Exception as e:
            self.logger.error(f"Failed to update session status: {e}")
    
    async def create_expert_knowledge(
        self,
        expert_user_id: str,
        problem_description: str,
        solution: str,
        machine_version: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create new expert knowledge entry.
        
        Args:
            expert_user_id: ID of the expert user
            problem_description: Description of the problem
            solution: Expert solution
            machine_version: Applicable machine version
            tags: Knowledge tags
            metadata: Additional metadata
            
        Returns:
            Dictionary containing knowledge entry information
        """
        try:
            knowledge_id = str(uuid.uuid4())
            
            with get_db_session() as db:
                query = text("""
                    INSERT INTO expert_knowledge 
                    (id, expert_user_id, problem_description, solution, machine_version, 
                     tags, verified, expert_metadata, created_at, updated_at)
                    VALUES (:id, :expert_user_id, :problem_description, :solution, :machine_version,
                            :tags, :verified, :metadata, :created_at, :updated_at)
                """)
                db.execute(query, {
                    'id': knowledge_id,
                    'expert_user_id': expert_user_id,
                    'problem_description': problem_description,
                    'solution': solution,
                    'machine_version': machine_version,
                    'tags': json.dumps(tags or []),
                    'verified': False,  # Requires verification by default
                    'metadata': json.dumps(metadata or {}),
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                })
            
            self.logger.info(f"Created expert knowledge entry {knowledge_id}")
            
            return {
                "knowledge_id": knowledge_id,
                "expert_user_id": expert_user_id,
                "problem_description": problem_description,
                "solution": solution,
                "machine_version": machine_version,
                "tags": tags or [],
                "verified": False,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create expert knowledge: {e}")
            raise
    
    async def create_expert_feedback(
        self,
        session_id: str,
        expert_user_id: str,
        feedback_type: FeedbackTypeEnum,
        rating: int,
        message_id: Optional[str] = None,
        feedback_text: Optional[str] = None,
        suggested_improvement: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create expert feedback on AI responses.
        
        Args:
            session_id: ID of the troubleshooting session
            expert_user_id: ID of the expert user
            feedback_type: Type of feedback
            rating: Rating from 1-5
            message_id: ID of the specific AI message (optional)
            feedback_text: Detailed feedback text
            suggested_improvement: Suggested improvement
            
        Returns:
            Dictionary containing feedback information
        """
        try:
            feedback_id = str(uuid.uuid4())
            
            with get_db_session() as db:
                query = text("""
                    INSERT INTO expert_feedback 
                    (id, session_id, message_id, expert_user_id, feedback_type, rating,
                     feedback_text, suggested_improvement, created_at)
                    VALUES (:id, :session_id, :message_id, :expert_user_id, :feedback_type, :rating,
                            :feedback_text, :suggested_improvement, :created_at)
                """)
                db.execute(query, {
                    'id': feedback_id,
                    'session_id': session_id,
                    'message_id': message_id,
                    'expert_user_id': expert_user_id,
                    'feedback_type': feedback_type.value,
                    'rating': rating,
                    'feedback_text': feedback_text,
                    'suggested_improvement': suggested_improvement,
                    'created_at': datetime.utcnow()
                })
            
            self.logger.info(f"Created expert feedback {feedback_id} for session {session_id}")
            
            return {
                "feedback_id": feedback_id,
                "session_id": session_id,
                "message_id": message_id,
                "expert_user_id": expert_user_id,
                "feedback_type": feedback_type.value,
                "rating": rating,
                "feedback_text": feedback_text,
                "suggested_improvement": suggested_improvement,
                "created_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create expert feedback: {e}")
            raise
    
    async def get_expert_knowledge_for_integration(
        self, 
        problem_keywords: List[str],
        machine_version: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve expert knowledge for integration into troubleshooting responses.
        
        Args:
            problem_keywords: Keywords to search for
            machine_version: Filter by machine version
            limit: Maximum number of results
            
        Returns:
            List of relevant expert knowledge entries
        """
        try:
            with get_db_session() as db:
                # Build search query
                search_conditions = []
                params = {'limit': limit}
                
                if problem_keywords:
                    # Simple keyword search in problem description and solution
                    keyword_conditions = []
                    for i, keyword in enumerate(problem_keywords[:3]):  # Limit to 3 keywords
                        keyword_conditions.append(f"(LOWER(problem_description) LIKE :keyword_{i} OR LOWER(solution) LIKE :keyword_{i})")
                        params[f'keyword_{i}'] = f'%{keyword.lower()}%'
                    
                    if keyword_conditions:
                        search_conditions.append(f"({' OR '.join(keyword_conditions)})")
                
                if machine_version:
                    search_conditions.append("(machine_version = :machine_version OR machine_version IS NULL)")
                    params['machine_version'] = machine_version
                
                # Only include verified knowledge
                search_conditions.append("verified = true")
                
                where_clause = " AND ".join(search_conditions) if search_conditions else "verified = true"
                
                query = text(f"""
                    SELECT id, expert_user_id, problem_description, solution, machine_version, 
                           tags, created_at, updated_at
                    FROM expert_knowledge 
                    WHERE {where_clause}
                    ORDER BY created_at DESC
                    LIMIT :limit
                """)
                
                results = db.execute(query, params).fetchall()
                
                knowledge_entries = []
                for row in results:
                    knowledge_entries.append({
                        "knowledge_id": str(row.id),
                        "expert_user_id": str(row.expert_user_id),
                        "problem_description": row.problem_description,
                        "solution": row.solution,
                        "machine_version": row.machine_version,
                        "tags": json.loads(row.tags) if row.tags else [],
                        "created_at": row.created_at.isoformat(),
                        "updated_at": row.updated_at.isoformat()
                    })
                
                self.logger.info(f"Retrieved {len(knowledge_entries)} expert knowledge entries")
                return knowledge_entries
                
        except Exception as e:
            self.logger.error(f"Error retrieving expert knowledge: {e}")
            return []


# Global instance
escalation_service = EscalationService()