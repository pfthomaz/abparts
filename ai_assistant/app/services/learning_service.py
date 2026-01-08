"""
Learning service for AI Assistant continuous improvement and solution prioritization.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func, desc
import json
from dataclasses import dataclass

from ..database import get_db
from .analytics_service import analytics_service

logger = logging.getLogger(__name__)


@dataclass
class SolutionPriority:
    """Solution priority data structure."""
    solution_text: str
    problem_category: str
    machine_model: Optional[str]
    priority_score: float
    success_rate: float
    times_used: int
    avg_effectiveness: float
    recency_factor: float
    expert_verified: bool


@dataclass
class LearningInsight:
    """Learning insight from historical data."""
    insight_type: str  # pattern, trend, anomaly, recommendation
    description: str
    confidence: float
    supporting_data: Dict[str, Any]
    actionable_recommendation: str


class LearningService:
    """Service for continuous learning and solution prioritization."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def prioritize_solutions(
        self,
        db: Session,
        problem_category: str,
        machine_model: Optional[str] = None,
        limit: int = 10
    ) -> List[SolutionPriority]:
        """
        Prioritize solutions based on historical success, recency, and expert verification.
        """
        try:
            # Build query with optional machine model filter
            machine_filter = ""
            params = {
                "problem_category": problem_category,
                "limit": limit,
                "days_ago": 90  # Consider solutions from last 90 days for recency
            }
            
            if machine_model:
                machine_filter = "AND (machine_model = :machine_model OR machine_model IS NULL)"
                params["machine_model"] = machine_model
            
            query = text(f"""
                SELECT 
                    solution_text,
                    problem_category,
                    machine_model,
                    success_rate,
                    times_suggested,
                    times_successful,
                    expert_verified,
                    AVG(CASE 
                        WHEN effectiveness = 'very_effective' THEN 4
                        WHEN effectiveness = 'effective' THEN 3
                        WHEN effectiveness = 'somewhat_effective' THEN 2
                        ELSE 1 
                    END) as avg_effectiveness,
                    MAX(updated_at) as last_used,
                    -- Recency factor: more recent = higher score
                    CASE 
                        WHEN MAX(updated_at) > NOW() - INTERVAL ':days_ago days' THEN 1.0
                        ELSE 0.5 + (EXTRACT(EPOCH FROM (MAX(updated_at) - (NOW() - INTERVAL ':days_ago days'))) / 
                                   EXTRACT(EPOCH FROM INTERVAL ':days_ago days')) * 0.5
                    END as recency_factor
                FROM solution_effectiveness 
                WHERE problem_category = :problem_category 
                {machine_filter}
                AND times_suggested >= 2  -- Only consider solutions used at least twice
                GROUP BY solution_text, problem_category, machine_model, success_rate, 
                         times_suggested, times_successful, expert_verified
                ORDER BY 
                    -- Priority calculation: success_rate * recency * expert_bonus * usage_factor
                    (success_rate / 100.0) * 
                    CASE 
                        WHEN MAX(updated_at) > NOW() - INTERVAL ':days_ago days' THEN 1.0
                        ELSE 0.5 + (EXTRACT(EPOCH FROM (MAX(updated_at) - (NOW() - INTERVAL ':days_ago days'))) / 
                                   EXTRACT(EPOCH FROM INTERVAL ':days_ago days')) * 0.5
                    END *
                    CASE WHEN expert_verified THEN 1.2 ELSE 1.0 END *
                    LEAST(times_suggested / 10.0, 1.0)  -- Usage factor capped at 1.0
                    DESC
                LIMIT :limit
            """)
            
            result = db.execute(query, params).fetchall()
            
            solutions = []
            for row in result:
                # Calculate priority score
                success_rate = float(row.success_rate)
                recency_factor = float(row.recency_factor) if row.recency_factor else 0.5
                expert_bonus = 1.2 if row.expert_verified else 1.0
                usage_factor = min(row.times_suggested / 10.0, 1.0)
                
                priority_score = (success_rate / 100.0) * recency_factor * expert_bonus * usage_factor
                
                solutions.append(SolutionPriority(
                    solution_text=row.solution_text,
                    problem_category=row.problem_category,
                    machine_model=row.machine_model,
                    priority_score=priority_score,
                    success_rate=success_rate,
                    times_used=row.times_suggested,
                    avg_effectiveness=float(row.avg_effectiveness) if row.avg_effectiveness else 0,
                    recency_factor=recency_factor,
                    expert_verified=row.expert_verified
                ))
            
            self.logger.info(f"Prioritized {len(solutions)} solutions for category: {problem_category}")
            return solutions
            
        except Exception as e:
            self.logger.error(f"Error prioritizing solutions: {e}")
            return []
    
    async def learn_from_session_outcome(
        self,
        db: Session,
        session_id: str,
        outcome: str,
        solutions_used: List[str],
        user_feedback: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Learn from a completed session outcome to improve future recommendations.
        """
        try:
            # Get session details
            session_query = text("""
                SELECT machine_id, session_metadata 
                FROM ai_sessions 
                WHERE session_id = :session_id
            """)
            
            session = db.execute(session_query, {"session_id": session_id}).fetchone()
            
            if not session:
                self.logger.warning(f"Session not found: {session_id}")
                return False
            
            # Extract problem category from session metadata
            session_metadata = json.loads(session.session_metadata) if session.session_metadata else {}
            problem_category = session_metadata.get("problem_category", "general")
            
            # Get machine model if available
            machine_model = None
            if session.machine_id:
                machine_query = text("""
                    SELECT model FROM machines WHERE id = :machine_id
                """)
                machine_result = db.execute(machine_query, {"machine_id": session.machine_id}).fetchone()
                machine_model = machine_result.model if machine_result else None
            
            # Update solution effectiveness based on outcome
            success_achieved = outcome in ["resolved", "completed"]
            
            for solution_text in solutions_used:
                # Determine effectiveness based on outcome and user feedback
                effectiveness = self._determine_effectiveness(outcome, user_feedback)
                
                # Update or create solution effectiveness record
                await analytics_service.track_solution_effectiveness(
                    db,
                    session_id,
                    {
                        "solution_text": solution_text,
                        "problem_category": problem_category,
                        "machine_model": machine_model,
                        "effectiveness": effectiveness,
                        "user_feedback": json.dumps(user_feedback) if user_feedback else None,
                        "expert_verified": False
                    }
                )
            
            # Generate learning insights
            await self._generate_learning_insights(db, session_id, outcome, solutions_used)
            
            self.logger.info(f"Learned from session outcome: {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error learning from session outcome: {e}")
            return False
    
    async def get_learning_insights(
        self,
        db: Session,
        days: int = 30,
        limit: int = 10
    ) -> List[LearningInsight]:
        """
        Generate learning insights from recent data patterns.
        """
        try:
            insights = []
            
            # Insight 1: Identify trending problems
            trending_problems = await self._identify_trending_problems(db, days)
            if trending_problems:
                insights.append(LearningInsight(
                    insight_type="trend",
                    description=f"Trending problem categories: {', '.join(trending_problems[:3])}",
                    confidence=0.8,
                    supporting_data={"trending_categories": trending_problems},
                    actionable_recommendation="Consider creating specialized knowledge base content for these trending issues."
                ))
            
            # Insight 2: Identify underperforming solutions
            underperforming = await self._identify_underperforming_solutions(db, days)
            if underperforming:
                insights.append(LearningInsight(
                    insight_type="anomaly",
                    description=f"Found {len(underperforming)} solutions with declining success rates",
                    confidence=0.7,
                    supporting_data={"underperforming_solutions": underperforming},
                    actionable_recommendation="Review and update these solutions or mark them for expert review."
                ))
            
            # Insight 3: Identify knowledge gaps
            knowledge_gaps = await self._identify_knowledge_gaps(db, days)
            if knowledge_gaps:
                insights.append(LearningInsight(
                    insight_type="pattern",
                    description=f"Knowledge gaps identified in {len(knowledge_gaps)} areas",
                    confidence=0.9,
                    supporting_data={"knowledge_gaps": knowledge_gaps},
                    actionable_recommendation="Prioritize creating knowledge base content for these areas."
                ))
            
            # Insight 4: Success pattern analysis
            success_patterns = await self._analyze_success_patterns(db, days)
            if success_patterns:
                insights.append(LearningInsight(
                    insight_type="pattern",
                    description="Identified successful troubleshooting patterns",
                    confidence=0.8,
                    supporting_data=success_patterns,
                    actionable_recommendation="Promote these successful patterns in AI responses."
                ))
            
            return insights[:limit]
            
        except Exception as e:
            self.logger.error(f"Error generating learning insights: {e}")
            return []
    
    async def update_solution_priority(
        self,
        db: Session,
        solution_text: str,
        problem_category: str,
        machine_model: Optional[str],
        success_feedback: bool,
        expert_verified: bool = False
    ) -> bool:
        """
        Update solution priority based on new feedback.
        """
        try:
            # Find existing solution
            query = text("""
                SELECT effectiveness_id, times_suggested, times_successful
                FROM solution_effectiveness 
                WHERE solution_text = :solution_text 
                AND problem_category = :problem_category 
                AND COALESCE(machine_model, '') = COALESCE(:machine_model, '')
            """)
            
            existing = db.execute(query, {
                "solution_text": solution_text,
                "problem_category": problem_category,
                "machine_model": machine_model
            }).fetchone()
            
            if existing:
                # Update existing solution
                new_successful = existing.times_successful + (1 if success_feedback else 0)
                new_suggested = existing.times_suggested + 1
                
                update_query = text("""
                    UPDATE solution_effectiveness 
                    SET times_suggested = :times_suggested,
                        times_successful = :times_successful,
                        expert_verified = :expert_verified OR expert_verified,
                        updated_at = NOW()
                    WHERE effectiveness_id = :effectiveness_id
                """)
                
                db.execute(update_query, {
                    "effectiveness_id": existing.effectiveness_id,
                    "times_suggested": new_suggested,
                    "times_successful": new_successful,
                    "expert_verified": expert_verified
                })
            else:
                # Create new solution record
                effectiveness = "effective" if success_feedback else "somewhat_effective"
                
                insert_query = text("""
                    INSERT INTO solution_effectiveness (
                        solution_text, problem_category, machine_model,
                        effectiveness, expert_verified, times_suggested, times_successful
                    ) VALUES (
                        :solution_text, :problem_category, :machine_model,
                        :effectiveness, :expert_verified, 1, :times_successful
                    )
                """)
                
                db.execute(insert_query, {
                    "solution_text": solution_text,
                    "problem_category": problem_category,
                    "machine_model": machine_model,
                    "effectiveness": effectiveness,
                    "expert_verified": expert_verified,
                    "times_successful": 1 if success_feedback else 0
                })
            
            db.commit()
            self.logger.info(f"Updated solution priority for: {solution_text[:50]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating solution priority: {e}")
            db.rollback()
            return False
    
    async def _identify_trending_problems(self, db: Session, days: int) -> List[str]:
        """Identify trending problem categories."""
        try:
            query = text("""
                SELECT 
                    JSON_EXTRACT(session_metadata, '$.problem_category') as problem_category,
                    COUNT(*) as session_count
                FROM ai_sessions 
                WHERE created_at >= NOW() - INTERVAL ':days days'
                AND session_metadata IS NOT NULL
                GROUP BY JSON_EXTRACT(session_metadata, '$.problem_category')
                HAVING COUNT(*) >= 3
                ORDER BY session_count DESC
                LIMIT 10
            """)
            
            result = db.execute(query, {"days": days}).fetchall()
            return [row.problem_category for row in result if row.problem_category]
            
        except Exception as e:
            self.logger.error(f"Error identifying trending problems: {e}")
            return []
    
    async def _identify_underperforming_solutions(self, db: Session, days: int) -> List[Dict[str, Any]]:
        """Identify solutions with declining success rates."""
        try:
            query = text("""
                SELECT 
                    solution_text,
                    problem_category,
                    machine_model,
                    success_rate,
                    times_suggested
                FROM solution_effectiveness 
                WHERE updated_at >= NOW() - INTERVAL ':days days'
                AND times_suggested >= 5
                AND success_rate < 50
                ORDER BY success_rate ASC
                LIMIT 10
            """)
            
            result = db.execute(query, {"days": days}).fetchall()
            
            underperforming = []
            for row in result:
                underperforming.append({
                    "solution_text": row.solution_text,
                    "problem_category": row.problem_category,
                    "machine_model": row.machine_model,
                    "success_rate": float(row.success_rate),
                    "times_suggested": row.times_suggested
                })
            
            return underperforming
            
        except Exception as e:
            self.logger.error(f"Error identifying underperforming solutions: {e}")
            return []
    
    async def _identify_knowledge_gaps(self, db: Session, days: int) -> List[Dict[str, Any]]:
        """Identify areas where knowledge base is insufficient."""
        try:
            # Find sessions that escalated due to lack of knowledge
            query = text("""
                SELECT 
                    JSON_EXTRACT(session_metadata, '$.problem_category') as problem_category,
                    COUNT(*) as escalation_count
                FROM ai_sessions s
                JOIN session_outcomes so ON s.session_id = so.session_id
                WHERE s.created_at >= NOW() - INTERVAL ':days days'
                AND so.outcome = 'escalated'
                AND so.escalation_reason LIKE '%knowledge%'
                GROUP BY JSON_EXTRACT(session_metadata, '$.problem_category')
                HAVING COUNT(*) >= 2
                ORDER BY escalation_count DESC
            """)
            
            result = db.execute(query, {"days": days}).fetchall()
            
            gaps = []
            for row in result:
                if row.problem_category:
                    gaps.append({
                        "problem_category": row.problem_category,
                        "escalation_count": row.escalation_count
                    })
            
            return gaps
            
        except Exception as e:
            self.logger.error(f"Error identifying knowledge gaps: {e}")
            return []
    
    async def _analyze_success_patterns(self, db: Session, days: int) -> Dict[str, Any]:
        """Analyze patterns in successful troubleshooting sessions."""
        try:
            # Find common characteristics of successful sessions
            query = text("""
                SELECT 
                    AVG(resolution_time_minutes) as avg_resolution_time,
                    AVG(steps_to_resolution) as avg_steps,
                    AVG(user_satisfaction_rating) as avg_satisfaction,
                    COUNT(*) as successful_sessions
                FROM session_outcomes 
                WHERE created_at >= NOW() - INTERVAL ':days days'
                AND outcome = 'resolved'
                AND problem_resolved = true
            """)
            
            result = db.execute(query, {"days": days}).fetchone()
            
            if result and result.successful_sessions > 0:
                return {
                    "avg_resolution_time_minutes": float(result.avg_resolution_time) if result.avg_resolution_time else 0,
                    "avg_steps_to_resolution": float(result.avg_steps) if result.avg_steps else 0,
                    "avg_user_satisfaction": float(result.avg_satisfaction) if result.avg_satisfaction else 0,
                    "total_successful_sessions": result.successful_sessions
                }
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error analyzing success patterns: {e}")
            return {}
    
    async def _generate_learning_insights(
        self,
        db: Session,
        session_id: str,
        outcome: str,
        solutions_used: List[str]
    ) -> None:
        """Generate specific learning insights from a session."""
        try:
            # This could be expanded to generate more sophisticated insights
            # For now, we'll log the learning event
            self.logger.info(f"Generated learning insights for session {session_id}: outcome={outcome}, solutions_count={len(solutions_used)}")
            
        except Exception as e:
            self.logger.error(f"Error generating learning insights: {e}")
    
    def _determine_effectiveness(
        self,
        outcome: str,
        user_feedback: Optional[Dict[str, Any]]
    ) -> str:
        """Determine solution effectiveness based on outcome and feedback."""
        if outcome == "resolved":
            if user_feedback and user_feedback.get("satisfaction", 0) >= 4:
                return "very_effective"
            else:
                return "effective"
        elif outcome == "escalated":
            return "not_effective"
        elif outcome == "abandoned":
            return "not_effective"
        else:
            return "somewhat_effective"


# Global learning service instance
learning_service = LearningService()