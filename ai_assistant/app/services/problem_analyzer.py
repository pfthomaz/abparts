"""
Advanced problem analysis service for AutoBoss AI Assistant.

This service provides sophisticated problem analysis capabilities including
confidence scoring, fallback mechanisms, and diagnostic assessment generation.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..llm_client import LLMClient, ConversationMessage
from .troubleshooting_types import DiagnosticAssessment, ConfidenceLevel

logger = logging.getLogger(__name__)


class ProblemType(Enum):
    """Types of problems that can be analyzed."""
    STARTUP = "startup"
    PERFORMANCE = "performance"
    MECHANICAL = "mechanical"
    ELECTRICAL = "electrical"
    HYDRAULIC = "hydraulic"
    REMOTE_CONTROL = "remote_control"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


@dataclass
class ProblemKeywords:
    """Keywords associated with different problem types."""
    startup: List[str]
    performance: List[str]
    mechanical: List[str]
    electrical: List[str]
    hydraulic: List[str]
    remote_control: List[str]
    maintenance: List[str]


class ProblemAnalyzer:
    """Advanced problem analysis with confidence scoring and fallback mechanisms."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.problem_keywords = self._initialize_keywords()
        
    def _initialize_keywords(self) -> ProblemKeywords:
        """Initialize problem type keywords for classification."""
        return ProblemKeywords(
            startup=[
                "start", "startup", "boot", "power on", "turn on", "initialize", 
                "won't start", "doesn't start", "not starting", "startup failure",
                "power", "switch", "button", "remote start", "ignition"
            ],
            performance=[
                "cleaning", "suction", "debris", "dirt", "performance", "efficiency",
                "slow", "weak", "poor cleaning", "not cleaning", "leaves debris",
                "suction power", "vacuum", "pickup", "collection"
            ],
            mechanical=[
                "wheels", "movement", "stuck", "grinding", "noise", "vibration",
                "mechanical", "moving parts", "rotation", "belt", "gear",
                "won't move", "doesn't move", "jerky movement", "strange noise"
            ],
            electrical=[
                "electrical", "power", "battery", "charging", "lights", "display",
                "control panel", "electronics", "circuit", "fuse", "wiring",
                "no power", "dead battery", "won't charge", "electrical fault"
            ],
            hydraulic=[
                "hydraulic", "pressure", "fluid", "leak", "pump", "hose",
                "water pressure", "flow", "circulation", "hydraulic system",
                "low pressure", "no pressure", "fluid leak", "pump noise"
            ],
            remote_control=[
                "remote", "control", "controller", "signal", "connection",
                "wireless", "communication", "range", "response", "lag",
                "remote not working", "no response", "intermittent", "signal loss"
            ],
            maintenance=[
                "maintenance", "service", "filter", "replacement", "cleaning",
                "scheduled", "overdue", "parts", "wear", "inspection",
                "needs service", "maintenance due", "filter clogged", "worn parts"
            ]
        )
    
    async def analyze_problem_with_confidence(
        self,
        problem_description: str,
        machine_context: Optional[Dict] = None,
        language: str = "en"
    ) -> Tuple[DiagnosticAssessment, float]:
        """
        Analyze problem with confidence scoring and fallback mechanisms.
        
        Args:
            problem_description: User's description of the problem
            machine_context: Information about the specific machine
            language: Language for responses
            
        Returns:
            Tuple of (DiagnosticAssessment, confidence_score)
        """
        logger.info(f"Analyzing problem with confidence scoring: {problem_description[:100]}...")
        
        # Step 1: Keyword-based classification for initial confidence
        problem_type, keyword_confidence = self._classify_problem_by_keywords(problem_description)
        
        # Step 2: LLM-based analysis for detailed assessment
        llm_assessment = await self._llm_problem_analysis(
            problem_description, machine_context, language, problem_type
        )
        
        # Step 3: Calculate overall confidence score
        overall_confidence = self._calculate_confidence_score(
            keyword_confidence, llm_assessment, problem_description, machine_context
        )
        
        # Step 4: Apply fallback mechanisms if confidence is low
        if overall_confidence < 0.5:
            logger.info(f"Low confidence ({overall_confidence:.2f}), applying fallback mechanisms")
            llm_assessment = await self._apply_fallback_analysis(
                problem_description, machine_context, language, overall_confidence
            )
        
        # Step 5: Adjust confidence level in assessment
        llm_assessment.confidence_level = self._score_to_confidence_level(overall_confidence)
        
        return llm_assessment, overall_confidence
    
    def _classify_problem_by_keywords(self, problem_description: str) -> Tuple[ProblemType, float]:
        """Classify problem type based on keywords and return confidence."""
        description_lower = problem_description.lower()
        
        # Count keyword matches for each category
        category_scores = {}
        
        for problem_type in ProblemType:
            if problem_type == ProblemType.UNKNOWN:
                continue
                
            keywords = getattr(self.problem_keywords, problem_type.value)
            matches = sum(1 for keyword in keywords if keyword in description_lower)
            
            if matches > 0:
                # Weight by keyword specificity and frequency
                specificity_weight = 1.0 + (len(keywords) - matches) / len(keywords)
                category_scores[problem_type] = matches * specificity_weight
        
        if not category_scores:
            return ProblemType.UNKNOWN, 0.1
        
        # Find best match
        best_type = max(category_scores, key=category_scores.get)
        best_score = category_scores[best_type]
        
        # Calculate confidence based on score and description length
        max_possible_score = len(getattr(self.problem_keywords, best_type.value))
        confidence = min(best_score / max_possible_score, 1.0)
        
        # Adjust confidence based on description quality
        description_quality = self._assess_description_quality(problem_description)
        confidence *= description_quality
        
        logger.info(f"Keyword classification: {best_type.value} with confidence {confidence:.2f}")
        return best_type, confidence
    
    def _assess_description_quality(self, description: str) -> float:
        """Assess the quality and completeness of the problem description."""
        quality_score = 0.5  # Base score
        
        # Length factor (optimal range: 20-200 characters)
        length = len(description)
        if 20 <= length <= 200:
            quality_score += 0.2
        elif length > 200:
            quality_score += 0.1
        
        # Specificity indicators
        specific_terms = [
            "when", "after", "during", "before", "while", "exactly", "specifically",
            "always", "sometimes", "never", "error", "message", "code", "number"
        ]
        specificity_matches = sum(1 for term in specific_terms if term in description.lower())
        quality_score += min(specificity_matches * 0.05, 0.2)
        
        # Technical detail indicators
        technical_terms = [
            "pressure", "temperature", "voltage", "rpm", "speed", "flow", "level",
            "gauge", "meter", "sensor", "switch", "valve", "pump", "motor"
        ]
        technical_matches = sum(1 for term in technical_terms if term in description.lower())
        quality_score += min(technical_matches * 0.03, 0.15)
        
        # Symptom clarity
        symptom_words = [
            "noise", "sound", "vibration", "leak", "smoke", "smell", "hot", "cold",
            "slow", "fast", "stuck", "loose", "tight", "broken", "cracked"
        ]
        symptom_matches = sum(1 for word in symptom_words if word in description.lower())
        quality_score += min(symptom_matches * 0.02, 0.1)
        
        return min(quality_score, 1.0)
    
    async def _llm_problem_analysis(
        self,
        problem_description: str,
        machine_context: Optional[Dict],
        language: str,
        suggested_type: ProblemType
    ) -> DiagnosticAssessment:
        """Perform LLM-based problem analysis with suggested problem type."""
        
        # Build enhanced system prompt with suggested type
        system_prompt = self._build_enhanced_diagnostic_prompt(
            machine_context, language, suggested_type
        )
        
        # Build analysis prompt
        analysis_prompt = self._build_detailed_analysis_prompt(
            problem_description, language, suggested_type
        )
        
        messages = [
            ConversationMessage(role="system", content=system_prompt),
            ConversationMessage(role="user", content=analysis_prompt)
        ]
        
        # Get LLM analysis
        response = await self.llm_client.generate_response(messages, language=language)
        
        if response.success:
            return self._parse_enhanced_diagnostic_response(response.content, language)
        else:
            # Fallback to keyword-based assessment
            return self._create_keyword_based_assessment(
                problem_description, suggested_type, language
            )
    
    def _build_enhanced_diagnostic_prompt(
        self,
        machine_context: Optional[Dict],
        language: str,
        suggested_type: ProblemType
    ) -> str:
        """Build enhanced system prompt with problem type suggestion."""
        
        base_prompts = {
            "en": f"""You are an expert AutoBoss machine diagnostic assistant with advanced problem analysis capabilities.

Based on initial analysis, this appears to be a {suggested_type.value.replace('_', ' ')} related issue.

Your response must be in this exact JSON format:
{{
    "problem_category": "category name",
    "likely_causes": ["cause 1", "cause 2", "cause 3"],
    "confidence_level": "high|medium|low|very_low",
    "recommended_steps": ["step 1", "step 2", "step 3"],
    "safety_warnings": ["warning 1", "warning 2"],
    "estimated_duration": 30,
    "requires_expert": false,
    "diagnostic_reasoning": "explanation of your analysis process",
    "alternative_causes": ["alternative 1", "alternative 2"]
}}

Focus on providing:
1. Precise problem categorization
2. Most likely root causes based on symptoms
3. Realistic confidence assessment
4. Step-by-step troubleshooting approach
5. Safety considerations
6. Time estimates
7. Clear reasoning for your diagnosis
8. Alternative possibilities to consider""",
            
            "el": f"""Είστε ειδικός βοηθός διάγνωσης μηχανημάτων AutoBoss με προηγμένες δυνατότητες ανάλυσης προβλημάτων.

Με βάση την αρχική ανάλυση, αυτό φαίνεται να είναι ένα ζήτημα που σχετίζεται με {suggested_type.value.replace('_', ' ')}.

Η απάντησή σας πρέπει να είναι σε αυτή την ακριβή μορφή JSON:
{{
    "problem_category": "όνομα κατηγορίας",
    "likely_causes": ["αιτία 1", "αιτία 2", "αιτία 3"],
    "confidence_level": "high|medium|low|very_low",
    "recommended_steps": ["βήμα 1", "βήμα 2", "βήμα 3"],
    "safety_warnings": ["προειδοποίηση 1", "προειδοποίηση 2"],
    "estimated_duration": 30,
    "requires_expert": false,
    "diagnostic_reasoning": "εξήγηση της διαδικασίας ανάλυσής σας",
    "alternative_causes": ["εναλλακτική 1", "εναλλακτική 2"]
}}"""
        }
        
        prompt = base_prompts.get(language, base_prompts["en"])
        
        if machine_context:
            machine_info = f"""

Machine Information:
- Model: {machine_context.get('model', 'Unknown')}
- Serial Number: {machine_context.get('serial_number', 'Unknown')}
- Operating Hours: {machine_context.get('operating_hours', 'Unknown')}
- Last Maintenance: {machine_context.get('last_maintenance', 'Unknown')}
- Installation Date: {machine_context.get('installation_date', 'Unknown')}

Use this machine-specific information to provide more targeted diagnostic analysis."""
            prompt += machine_info
        
        return prompt
    
    def _build_detailed_analysis_prompt(
        self,
        problem_description: str,
        language: str,
        suggested_type: ProblemType
    ) -> str:
        """Build detailed analysis prompt with problem type context."""
        
        prompts = {
            "en": f"""Analyze this AutoBoss machine problem with advanced diagnostic techniques:

Problem Description: {problem_description}

Initial Classification: {suggested_type.value.replace('_', ' ')} issue

Provide comprehensive analysis including:
1. Validate or refine the initial classification
2. Identify the most probable root causes
3. Assess your confidence level honestly
4. Create a logical troubleshooting sequence
5. Consider safety implications
6. Estimate realistic timeframes
7. Explain your diagnostic reasoning
8. Suggest alternative causes to investigate

Focus on actionable, specific guidance that a technician can follow.""",
            
            "el": f"""Αναλύστε αυτό το πρόβλημα μηχανήματος AutoBoss με προηγμένες διαγνωστικές τεχνικές:

Περιγραφή Προβλήματος: {problem_description}

Αρχική Κατηγοριοποίηση: Ζήτημα {suggested_type.value.replace('_', ' ')}

Παρέχετε ολοκληρωμένη ανάλυση που περιλαμβάνει:
1. Επικυρώστε ή βελτιώστε την αρχική κατηγοριοποίηση
2. Εντοπίστε τις πιο πιθανές βασικές αιτίες
3. Αξιολογήστε το επίπεδο εμπιστοσύνης σας ειλικρινά
4. Δημιουργήστε μια λογική ακολουθία αντιμετώπισης προβλημάτων
5. Εξετάστε τις επιπτώσεις ασφαλείας
6. Εκτιμήστε ρεαλιστικά χρονοδιαγράμματα
7. Εξηγήστε τη διαγνωστική σας συλλογιστική
8. Προτείνετε εναλλακτικές αιτίες για διερεύνηση"""
        }
        
        return prompts.get(language, prompts["en"])
    
    def _parse_enhanced_diagnostic_response(
        self, 
        response_content: str, 
        language: str
    ) -> DiagnosticAssessment:
        """Parse enhanced LLM response with additional fields."""
        try:
            # Extract JSON from response
            import json
            response_content = response_content.strip()
            start_idx = response_content.find('{')
            end_idx = response_content.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_content = response_content[start_idx:end_idx]
            data = json.loads(json_content)
            
            # Parse confidence level
            confidence_mapping = {
                'high': ConfidenceLevel.high,
                'medium': ConfidenceLevel.medium,
                'low': ConfidenceLevel.low,
                'very_low': ConfidenceLevel.very_low
            }
            
            confidence_level = confidence_mapping.get(
                data.get('confidence_level', 'medium').lower(),
                ConfidenceLevel.medium
            )
            
            return DiagnosticAssessment(
                problem_category=data.get('problem_category', 'other'),
                likely_causes=data.get('likely_causes', [])[:5],
                confidence_level=confidence_level,
                recommended_steps=data.get('recommended_steps', [])[:5],
                safety_warnings=data.get('safety_warnings', [])[:3],
                estimated_duration=min(max(data.get('estimated_duration', 30), 5), 180),
                requires_expert=bool(data.get('requires_expert', False))
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse enhanced diagnostic response: {e}")
            return self._create_generic_assessment(language)
    
    def _calculate_confidence_score(
        self,
        keyword_confidence: float,
        llm_assessment: DiagnosticAssessment,
        problem_description: str,
        machine_context: Optional[Dict]
    ) -> float:
        """Calculate overall confidence score from multiple factors."""
        
        # Base confidence from keyword analysis
        confidence = keyword_confidence * 0.4
        
        # LLM confidence level contribution
        llm_confidence_scores = {
            ConfidenceLevel.high: 0.9,
            ConfidenceLevel.medium: 0.7,
            ConfidenceLevel.low: 0.4,
            ConfidenceLevel.very_low: 0.2
        }
        llm_confidence = llm_confidence_scores.get(llm_assessment.confidence_level, 0.5)
        confidence += llm_confidence * 0.4
        
        # Machine context bonus
        if machine_context:
            context_completeness = sum([
                1 for key in ['model', 'serial_number', 'operating_hours', 'last_maintenance']
                if machine_context.get(key) and machine_context[key] != 'Unknown'
            ]) / 4
            confidence += context_completeness * 0.1
        
        # Problem description quality bonus
        description_quality = self._assess_description_quality(problem_description)
        confidence += (description_quality - 0.5) * 0.1
        
        return min(max(confidence, 0.0), 1.0)
    
    async def _apply_fallback_analysis(
        self,
        problem_description: str,
        machine_context: Optional[Dict],
        language: str,
        current_confidence: float
    ) -> DiagnosticAssessment:
        """Apply fallback mechanisms when confidence is low."""
        
        logger.info(f"Applying fallback analysis for low confidence ({current_confidence:.2f})")
        
        # Fallback strategy 1: Generic troubleshooting approach
        if current_confidence < 0.2:
            return self._create_generic_troubleshooting_assessment(language)
        
        # Fallback strategy 2: Simplified LLM analysis with more specific prompts
        elif current_confidence < 0.4:
            return await self._simplified_llm_analysis(
                problem_description, machine_context, language
            )
        
        # Fallback strategy 3: Enhanced keyword-based analysis
        else:
            return self._create_enhanced_keyword_assessment(
                problem_description, language
            )
    
    def _create_generic_troubleshooting_assessment(self, language: str) -> DiagnosticAssessment:
        """Create generic troubleshooting assessment for very low confidence."""
        
        generic_responses = {
            "en": {
                "category": "other",
                "causes": [
                    "Insufficient information to determine specific cause",
                    "Multiple potential issues require systematic investigation",
                    "Problem may require expert diagnosis"
                ],
                "steps": [
                    "Perform basic visual inspection of the machine",
                    "Check all power connections and switches",
                    "Verify that all safety systems are functioning",
                    "Document any unusual sounds, smells, or visual indicators",
                    "Contact technical support with detailed observations"
                ],
                "warnings": [
                    "Ensure machine is powered off before any inspection",
                    "Do not attempt repairs without proper training",
                    "Contact expert support if problem persists"
                ]
            },
            "el": {
                "category": "other",
                "causes": [
                    "Ανεπαρκείς πληροφορίες για προσδιορισμό συγκεκριμένης αιτίας",
                    "Πολλαπλά πιθανά προβλήματα απαιτούν συστηματική διερεύνηση",
                    "Το πρόβλημα μπορεί να απαιτεί διάγνωση ειδικού"
                ],
                "steps": [
                    "Εκτελέστε βασική οπτική επιθεώρηση του μηχανήματος",
                    "Ελέγξτε όλες τις συνδέσεις τροφοδοσίας και διακόπτες",
                    "Επαληθεύστε ότι όλα τα συστήματα ασφαλείας λειτουργούν",
                    "Καταγράψτε τυχόν ασυνήθιστους ήχους, οσμές ή οπτικούς δείκτες",
                    "Επικοινωνήστε με την τεχνική υποστήριξη με λεπτομερείς παρατηρήσεις"
                ],
                "warnings": [
                    "Βεβαιωθείτε ότι το μηχάνημα είναι απενεργοποιημένο πριν από οποιαδήποτε επιθεώρηση",
                    "Μην επιχειρήσετε επισκευές χωρίς κατάλληλη εκπαίδευση",
                    "Επικοινωνήστε με την υποστήριξη ειδικών εάν το πρόβλημα παραμένει"
                ]
            }
        }
        
        responses = generic_responses.get(language, generic_responses["en"])
        
        return DiagnosticAssessment(
            problem_category=responses["category"],
            likely_causes=responses["causes"],
            confidence_level=ConfidenceLevel.very_low,
            recommended_steps=responses["steps"],
            safety_warnings=responses["warnings"],
            estimated_duration=45,
            requires_expert=True
        )
    
    async def _simplified_llm_analysis(
        self,
        problem_description: str,
        machine_context: Optional[Dict],
        language: str
    ) -> DiagnosticAssessment:
        """Perform simplified LLM analysis with more specific prompts."""
        
        system_prompt = f"""You are an AutoBoss troubleshooting assistant. The problem description is unclear or incomplete.

Provide a conservative diagnostic assessment in JSON format:
{{
    "problem_category": "most likely category",
    "likely_causes": ["general cause 1", "general cause 2"],
    "confidence_level": "low",
    "recommended_steps": ["basic step 1", "basic step 2", "contact support"],
    "safety_warnings": ["safety warning"],
    "estimated_duration": 30,
    "requires_expert": true
}}

Focus on safe, basic troubleshooting steps and recommend expert consultation."""
        
        user_prompt = f"""Problem: {problem_description}

Provide conservative troubleshooting guidance for this unclear problem description."""
        
        messages = [
            ConversationMessage(role="system", content=system_prompt),
            ConversationMessage(role="user", content=user_prompt)
        ]
        
        response = await self.llm_client.generate_response(messages, language=language)
        
        if response.success:
            return self._parse_enhanced_diagnostic_response(response.content, language)
        else:
            return self._create_generic_troubleshooting_assessment(language)
    
    def _create_enhanced_keyword_assessment(
        self, 
        problem_description: str, 
        language: str
    ) -> DiagnosticAssessment:
        """Create enhanced assessment based on keyword analysis."""
        
        problem_type, _ = self._classify_problem_by_keywords(problem_description)
        
        # Create assessment based on problem type
        if problem_type == ProblemType.STARTUP:
            return self._create_startup_assessment(language)
        elif problem_type == ProblemType.PERFORMANCE:
            return self._create_performance_assessment(language)
        elif problem_type == ProblemType.MECHANICAL:
            return self._create_mechanical_assessment(language)
        elif problem_type == ProblemType.ELECTRICAL:
            return self._create_electrical_assessment(language)
        elif problem_type == ProblemType.HYDRAULIC:
            return self._create_hydraulic_assessment(language)
        elif problem_type == ProblemType.REMOTE_CONTROL:
            return self._create_remote_control_assessment(language)
        elif problem_type == ProblemType.MAINTENANCE:
            return self._create_maintenance_assessment(language)
        else:
            return self._create_generic_troubleshooting_assessment(language)
    
    def _create_startup_assessment(self, language: str) -> DiagnosticAssessment:
        """Create startup-specific assessment."""
        responses = {
            "en": {
                "causes": ["Power supply issue", "Control system malfunction", "Safety interlock engaged"],
                "steps": ["Check power connections", "Verify control panel operation", "Check safety switches"],
                "warnings": ["Ensure proper electrical safety procedures"]
            }
        }
        
        response = responses.get(language, responses["en"])
        
        return DiagnosticAssessment(
            problem_category="startup",
            likely_causes=response["causes"],
            confidence_level=ConfidenceLevel.medium,
            recommended_steps=response["steps"],
            safety_warnings=response["warnings"],
            estimated_duration=30,
            requires_expert=False
        )
    
    def _create_performance_assessment(self, language: str) -> DiagnosticAssessment:
        """Create performance-specific assessment."""
        responses = {
            "en": {
                "causes": ["Clogged filters", "Reduced suction power", "Worn cleaning components"],
                "steps": ["Inspect and clean filters", "Check suction system", "Examine cleaning brushes"],
                "warnings": ["Turn off machine before maintenance"]
            }
        }
        
        response = responses.get(language, responses["en"])
        
        return DiagnosticAssessment(
            problem_category="cleaning_performance",
            likely_causes=response["causes"],
            confidence_level=ConfidenceLevel.medium,
            recommended_steps=response["steps"],
            safety_warnings=response["warnings"],
            estimated_duration=25,
            requires_expert=False
        )
    
    def _create_mechanical_assessment(self, language: str) -> DiagnosticAssessment:
        """Create mechanical-specific assessment."""
        responses = {
            "en": {
                "causes": ["Worn mechanical parts", "Lubrication issues", "Misalignment"],
                "steps": ["Inspect moving parts", "Check lubrication points", "Verify alignment"],
                "warnings": ["Ensure machine is stopped before inspection"]
            }
        }
        
        response = responses.get(language, responses["en"])
        
        return DiagnosticAssessment(
            problem_category="mechanical",
            likely_causes=response["causes"],
            confidence_level=ConfidenceLevel.medium,
            recommended_steps=response["steps"],
            safety_warnings=response["warnings"],
            estimated_duration=35,
            requires_expert=False
        )
    
    def _create_electrical_assessment(self, language: str) -> DiagnosticAssessment:
        """Create electrical-specific assessment."""
        responses = {
            "en": {
                "causes": ["Power supply fault", "Electrical connection issue", "Control system failure"],
                "steps": ["Check power supply", "Inspect electrical connections", "Test control systems"],
                "warnings": ["Follow electrical safety procedures", "Turn off power before inspection"]
            }
        }
        
        response = responses.get(language, responses["en"])
        
        return DiagnosticAssessment(
            problem_category="electrical",
            likely_causes=response["causes"],
            confidence_level=ConfidenceLevel.medium,
            recommended_steps=response["steps"],
            safety_warnings=response["warnings"],
            estimated_duration=40,
            requires_expert=True
        )
    
    def _create_hydraulic_assessment(self, language: str) -> DiagnosticAssessment:
        """Create hydraulic-specific assessment."""
        responses = {
            "en": {
                "causes": ["Hydraulic fluid leak", "Pump malfunction", "Pressure regulation issue"],
                "steps": ["Check for fluid leaks", "Inspect hydraulic pump", "Test pressure levels"],
                "warnings": ["Handle hydraulic fluids safely", "Relieve pressure before service"]
            }
        }
        
        response = responses.get(language, responses["en"])
        
        return DiagnosticAssessment(
            problem_category="hydraulic",
            likely_causes=response["causes"],
            confidence_level=ConfidenceLevel.medium,
            recommended_steps=response["steps"],
            safety_warnings=response["warnings"],
            estimated_duration=30,
            requires_expert=False
        )
    
    def _create_remote_control_assessment(self, language: str) -> DiagnosticAssessment:
        """Create remote control-specific assessment."""
        responses = {
            "en": {
                "causes": ["Signal interference", "Battery issue", "Communication module fault"],
                "steps": ["Check remote battery", "Test signal range", "Inspect communication module"],
                "warnings": ["Ensure safe operating distance"]
            }
        }
        
        response = responses.get(language, responses["en"])
        
        return DiagnosticAssessment(
            problem_category="remote_control",
            likely_causes=response["causes"],
            confidence_level=ConfidenceLevel.medium,
            recommended_steps=response["steps"],
            safety_warnings=response["warnings"],
            estimated_duration=20,
            requires_expert=False
        )
    
    def _create_maintenance_assessment(self, language: str) -> DiagnosticAssessment:
        """Create maintenance-specific assessment."""
        responses = {
            "en": {
                "causes": ["Scheduled maintenance overdue", "Component wear", "Filter replacement needed"],
                "steps": ["Review maintenance schedule", "Inspect wear components", "Replace filters as needed"],
                "warnings": ["Follow maintenance safety procedures"]
            }
        }
        
        response = responses.get(language, responses["en"])
        
        return DiagnosticAssessment(
            problem_category="maintenance",
            likely_causes=response["causes"],
            confidence_level=ConfidenceLevel.medium,
            recommended_steps=response["steps"],
            safety_warnings=response["warnings"],
            estimated_duration=45,
            requires_expert=False
        )
    
    def _create_keyword_based_assessment(
        self, 
        problem_description: str, 
        problem_type: ProblemType, 
        language: str
    ) -> DiagnosticAssessment:
        """Create assessment based on keyword classification."""
        
        if problem_type == ProblemType.STARTUP:
            return self._create_startup_assessment(language)
        elif problem_type == ProblemType.PERFORMANCE:
            return self._create_performance_assessment(language)
        else:
            return self._create_generic_troubleshooting_assessment(language)
    
    def _create_generic_assessment(self, language: str) -> DiagnosticAssessment:
        """Create generic assessment when all else fails."""
        return self._create_generic_troubleshooting_assessment(language)
    
    def _score_to_confidence_level(self, score: float) -> ConfidenceLevel:
        """Convert numeric confidence score to confidence level enum."""
        if score >= 0.8:
            return ConfidenceLevel.high
        elif score >= 0.5:
            return ConfidenceLevel.medium
        elif score >= 0.2:
            return ConfidenceLevel.low
        else:
            return ConfidenceLevel.very_low