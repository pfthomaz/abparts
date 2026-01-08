"""
Analytics and performance monitoring API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..database import get_db
from ..schemas import *
from ..services.analytics_service import analytics_service, SessionOutcome, SolutionEffectiveness, AIResponseMetrics, UserSatisfactionFeedback
from ..services.ab_testing_service import ab_testing_service, ABTestVariant
from ..services.learning_service import learning_service

router = APIRouter()


# Analytics endpoints
@router.get("/analytics/session-metrics", response_model=Dict[str, Any])
async def get_session_metrics(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get session success metrics for the specified period."""
    try:
        metrics = await analytics_service.get_session_success_metrics(db, days)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session metrics: {str(e)}")


@router.get("/analytics/top-solutions", response_model=List[Dict[str, Any]])
async def get_top_solutions(
    limit: int = Query(20, description="Maximum number of solutions to return"),
    min_suggestions: int = Query(3, description="Minimum number of suggestions required"),
    db: Session = Depends(get_db)
):
    """Get top performing solutions based on success rate."""
    try:
        solutions = await analytics_service.get_top_performing_solutions(db, limit, min_suggestions)
        return solutions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving top solutions: {str(e)}")


@router.get("/analytics/response-quality", response_model=Dict[str, Any])
async def get_response_quality_metrics(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get AI response quality metrics."""
    try:
        metrics = await analytics_service.get_ai_response_quality_metrics(db, days)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving response quality metrics: {str(e)}")


@router.post("/analytics/session-outcome")
async def track_session_outcome(
    session_id: str,
    outcome: str,
    resolution_time_minutes: Optional[int] = None,
    steps_to_resolution: Optional[int] = None,
    user_satisfaction_rating: Optional[int] = None,
    problem_resolved: bool = False,
    escalation_reason: Optional[str] = None,
    success_factors: List[str] = [],
    failure_factors: List[str] = [],
    db: Session = Depends(get_db)
):
    """Track the outcome of a troubleshooting session."""
    try:
        session_outcome = SessionOutcome(
            session_id=session_id,
            outcome=outcome,
            resolution_time_minutes=resolution_time_minutes,
            steps_to_resolution=steps_to_resolution,
            user_satisfaction_rating=user_satisfaction_rating,
            problem_resolved=problem_resolved,
            escalation_reason=escalation_reason,
            success_factors=success_factors,
            failure_factors=failure_factors
        )
        
        success = await analytics_service.track_session_outcome(db, session_outcome)
        
        if success:
            return {"status": "success", "message": "Session outcome tracked successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to track session outcome")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking session outcome: {str(e)}")


@router.post("/analytics/solution-effectiveness")
async def track_solution_effectiveness(
    session_id: str,
    solution_text: str,
    problem_category: str,
    machine_model: Optional[str] = None,
    effectiveness: str = "effective",
    user_feedback: Optional[str] = None,
    expert_verified: bool = False,
    db: Session = Depends(get_db)
):
    """Track the effectiveness of a solution."""
    try:
        solution_effectiveness = SolutionEffectiveness(
            solution_text=solution_text,
            problem_category=problem_category,
            machine_model=machine_model,
            effectiveness=effectiveness,
            user_feedback=user_feedback,
            expert_verified=expert_verified
        )
        
        success = await analytics_service.track_solution_effectiveness(db, session_id, solution_effectiveness)
        
        if success:
            return {"status": "success", "message": "Solution effectiveness tracked successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to track solution effectiveness")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking solution effectiveness: {str(e)}")


@router.post("/analytics/response-metrics")
async def track_response_metrics(
    session_id: str,
    message_id: str,
    response_time_ms: int,
    token_count: Optional[int] = None,
    confidence_score: Optional[float] = None,
    relevance_score: Optional[float] = None,
    knowledge_sources_used: int = 0,
    contains_safety_warning: bool = False,
    requires_expert_review: bool = False,
    db: Session = Depends(get_db)
):
    """Track AI response quality metrics."""
    try:
        metrics = AIResponseMetrics(
            session_id=session_id,
            message_id=message_id,
            response_time_ms=response_time_ms,
            token_count=token_count,
            confidence_score=confidence_score,
            relevance_score=relevance_score,
            knowledge_sources_used=knowledge_sources_used,
            contains_safety_warning=contains_safety_warning,
            requires_expert_review=requires_expert_review
        )
        
        success = await analytics_service.track_ai_response_metrics(db, metrics)
        
        if success:
            return {"status": "success", "message": "Response metrics tracked successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to track response metrics")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking response metrics: {str(e)}")


@router.post("/analytics/user-feedback")
async def collect_user_feedback(
    session_id: str,
    user_id: str,
    overall_satisfaction: int,
    response_helpfulness: Optional[int] = None,
    response_accuracy: Optional[int] = None,
    ease_of_use: Optional[int] = None,
    would_recommend: Optional[bool] = None,
    feedback_text: Optional[str] = None,
    improvement_suggestions: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Collect user satisfaction feedback."""
    try:
        feedback = UserSatisfactionFeedback(
            session_id=session_id,
            user_id=user_id,
            overall_satisfaction=overall_satisfaction,
            response_helpfulness=response_helpfulness,
            response_accuracy=response_accuracy,
            ease_of_use=ease_of_use,
            would_recommend=would_recommend,
            feedback_text=feedback_text,
            improvement_suggestions=improvement_suggestions
        )
        
        success = await analytics_service.collect_user_satisfaction_feedback(db, feedback)
        
        if success:
            return {"status": "success", "message": "User feedback collected successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to collect user feedback")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error collecting user feedback: {str(e)}")


@router.get("/analytics/system-performance", response_model=Dict[str, Any])
async def get_system_performance(
    db: Session = Depends(get_db)
):
    """Get system-wide performance metrics."""
    try:
        metrics = await analytics_service.calculate_system_performance_metrics(db)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving system performance: {str(e)}")


# A/B Testing endpoints
@router.post("/ab-testing/experiments")
async def create_ab_experiment(
    experiment_name: str,
    description: str,
    control_approach: str,
    variant_approach: str,
    success_metric: str,
    target_sample_size: int = 100,
    duration_days: int = 30,
    created_by: str = "system",
    db: Session = Depends(get_db)
):
    """Create a new A/B test experiment."""
    try:
        experiment_id = await ab_testing_service.create_experiment(
            db, experiment_name, description, control_approach, variant_approach,
            success_metric, target_sample_size, duration_days, created_by
        )
        
        if experiment_id:
            return {"status": "success", "experiment_id": experiment_id, "message": "A/B test experiment created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create A/B test experiment")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating A/B test experiment: {str(e)}")


@router.get("/ab-testing/experiments", response_model=List[Dict[str, Any]])
async def get_active_experiments(
    db: Session = Depends(get_db)
):
    """Get all active A/B test experiments."""
    try:
        experiments = await ab_testing_service.get_active_experiments(db)
        return experiments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving active experiments: {str(e)}")


@router.get("/ab-testing/experiments/{experiment_id}/results", response_model=Dict[str, Any])
async def get_experiment_results(
    experiment_id: str,
    db: Session = Depends(get_db)
):
    """Get results and analysis for an A/B test experiment."""
    try:
        results = await ab_testing_service.get_experiment_results(db, experiment_id)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving experiment results: {str(e)}")


@router.post("/ab-testing/sessions/{session_id}/assign")
async def assign_session_to_experiment(
    session_id: str,
    experiment_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Assign a session to an A/B test experiment."""
    try:
        variant = await ab_testing_service.assign_session_to_experiment(db, session_id, experiment_id)
        
        if variant:
            return {"status": "success", "variant": variant.value, "message": "Session assigned to A/B test"}
        else:
            return {"status": "no_assignment", "message": "No active experiments available for assignment"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assigning session to A/B test: {str(e)}")


@router.post("/ab-testing/sessions/{session_id}/result")
async def record_ab_test_result(
    session_id: str,
    success_achieved: bool,
    metric_value: Optional[float] = None,
    additional_metrics: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """Record the result of an A/B test session."""
    try:
        success = await ab_testing_service.record_test_result(
            db, session_id, success_achieved, metric_value, additional_metrics
        )
        
        if success:
            return {"status": "success", "message": "A/B test result recorded successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to record A/B test result")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording A/B test result: {str(e)}")


@router.post("/ab-testing/experiments/{experiment_id}/end")
async def end_experiment(
    experiment_id: str,
    db: Session = Depends(get_db)
):
    """End an A/B test experiment."""
    try:
        success = await ab_testing_service.end_experiment(db, experiment_id)
        
        if success:
            return {"status": "success", "message": "A/B test experiment ended successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to end A/B test experiment")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ending A/B test experiment: {str(e)}")


# Learning and optimization endpoints
@router.get("/learning/prioritized-solutions", response_model=List[Dict[str, Any]])
async def get_prioritized_solutions(
    problem_category: str,
    machine_model: Optional[str] = None,
    limit: int = Query(10, description="Maximum number of solutions to return"),
    db: Session = Depends(get_db)
):
    """Get prioritized solutions based on historical success."""
    try:
        solutions = await learning_service.prioritize_solutions(db, problem_category, machine_model, limit)
        
        # Convert to dict format for JSON response
        result = []
        for solution in solutions:
            result.append({
                "solution_text": solution.solution_text,
                "problem_category": solution.problem_category,
                "machine_model": solution.machine_model,
                "priority_score": solution.priority_score,
                "success_rate": solution.success_rate,
                "times_used": solution.times_used,
                "avg_effectiveness": solution.avg_effectiveness,
                "recency_factor": solution.recency_factor,
                "expert_verified": solution.expert_verified
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving prioritized solutions: {str(e)}")


@router.get("/learning/insights", response_model=List[Dict[str, Any]])
async def get_learning_insights(
    days: int = Query(30, description="Number of days to analyze"),
    limit: int = Query(10, description="Maximum number of insights to return"),
    db: Session = Depends(get_db)
):
    """Get learning insights from recent data patterns."""
    try:
        insights = await learning_service.get_learning_insights(db, days, limit)
        
        # Convert to dict format for JSON response
        result = []
        for insight in insights:
            result.append({
                "insight_type": insight.insight_type,
                "description": insight.description,
                "confidence": insight.confidence,
                "supporting_data": insight.supporting_data,
                "actionable_recommendation": insight.actionable_recommendation
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving learning insights: {str(e)}")


@router.post("/learning/session-outcome")
async def learn_from_session(
    session_id: str,
    outcome: str,
    solutions_used: List[str],
    user_feedback: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """Learn from a completed session outcome."""
    try:
        success = await learning_service.learn_from_session_outcome(
            db, session_id, outcome, solutions_used, user_feedback
        )
        
        if success:
            return {"status": "success", "message": "Learning from session outcome completed"}
        else:
            raise HTTPException(status_code=500, detail="Failed to learn from session outcome")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error learning from session outcome: {str(e)}")


@router.post("/learning/solution-priority")
async def update_solution_priority(
    solution_text: str,
    problem_category: str,
    machine_model: Optional[str] = None,
    success_feedback: bool = True,
    expert_verified: bool = False,
    db: Session = Depends(get_db)
):
    """Update solution priority based on new feedback."""
    try:
        success = await learning_service.update_solution_priority(
            db, solution_text, problem_category, machine_model, success_feedback, expert_verified
        )
        
        if success:
            return {"status": "success", "message": "Solution priority updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update solution priority")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating solution priority: {str(e)}")


# Dashboard endpoint for administrators
@router.get("/dashboard", response_model=Dict[str, Any])
async def get_analytics_dashboard(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics dashboard data."""
    try:
        # Gather all dashboard data
        session_metrics = await analytics_service.get_session_success_metrics(db, days)
        top_solutions = await analytics_service.get_top_performing_solutions(db, 10, 3)
        response_quality = await analytics_service.get_ai_response_quality_metrics(db, days)
        system_performance = await analytics_service.calculate_system_performance_metrics(db)
        active_experiments = await ab_testing_service.get_active_experiments(db)
        learning_insights = await learning_service.get_learning_insights(db, days, 5)
        
        # Convert learning insights to dict format
        insights_dict = []
        for insight in learning_insights:
            insights_dict.append({
                "insight_type": insight.insight_type,
                "description": insight.description,
                "confidence": insight.confidence,
                "supporting_data": insight.supporting_data,
                "actionable_recommendation": insight.actionable_recommendation
            })
        
        return {
            "period_days": days,
            "session_metrics": session_metrics,
            "top_solutions": top_solutions,
            "response_quality": response_quality,
            "system_performance": system_performance,
            "active_experiments": active_experiments,
            "learning_insights": insights_dict,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics dashboard: {str(e)}")