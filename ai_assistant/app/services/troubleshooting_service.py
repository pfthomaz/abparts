"""
Troubleshooting workflow service for AutoBoss AI Assistant.

This service manages interactive troubleshooting sessions, providing step-by-step
guidance and adapting based on user feedback.
"""

import json
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..models import TroubleshootingStep
from ..llm_client import LLMClient, ConversationMessage
from ..session_manager import SessionManager
from ..database import get_db_session
from .problem_analyzer import ProblemAnalyzer
from .abparts_integration import abparts_integration
from .troubleshooting_types import (
    DiagnosticAssessment, TroubleshootingStepData, WorkflowState,
    ConfidenceLevel, StepStatus
)
from sqlalchemy import text

logger = logging.getLogger(__name__)


class TroubleshootingService:
    """Service for managing interactive troubleshooting workflows."""
    
    def __init__(self, llm_client: LLMClient, session_manager: SessionManager):
        self.llm_client = llm_client
        self.session_manager = session_manager
        self.problem_analyzer = ProblemAnalyzer(llm_client)
        
    async def start_troubleshooting_workflow(
        self,
        session_id: str,
        problem_description: str,
        machine_id: Optional[str] = None,
        user_id: Optional[str] = None,
        language: str = "en"
    ) -> DiagnosticAssessment:
        """
        Start a new troubleshooting workflow with initial problem analysis.
        
        Args:
            session_id: ID of the troubleshooting session
            problem_description: User's description of the problem
            machine_id: ID of the specific machine (optional)
            user_id: ID of the user for context (optional)
            language: Language for responses
            
        Returns:
            Initial diagnostic assessment
        """
        logger.info(f"Starting troubleshooting workflow for session {session_id}")
        
        # Get machine context if machine_id is provided
        machine_context = None
        if machine_id:
            machine_details = await abparts_integration.get_machine_details(machine_id)
            if machine_details:
                # Get additional context
                maintenance_history = await abparts_integration.get_maintenance_history(machine_id, limit=5)
                parts_usage = await abparts_integration.get_parts_usage_data(machine_id, days=30)
                hours_history = await abparts_integration.get_machine_hours_history(machine_id, limit=5)
                maintenance_suggestions = await abparts_integration.get_preventive_maintenance_suggestions(machine_id)
                
                machine_context = {
                    "machine_details": machine_details,
                    "recent_maintenance": maintenance_history,
                    "recent_parts_usage": parts_usage,
                    "hours_history": hours_history,
                    "maintenance_suggestions": maintenance_suggestions
                }
                
                logger.info(f"Retrieved machine context for {machine_id}: {machine_details['name']} ({machine_details['model_type']})")
        
        # Get user preferences if user_id is provided
        user_context = None
        if user_id:
            user_preferences = await abparts_integration.get_user_preferences(user_id)
            if user_preferences:
                user_context = user_preferences
                # Use user's preferred language if not explicitly specified
                if language == "en" and user_preferences.get("preferred_language"):
                    language = user_preferences["preferred_language"]
                
                logger.info(f"Retrieved user context for {user_id}: {user_preferences['name']} (lang: {language})")
        
        # Generate initial diagnostic assessment with enhanced context
        assessment = await self._analyze_problem_description(
            problem_description, machine_context, user_context, language
        )
        
        # Store assessment in database with enhanced context
        await self._store_diagnostic_assessment(session_id, assessment, machine_context, user_context)
        
        # Generate first troubleshooting step
        if assessment.confidence_level != ConfidenceLevel.very_low:
            first_step = await self._generate_first_step(
                session_id, assessment, machine_context, language
            )
            await self._store_troubleshooting_step(session_id, first_step)
        
        logger.info(f"Diagnostic assessment completed with {assessment.confidence_level.value} confidence")
        return assessment
    
    async def _analyze_problem_description(
        self,
        problem_description: str,
        machine_context: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> DiagnosticAssessment:
        """Analyze problem description and generate diagnostic assessment using advanced analyzer."""
        
        # Use the advanced problem analyzer with confidence scoring
        assessment, confidence_score = await self.problem_analyzer.analyze_problem_with_confidence(
            problem_description=problem_description,
            machine_context=machine_context,
            user_context=user_context,
            language=language
        )
        
        logger.info(f"Problem analysis completed with confidence score: {confidence_score:.2f}")
        logger.info(f"Assessment: {assessment.problem_category} - {assessment.confidence_level.value}")
        
        return assessment
    
    def _build_diagnostic_system_prompt(
        self, 
        machine_context: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> str:
        """Build system prompt for diagnostic analysis."""
        
        base_prompts = {
            "en": """You are an expert AutoBoss machine diagnostic assistant. Analyze problems and provide structured troubleshooting guidance.

Your response must be in this exact JSON format:
{
    "problem_category": "category name",
    "likely_causes": ["cause 1", "cause 2", "cause 3"],
    "confidence_level": "high|medium|low|very_low",
    "recommended_steps": ["step 1", "step 2", "step 3"],
    "safety_warnings": ["warning 1", "warning 2"],
    "estimated_duration": 30,
    "requires_expert": false
}

Categories: "startup", "cleaning_performance", "mechanical", "electrical", "hydraulic", "remote_control", "maintenance", "other"
Confidence levels: high (80-100%), medium (50-79%), low (20-49%), very_low (0-19%)""",
            
            "el": """Είστε ειδικός βοηθός διάγνωσης μηχανημάτων AutoBoss. Αναλύστε προβλήματα και παρέχετε δομημένη καθοδήγηση αντιμετώπισης προβλημάτων.

Η απάντησή σας πρέπει να είναι σε αυτή την ακριβή μορφή JSON:
{
    "problem_category": "όνομα κατηγορίας",
    "likely_causes": ["αιτία 1", "αιτία 2", "αιτία 3"],
    "confidence_level": "high|medium|low|very_low",
    "recommended_steps": ["βήμα 1", "βήμα 2", "βήμα 3"],
    "safety_warnings": ["προειδοποίηση 1", "προειδοποίηση 2"],
    "estimated_duration": 30,
    "requires_expert": false
}

Κατηγορίες: "startup", "cleaning_performance", "mechanical", "electrical", "hydraulic", "remote_control", "maintenance", "other"
Επίπεδα εμπιστοσύνης: high (80-100%), medium (50-79%), low (20-49%), very_low (0-19%)""",
            
            "ar": """أنت مساعد خبير في تشخيص آلات AutoBoss. حلل المشاكل وقدم إرشادات منظمة لاستكشاف الأخطاء وإصلاحها.

يجب أن تكون إجابتك بهذا التنسيق JSON الدقيق:
{
    "problem_category": "اسم الفئة",
    "likely_causes": ["السبب 1", "السبب 2", "السبب 3"],
    "confidence_level": "high|medium|low|very_low",
    "recommended_steps": ["الخطوة 1", "الخطوة 2", "الخطوة 3"],
    "safety_warnings": ["تحذير 1", "تحذير 2"],
    "estimated_duration": 30,
    "requires_expert": false
}

الفئات: "startup", "cleaning_performance", "mechanical", "electrical", "hydraulic", "remote_control", "maintenance", "other"
مستويات الثقة: high (80-100%), medium (50-79%), low (20-49%), very_low (0-19%)""",
            
            "es": """Eres un asistente experto en diagnóstico de máquinas AutoBoss. Analiza problemas y proporciona orientación estructurada para la solución de problemas.

Tu respuesta debe estar en este formato JSON exacto:
{
    "problem_category": "nombre de categoría",
    "likely_causes": ["causa 1", "causa 2", "causa 3"],
    "confidence_level": "high|medium|low|very_low",
    "recommended_steps": ["paso 1", "paso 2", "paso 3"],
    "safety_warnings": ["advertencia 1", "advertencia 2"],
    "estimated_duration": 30,
    "requires_expert": false
}

Categorías: "startup", "cleaning_performance", "mechanical", "electrical", "hydraulic", "remote_control", "maintenance", "other"
Niveles de confianza: high (80-100%), medium (50-79%), low (20-49%), very_low (0-19%)""",
            
            "tr": """AutoBoss makine teşhis konusunda uzman bir asistansınız. Sorunları analiz edin ve yapılandırılmış sorun giderme rehberliği sağlayın.

Yanıtınız tam olarak bu JSON formatında olmalıdır:
{
    "problem_category": "kategori adı",
    "likely_causes": ["neden 1", "neden 2", "neden 3"],
    "confidence_level": "high|medium|low|very_low",
    "recommended_steps": ["adım 1", "adım 2", "adım 3"],
    "safety_warnings": ["uyarı 1", "uyarı 2"],
    "estimated_duration": 30,
    "requires_expert": false
}

Kategoriler: "startup", "cleaning_performance", "mechanical", "electrical", "hydraulic", "remote_control", "maintenance", "other"
Güven seviyeleri: high (80-100%), medium (50-79%), low (20-49%), very_low (0-19%)""",
            
            "no": """Du er en ekspert AutoBoss maskin diagnoseassistent. Analyser problemer og gi strukturert feilsøkingsveiledning.

Ditt svar må være i dette nøyaktige JSON-formatet:
{
    "problem_category": "kategorinavn",
    "likely_causes": ["årsak 1", "årsak 2", "årsak 3"],
    "confidence_level": "high|medium|low|very_low",
    "recommended_steps": ["trinn 1", "trinn 2", "trinn 3"],
    "safety_warnings": ["advarsel 1", "advarsel 2"],
    "estimated_duration": 30,
    "requires_expert": false
}

Kategorier: "startup", "cleaning_performance", "mechanical", "electrical", "hydraulic", "remote_control", "maintenance", "other"
Tillitsnivåer: high (80-100%), medium (50-79%), low (20-49%), very_low (0-19%)"""
        }
        
        prompt = base_prompts.get(language, base_prompts["en"])
        
        # Add machine context information
        if machine_context and machine_context.get("machine_details"):
            machine_details = machine_context["machine_details"]
            machine_info = f"""

Machine Information:
- Model: {machine_details.get('model_type', 'Unknown')}
- Serial Number: {machine_details.get('serial_number', 'Unknown')}
- Name: {machine_details.get('name', 'Unknown')}
- Current Hours: {machine_details.get('latest_hours', 'Unknown')}
- Organization: {machine_details.get('customer_organization', {}).get('name', 'Unknown')}"""
            
            # Add recent maintenance history
            if machine_context.get("recent_maintenance"):
                maintenance_history = machine_context["recent_maintenance"][:3]  # Last 3 records
                machine_info += "\n\nRecent Maintenance History:"
                for i, record in enumerate(maintenance_history, 1):
                    machine_info += f"\n{i}. {record['maintenance_date'][:10]} - {record['maintenance_type']} - {record['description'][:100]}"
            
            # Add maintenance suggestions
            if machine_context.get("maintenance_suggestions"):
                suggestions = machine_context["maintenance_suggestions"][:2]  # Top 2 suggestions
                machine_info += "\n\nMaintenance Suggestions:"
                for i, suggestion in enumerate(suggestions, 1):
                    machine_info += f"\n{i}. {suggestion['type']} service ({suggestion['priority']} priority) - {suggestion['description']}"
            
            machine_info += "\n\nUse this machine-specific information to provide more targeted diagnostic analysis."
            prompt += machine_info
        
        # Add user context information
        if user_context:
            user_info = f"""

User Context:
- Organization: {user_context.get('organization', {}).get('name', 'Unknown')}
- Role: {user_context.get('role', 'Unknown')}
- Preferred Language: {user_context.get('preferred_language', 'en')}

Consider the user's role and organization when providing recommendations."""
            prompt += user_info
        
        return prompt
    
    def _build_analysis_prompt(self, problem_description: str, language: str) -> str:
        """Build analysis prompt for the specific problem."""
        
        prompts = {
            "en": f"""Analyze this AutoBoss machine problem and provide a structured diagnostic assessment:

Problem Description: {problem_description}

Provide your analysis in the exact JSON format specified in the system prompt. Focus on:
1. Categorizing the problem type
2. Identifying the most likely causes
3. Assessing your confidence level
4. Recommending initial troubleshooting steps
5. Noting any safety concerns
6. Estimating time needed
7. Determining if expert help is needed""",
            
            "el": f"""Αναλύστε αυτό το πρόβλημα μηχανήματος AutoBoss και παρέχετε μια δομημένη διαγνωστική αξιολόγηση:

Περιγραφή Προβλήματος: {problem_description}

Παρέχετε την ανάλυσή σας στην ακριβή μορφή JSON που καθορίζεται στην προτροπή συστήματος. Εστιάστε σε:
1. Κατηγοριοποίηση του τύπου προβλήματος
2. Εντοπισμός των πιο πιθανών αιτιών
3. Αξιολόγηση του επιπέδου εμπιστοσύνης σας
4. Σύσταση αρχικών βημάτων αντιμετώπισης προβλημάτων
5. Σημείωση τυχόν ανησυχιών ασφαλείας
6. Εκτίμηση του χρόνου που χρειάζεται
7. Καθορισμός εάν χρειάζεται βοήθεια ειδικού""",
            
            "ar": f"""حلل مشكلة آلة AutoBoss هذه وقدم تقييماً تشخيصياً منظماً:

وصف المشكلة: {problem_description}

قدم تحليلك بتنسيق JSON الدقيق المحدد في موجه النظام. ركز على:
1. تصنيف نوع المشكلة
2. تحديد الأسباب الأكثر احتمالاً
3. تقييم مستوى ثقتك
4. التوصية بخطوات استكشاف الأخطاء الأولية
5. ملاحظة أي مخاوف تتعلق بالسلامة
6. تقدير الوقت المطلوب
7. تحديد ما إذا كانت هناك حاجة لمساعدة خبير""",
            
            "es": f"""Analiza este problema de la máquina AutoBoss y proporciona una evaluación diagnóstica estructurada:

Descripción del Problema: {problem_description}

Proporciona tu análisis en el formato JSON exacto especificado en el prompt del sistema. Enfócate en:
1. Categorizar el tipo de problema
2. Identificar las causas más probables
3. Evaluar tu nivel de confianza
4. Recomendar pasos iniciales de solución de problemas
5. Notar cualquier preocupación de seguridad
6. Estimar el tiempo necesario
7. Determinar si se necesita ayuda experta""",
            
            "tr": f"""Bu AutoBoss makine problemini analiz edin ve yapılandırılmış bir tanı değerlendirmesi sağlayın:

Sorun Açıklaması: {problem_description}

Analizinizi sistem isteminde belirtilen tam JSON formatında sağlayın. Şunlara odaklanın:
1. Sorun türünü kategorize etme
2. En olası nedenleri belirleme
3. Güven seviyenizi değerlendirme
4. İlk sorun giderme adımlarını önerme
5. Herhangi bir güvenlik endişesini not etme
6. Gereken süreyi tahmin etme
7. Uzman yardımına ihtiyaç olup olmadığını belirleme""",
            
            "no": f"""Analyser dette AutoBoss maskinproblemet og gi en strukturert diagnostisk vurdering:

Problembeskrivelse: {problem_description}

Gi din analyse i det nøyaktige JSON-formatet spesifisert i systemprompten. Fokuser på:
1. Kategorisere problemtypen
2. Identifisere de mest sannsynlige årsakene
3. Vurdere ditt tillitsnivå
4. Anbefale innledende feilsøkingstrinn
5. Merke seg eventuelle sikkerhetsproblemer
6. Estimere tiden som trengs
7. Bestemme om eksperthjelp er nødvendig"""
        }
        
        return prompts.get(language, prompts["en"])
    
    def _parse_diagnostic_response(self, response_content: str, language: str) -> DiagnosticAssessment:
        """Parse LLM response into structured diagnostic assessment."""
        try:
            # Try to extract JSON from response
            response_content = response_content.strip()
            
            # Find JSON content (handle cases where LLM adds extra text)
            start_idx = response_content.find('{')
            end_idx = response_content.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_content = response_content[start_idx:end_idx]
            data = json.loads(json_content)
            
            # Validate required fields
            required_fields = [
                'problem_category', 'likely_causes', 'confidence_level',
                'recommended_steps', 'safety_warnings', 'estimated_duration', 'requires_expert'
            ]
            
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Parse confidence level
            confidence_mapping = {
                'high': ConfidenceLevel.high,
                'medium': ConfidenceLevel.medium,
                'low': ConfidenceLevel.low,
                'very_low': ConfidenceLevel.very_low
            }
            
            confidence_level = confidence_mapping.get(
                data['confidence_level'].lower(), 
                ConfidenceLevel.medium
            )
            
            return DiagnosticAssessment(
                problem_category=data['problem_category'],
                likely_causes=data['likely_causes'][:5],  # Limit to 5 causes
                confidence_level=confidence_level,
                recommended_steps=data['recommended_steps'][:5],  # Limit to 5 steps
                safety_warnings=data['safety_warnings'][:3],  # Limit to 3 warnings
                estimated_duration=min(max(data['estimated_duration'], 5), 180),  # 5-180 minutes
                requires_expert=bool(data['requires_expert'])
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse diagnostic response: {e}")
            # Fallback to generic assessment
            return self._create_generic_assessment("Unknown problem", language)
    
    def _create_generic_assessment(self, problem_description: str, language: str) -> DiagnosticAssessment:
        """Create a generic diagnostic assessment when analysis fails."""
        
        generic_responses = {
            "en": {
                "category": "other",
                "causes": ["Unknown cause", "Requires further investigation"],
                "steps": ["Check basic connections", "Verify power supply", "Consult manual"],
                "warnings": ["Ensure machine is powered off before inspection"]
            },
            "el": {
                "category": "other",
                "causes": ["Άγνωστη αιτία", "Απαιτεί περαιτέρω διερεύνηση"],
                "steps": ["Ελέγξτε τις βασικές συνδέσεις", "Επαληθεύστε την τροφοδοσία", "Συμβουλευτείτε το εγχειρίδιο"],
                "warnings": ["Βεβαιωθείτε ότι το μηχάνημα είναι απενεργοποιημένο πριν από την επιθεώρηση"]
            },
            "ar": {
                "category": "other",
                "causes": ["سبب غير معروف", "يتطلب مزيد من التحقيق"],
                "steps": ["تحقق من الاتصالات الأساسية", "تحقق من مصدر الطاقة", "راجع الدليل"],
                "warnings": ["تأكد من إيقاف تشغيل الآلة قبل الفحص"]
            },
            "es": {
                "category": "other",
                "causes": ["Causa desconocida", "Requiere más investigación"],
                "steps": ["Verificar conexiones básicas", "Verificar suministro de energía", "Consultar manual"],
                "warnings": ["Asegurar que la máquina esté apagada antes de la inspección"]
            },
            "tr": {
                "category": "other",
                "causes": ["Bilinmeyen neden", "Daha fazla araştırma gerektirir"],
                "steps": ["Temel bağlantıları kontrol edin", "Güç kaynağını doğrulayın", "Kılavuza başvurun"],
                "warnings": ["İncelemeden önce makinenin kapalı olduğundan emin olun"]
            },
            "no": {
                "category": "other",
                "causes": ["Ukjent årsak", "Krever videre undersøkelse"],
                "steps": ["Sjekk grunnleggende tilkoblinger", "Verifiser strømforsyning", "Konsulter manual"],
                "warnings": ["Sørg for at maskinen er slått av før inspeksjon"]
            }
        }
        
        responses = generic_responses.get(language, generic_responses["en"])
        
        return DiagnosticAssessment(
            problem_category=responses["category"],
            likely_causes=responses["causes"],
            confidence_level=ConfidenceLevel.very_low,
            recommended_steps=responses["steps"],
            safety_warnings=responses["warnings"],
            estimated_duration=30,
            requires_expert=True
        )
    
    async def _generate_first_step(
        self,
        session_id: str,
        assessment: DiagnosticAssessment,
        machine_context: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> TroubleshootingStepData:
        """Generate the first troubleshooting step based on assessment."""
        
        step_id = str(uuid.uuid4())
        
        # Use the first recommended step from assessment, enhanced with machine context
        base_instruction = assessment.recommended_steps[0] if assessment.recommended_steps else "Begin troubleshooting"
        
        # Enhance instruction with machine-specific information
        if machine_context and machine_context.get("machine_details"):
            machine_details = machine_context["machine_details"]
            model_type = machine_details.get("model_type", "")
            current_hours = machine_details.get("latest_hours", 0)
            
            # Add model-specific guidance
            if model_type in ["V3.1B", "V4.0"]:
                base_instruction += f" (for {model_type} model)"
            
            # Add hours-based context
            if current_hours > 0:
                base_instruction += f" - Machine has {current_hours} operating hours"
        
        instruction = base_instruction
        
        # Generate expected outcomes based on the step
        expected_outcomes = await self._generate_step_outcomes(instruction, language)
        
        return TroubleshootingStepData(
            step_id=step_id,
            step_number=1,
            instruction=instruction,
            expected_outcomes=expected_outcomes,
            user_feedback=None,
            status=StepStatus.pending,
            confidence_score=self._confidence_to_score(assessment.confidence_level),
            next_steps={},  # Will be populated based on user feedback
            requires_feedback=True,
            estimated_duration=assessment.estimated_duration // len(assessment.recommended_steps),
            safety_warnings=assessment.safety_warnings,
            created_at=datetime.utcnow(),
            completed_at=None
        )
    
    async def _generate_step_outcomes(self, instruction: str, language: str) -> List[str]:
        """Generate expected outcomes for a troubleshooting step."""
        
        outcome_templates = {
            "en": ["Problem resolved", "No change observed", "Problem partially resolved", "New symptoms appeared"],
            "el": ["Το πρόβλημα επιλύθηκε", "Δεν παρατηρήθηκε αλλαγή", "Το πρόβλημα επιλύθηκε μερικώς", "Εμφανίστηκαν νέα συμπτώματα"],
            "ar": ["تم حل المشكلة", "لم يلاحظ أي تغيير", "تم حل المشكلة جزئياً", "ظهرت أعراض جديدة"],
            "es": ["Problema resuelto", "No se observó cambio", "Problema parcialmente resuelto", "Aparecieron nuevos síntomas"],
            "tr": ["Sorun çözüldü", "Değişiklik gözlenmedi", "Sorun kısmen çözüldü", "Yeni belirtiler ortaya çıktı"],
            "no": ["Problem løst", "Ingen endring observert", "Problem delvis løst", "Nye symptomer dukket opp"]
        }
        
        return outcome_templates.get(language, outcome_templates["en"])
    
    def _confidence_to_score(self, confidence_level: ConfidenceLevel) -> float:
        """Convert confidence level to numeric score."""
        mapping = {
            ConfidenceLevel.high: 0.9,
            ConfidenceLevel.medium: 0.7,
            ConfidenceLevel.low: 0.4,
            ConfidenceLevel.very_low: 0.2
        }
        return mapping.get(confidence_level, 0.5)
    
    async def _store_diagnostic_assessment(
        self, 
        session_id: str, 
        assessment: DiagnosticAssessment,
        machine_context: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Store diagnostic assessment in database."""
        try:
            with get_db_session() as db:
                # Store as JSON in session metadata
                metadata = {
                    "diagnostic_assessment": {
                        "problem_category": assessment.problem_category,
                        "likely_causes": assessment.likely_causes,
                        "confidence_level": assessment.confidence_level.value,
                        "recommended_steps": assessment.recommended_steps,
                        "safety_warnings": assessment.safety_warnings,
                        "estimated_duration": assessment.estimated_duration,
                        "requires_expert": assessment.requires_expert,
                        "created_at": datetime.utcnow().isoformat()
                    }
                }
                
                # Add machine context to metadata
                if machine_context:
                    metadata["machine_context"] = machine_context
                
                # Add user context to metadata
                if user_context:
                    metadata["user_context"] = user_context
                
                query = text("""
                    UPDATE ai_sessions 
                    SET session_metadata = :metadata, updated_at = NOW()
                    WHERE session_id = :session_id
                """)
                db.execute(query, {
                    'session_id': session_id,
                    'metadata': json.dumps(metadata)
                })
                
        except Exception as e:
            logger.error(f"Failed to store diagnostic assessment: {e}")
    
    async def _store_troubleshooting_step(
        self, 
        session_id: str, 
        step: TroubleshootingStepData
    ) -> None:
        """Store troubleshooting step in database."""
        try:
            with get_db_session() as db:
                query = text("""
                    INSERT INTO troubleshooting_steps 
                    (step_id, session_id, step_number, instruction, expected_outcomes, 
                     user_feedback, completed, success, created_at)
                    VALUES (:step_id, :session_id, :step_number, :instruction, :expected_outcomes,
                            :user_feedback, :completed, :success, :created_at)
                """)
                db.execute(query, {
                    'step_id': step.step_id,
                    'session_id': session_id,
                    'step_number': step.step_number,
                    'instruction': step.instruction,
                    'expected_outcomes': json.dumps(step.expected_outcomes),
                    'user_feedback': step.user_feedback,
                    'completed': step.status == StepStatus.completed,
                    'success': step.status == StepStatus.completed,
                    'created_at': step.created_at
                })
                
        except Exception as e:
            logger.error(f"Failed to store troubleshooting step: {e}")
    
    async def process_user_feedback(
        self,
        session_id: str,
        step_id: str,
        user_feedback: str,
        language: str = "en"
    ) -> Optional[TroubleshootingStepData]:
        """
        Process user feedback for a troubleshooting step and generate next step.
        
        Args:
            session_id: ID of the troubleshooting session
            step_id: ID of the current step
            user_feedback: User's feedback on the step outcome
            language: Language for responses
            
        Returns:
            Next troubleshooting step or None if workflow is complete
        """
        logger.info(f"Processing user feedback for step {step_id} in session {session_id}")
        
        # Update current step with feedback
        await self._update_step_feedback(step_id, user_feedback)
        
        # Analyze feedback and determine next action
        next_action = await self._analyze_feedback(session_id, step_id, user_feedback, language)
        
        if next_action == "resolved":
            # Problem is resolved, complete the workflow
            await self.session_manager.update_session_status(session_id, "completed", "Problem resolved through troubleshooting")
            return None
        elif next_action == "escalate":
            # Escalate to expert support
            await self.session_manager.update_session_status(session_id, "escalated", "Requires expert assistance")
            return None
        else:
            # Generate next troubleshooting step
            return await self._generate_next_step(session_id, step_id, user_feedback, language)
    
    async def _update_step_feedback(self, step_id: str, user_feedback: str) -> None:
        """Update troubleshooting step with user feedback."""
        try:
            with get_db_session() as db:
                query = text("""
                    UPDATE troubleshooting_steps 
                    SET user_feedback = :feedback, completed = true, completed_at = NOW()
                    WHERE step_id = :step_id
                """)
                db.execute(query, {
                    'step_id': step_id,
                    'feedback': user_feedback
                })
                
        except Exception as e:
            logger.error(f"Failed to update step feedback: {e}")
    
    async def _analyze_feedback(
        self, 
        session_id: str, 
        step_id: str, 
        user_feedback: str, 
        language: str
    ) -> str:
        """Analyze user feedback to determine next action."""
        
        # Simple keyword-based analysis for now
        feedback_lower = user_feedback.lower()
        
        # Check for resolution indicators
        resolution_keywords = {
            "en": ["fixed", "resolved", "working", "solved", "better", "good"],
            "el": ["διορθώθηκε", "επιλύθηκε", "λειτουργεί", "καλύτερα", "καλό"],
            "ar": ["تم إصلاحه", "تم حله", "يعمل", "أفضل", "جيد"],
            "es": ["arreglado", "resuelto", "funcionando", "mejor", "bueno"],
            "tr": ["düzeltildi", "çözüldü", "çalışıyor", "daha iyi", "iyi"],
            "no": ["fikset", "løst", "fungerer", "bedre", "bra"]
        }
        
        # Check for escalation indicators
        escalation_keywords = {
            "en": ["worse", "broken", "failed", "can't", "unable", "stuck"],
            "el": ["χειρότερα", "χαλασμένο", "απέτυχε", "δεν μπορώ", "κολλημένο"],
            "ar": ["أسوأ", "معطل", "فشل", "لا أستطيع", "عالق"],
            "es": ["peor", "roto", "falló", "no puedo", "atascado"],
            "tr": ["daha kötü", "bozuk", "başarısız", "yapamıyorum", "takıldı"],
            "no": ["verre", "ødelagt", "mislyktes", "kan ikke", "fast"]
        }
        
        resolution_words = resolution_keywords.get(language, resolution_keywords["en"])
        escalation_words = escalation_keywords.get(language, escalation_keywords["en"])
        
        if any(word in feedback_lower for word in resolution_words):
            return "resolved"
        elif any(word in feedback_lower for word in escalation_words):
            return "escalate"
        else:
            return "continue"
    
    async def _generate_next_step(
        self,
        session_id: str,
        current_step_id: str,
        user_feedback: str,
        language: str
    ) -> TroubleshootingStepData:
        """Generate the next troubleshooting step based on current progress."""
        
        # Get current step and session context
        current_step = await self._get_troubleshooting_step(current_step_id)
        session_data = await self.session_manager.get_session(session_id)
        
        if not current_step or not session_data:
            raise ValueError("Could not retrieve step or session data")
        
        # Build context for next step generation
        context = {
            "current_step": current_step.instruction,
            "user_feedback": user_feedback,
            "step_number": current_step.step_number + 1,
            "session_metadata": session_data.get("metadata", {})
        }
        
        # Generate next step using LLM
        next_step_content = await self._generate_step_with_llm(context, language)
        
        # Create next step data
        step_id = str(uuid.uuid4())
        expected_outcomes = await self._generate_step_outcomes(next_step_content, language)
        
        next_step = TroubleshootingStepData(
            step_id=step_id,
            step_number=current_step.step_number + 1,
            instruction=next_step_content,
            expected_outcomes=expected_outcomes,
            user_feedback=None,
            status=StepStatus.pending,
            confidence_score=0.7,  # Default confidence for generated steps
            next_steps={},
            requires_feedback=True,
            estimated_duration=15,  # Default 15 minutes per step
            safety_warnings=[],
            created_at=datetime.utcnow(),
            completed_at=None
        )
        
        # Store the next step
        await self._store_troubleshooting_step(session_id, next_step)
        
        return next_step
    
    async def _generate_step_with_llm(self, context: Dict[str, Any], language: str) -> str:
        """Generate next troubleshooting step using LLM."""
        
        system_prompts = {
            "en": """You are an AutoBoss troubleshooting expert. Based on the current step and user feedback, generate the next logical troubleshooting step.

Provide only the instruction text for the next step. Be specific, clear, and actionable. Focus on one task at a time.""",
            
            "el": """Είστε ειδικός αντιμετώπισης προβλημάτων AutoBoss. Με βάση το τρέχον βήμα και τα σχόλια του χρήστη, δημιουργήστε το επόμενο λογικό βήμα αντιμετώπισης προβλημάτων.

Παρέχετε μόνο το κείμενο οδηγιών για το επόμενο βήμα. Να είστε συγκεκριμένοι, σαφείς και πρακτικοί. Εστιάστε σε μία εργασία κάθε φορά.""",
            
            "ar": """أنت خبير في استكشاف أخطاء AutoBoss وإصلاحها. بناءً على الخطوة الحالية وتعليقات المستخدم، قم بإنشاء الخطوة التالية المنطقية لاستكشاف الأخطاء وإصلاحها.

قدم فقط نص التعليمات للخطوة التالية. كن محدداً وواضحاً وقابلاً للتنفيذ. ركز على مهمة واحدة في كل مرة.""",
            
            "es": """Eres un experto en solución de problemas de AutoBoss. Basándote en el paso actual y los comentarios del usuario, genera el siguiente paso lógico de solución de problemas.

Proporciona solo el texto de instrucción para el siguiente paso. Sé específico, claro y práctico. Enfócate en una tarea a la vez.""",
            
            "tr": """AutoBoss sorun giderme uzmanısınız. Mevcut adım ve kullanıcı geri bildirimlerine dayanarak, bir sonraki mantıklı sorun giderme adımını oluşturun.

Sadece bir sonraki adım için talimat metnini sağlayın. Spesifik, açık ve uygulanabilir olun. Bir seferde bir göreve odaklanın.""",
            
            "no": """Du er en AutoBoss feilsøkingsekspert. Basert på gjeldende trinn og tilbakemelding fra brukeren, generer neste logiske feilsøkingstrinn.

Gi bare instruksjonsteksten for neste trinn. Vær spesifikk, klar og handlingsrettet. Fokuser på én oppgave om gangen."""
        }
        
        user_prompts = {
            "en": f"""Current step: {context['current_step']}
User feedback: {context['user_feedback']}
Step number: {context['step_number']}

Generate the next troubleshooting step based on this information.""",
            
            "el": f"""Τρέχον βήμα: {context['current_step']}
Σχόλια χρήστη: {context['user_feedback']}
Αριθμός βήματος: {context['step_number']}

Δημιουργήστε το επόμενο βήμα αντιμετώπισης προβλημάτων με βάση αυτές τις πληροφορίες.""",
            
            "ar": f"""الخطوة الحالية: {context['current_step']}
تعليقات المستخدم: {context['user_feedback']}
رقم الخطوة: {context['step_number']}

قم بإنشاء خطوة استكشاف الأخطاء التالية بناءً على هذه المعلومات.""",
            
            "es": f"""Paso actual: {context['current_step']}
Comentarios del usuario: {context['user_feedback']}
Número de paso: {context['step_number']}

Genera el siguiente paso de solución de problemas basado en esta información.""",
            
            "tr": f"""Mevcut adım: {context['current_step']}
Kullanıcı geri bildirimi: {context['user_feedback']}
Adım numarası: {context['step_number']}

Bu bilgilere dayanarak bir sonraki sorun giderme adımını oluşturun.""",
            
            "no": f"""Gjeldende trinn: {context['current_step']}
Tilbakemelding fra bruker: {context['user_feedback']}
Trinnnummer: {context['step_number']}

Generer neste feilsøkingstrinn basert på denne informasjonen."""
        }
        
        system_prompt = system_prompts.get(language, system_prompts["en"])
        user_prompt = user_prompts.get(language, user_prompts["en"])
        
        messages = [
            ConversationMessage(role="system", content=system_prompt),
            ConversationMessage(role="user", content=user_prompt)
        ]
        
        response = await self.llm_client.generate_response(messages, language=language)
        
        if response.success:
            return response.content.strip()
        else:
            # Fallback to generic next step
            fallback_steps = {
                "en": "Continue with the next logical troubleshooting step based on the current situation.",
                "el": "Συνεχίστε με το επόμενο λογικό βήμα αντιμετώπισης προβλημάτων με βάση την τρέχουσα κατάσταση.",
                "ar": "تابع مع الخطوة التالية المنطقية لاستكشاف الأخطاء بناءً على الوضع الحالي.",
                "es": "Continúa con el siguiente paso lógico de solución de problemas basado en la situación actual.",
                "tr": "Mevcut duruma göre bir sonraki mantıklı sorun giderme adımıyla devam edin.",
                "no": "Fortsett med neste logiske feilsøkingstrinn basert på gjeldende situasjon."
            }
            return fallback_steps.get(language, fallback_steps["en"])
    
    async def _get_troubleshooting_step(self, step_id: str) -> Optional[TroubleshootingStepData]:
        """Retrieve troubleshooting step from database."""
        try:
            with get_db_session() as db:
                query = text("""
                    SELECT step_id, session_id, step_number, instruction, expected_outcomes,
                           user_feedback, completed, success, created_at, completed_at
                    FROM troubleshooting_steps 
                    WHERE step_id = :step_id
                """)
                result = db.execute(query, {'step_id': step_id}).fetchone()
                
                if not result:
                    return None
                
                return TroubleshootingStepData(
                    step_id=str(result.step_id),
                    step_number=result.step_number,
                    instruction=result.instruction,
                    expected_outcomes=json.loads(result.expected_outcomes or '[]'),
                    user_feedback=result.user_feedback,
                    status=StepStatus.completed if result.completed else StepStatus.pending,
                    confidence_score=0.7,  # Default value
                    next_steps={},
                    requires_feedback=True,
                    estimated_duration=15,
                    safety_warnings=[],
                    created_at=result.created_at,
                    completed_at=result.completed_at
                )
                
        except Exception as e:
            logger.error(f"Failed to retrieve troubleshooting step: {e}")
            return None
    
    async def get_workflow_state(self, session_id: str) -> Optional[WorkflowState]:
        """Get current workflow state for a session."""
        try:
            # Get session data
            session_data = await self.session_manager.get_session(session_id)
            if not session_data:
                return None
            
            # Get diagnostic assessment from metadata
            metadata = session_data.get("metadata", {})
            diagnostic_data = metadata.get("diagnostic_assessment")
            diagnostic_assessment = None
            
            if diagnostic_data:
                diagnostic_assessment = DiagnosticAssessment(
                    problem_category=diagnostic_data["problem_category"],
                    likely_causes=diagnostic_data["likely_causes"],
                    confidence_level=ConfidenceLevel(diagnostic_data["confidence_level"]),
                    recommended_steps=diagnostic_data["recommended_steps"],
                    safety_warnings=diagnostic_data["safety_warnings"],
                    estimated_duration=diagnostic_data["estimated_duration"],
                    requires_expert=diagnostic_data["requires_expert"]
                )
            
            # Get troubleshooting steps
            with get_db_session() as db:
                query = text("""
                    SELECT step_id, step_number, instruction, expected_outcomes,
                           user_feedback, completed, success, created_at, completed_at
                    FROM troubleshooting_steps 
                    WHERE session_id = :session_id
                    ORDER BY step_number ASC
                """)
                results = db.execute(query, {'session_id': session_id}).fetchall()
                
                completed_steps = []
                current_step = None
                
                for row in results:
                    step = TroubleshootingStepData(
                        step_id=str(row.step_id),
                        step_number=row.step_number,
                        instruction=row.instruction,
                        expected_outcomes=json.loads(row.expected_outcomes or '[]'),
                        user_feedback=row.user_feedback,
                        status=StepStatus.completed if row.completed else StepStatus.pending,
                        confidence_score=0.7,
                        next_steps={},
                        requires_feedback=True,
                        estimated_duration=15,
                        safety_warnings=[],
                        created_at=row.created_at,
                        completed_at=row.completed_at
                    )
                    
                    if row.completed:
                        completed_steps.append(step)
                    else:
                        current_step = step
            
            return WorkflowState(
                session_id=session_id,
                current_step=current_step,
                completed_steps=completed_steps,
                diagnostic_assessment=diagnostic_assessment,
                workflow_status=session_data["status"],
                resolution_found=session_data["status"] == "completed",
                escalation_reason=session_data.get("resolution_summary") if session_data["status"] == "escalated" else None
            )
            
        except Exception as e:
            logger.error(f"Failed to get workflow state: {e}")
            return None