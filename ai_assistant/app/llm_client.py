"""
LLM Client for OpenAI integration.

This module provides a robust client for interacting with OpenAI's API,
including error handling, retries, and fallback mechanisms.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import time

import openai
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from .config import settings

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Available OpenAI models."""
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_3_5_TURBO = "gpt-3.5-turbo"


@dataclass
class LLMResponse:
    """Response from LLM with metadata."""
    content: str
    model_used: str
    tokens_used: int
    response_time: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class ConversationMessage:
    """Message in a conversation."""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: Optional[float] = None


class LLMClient:
    """
    Robust OpenAI client with error handling and fallback mechanisms.
    
    Features:
    - Automatic retries with exponential backoff
    - Model fallback (GPT-4 -> GPT-3.5-turbo)
    - Rate limit handling
    - Comprehensive error logging
    - Token usage tracking
    """
    
    def __init__(self):
        self.client: Optional[AsyncOpenAI] = None
        self.primary_model = settings.OPENAI_MODEL
        self.fallback_model = settings.OPENAI_FALLBACK_MODEL
        self.max_retries = settings.OPENAI_MAX_RETRIES
        self.timeout = settings.OPENAI_TIMEOUT
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE
        
    async def initialize(self) -> None:
        """Initialize the OpenAI client."""
        try:
            if not settings.OPENAI_API_KEY:
                logger.warning("OpenAI API key not set. LLM functionality will be limited.")
                return
                
            self.client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=self.timeout
            )
            
            # Test the connection
            await self._test_connection()
            logger.info("LLM client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            # Don't raise the exception - allow service to start without LLM
            logger.warning("LLM client initialization failed. Service will continue without AI functionality.")
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.client:
            await self.client.close()
            logger.info("LLM client cleaned up")
    
    async def _test_connection(self) -> None:
        """Test the OpenAI API connection."""
        if not self.client:
            return
            
        try:
            response = await self.client.chat.completions.create(
                model=self.fallback_model,  # Use fallback for testing
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            logger.info("OpenAI API connection test successful")
        except Exception as e:
            logger.error(f"OpenAI API connection test failed: {e}")
            raise
    
    def _clean_response_formatting(self, content: str) -> str:
        """
        Clean up markdown formatting and make text speech-friendly.
        
        Args:
            content: Raw response content
            
        Returns:
            Cleaned content without markdown formatting
        """
        if not content:
            return content
            
        # Remove markdown bold formatting
        content = content.replace('**', '')
        content = content.replace('__', '')
        
        # Remove markdown italic formatting
        content = content.replace('*', '')
        content = content.replace('_', '')
        
        # Clean up any remaining markdown-style formatting
        import re
        
        # Remove markdown headers
        content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
        
        # Remove markdown links but keep the text
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
        
        # Remove markdown code blocks
        content = re.sub(r'```[^`]*```', '', content)
        content = re.sub(r'`([^`]+)`', r'\1', content)
        
        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = content.strip()
        
        return content

    async def generate_response(
        self,
        messages: List[ConversationMessage],
        language: str = "en",
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> LLMResponse:
        """
        Generate a response using the LLM with knowledge base integration.
        
        Args:
            messages: Conversation history
            language: Target language for response
            model: Specific model to use (optional)
            max_tokens: Maximum tokens for response
            temperature: Response creativity (0.0-1.0)
            
        Returns:
            LLMResponse with generated content and metadata
        """
        start_time = time.time()
        
        # If client is not initialized, return a mock response
        if not self.client:
            return LLMResponse(
                content="AI assistant unavailable. Check OpenAI API configuration.",
                model_used="mock",
                tokens_used=0,
                response_time=time.time() - start_time,
                success=False,
                error_message="OpenAI client not initialized"
            )
        
        # Prepare parameters
        model_to_use = model or self.primary_model
        max_tokens = max_tokens or self.max_tokens
        temperature = temperature or self.temperature
        
        # Get the user's latest message for knowledge base search
        user_message = ""
        if messages:
            # Find the last user message
            for msg in reversed(messages):
                if msg.role == "user":
                    user_message = msg.content
                    break
        
        # Search knowledge base for relevant information
        knowledge_context = ""
        if user_message:
            try:
                # Import here to avoid circular imports
                from .services.knowledge_base import KnowledgeBaseService
                from .services.vector_database import VectorDatabase
                
                # Initialize knowledge base service
                vector_db = VectorDatabase()
                knowledge_service = KnowledgeBaseService(self, vector_db)
                
                # Enhanced search strategy with multiple specific queries
                search_queries = [user_message]
                
                # Add specific search terms for common queries
                if any(word in user_message.lower() for word in ['start', 'startup', 'begin', 'turn on', 'power on', 'how to start']):
                    search_queries.extend([
                        "Section 8 Step 3 Pre-operation Check and Warm-Up",
                        "Turn on master switch PLC set desired cleaning profile depth",
                        "Attach umbilical hose rear Power Pack Assembly",
                        "Lift AutoBoss into water start up via remote control",
                        "Step 3 Pre-operation Check Warm-Up master switch",
                        "operating the AutoBoss Section 8 startup procedure",
                        "Step 1 Turn on master switch Step 2 PLC set desired cleaning",
                        "Step 4 Lift AutoBoss into water start up remote control"
                    ])
                
                # Also search for troubleshooting if user mentions problems
                if any(word in user_message.lower() for word in ['problem', 'issue', 'trouble', 'not working', 'broken', 'error']):
                    search_queries.extend([
                        "troubleshooting guide Section 10",
                        "HP Water Gauge Reading Low",
                        "Walking Wheels slow won't turn",
                        "Remote working intermittently"
                    ])
                
                # Search for HP gauge specific issues
                if any(word in user_message.lower() for word in ['hp', 'pressure', 'gauge', 'red', 'low', 'high']):
                    search_queries.extend([
                        "HP Water Gauge Reading Low in low red zone",
                        "HP Water Gauge Reading High in high red zone", 
                        "charge pressure gauge",
                        "water pressure system",
                        "unloader valve system"
                    ])
                
                # Search for maintenance related queries
                if any(word in user_message.lower() for word in ['maintenance', 'service', 'repair', 'replace', 'check']):
                    search_queries.extend([
                        "Daily Monitoring and Maintenance",
                        "Weekly Monitoring and Maintenance",
                        "250 hour maintenance requirements",
                        "500 hour maintenance requirements",
                        "maintenance check sheet"
                    ])
                
                # Always search for resolved support cases - these contain real field experience
                search_queries.append(f"Resolved Case {user_message}")
                
                all_results = []
                for query in search_queries:
                    search_results = await knowledge_service.search_documents(
                        query=query,
                        language=language,
                        limit=8  # Get top 8 results per query for broader coverage
                    )
                    all_results.extend(search_results)
                
                # Remove duplicates and get best results
                seen_docs = set()
                unique_results = []
                for result in all_results:
                    doc_id = result['document']['document_id']
                    chunk_key = f"{doc_id}_{result['matched_content'][:100]}"  # Use content snippet as key
                    if chunk_key not in seen_docs:
                        seen_docs.add(chunk_key)
                        unique_results.append(result)
                
                # Sort by relevance and take top 12 for maximum coverage
                unique_results.sort(key=lambda x: x['relevance_score'], reverse=True)
                # Filter out low-relevance results (below 0.3 threshold)
                unique_results = [r for r in unique_results if r['relevance_score'] > 0.3]
                final_results = unique_results[:12]
                
                # Build context from search results with better formatting
                if final_results:
                    context_parts = []
                    for i, result in enumerate(final_results):
                        doc = result['document']
                        content = result['matched_content']
                        # Include full chunk content (chunks are now 500 chars, so no need to truncate aggressively)
                        if len(content) > 800:
                            content = content[:800] + "..."
                        
                        # Add machine model info if available
                        model_info = ""
                        if doc.get('machine_models'):
                            model_info = f" (AutoBoss {', '.join(doc['machine_models'])})"
                        
                        # Add source type for resolved cases
                        source_type = ""
                        if doc.get('document_type') == 'support_case':
                            source_type = " [VERIFIED FIELD EXPERIENCE]"
                        
                        context_parts.append(f"=== KNOWLEDGE ENTRY {i+1}{source_type} ===\nFrom: {doc['title']}{model_info}\nRelevance: {result['relevance_score']:.3f}\nContent: {content}")
                    
                    knowledge_context = "\n\n".join(context_parts)
                    logger.info(f"Found {len(final_results)} relevant knowledge base entries (filtered from {len(unique_results)} unique)")
                    logger.debug(f"Knowledge context length: {len(knowledge_context)} characters")
                    logger.debug(f"Search queries used: {search_queries}")
                
            except Exception as e:
                logger.warning(f"Failed to search knowledge base: {e}")
                # Continue without knowledge base context
        
        # Convert messages to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Build system message based on whether we have knowledge context
        system_content = ""
        
        if knowledge_context:
            # Create a concise system prompt with proper formatting
            system_content = f"""You are AutoBoss AI Assistant, the ONLY support assistant for AutoBoss net cleaning machines manufactured by BossAqua and distributed by Oraseas EE.

CRITICAL RULES:
- You MUST answer ONLY based on the knowledge base content provided below.
- NEVER provide generic troubleshooting advice that does not come from the knowledge base.
- AutoBoss machines are specialized underwater net cleaning robots. They have NO power cords, NO standard electrical outlets, NO household components.
- If the knowledge base content does not contain information relevant to the user's question, say: "I don't have specific information about this in my knowledge base. Please contact Oraseas support for assistance."
- NEVER guess or infer solutions from general engineering knowledge. Only state facts from the provided content.
- If a resolved support case is referenced, treat it as verified field experience.

KNOWLEDGE BASE CONTENT:
{knowledge_context}

RESPONSE FORMAT:
1. Be direct and concise - no pleasantries like "I'm sorry to hear that"
2. Provide step-by-step instructions when the knowledge base contains them
3. Include section references and specific values/readings when available
4. Prioritize safety warnings from the manual
5. Use plain text formatting - NO markdown asterisks or bold formatting
6. For emphasis, use CAPITAL LETTERS or numbered lists
7. Respond in {language}

RESPONSE STYLE:
- Direct and to-the-point
- Clear numbered steps from the manual
- No unnecessary pleasantries
- Technical but accessible language
- Always cite the source (manual section, resolved case number, etc.)
- If information is from a resolved support case, mention it was verified in the field"""
            logger.info(f"Using comprehensive system prompt with {len(knowledge_context)} characters of manual content")
        else:
            # No knowledge context - strictly refuse to provide generic advice
            system_content = f"""You are AutoBoss AI Assistant, the ONLY support assistant for AutoBoss net cleaning machines manufactured by BossAqua and distributed by Oraseas EE.

CRITICAL RULES:
- You could NOT find relevant information in the knowledge base for this query.
- DO NOT provide generic troubleshooting advice or guess solutions.
- DO NOT suggest things like "check the power cord", "restart the device", or any generic advice that does not apply to AutoBoss machines.
- AutoBoss machines are specialized underwater net cleaning robots with hydraulic systems, PLC controllers, HP water jets, walking wheels, and remote control operation. They have NO power cords, NO standard electrical components.
- You MUST tell the user that you don't have specific information about their query in the knowledge base.
- Suggest they contact Oraseas support directly for assistance.
- If the question is clearly about AutoBoss but you lack the specific information, acknowledge this honestly.

RESPONSE: Tell the user you could not find relevant information in the AutoBoss knowledge base for their specific question. Suggest contacting Oraseas EE support team directly. Be direct and concise. Use plain text - NO markdown formatting or asterisks.

Respond in {language}."""
            logger.info("Using basic system prompt - no knowledge context found")
        
        openai_messages.insert(0, {
            "role": "system",
            "content": system_content
        })
        
        # Attempt generation with retries and fallback
        for attempt in range(self.max_retries):
            try:
                response = await self._make_api_call(
                    messages=openai_messages,
                    model=model_to_use,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                response_time = time.time() - start_time
                
                # Clean the response content to remove markdown formatting
                cleaned_content = self._clean_response_formatting(response.choices[0].message.content)
                
                return LLMResponse(
                    content=cleaned_content,
                    model_used=response.model,
                    tokens_used=response.usage.total_tokens,
                    response_time=response_time,
                    success=True
                )
                
            except openai.RateLimitError as e:
                logger.warning(f"Rate limit hit on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    return self._create_error_response(
                        f"Rate limit exceeded after {self.max_retries} attempts",
                        time.time() - start_time
                    )
                    
            except openai.APIError as e:
                logger.error(f"OpenAI API error on attempt {attempt + 1}: {e}")
                
                # Try fallback model if using primary model
                if model_to_use == self.primary_model and attempt == 0:
                    logger.info("Falling back to secondary model")
                    model_to_use = self.fallback_model
                    continue
                    
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    return self._create_error_response(
                        f"API error after {self.max_retries} attempts: {str(e)}",
                        time.time() - start_time
                    )
                    
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    return self._create_error_response(
                        f"Unexpected error after {self.max_retries} attempts: {str(e)}",
                        time.time() - start_time
                    )
        
        # Should not reach here, but just in case
        return self._create_error_response(
            "Failed to generate response after all retries",
            time.time() - start_time
        )
    
    async def _make_api_call(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_tokens: int,
        temperature: float
    ) -> ChatCompletion:
        """Make the actual API call to OpenAI."""
        return await self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=self.timeout
        )
    
    def _get_language_instruction(self, language: str) -> str:
        """Get language-specific instruction for the LLM."""
        language_instructions = {
            "en": {
                "instruction": "Respond in English",
                "context": "You are an expert AutoBoss machine troubleshooting assistant. Provide clear, step-by-step guidance for diagnosing and resolving issues with AutoBoss net cleaning machines. Use technical terminology appropriately and always prioritize safety."
            },
            "el": {
                "instruction": "Απαντήστε στα Ελληνικά (Greek)",
                "context": "Είστε ειδικός βοηθός αντιμετώπισης προβλημάτων μηχανημάτων AutoBoss. Παρέχετε σαφείς, βήμα προς βήμα οδηγίες για τη διάγνωση και την επίλυση προβλημάτων με τα μηχανήματα καθαρισμού δικτύων AutoBoss. Χρησιμοποιήστε την τεχνική ορολογία κατάλληλα και δώστε πάντα προτεραιότητα στην ασφάλεια."
            },
            "ar": {
                "instruction": "أجب باللغة العربية (Arabic)",
                "context": "أنت مساعد خبير في استكشاف أخطاء آلات AutoBoss وإصلاحها. قدم إرشادات واضحة خطوة بخطوة لتشخيص وحل المشاكل مع آلات تنظيف الشباك AutoBoss. استخدم المصطلحات التقنية بشكل مناسب وأعط الأولوية دائماً للسلامة."
            },
            "es": {
                "instruction": "Responde en Español (Spanish)",
                "context": "Eres un asistente experto en solución de problemas de máquinas AutoBoss. Proporciona orientación clara, paso a paso, para diagnosticar y resolver problemas con las máquinas de limpieza de redes AutoBoss. Usa la terminología técnica apropiadamente y siempre prioriza la seguridad."
            },
            "tr": {
                "instruction": "Türkçe yanıtlayın (Turkish)",
                "context": "AutoBoss makine sorun giderme konusunda uzman bir asistansınız. AutoBoss ağ temizleme makinelerindeki sorunları teşhis etmek ve çözmek için açık, adım adım rehberlik sağlayın. Teknik terminolojiyi uygun şekilde kullanın ve her zaman güvenliği önceliklendirin."
            },
            "no": {
                "instruction": "Svar på Norsk (Norwegian)",
                "context": "Du er en ekspert AutoBoss maskin feilsøkingsassistent. Gi klar, trinn-for-trinn veiledning for å diagnostisere og løse problemer med AutoBoss nettrengjøringsmaskiner. Bruk teknisk terminologi på riktig måte og prioriter alltid sikkerhet."
            }
        }
        
        lang_config = language_instructions.get(language, language_instructions["en"])
        return f"{lang_config['instruction']}. {lang_config['context']}"
    
    def _create_error_response(self, error_message: str, response_time: float) -> LLMResponse:
        """Create an error response."""
        return LLMResponse(
            content="AI assistant temporarily unavailable. Please try again.",
            model_used="error",
            tokens_used=0,
            response_time=response_time,
            success=False,
            error_message=error_message
        )
    
    async def analyze_problem(
        self,
        problem_description: str,
        machine_context: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> LLMResponse:
        """
        Analyze a problem description and provide initial diagnostic assessment.
        
        Args:
            problem_description: User's description of the problem
            machine_context: Information about the specific machine
            language: Language for the response
            
        Returns:
            LLMResponse with diagnostic analysis
        """
        # Build system prompt
        system_prompt = self._build_diagnostic_system_prompt(machine_context, language)
        
        # Build user prompt
        user_prompt = f"Problem description: {problem_description}\n\nPlease provide an initial diagnostic assessment and suggest troubleshooting steps."
        
        messages = [
            ConversationMessage(role="system", content=system_prompt),
            ConversationMessage(role="user", content=user_prompt)
        ]
        
        return await self.generate_response(messages, language=language)
    
    def _build_diagnostic_system_prompt(self, machine_context: Optional[Dict[str, Any]] = None, language: str = "en") -> str:
        """Build system prompt for diagnostic analysis."""
        
        # Language-specific base prompts
        base_prompts = {
            "en": """You are an expert AutoBoss machine troubleshooting assistant. Your role is to help operators diagnose and resolve issues with their AutoBoss net cleaning machines.

When analyzing problems:
1. Ask clarifying questions if the problem description is unclear
2. Provide step-by-step diagnostic procedures
3. Suggest the most likely causes first
4. Include safety considerations
5. Recommend when to escalate to expert support

Always be helpful, clear, and safety-conscious in your responses.""",
            
            "el": """Είστε ειδικός βοηθός αντιμετώπισης προβλημάτων μηχανημάτων AutoBoss. Ο ρόλος σας είναι να βοηθήσετε τους χειριστές να διαγνώσουν και να επιλύσουν προβλήματα με τα μηχανήματα καθαρισμού δικτύων AutoBoss.

Κατά την ανάλυση προβλημάτων:
1. Κάντε διευκρινιστικές ερωτήσεις εάν η περιγραφή του προβλήματος δεν είναι σαφής
2. Παρέχετε βήμα προς βήμα διαγνωστικές διαδικασίες
3. Προτείνετε πρώτα τις πιο πιθανές αιτίες
4. Συμπεριλάβετε θέματα ασφαλείας
5. Συστήστε πότε να κλιμακώσετε σε ειδική υποστήριξη

Να είστε πάντα χρήσιμοι, σαφείς και προσεκτικοί στην ασφάλεια στις απαντήσεις σας.""",
            
            "ar": """أنت مساعد خبير في استكشاف أخطاء آلات AutoBoss وإصلاحها. دورك هو مساعدة المشغلين في تشخيص وحل المشاكل مع آلات تنظيف الشباك AutoBoss.

عند تحليل المشاكل:
1. اطرح أسئلة توضيحية إذا كان وصف المشكلة غير واضح
2. قدم إجراءات تشخيصية خطوة بخطوة
3. اقترح الأسباب الأكثر احتمالاً أولاً
4. اشمل اعتبارات السلامة
5. أوصِ بموعد التصعيد إلى الدعم المتخصص

كن دائماً مفيداً وواضحاً ومهتماً بالسلامة في ردودك.""",
            
            "es": """Eres un asistente experto en solución de problemas de máquinas AutoBoss. Tu función es ayudar a los operadores a diagnosticar y resolver problemas con sus máquinas de limpieza de redes AutoBoss.

Al analizar problemas:
1. Haz preguntas aclaratorias si la descripción del problema no está clara
2. Proporciona procedimientos de diagnóstico paso a paso
3. Sugiere las causas más probables primero
4. Incluye consideraciones de seguridad
5. Recomienda cuándo escalar al soporte experto

Sé siempre útil, claro y consciente de la seguridad en tus respuestas.""",
            
            "tr": """AutoBoss makine sorun giderme konusunda uzman bir asistansınız. Rolünüz, operatörlerin AutoBoss ağ temizleme makinelerindeki sorunları teşhis etmelerine ve çözmelerine yardımcı olmaktır.

Sorunları analiz ederken:
1. Sorun açıklaması belirsizse açıklayıcı sorular sorun
2. Adım adım tanı prosedürleri sağlayın
3. En olası nedenleri önce önerin
4. Güvenlik hususlarını dahil edin
5. Uzman desteğe ne zaman yükseltileceğini tavsiye edin

Yanıtlarınızda her zaman yardımcı, açık ve güvenlik bilincinde olun.""",
            
            "no": """Du er en ekspert AutoBoss maskin feilsøkingsassistent. Din rolle er å hjelpe operatører med å diagnostisere og løse problemer med deres AutoBoss nettrengjøringsmaskiner.

Når du analyserer problemer:
1. Still oppklarende spørsmål hvis problembeskrivelsen er uklar
2. Gi trinn-for-trinn diagnostiske prosedyrer
3. Foreslå de mest sannsynlige årsakene først
4. Inkluder sikkerhetshensyn
5. Anbefal når man skal eskalere til ekspertstøtte

Vær alltid hjelpsom, klar og sikkerhetsbevisst i dine svar."""
        }

        base_prompt = base_prompts.get(language, base_prompts["en"])

        if machine_context:
            # Extract machine details
            machine_details = machine_context.get("machine_details", {})
            recent_maintenance = machine_context.get("recent_maintenance", [])
            recent_parts_usage = machine_context.get("recent_parts_usage", [])
            hours_trend = machine_context.get("hours_trend", [])
            maintenance_suggestions = machine_context.get("maintenance_suggestions", [])
            
            machine_info_prompts = {
                "en": f"""

MACHINE CONTEXT:
- Model: {machine_details.get('model_type', 'Unknown')}
- Serial Number: {machine_details.get('serial_number', 'Unknown')}
- Current Hours: {machine_details.get('current_hours', 0)}
- Organization: {machine_details.get('organization', 'Unknown')}
- Country: {machine_details.get('country', 'Unknown')}

RECENT MAINTENANCE HISTORY:
{self._format_maintenance_history(recent_maintenance, language)}

RECENT PARTS USAGE:
{self._format_parts_usage(recent_parts_usage, language)}

MACHINE HOURS TREND:
{self._format_hours_trend(hours_trend, language)}

MAINTENANCE RECOMMENDATIONS:
{self._format_maintenance_suggestions(maintenance_suggestions, language)}

Use this comprehensive machine information to provide highly targeted troubleshooting advice. Consider the machine's usage patterns, maintenance history, and any overdue maintenance when diagnosing problems.""",
                
                "el": f"""

ΠΛΑΙΣΙΟ ΜΗΧΑΝΗΜΑΤΟΣ:
- Μοντέλο: {machine_details.get('model_type', 'Άγνωστο')}
- Σειριακός Αριθμός: {machine_details.get('serial_number', 'Άγνωστος')}
- Τρέχουσες Ώρες: {machine_details.get('current_hours', 0)}
- Οργανισμός: {machine_details.get('organization', 'Άγνωστος')}
- Χώρα: {machine_details.get('country', 'Άγνωστη')}

ΠΡΌΣΦΑΤΟ ΙΣΤΟΡΙΚΟ ΣΥΝΤΗΡΗΣΗΣ:
{self._format_maintenance_history(recent_maintenance, language)}

ΠΡΟΣΦΑΤΗ ΧΡΗΣΗ ΑΝΤΑΛΛΑΚΤΙΚΩΝ:
{self._format_parts_usage(recent_parts_usage, language)}

ΤΑΣΗ ΩΡΩΝ ΜΗΧΑΝΗΜΑΤΟΣ:
{self._format_hours_trend(hours_trend, language)}

ΣΥΣΤΑΣΕΙΣ ΣΥΝΤΗΡΗΣΗΣ:
{self._format_maintenance_suggestions(maintenance_suggestions, language)}

Χρησιμοποιήστε αυτές τις περιεκτικές πληροφορίες μηχανήματος για να παρέχετε εξαιρετικά στοχευμένες συμβουλές αντιμετώπισης προβλημάτων.""",
                
                "ar": f"""

سياق الآلة:
- الطراز: {machine_details.get('model_type', 'غير معروف')}
- الرقم التسلسلي: {machine_details.get('serial_number', 'غير معروف')}
- الساعات الحالية: {machine_details.get('current_hours', 0)}
- المنظمة: {machine_details.get('organization', 'غير معروف')}
- البلد: {machine_details.get('country', 'غير معروف')}

تاريخ الصيانة الحديث:
{self._format_maintenance_history(recent_maintenance, language)}

استخدام القطع الحديث:
{self._format_parts_usage(recent_parts_usage, language)}

اتجاه ساعات الآلة:
{self._format_hours_trend(hours_trend, language)}

توصيات الصيانة:
{self._format_maintenance_suggestions(maintenance_suggestions, language)}

استخدم هذه المعلومات الشاملة للآلة لتقديم نصائح استكشاف أخطاء مستهدفة للغاية.""",
                
                "es": f"""

CONTEXTO DE LA MÁQUINA:
- Modelo: {machine_details.get('model_type', 'Desconocido')}
- Número de Serie: {machine_details.get('serial_number', 'Desconocido')}
- Horas Actuales: {machine_details.get('current_hours', 0)}
- Organización: {machine_details.get('organization', 'Desconocida')}
- País: {machine_details.get('country', 'Desconocido')}

HISTORIAL DE MANTENIMIENTO RECIENTE:
{self._format_maintenance_history(recent_maintenance, language)}

USO RECIENTE DE PIEZAS:
{self._format_parts_usage(recent_parts_usage, language)}

TENDENCIA DE HORAS DE MÁQUINA:
{self._format_hours_trend(hours_trend, language)}

RECOMENDACIONES DE MANTENIMIENTO:
{self._format_maintenance_suggestions(maintenance_suggestions, language)}

Usa esta información integral de la máquina para proporcionar consejos de solución de problemas altamente dirigidos.""",
                
                "tr": f"""

MAKİNE BAĞLAMI:
- Model: {machine_details.get('model_type', 'Bilinmiyor')}
- Seri Numarası: {machine_details.get('serial_number', 'Bilinmiyor')}
- Mevcut Saatler: {machine_details.get('current_hours', 0)}
- Organizasyon: {machine_details.get('organization', 'Bilinmiyor')}
- Ülke: {machine_details.get('country', 'Bilinmiyor')}

SON BAKIM GEÇMİŞİ:
{self._format_maintenance_history(recent_maintenance, language)}

SON PARÇA KULLANIMI:
{self._format_parts_usage(recent_parts_usage, language)}

MAKİNE SAATLERİ EĞİLİMİ:
{self._format_hours_trend(hours_trend, language)}

BAKIM ÖNERİLERİ:
{self._format_maintenance_suggestions(maintenance_suggestions, language)}

Son derece hedefli sorun giderme tavsiyeleri sağlamak için bu kapsamlı makine bilgilerini kullanın.""",
                
                "no": f"""

MASKINKONTEKST:
- Modell: {machine_details.get('model_type', 'Ukjent')}
- Serienummer: {machine_details.get('serial_number', 'Ukjent')}
- Nåværende timer: {machine_details.get('current_hours', 0)}
- Organisasjon: {machine_details.get('organization', 'Ukjent')}
- Land: {machine_details.get('country', 'Ukjent')}

NYLIG VEDLIKEHOLDSHISTORIKK:
{self._format_maintenance_history(recent_maintenance, language)}

NYLIG DELEBRUK:
{self._format_parts_usage(recent_parts_usage, language)}

MASKINTIMERTREND:
{self._format_hours_trend(hours_trend, language)}

VEDLIKEHOLDSANBEFALINGER:
{self._format_maintenance_suggestions(maintenance_suggestions, language)}

Bruk denne omfattende maskininformasjonen til å gi svært målrettet feilsøkingsråd."""
            }
            
            machine_info = machine_info_prompts.get(language, machine_info_prompts["en"])
            base_prompt += machine_info
        
        return base_prompt
    
    def _format_maintenance_history(self, maintenance_history: List[Dict[str, Any]], language: str) -> str:
        """Format maintenance history for display in prompts."""
        if not maintenance_history:
            return "No recent maintenance records available."
        
        formatted_records = []
        for record in maintenance_history:
            date = record.get("date", "Unknown")
            maintenance_type = record.get("type", "Unknown")
            description = record.get("description", "No description")
            parts_used = record.get("parts_used", 0)
            performed_by = record.get("performed_by", "Unknown")
            
            formatted_records.append(f"- {date}: {maintenance_type} - {description} ({parts_used} parts used, by {performed_by})")
        
        return "\n".join(formatted_records)
    
    def _format_parts_usage(self, parts_usage: List[Dict[str, Any]], language: str) -> str:
        """Format parts usage for display in prompts."""
        if not parts_usage:
            return "No recent parts usage records available."
        
        formatted_usage = []
        for usage in parts_usage:
            date = usage.get("date", "Unknown")
            part_name = usage.get("part_name", "Unknown part")
            part_number = usage.get("part_number", "Unknown")
            quantity = usage.get("quantity", 0)
            is_proprietary = usage.get("is_proprietary", False)
            proprietary_note = " (Proprietary)" if is_proprietary else ""
            
            formatted_usage.append(f"- {date}: {part_name} ({part_number}){proprietary_note} - Qty: {quantity}")
        
        return "\n".join(formatted_usage)
    
    def _format_hours_trend(self, hours_trend: List[Dict[str, Any]], language: str) -> str:
        """Format machine hours trend for display in prompts."""
        if not hours_trend:
            return "No recent hours records available."
        
        formatted_hours = []
        for record in hours_trend:
            date = record.get("date", "Unknown")
            hours = record.get("hours", 0)
            recorded_by = record.get("recorded_by", "Unknown")
            
            formatted_hours.append(f"- {date}: {hours} hours (recorded by {recorded_by})")
        
        return "\n".join(formatted_hours)
    
    def _format_maintenance_suggestions(self, suggestions: List[Dict[str, Any]], language: str) -> str:
        """Format maintenance suggestions for display in prompts."""
        if not suggestions:
            return "No maintenance recommendations at this time."
        
        formatted_suggestions = []
        for suggestion in suggestions:
            suggestion_type = suggestion.get("type", "Unknown")
            description = suggestion.get("description", "No description")
            priority = suggestion.get("priority", "medium")
            overdue_hours = suggestion.get("overdue_hours", 0)
            
            priority_indicator = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
            overdue_note = f" (Overdue by {overdue_hours} hours)" if overdue_hours > 0 else ""
            
            formatted_suggestions.append(f"- {priority_indicator} {suggestion_type}: {description}{overdue_note}")
        
        return "\n".join(formatted_suggestions)
    
    async def generate_simple_response(
        self,
        prompt: str,
        context: Dict[str, Any],
        language: str = "en"
    ) -> str:
        """
        Simple generate_response method for compatibility with sessions router.
        
        Args:
            prompt: User's message/prompt
            context: Context information including conversation history
            language: Target language for response
            
        Returns:
            Generated response content
        """
        # If client is not initialized, return a mock response
        if not self.client:
            return "AI assistant unavailable. Check OpenAI API configuration."
        
        # Convert context to messages format
        messages = []
        
        # Add system message
        system_msg = f"You are AutoBoss AI Assistant, helping users troubleshoot AutoBoss net cleaning machines. Respond in {language}."
        messages.append(ConversationMessage(role="system", content=system_msg))
        
        # Add conversation history if available
        if "conversation_history" in context:
            for msg in context["conversation_history"]:
                messages.append(ConversationMessage(
                    role=msg["sender"] if msg["sender"] != "assistant" else "assistant",
                    content=msg["content"]
                ))
        
        # Add current user message
        messages.append(ConversationMessage(role="user", content=prompt))
        
        # Generate response using the full method
        response = await self.generate_response(
            messages=messages,
            language=language
        )
        
        return response.content if response.success else (response.error_message or "Could not generate response.")
    
    async def generate_embedding(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """
        Generate embedding vector for text using OpenAI embeddings API.
        
        Args:
            text: Text to generate embedding for
            model: Embedding model to use
            
        Returns:
            List of floats representing the embedding vector
        """
        if not self.client:
            logger.error("OpenAI client not initialized for embedding generation")
            # Return a zero vector of the expected dimension (1536 for ada-002)
            return [0.0] * 1536
        
        try:
            # Clean and truncate text if necessary
            text = text.strip()
            if len(text) > 8000:  # OpenAI embedding limit is ~8191 tokens
                text = text[:8000]
            
            if not text:
                logger.warning("Empty text provided for embedding generation")
                return [0.0] * 1536
            
            response = await self.client.embeddings.create(
                model=model,
                input=text
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding of dimension {len(embedding)} for text length {len(text)}")
            
            return embedding
            
        except openai.RateLimitError as e:
            logger.warning(f"Rate limit hit during embedding generation: {e}")
            # Wait and retry once
            await asyncio.sleep(1)
            try:
                response = await self.client.embeddings.create(
                    model=model,
                    input=text
                )
                return response.data[0].embedding
            except Exception as retry_e:
                logger.error(f"Failed to generate embedding after retry: {retry_e}")
                return [0.0] * 1536
                
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return [0.0] * 1536