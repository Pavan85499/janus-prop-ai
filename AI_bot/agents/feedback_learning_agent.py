"""
Feedback & Learning Agent for Real Estate AI System

This agent implements a continuous learning pipeline that:
- Feeds results back into retraining/adjustments
- Monitors AI accuracy and user behavior
- Provides internal dashboard metrics
- Enables continuous model improvement
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4
import structlog
from pydantic import BaseModel, Field
import json

from agents.base_agent import BaseAgent, AgentConfig, AgentResponse


class UserFeedback(BaseModel):
    """User feedback on AI predictions and insights."""
    
    feedback_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    property_id: str
    insight_id: str
    feedback_type: str  # "accuracy", "usefulness", "action_taken", "correction"
    rating: Optional[int] = Field(None, ge=1, le=5)  # 1-5 scale
    comment: Optional[str] = None
    action_taken: Optional[str] = None  # What action the user took
    expected_outcome: Optional[str] = None  # What user expected vs what happened
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PredictionAccuracy(BaseModel):
    """Accuracy metrics for AI predictions."""
    
    prediction_id: str
    property_id: str
    insight_type: str
    predicted_value: Any
    actual_value: Any
    accuracy_score: float  # 0.0 to 1.0
    confidence_level: float  # AI's confidence in the prediction
    prediction_date: datetime
    actual_date: datetime
    error_margin: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LearningMetrics(BaseModel):
    """Overall learning and improvement metrics."""
    
    agent_id: str
    metric_date: datetime
    total_predictions: int
    accurate_predictions: int
    accuracy_rate: float
    average_confidence: float
    user_satisfaction_score: float
    improvement_trend: str  # "improving", "stable", "declining"
    top_insight_types: List[Dict[str, Any]]
    areas_for_improvement: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FeedbackLearningAgent(BaseAgent):
    """
    Agent responsible for continuous learning and feedback collection.
    
    Features:
    - Collect user feedback on AI insights
    - Track prediction accuracy over time
    - Monitor user behavior patterns
    - Generate learning metrics for internal dashboard
    - Identify areas for model improvement
    """
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.logger = structlog.get_logger(self.__class__.__name__)
        
        # Storage for feedback and metrics
        self.user_feedback: List[UserFeedback] = []
        self.prediction_accuracy: List[PredictionAccuracy] = []
        self.learning_metrics: Dict[str, LearningMetrics] = {}
        
        # Configuration
        self.feedback_retention_days = 365  # Keep feedback for 1 year
        self.metrics_update_interval = 24  # Update metrics every 24 hours
        self.min_feedback_for_learning = 10  # Minimum feedback before learning
        
    def _get_supported_operations(self) -> List[str]:
        """Return list of operations this agent supports."""
        return [
            "collect_feedback",
            "track_prediction_accuracy",
            "generate_learning_metrics",
            "identify_improvement_areas",
            "get_agent_performance",
            "export_learning_data"
        ]

    async def _process_request_impl(
        self,
        request: Union[str, Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a feedback or learning request."""
        if isinstance(request, str):
            response = await self._handle_text_request(request, context)
        else:
            response = await self._handle_structured_request(request, context)

        if response.success:
            return response.data
        else:
            raise Exception(response.error)
    
    async def _handle_text_request(self, request: str, context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Handle natural language requests."""
        request_lower = request.lower()
        
        if "feedback" in request_lower:
            return await self._handle_feedback_text(request, context)
        elif "accuracy" in request_lower or "performance" in request_lower:
            return await self._handle_accuracy_text(request, context)
        elif "metrics" in request_lower or "dashboard" in request_lower:
            return await self._handle_metrics_text(request, context)
        else:
            return AgentResponse(
                success=True,
                data={
                    "message": "Text-based requests supported for feedback, accuracy, and metrics",
                    "examples": [
                        "Show feedback for property analysis",
                        "Get accuracy metrics for market predictions",
                        "Generate learning dashboard metrics"
                    ]
                }
            )
    
    async def _handle_structured_request(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Handle structured requests."""
        request_type = request.get("type")
        
        if request_type == "collect_feedback":
            return await self._collect_feedback(request, context)
        elif request_type == "track_prediction_accuracy":
            return await self._track_prediction_accuracy(request, context)
        elif request_type == "generate_learning_metrics":
            return await self._generate_learning_metrics(request, context)
        elif request_type == "get_agent_performance":
            return await self._get_agent_performance(request, context)
        else:
            return AgentResponse(
                success=False,
                error=f"Unsupported request type: {request_type}",
                data=None
            )
    
    async def _collect_feedback(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Collect user feedback on AI insights."""
        try:
            feedback_data = request.get("feedback", {})
            
            # Validate required fields
            required_fields = ["user_id", "property_id", "insight_id", "feedback_type"]
            for field in required_fields:
                if field not in feedback_data:
                    return AgentResponse(
                        success=False,
                        error=f"Required field missing: {field}",
                        data=None
                    )
            
            # Create feedback object
            feedback = UserFeedback(**feedback_data)
            
            # Store feedback
            self.user_feedback.append(feedback)
            
            # Clean old feedback
            await self._cleanup_old_feedback()
            
            # Check if we have enough feedback for learning
            if len(self.user_feedback) >= self.min_feedback_for_learning:
                await self._trigger_learning_cycle()
            
            self.logger.info(
                "Feedback collected",
                feedback_id=feedback.feedback_id,
                user_id=feedback.user_id,
                feedback_type=feedback.feedback_type
            )
            
            return AgentResponse(
                success=True,
                data={
                    "message": "Feedback collected successfully",
                    "feedback_id": feedback.feedback_id,
                    "total_feedback": len(self.user_feedback)
                }
            )
            
        except Exception as e:
            self.logger.error("Error collecting feedback", error=str(e))
            return AgentResponse(
                success=False,
                error=f"Failed to collect feedback: {str(e)}",
                data=None
            )
    
    async def _track_prediction_accuracy(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Track the accuracy of AI predictions."""
        try:
            accuracy_data = request.get("accuracy_data", {})
            
            # Validate required fields
            required_fields = ["prediction_id", "property_id", "insight_type", "predicted_value", "actual_value"]
            for field in required_fields:
                if field not in accuracy_data:
                    return AgentResponse(
                        success=False,
                        error=f"Required field missing: {field}",
                        data=None
                    )
            
            # Calculate accuracy score
            predicted = accuracy_data["predicted_value"]
            actual = accuracy_data["actual_value"]
            
            if isinstance(predicted, (int, float)) and isinstance(actual, (int, float)):
                # Numeric prediction accuracy
                if actual != 0:
                    error_margin = abs(predicted - actual) / actual
                    accuracy_score = max(0.0, 1.0 - error_margin)
                else:
                    accuracy_score = 1.0 if predicted == actual else 0.0
            else:
                # Categorical prediction accuracy
                accuracy_score = 1.0 if predicted == actual else 0.0
                error_margin = 0.0
            
            # Create accuracy record
            accuracy_record = PredictionAccuracy(
                prediction_id=accuracy_data["prediction_id"],
                property_id=accuracy_data["property_id"],
                insight_type=accuracy_data["insight_type"],
                predicted_value=predicted,
                actual_value=actual,
                accuracy_score=accuracy_score,
                confidence_level=accuracy_data.get("confidence_level", 0.0),
                prediction_date=accuracy_data.get("prediction_date", datetime.utcnow()),
                actual_date=accuracy_data.get("actual_date", datetime.utcnow()),
                error_margin=error_margin,
                metadata=accuracy_data.get("metadata", {})
            )
            
            # Store accuracy record
            self.prediction_accuracy.append(accuracy_record)
            
            self.logger.info(
                "Prediction accuracy tracked",
                prediction_id=accuracy_record.prediction_id,
                accuracy_score=accuracy_score,
                insight_type=accuracy_record.insight_type
            )
            
            return AgentResponse(
                success=True,
                data={
                    "message": "Prediction accuracy tracked successfully",
                    "accuracy_score": accuracy_score,
                    "total_accuracy_records": len(self.prediction_accuracy)
                }
            )
            
        except Exception as e:
            self.logger.error("Error tracking prediction accuracy", error=str(e))
            return AgentResponse(
                success=False,
                error=f"Failed to track prediction accuracy: {str(e)}",
                data=None
            )
    
    async def _generate_learning_metrics(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Generate comprehensive learning metrics for internal dashboard."""
        try:
            agent_id = request.get("agent_id", "all")
            date_range = request.get("date_range", 30)  # days
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=date_range)
            
            # Filter data by date range
            recent_feedback = [
                f for f in self.user_feedback 
                if start_date <= f.timestamp <= end_date
            ]
            
            recent_accuracy = [
                a for a in self.prediction_accuracy
                if start_date <= a.prediction_date <= end_date
            ]
            
            # Generate metrics
            metrics = await self._calculate_learning_metrics(
                agent_id, recent_feedback, recent_accuracy, start_date, end_date
            )
            
            # Store metrics
            self.learning_metrics[agent_id] = metrics
            
            return AgentResponse(
                success=True,
                data=metrics.dict()
            )
            
        except Exception as e:
            self.logger.error("Error generating learning metrics", error=str(e))
            return AgentResponse(
                success=False,
                error=f"Failed to generate learning metrics: {str(e)}",
                data=None
            )
    
    async def _calculate_learning_metrics(
        self, 
        agent_id: str, 
        feedback: List[UserFeedback], 
        accuracy: List[PredictionAccuracy],
        start_date: datetime,
        end_date: datetime
    ) -> LearningMetrics:
        """Calculate comprehensive learning metrics."""
        
        # Calculate accuracy metrics
        total_predictions = len(accuracy)
        accurate_predictions = len([a for a in accuracy if a.accuracy_score >= 0.8])
        accuracy_rate = accurate_predictions / total_predictions if total_predictions > 0 else 0.0
        
        # Calculate average confidence
        if accuracy:
            average_confidence = sum(a.confidence_level for a in accuracy) / len(accuracy)
        else:
            average_confidence = 0.0
        
        # Calculate user satisfaction
        if feedback:
            satisfaction_scores = [f.rating for f in feedback if f.rating is not None]
            user_satisfaction_score = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 0.0
        else:
            user_satisfaction_score = 0.0
        
        # Determine improvement trend
        if len(accuracy) >= 20:
            # Split into two halves and compare
            mid_point = len(accuracy) // 2
            first_half = accuracy[:mid_point]
            second_half = accuracy[mid_point:]
            
            first_accuracy = sum(a.accuracy_score for a in first_half) / len(first_half)
            second_accuracy = sum(a.accuracy_score for a in second_half) / len(second_half)
            
            if second_accuracy > first_accuracy + 0.05:
                improvement_trend = "improving"
            elif second_accuracy < first_accuracy - 0.05:
                improvement_trend = "declining"
            else:
                improvement_trend = "stable"
        else:
            improvement_trend = "insufficient_data"
        
        # Identify top insight types
        insight_type_counts = {}
        for a in accuracy:
            insight_type = a.insight_type
            if insight_type not in insight_type_counts:
                insight_type_counts[insight_type] = {"count": 0, "total_accuracy": 0.0}
            insight_type_counts[insight_type]["count"] += 1
            insight_type_counts[insight_type]["total_accuracy"] += a.accuracy_score
        
        top_insight_types = []
        for insight_type, data in insight_type_counts.items():
            avg_accuracy = data["total_accuracy"] / data["count"]
            top_insight_types.append({
                "insight_type": insight_type,
                "count": data["count"],
                "average_accuracy": avg_accuracy
            })
        
        # Sort by count and take top 5
        top_insight_types.sort(key=lambda x: x["count"], reverse=True)
        top_insight_types = top_insight_types[:5]
        
        # Identify areas for improvement
        areas_for_improvement = []
        
        if accuracy_rate < 0.8:
            areas_for_improvement.append("Overall prediction accuracy needs improvement")
        
        if average_confidence < 0.7:
            areas_for_improvement.append("Confidence calibration needs adjustment")
        
        if user_satisfaction_score < 4.0:
            areas_for_improvement.append("User satisfaction needs improvement")
        
        # Check specific insight types
        for insight_data in top_insight_types:
            if insight_data["average_accuracy"] < 0.7:
                areas_for_improvement.append(f"{insight_data['insight_type']} predictions need improvement")
        
        return LearningMetrics(
            agent_id=agent_id,
            metric_date=datetime.utcnow(),
            total_predictions=total_predictions,
            accurate_predictions=accurate_predictions,
            accuracy_rate=accuracy_rate,
            average_confidence=average_confidence,
            user_satisfaction_score=user_satisfaction_score,
            improvement_trend=improvement_trend,
            top_insight_types=top_insight_types,
            areas_for_improvement=areas_for_improvement
        )
    
    async def _get_agent_performance(self, request: Dict[str, Any], context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Get performance metrics for a specific agent."""
        try:
            agent_id = request.get("agent_id")
            
            if not agent_id:
                return AgentResponse(
                    success=False,
                    error="Agent ID is required",
                    data=None
                )
            
            if agent_id not in self.learning_metrics:
                return AgentResponse(
                    success=False,
                    error=f"No metrics available for agent {agent_id}",
                    data=None
                )
            
            metrics = self.learning_metrics[agent_id]
            
            return AgentResponse(
                success=True,
                data=metrics.dict()
            )
            
        except Exception as e:
            self.logger.error("Error getting agent performance", error=str(e))
            return AgentResponse(
                success=False,
                error=f"Failed to get agent performance: {str(e)}",
                data=None
            )
    
    async def _handle_feedback_text(self, request: str, context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Handle feedback-related text requests."""
        if "show" in request.lower() or "get" in request.lower():
            # Return summary of recent feedback
            recent_feedback = self.user_feedback[-10:] if self.user_feedback else []
            
            return AgentResponse(
                success=True,
                data={
                    "message": f"Recent feedback summary",
                    "total_feedback": len(self.user_feedback),
                    "recent_feedback": [
                        {
                            "feedback_id": f.feedback_id,
                            "feedback_type": f.feedback_type,
                            "rating": f.rating,
                            "timestamp": f.timestamp.isoformat()
                        }
                        for f in recent_feedback
                    ]
                }
            )
        else:
            return AgentResponse(
                success=True,
                data={
                    "message": "Feedback collection ready",
                    "supported_types": ["accuracy", "usefulness", "action_taken", "correction"]
                }
            )
    
    async def _handle_accuracy_text(self, request: str, context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Handle accuracy-related text requests."""
        if "metrics" in request.lower():
            return await self._generate_learning_metrics({
                "type": "generate_learning_metrics",
                "agent_id": "all",
                "date_range": 30
            }, context)
        else:
            return AgentResponse(
                success=True,
                data={
                    "message": "Accuracy tracking active",
                    "total_accuracy_records": len(self.prediction_accuracy)
                }
            )
    
    async def _handle_metrics_text(self, request: str, context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Handle metrics-related text requests."""
        return await self._generate_learning_metrics({
            "type": "generate_learning_metrics",
            "agent_id": "all",
            "date_range": 30
        }, context)
    
    async def _cleanup_old_feedback(self):
        """Remove old feedback data to manage storage."""
        cutoff_date = datetime.utcnow() - timedelta(days=self.feedback_retention_days)
        
        original_count = len(self.user_feedback)
        self.user_feedback = [f for f in self.user_feedback if f.timestamp > cutoff_date]
        
        removed_count = original_count - len(self.user_feedback)
        if removed_count > 0:
            self.logger.info(f"Cleaned up {removed_count} old feedback records")
    
    async def _trigger_learning_cycle(self):
        """Trigger a learning cycle when sufficient feedback is available."""
        self.logger.info("Triggering learning cycle", feedback_count=len(self.user_feedback))
        
        # In production, this would:
        # 1. Analyze feedback patterns
        # 2. Identify model weaknesses
        # 3. Trigger retraining if needed
        # 4. Update model parameters
        
        # For now, just log the event
        self.logger.info("Learning cycle triggered - model improvement analysis ready")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of this agent."""
        return {
            "status": "healthy",
            "agent_type": "feedback_learning",
            "capabilities": await self.get_capabilities(),
            "feedback_count": len(self.user_feedback),
            "accuracy_records": len(self.prediction_accuracy),
            "learning_metrics": len(self.learning_metrics),
            "last_check": datetime.utcnow().isoformat()
        }
    
    async def shutdown(self):
        """Shutdown the agent."""
        self.logger.info("Feedback & Learning Agent shutting down")
        await super().shutdown()
