"""
A/B Testing service for troubleshooting approaches.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text, func
import json
import random
from dataclasses import dataclass
from enum import Enum

from ..database import get_db

logger = logging.getLogger(__name__)


class ABTestVariant(str, Enum):
    """A/B test variant types."""
    CONTROL = "control"
    VARIANT = "variant"


@dataclass
class ABTestExperiment:
    """A/B test experiment configuration."""
    experiment_id: str
    experiment_name: str
    description: str
    start_date: datetime
    end_date: Optional[datetime]
    is_active: bool
    control_approach: str
    variant_approach: str
    success_metric: str
    target_sample_size: int
    created_by: str


@dataclass
class ABTestAssignment:
    """A/B test session assignment."""
    assignment_id: str
    experiment_id: str
    session_id: str
    variant: ABTestVariant
    assigned_at: datetime


@dataclass
class ABTestResult:
    """A/B test result data."""
    result_id: str
    experiment_id: str
    session_id: str
    variant: ABTestVariant
    success_achieved: bool
    metric_value: Optional[float]
    additional_metrics: Dict[str, Any]


class ABTestingService:
    """Service for managing A/B tests for troubleshooting approaches."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def create_experiment(
        self,
        db: Session,
        experiment_name: str,
        description: str,
        control_approach: str,
        variant_approach: str,
        success_metric: str,
        target_sample_size: int = 100,
        duration_days: int = 30,
        created_by: str = "system"
    ) -> Optional[str]:
        """Create a new A/B test experiment."""
        try:
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=duration_days)
            
            query = text("""
                INSERT INTO ab_test_experiments (
                    experiment_name, description, start_date, end_date,
                    control_approach, variant_approach, success_metric,
                    target_sample_size, created_by
                ) VALUES (
                    :experiment_name, :description, :start_date, :end_date,
                    :control_approach, :variant_approach, :success_metric,
                    :target_sample_size, :created_by
                ) RETURNING experiment_id
            """)
            
            result = db.execute(query, {
                "experiment_name": experiment_name,
                "description": description,
                "start_date": start_date,
                "end_date": end_date,
                "control_approach": control_approach,
                "variant_approach": variant_approach,
                "success_metric": success_metric,
                "target_sample_size": target_sample_size,
                "created_by": created_by
            }).fetchone()
            
            db.commit()
            
            experiment_id = result.experiment_id
            self.logger.info(f"Created A/B test experiment: {experiment_id}")
            return experiment_id
            
        except Exception as e:
            self.logger.error(f"Error creating A/B test experiment: {e}")
            db.rollback()
            return None
    
    async def assign_session_to_experiment(
        self,
        db: Session,
        session_id: str,
        experiment_id: Optional[str] = None
    ) -> Optional[ABTestVariant]:
        """Assign a session to an active A/B test experiment."""
        try:
            # If no specific experiment, find an active one
            if not experiment_id:
                experiment_id = await self._get_active_experiment(db)
                if not experiment_id:
                    return None
            
            # Check if session is already assigned
            existing_query = text("""
                SELECT variant FROM ab_test_assignments 
                WHERE session_id = :session_id AND experiment_id = :experiment_id
            """)
            
            existing = db.execute(existing_query, {
                "session_id": session_id,
                "experiment_id": experiment_id
            }).fetchone()
            
            if existing:
                return ABTestVariant(existing.variant)
            
            # Get current assignment counts
            counts_query = text("""
                SELECT 
                    variant,
                    COUNT(*) as count
                FROM ab_test_assignments 
                WHERE experiment_id = :experiment_id
                GROUP BY variant
            """)
            
            counts = db.execute(counts_query, {"experiment_id": experiment_id}).fetchall()
            
            control_count = 0
            variant_count = 0
            
            for count_row in counts:
                if count_row.variant == ABTestVariant.CONTROL.value:
                    control_count = count_row.count
                elif count_row.variant == ABTestVariant.VARIANT.value:
                    variant_count = count_row.count
            
            # Assign variant based on balanced randomization
            # Prefer the variant with fewer assignments, with some randomness
            if control_count == variant_count:
                # Equal counts, random assignment
                assigned_variant = random.choice([ABTestVariant.CONTROL, ABTestVariant.VARIANT])
            elif control_count < variant_count:
                # Prefer control to balance
                assigned_variant = ABTestVariant.CONTROL if random.random() < 0.7 else ABTestVariant.VARIANT
            else:
                # Prefer variant to balance
                assigned_variant = ABTestVariant.VARIANT if random.random() < 0.7 else ABTestVariant.CONTROL
            
            # Insert assignment
            assignment_query = text("""
                INSERT INTO ab_test_assignments (
                    experiment_id, session_id, variant
                ) VALUES (
                    :experiment_id, :session_id, :variant
                )
            """)
            
            db.execute(assignment_query, {
                "experiment_id": experiment_id,
                "session_id": session_id,
                "variant": assigned_variant.value
            })
            
            db.commit()
            
            self.logger.info(f"Assigned session {session_id} to variant {assigned_variant.value}")
            return assigned_variant
            
        except Exception as e:
            self.logger.error(f"Error assigning session to A/B test: {e}")
            db.rollback()
            return None
    
    async def record_test_result(
        self,
        db: Session,
        session_id: str,
        success_achieved: bool,
        metric_value: Optional[float] = None,
        additional_metrics: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Record the result of an A/B test session."""
        try:
            # Get the assignment for this session
            assignment_query = text("""
                SELECT experiment_id, variant 
                FROM ab_test_assignments 
                WHERE session_id = :session_id
            """)
            
            assignment = db.execute(assignment_query, {"session_id": session_id}).fetchone()
            
            if not assignment:
                self.logger.warning(f"No A/B test assignment found for session {session_id}")
                return False
            
            # Insert result
            result_query = text("""
                INSERT INTO ab_test_results (
                    experiment_id, session_id, variant, success_achieved,
                    metric_value, additional_metrics
                ) VALUES (
                    :experiment_id, :session_id, :variant, :success_achieved,
                    :metric_value, :additional_metrics
                )
            """)
            
            db.execute(result_query, {
                "experiment_id": assignment.experiment_id,
                "session_id": session_id,
                "variant": assignment.variant,
                "success_achieved": success_achieved,
                "metric_value": metric_value,
                "additional_metrics": json.dumps(additional_metrics) if additional_metrics else None
            })
            
            db.commit()
            
            self.logger.info(f"Recorded A/B test result for session {session_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording A/B test result: {e}")
            db.rollback()
            return False
    
    async def get_experiment_results(
        self,
        db: Session,
        experiment_id: str
    ) -> Dict[str, Any]:
        """Get results and analysis for an A/B test experiment."""
        try:
            # Get experiment details
            experiment_query = text("""
                SELECT * FROM ab_test_experiments 
                WHERE experiment_id = :experiment_id
            """)
            
            experiment = db.execute(experiment_query, {"experiment_id": experiment_id}).fetchone()
            
            if not experiment:
                return {"error": "Experiment not found"}
            
            # Get results summary
            results_query = text("""
                SELECT 
                    variant,
                    COUNT(*) as total_sessions,
                    COUNT(CASE WHEN success_achieved = true THEN 1 END) as successful_sessions,
                    AVG(CASE WHEN success_achieved = true THEN 1.0 ELSE 0.0 END) as success_rate,
                    AVG(metric_value) as avg_metric_value,
                    STDDEV(metric_value) as stddev_metric_value
                FROM ab_test_results 
                WHERE experiment_id = :experiment_id
                GROUP BY variant
            """)
            
            results = db.execute(results_query, {"experiment_id": experiment_id}).fetchall()
            
            # Process results
            control_results = None
            variant_results = None
            
            for result in results:
                result_data = {
                    "total_sessions": result.total_sessions,
                    "successful_sessions": result.successful_sessions,
                    "success_rate": float(result.success_rate) if result.success_rate else 0,
                    "avg_metric_value": float(result.avg_metric_value) if result.avg_metric_value else 0,
                    "stddev_metric_value": float(result.stddev_metric_value) if result.stddev_metric_value else 0
                }
                
                if result.variant == ABTestVariant.CONTROL.value:
                    control_results = result_data
                elif result.variant == ABTestVariant.VARIANT.value:
                    variant_results = result_data
            
            # Calculate statistical significance (basic implementation)
            statistical_analysis = self._calculate_statistical_significance(
                control_results, variant_results
            ) if control_results and variant_results else None
            
            return {
                "experiment": {
                    "experiment_id": experiment.experiment_id,
                    "experiment_name": experiment.experiment_name,
                    "description": experiment.description,
                    "start_date": experiment.start_date.isoformat(),
                    "end_date": experiment.end_date.isoformat() if experiment.end_date else None,
                    "is_active": experiment.is_active,
                    "control_approach": experiment.control_approach,
                    "variant_approach": experiment.variant_approach,
                    "success_metric": experiment.success_metric,
                    "target_sample_size": experiment.target_sample_size
                },
                "results": {
                    "control": control_results,
                    "variant": variant_results
                },
                "analysis": statistical_analysis
            }
            
        except Exception as e:
            self.logger.error(f"Error getting experiment results: {e}")
            return {"error": str(e)}
    
    async def get_active_experiments(self, db: Session) -> List[Dict[str, Any]]:
        """Get all active A/B test experiments."""
        try:
            query = text("""
                SELECT 
                    e.*,
                    COUNT(a.assignment_id) as total_assignments,
                    COUNT(r.result_id) as total_results
                FROM ab_test_experiments e
                LEFT JOIN ab_test_assignments a ON e.experiment_id = a.experiment_id
                LEFT JOIN ab_test_results r ON e.experiment_id = r.experiment_id
                WHERE e.is_active = true 
                AND (e.end_date IS NULL OR e.end_date > NOW())
                GROUP BY e.experiment_id
                ORDER BY e.created_at DESC
            """)
            
            experiments = db.execute(query).fetchall()
            
            result = []
            for exp in experiments:
                result.append({
                    "experiment_id": exp.experiment_id,
                    "experiment_name": exp.experiment_name,
                    "description": exp.description,
                    "start_date": exp.start_date.isoformat(),
                    "end_date": exp.end_date.isoformat() if exp.end_date else None,
                    "control_approach": exp.control_approach,
                    "variant_approach": exp.variant_approach,
                    "success_metric": exp.success_metric,
                    "target_sample_size": exp.target_sample_size,
                    "total_assignments": exp.total_assignments,
                    "total_results": exp.total_results,
                    "progress_percentage": (exp.total_assignments / exp.target_sample_size * 100) if exp.target_sample_size > 0 else 0
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting active experiments: {e}")
            return []
    
    async def end_experiment(
        self,
        db: Session,
        experiment_id: str
    ) -> bool:
        """End an A/B test experiment."""
        try:
            query = text("""
                UPDATE ab_test_experiments 
                SET is_active = false, end_date = NOW()
                WHERE experiment_id = :experiment_id
            """)
            
            db.execute(query, {"experiment_id": experiment_id})
            db.commit()
            
            self.logger.info(f"Ended A/B test experiment: {experiment_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error ending experiment: {e}")
            db.rollback()
            return False
    
    async def _get_active_experiment(self, db: Session) -> Optional[str]:
        """Get an active experiment that needs more participants."""
        try:
            query = text("""
                SELECT 
                    e.experiment_id,
                    COUNT(a.assignment_id) as current_assignments
                FROM ab_test_experiments e
                LEFT JOIN ab_test_assignments a ON e.experiment_id = a.experiment_id
                WHERE e.is_active = true 
                AND (e.end_date IS NULL OR e.end_date > NOW())
                GROUP BY e.experiment_id, e.target_sample_size
                HAVING COUNT(a.assignment_id) < e.target_sample_size
                ORDER BY COUNT(a.assignment_id) ASC
                LIMIT 1
            """)
            
            result = db.execute(query).fetchone()
            return result.experiment_id if result else None
            
        except Exception as e:
            self.logger.error(f"Error getting active experiment: {e}")
            return None
    
    def _calculate_statistical_significance(
        self,
        control_results: Dict[str, Any],
        variant_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate basic statistical significance between control and variant."""
        try:
            # Basic z-test for proportions
            p1 = control_results["success_rate"]
            n1 = control_results["total_sessions"]
            p2 = variant_results["success_rate"]
            n2 = variant_results["total_sessions"]
            
            if n1 == 0 or n2 == 0:
                return {"error": "Insufficient data for statistical analysis"}
            
            # Pooled proportion
            p_pool = (p1 * n1 + p2 * n2) / (n1 + n2)
            
            # Standard error
            se = (p_pool * (1 - p_pool) * (1/n1 + 1/n2)) ** 0.5
            
            if se == 0:
                return {"error": "Cannot calculate statistical significance"}
            
            # Z-score
            z_score = (p2 - p1) / se
            
            # Simple significance check (z > 1.96 for 95% confidence)
            is_significant = abs(z_score) > 1.96
            
            # Effect size (difference in success rates)
            effect_size = p2 - p1
            
            # Confidence interval for difference (approximate)
            margin_of_error = 1.96 * se
            ci_lower = effect_size - margin_of_error
            ci_upper = effect_size + margin_of_error
            
            return {
                "z_score": z_score,
                "is_significant": is_significant,
                "effect_size": effect_size,
                "effect_size_percentage": effect_size * 100,
                "confidence_interval": {
                    "lower": ci_lower,
                    "upper": ci_upper
                },
                "interpretation": self._interpret_results(effect_size, is_significant)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating statistical significance: {e}")
            return {"error": str(e)}
    
    def _interpret_results(self, effect_size: float, is_significant: bool) -> str:
        """Provide interpretation of A/B test results."""
        if not is_significant:
            return "No statistically significant difference between control and variant."
        
        if effect_size > 0.05:  # 5% improvement
            return "Variant shows significant improvement over control."
        elif effect_size < -0.05:  # 5% degradation
            return "Variant shows significant degradation compared to control."
        else:
            return "Statistically significant but small practical difference."


# Global A/B testing service instance
ab_testing_service = ABTestingService()