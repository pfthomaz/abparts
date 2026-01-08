"""
Analytics service for AI Assistant performance monitoring and learning.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_, or_
from decimal import Decimal
import json
import asyncio
from dataclasses import dataclass

from ..database import get_db
from ..models import (
    AISession, AIMessage, SessionStatus, MessageSender,
    KnowledgeDocument, DocumentChunk
)

logger = logging.getLogger(__name__)


@dataclass
class SessionOutcome:
    """Session outcome data structure."""
    session_id: str
    outcome: str  # resolved, escalated, abandoned, in_progress
    resolution_time_minutes: Optional[int]
    steps_to_resolution: Optional[int]
    user_satisfaction_rating: Optional[int]
    problem_resolved: bool
    escalation_reason: Optional[str]
    success_factors: List[str]
    failure_factors: List[str]


@dataclass
class SolutionEffectiveness:
    """Solution effectiveness tracking data."""
    solution_text: str
    problem_category: str
    machine_model: Optional[str]
    effectiveness: str  # not_effective, somewhat_effective, effective, very_effective
    user_feedback: Optional[str]
    expert_verified: bool


@dataclass
class AIResponseMetrics:
    """AI response quality metrics."""
    session_id: str
    message_id: str
    response_time_ms: int
    token_count: Optional[int]
    confidence_score: Optional[float]
    relevance_score: Optional[float]
    knowledge_sources_used: int
    contains_safety_warning: bool
    requires_expert_review: bool


@dataclass
class UserSatisfactionFeedback:
    """User satisfaction feedback data."""
    session_id: str
    user_id: str
    overall_satisfaction: int  # 1-5
    response_helpfulness: Optional[int]
    response_accuracy: Optional[int]
    ease_of_use: Optional[int]
    would_recommend: Optional[bool]
    feedback_text: Optional[str]
    improvement_suggestions: Optional[str]


class AnalyticsService:
    """Service for tracking AI Assistant analytics and performance metrics."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def track_session_outcome(
        self, 
        db: Session,
        session_outcome: SessionOutcome
    ) -> bool:
        """Track the outcome of a troubleshooting session."""
        try:
            # Insert session outcome
            query = text("""
                INSERT INTO session_outcomes (
                    session_id, outcome, resolution_time_minutes, steps_to_resolution,
                    user_satisfaction_rating, problem_resolved, escalation_reason,
                    success_factors, failure_factors
                ) VALUES (
                    :session_id, :outcome, :resolution_time_minutes, :steps_to_resolution,
                    :user_satisfaction_rating, :problem_resolved, :escalation_reason,
                    :success_factors, :failure_factors
                )
            """)
            
            db.execute(query, {
                "session_id": session_outcome.session_id,
                "outcome": session_outcome.outcome,
                "resolution_time_minutes": session_outcome.resolution_time_minutes,
                "steps_to_resolution": session_outcome.steps_to_resolution,
                "user_satisfaction_rating": session_outcome.user_satisfaction_rating,
                "problem_resolved": session_outcome.problem_resolved,
                "escalation_reason": session_outcome.escalation_reason,
                "success_factors": session_outcome.success_factors,
                "failure_factors": session_outcome.failure_factors
            })
            
            db.commit()
            self.logger.info(f"Tracked session outcome for session {session_outcome.session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error tracking session outcome: {e}")
            db.rollback()
            return False
    
    async def track_solution_effectiveness(
        self,
        db: Session,
        session_id: str,
        solution_effectiveness: SolutionEffectiveness
    ) -> bool:
        """Track the effectiveness of a solution provided to a user."""
        try:
            # Check if this solution already exists
            existing_query = text("""
                SELECT effectiveness_id, times_suggested, times_successful 
                FROM solution_effectiveness 
                WHERE solution_text = :solution_text 
                AND problem_category = :problem_category 
                AND COALESCE(machine_model, '') = COALESCE(:machine_model, '')
            """)
            
            existing = db.execute(existing_query, {
                "solution_text": solution_effectiveness.solution_text,
                "problem_category": solution_effectiveness.problem_category,
                "machine_model": solution_effectiveness.machine_model
            }).fetchone()
            
            if existing:
                # Update existing solution
                times_successful = existing.times_successful
                if solution_effectiveness.effectiveness in ['effective', 'very_effective']:
                    times_successful += 1
                
                update_query = text("""
                    UPDATE solution_effectiveness 
                    SET times_suggested = times_suggested + 1,
                        times_successful = :times_successful,
                        effectiveness = :effectiveness,
                        user_feedback = :user_feedback,
                        expert_verified = :expert_verified OR expert_verified,
                        updated_at = NOW()
                    WHERE effectiveness_id = :effectiveness_id
                """)
                
                db.execute(update_query, {
                    "effectiveness_id": existing.effectiveness_id,
                    "times_successful": times_successful,
                    "effectiveness": solution_effectiveness.effectiveness,
                    "user_feedback": solution_effectiveness.user_feedback,
                    "expert_verified": solution_effectiveness.expert_verified
                })
            else:
                # Insert new solution
                times_successful = 1 if solution_effectiveness.effectiveness in ['effective', 'very_effective'] else 0
                
                insert_query = text("""
                    INSERT INTO solution_effectiveness (
                        session_id, solution_text, problem_category, machine_model,
                        effectiveness, user_feedback, expert_verified,
                        times_suggested, times_successful
                    ) VALUES (
                        :session_id, :solution_text, :problem_category, :machine_model,
                        :effectiveness, :user_feedback, :expert_verified, 1, :times_successful
                    )
                """)
                
                db.execute(insert_query, {
                    "session_id": session_id,
                    "solution_text": solution_effectiveness.solution_text,
                    "problem_category": solution_effectiveness.problem_category,
                    "machine_model": solution_effectiveness.machine_model,
                    "effectiveness": solution_effectiveness.effectiveness,
                    "user_feedback": solution_effectiveness.user_feedback,
                    "expert_verified": solution_effectiveness.expert_verified,
                    "times_successful": times_successful
                })
            
            db.commit()
            self.logger.info(f"Tracked solution effectiveness for session {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error tracking solution effectiveness: {e}")
            db.rollback()
            return False
    
    async def track_ai_response_metrics(
        self,
        db: Session,
        metrics: AIResponseMetrics
    ) -> bool:
        """Track AI response quality metrics."""
        try:
            query = text("""
                INSERT INTO ai_response_metrics (
                    session_id, message_id, response_time_ms, token_count,
                    confidence_score, relevance_score, knowledge_sources_used,
                    contains_safety_warning, requires_expert_review
                ) VALUES (
                    :session_id, :message_id, :response_time_ms, :token_count,
                    :confidence_score, :relevance_score, :knowledge_sources_used,
                    :contains_safety_warning, :requires_expert_review
                )
            """)
            
            db.execute(query, {
                "session_id": metrics.session_id,
                "message_id": metrics.message_id,
                "response_time_ms": metrics.response_time_ms,
                "token_count": metrics.token_count,
                "confidence_score": metrics.confidence_score,
                "relevance_score": metrics.relevance_score,
                "knowledge_sources_used": metrics.knowledge_sources_used,
                "contains_safety_warning": metrics.contains_safety_warning,
                "requires_expert_review": metrics.requires_expert_review
            })
            
            db.commit()
            self.logger.info(f"Tracked AI response metrics for message {metrics.message_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error tracking AI response metrics: {e}")
            db.rollback()
            return False
    
    async def collect_user_satisfaction_feedback(
        self,
        db: Session,
        feedback: UserSatisfactionFeedback
    ) -> bool:
        """Collect user satisfaction feedback."""
        try:
            query = text("""
                INSERT INTO user_satisfaction_feedback (
                    session_id, user_id, overall_satisfaction, response_helpfulness,
                    response_accuracy, ease_of_use, would_recommend,
                    feedback_text, improvement_suggestions
                ) VALUES (
                    :session_id, :user_id, :overall_satisfaction, :response_helpfulness,
                    :response_accuracy, :ease_of_use, :would_recommend,
                    :feedback_text, :improvement_suggestions
                )
            """)
            
            db.execute(query, {
                "session_id": feedback.session_id,
                "user_id": feedback.user_id,
                "overall_satisfaction": feedback.overall_satisfaction,
                "response_helpfulness": feedback.response_helpfulness,
                "response_accuracy": feedback.response_accuracy,
                "ease_of_use": feedback.ease_of_use,
                "would_recommend": feedback.would_recommend,
                "feedback_text": feedback.feedback_text,
                "improvement_suggestions": feedback.improvement_suggestions
            })
            
            db.commit()
            self.logger.info(f"Collected user satisfaction feedback for session {feedback.session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error collecting user satisfaction feedback: {e}")
            db.rollback()
            return False
    
    async def get_session_success_metrics(
        self,
        db: Session,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get session success metrics for the specified number of days."""
        try:
            query = text("""
                SELECT * FROM session_success_metrics 
                WHERE date >= :start_date 
                ORDER BY date DESC
            """)
            
            start_date = datetime.utcnow() - timedelta(days=days)
            result = db.execute(query, {"start_date": start_date}).fetchall()
            
            metrics = []
            for row in result:
                metrics.append({
                    "date": row.date.isoformat(),
                    "total_sessions": row.total_sessions,
                    "resolved_sessions": row.resolved_sessions,
                    "escalated_sessions": row.escalated_sessions,
                    "abandoned_sessions": row.abandoned_sessions,
                    "success_rate_percentage": float(row.success_rate_percentage) if row.success_rate_percentage else 0,
                    "avg_resolution_time_minutes": float(row.avg_resolution_time_minutes) if row.avg_resolution_time_minutes else 0,
                    "avg_steps_to_resolution": float(row.avg_steps_to_resolution) if row.avg_steps_to_resolution else 0,
                    "avg_user_satisfaction": float(row.avg_user_satisfaction) if row.avg_user_satisfaction else 0
                })
            
            return {
                "period_days": days,
                "metrics": metrics,
                "summary": self._calculate_summary_metrics(metrics) if metrics else {}
            }
            
        except Exception as e:
            self.logger.error(f"Error getting session success metrics: {e}")
            return {"error": str(e)}
    
    async def get_top_performing_solutions(
        self,
        db: Session,
        limit: int = 20,
        min_suggestions: int = 3
    ) -> List[Dict[str, Any]]:
        """Get top performing solutions based on success rate."""
        try:
            query = text("""
                SELECT * FROM top_performing_solutions 
                WHERE times_suggested >= :min_suggestions
                LIMIT :limit
            """)
            
            result = db.execute(query, {
                "min_suggestions": min_suggestions,
                "limit": limit
            }).fetchall()
            
            solutions = []
            for row in result:
                solutions.append({
                    "problem_category": row.problem_category,
                    "machine_model": row.machine_model,
                    "solution_text": row.solution_text,
                    "times_suggested": row.times_suggested,
                    "times_successful": row.times_successful,
                    "success_rate": float(row.success_rate),
                    "avg_effectiveness_score": float(row.avg_effectiveness_score) if row.avg_effectiveness_score else 0
                })
            
            return solutions
            
        except Exception as e:
            self.logger.error(f"Error getting top performing solutions: {e}")
            return []
    
    async def get_ai_response_quality_metrics(
        self,
        db: Session,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get AI response quality metrics."""
        try:
            query = text("""
                SELECT * FROM ai_response_quality_metrics 
                WHERE date >= :start_date 
                ORDER BY date DESC
            """)
            
            start_date = datetime.utcnow() - timedelta(days=days)
            result = db.execute(query, {"start_date": start_date}).fetchall()
            
            metrics = []
            for row in result:
                metrics.append({
                    "date": row.date.isoformat(),
                    "total_responses": row.total_responses,
                    "avg_response_time_ms": float(row.avg_response_time_ms) if row.avg_response_time_ms else 0,
                    "avg_confidence_score": float(row.avg_confidence_score) if row.avg_confidence_score else 0,
                    "avg_relevance_score": float(row.avg_relevance_score) if row.avg_relevance_score else 0,
                    "avg_knowledge_sources_used": float(row.avg_knowledge_sources_used) if row.avg_knowledge_sources_used else 0,
                    "responses_needing_review": row.responses_needing_review,
                    "avg_user_feedback_rating": float(row.avg_user_feedback_rating) if row.avg_user_feedback_rating else 0,
                    "avg_expert_quality_rating": float(row.avg_expert_quality_rating) if row.avg_expert_quality_rating else 0
                })
            
            return {
                "period_days": days,
                "metrics": metrics
            }
            
        except Exception as e:
            self.logger.error(f"Error getting AI response quality metrics: {e}")
            return {"error": str(e)}
    
    async def calculate_system_performance_metrics(
        self,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate and store system-wide performance metrics."""
        try:
            metrics = {}
            
            # Calculate daily metrics
            today = datetime.utcnow().date()
            yesterday = today - timedelta(days=1)
            
            # Session success rate
            success_rate_query = text("""
                SELECT 
                    COUNT(*) as total_sessions,
                    COUNT(CASE WHEN outcome = 'resolved' THEN 1 END) as resolved_sessions
                FROM session_outcomes 
                WHERE DATE(created_at) = :date
            """)
            
            result = db.execute(success_rate_query, {"date": yesterday}).fetchone()
            if result and result.total_sessions > 0:
                success_rate = (result.resolved_sessions / result.total_sessions) * 100
                metrics["daily_success_rate"] = success_rate
                
                # Store metric
                await self._store_performance_metric(
                    db, "session_success_rate", success_rate, "percentage", 
                    "daily", yesterday, today
                )
            
            # Average response time
            response_time_query = text("""
                SELECT AVG(response_time_ms) as avg_response_time
                FROM ai_response_metrics 
                WHERE DATE(created_at) = :date
            """)
            
            result = db.execute(response_time_query, {"date": yesterday}).fetchone()
            if result and result.avg_response_time:
                avg_response_time = float(result.avg_response_time)
                metrics["daily_avg_response_time_ms"] = avg_response_time
                
                # Store metric
                await self._store_performance_metric(
                    db, "avg_response_time", avg_response_time, "ms",
                    "daily", yesterday, today
                )
            
            # User satisfaction
            satisfaction_query = text("""
                SELECT AVG(overall_satisfaction) as avg_satisfaction
                FROM user_satisfaction_feedback 
                WHERE DATE(created_at) = :date
            """)
            
            result = db.execute(satisfaction_query, {"date": yesterday}).fetchone()
            if result and result.avg_satisfaction:
                avg_satisfaction = float(result.avg_satisfaction)
                metrics["daily_avg_user_satisfaction"] = avg_satisfaction
                
                # Store metric
                await self._store_performance_metric(
                    db, "avg_user_satisfaction", avg_satisfaction, "rating",
                    "daily", yesterday, today
                )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating system performance metrics: {e}")
            return {"error": str(e)}
    
    async def _store_performance_metric(
        self,
        db: Session,
        metric_name: str,
        metric_value: float,
        metric_unit: str,
        time_period: str,
        period_start: datetime,
        period_end: datetime
    ) -> bool:
        """Store a performance metric in the database."""
        try:
            query = text("""
                INSERT INTO system_performance_metrics (
                    metric_name, metric_value, metric_unit, time_period,
                    period_start, period_end
                ) VALUES (
                    :metric_name, :metric_value, :metric_unit, :time_period,
                    :period_start, :period_end
                )
            """)
            
            db.execute(query, {
                "metric_name": metric_name,
                "metric_value": metric_value,
                "metric_unit": metric_unit,
                "time_period": time_period,
                "period_start": period_start,
                "period_end": period_end
            })
            
            db.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing performance metric: {e}")
            db.rollback()
            return False
    
    def _calculate_summary_metrics(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary metrics from daily metrics."""
        if not metrics:
            return {}
        
        total_sessions = sum(m["total_sessions"] for m in metrics)
        total_resolved = sum(m["resolved_sessions"] for m in metrics)
        
        return {
            "total_sessions": total_sessions,
            "total_resolved_sessions": total_resolved,
            "overall_success_rate": (total_resolved / total_sessions * 100) if total_sessions > 0 else 0,
            "avg_resolution_time_minutes": sum(m["avg_resolution_time_minutes"] for m in metrics) / len(metrics),
            "avg_steps_to_resolution": sum(m["avg_steps_to_resolution"] for m in metrics) / len(metrics),
            "avg_user_satisfaction": sum(m["avg_user_satisfaction"] for m in metrics) / len(metrics)
        }


# Global analytics service instance
analytics_service = AnalyticsService()