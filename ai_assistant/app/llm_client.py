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
                content="I'm sorry, but the AI assistant is currently unavailable. Please check that the OpenAI API key is configured correctly.",
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
                
                all_results = []
                for query in search_queries:
                    search_results = await knowledge_service.search_documents(
                        query=query,
                        language=language,
                        limit=3  # Get top 3 results per query
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
                
                # Sort by relevance and take top 5 for better coverage
                unique_results.sort(key=lambda x: x['relevance_score'], reverse=True)
                final_results = unique_results[:5]
                
                # Build context from search results with better formatting
                if final_results:
                    context_parts = []
                    for i, result in enumerate(final_results):
                        doc = result['document']
                        content = result['matched_content']
                        # Include more content for better context
                        if len(content) > 1000:
                            content = content[:1000] + "..."
                        context_parts.append(f"=== MANUAL SECTION {i+1} ===\nFrom: {doc['title']} (AutoBoss {', '.join(doc['machine_models'])})\nContent: {content}")
                    
                    knowledge_context = "\n\n".join(context_parts)
                    logger.info(f"Found {len(final_results)} relevant knowledge base entries")
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
            # Create a very direct and simple system prompt
            system_content = f"""MANUAL CONTENT:
{knowledge_context}

You are AutoBoss AI Assistant. Answer the user's question using ONLY the manual content shown above. Quote directly from the manual. Respond in {language}."""
            logger.info(f"Using direct system prompt with {len(knowledge_context)} characters of manual content")
        else:
            # No knowledge context - use basic system prompt
            system_content = f"""You are AutoBoss AI Assistant. You help with AutoBoss net cleaning machine troubleshooting and operation.

Respond in {language}. If you don't have specific information about AutoBoss procedures, clearly state that you need to refer to the official manual."""
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
                
                return LLMResponse(
                    content=response.choices[0].message.content,
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
            content="I apologize, but I'm experiencing technical difficulties. Please try again later.",
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
            machine_info_prompts = {
                "en": f"""

Machine Information:
- Model: {machine_context.get('model', 'Unknown')}
- Serial Number: {machine_context.get('serial_number', 'Unknown')}
- Installation Date: {machine_context.get('installation_date', 'Unknown')}
- Last Maintenance: {machine_context.get('last_maintenance', 'Unknown')}

Use this machine-specific information to provide more targeted troubleshooting advice.""",
                
                "el": f"""

Πληροφορίες Μηχανήματος:
- Μοντέλο: {machine_context.get('model', 'Άγνωστο')}
- Σειριακός Αριθμός: {machine_context.get('serial_number', 'Άγνωστος')}
- Ημερομηνία Εγκατάστασης: {machine_context.get('installation_date', 'Άγνωστη')}
- Τελευταία Συντήρηση: {machine_context.get('last_maintenance', 'Άγνωστη')}

Χρησιμοποιήστε αυτές τις πληροφορίες για το συγκεκριμένο μηχάνημα για να παρέχετε πιο στοχευμένες συμβουλές αντιμετώπισης προβλημάτων.""",
                
                "ar": f"""

معلومات الآلة:
- الطراز: {machine_context.get('model', 'غير معروف')}
- الرقم التسلسلي: {machine_context.get('serial_number', 'غير معروف')}
- تاريخ التركيب: {machine_context.get('installation_date', 'غير معروف')}
- آخر صيانة: {machine_context.get('last_maintenance', 'غير معروف')}

استخدم هذه المعلومات الخاصة بالآلة لتقديم نصائح أكثر تحديداً لاستكشاف الأخطاء وإصلاحها.""",
                
                "es": f"""

Información de la Máquina:
- Modelo: {machine_context.get('model', 'Desconocido')}
- Número de Serie: {machine_context.get('serial_number', 'Desconocido')}
- Fecha de Instalación: {machine_context.get('installation_date', 'Desconocida')}
- Último Mantenimiento: {machine_context.get('last_maintenance', 'Desconocido')}

Usa esta información específica de la máquina para proporcionar consejos de solución de problemas más dirigidos.""",
                
                "tr": f"""

Makine Bilgileri:
- Model: {machine_context.get('model', 'Bilinmiyor')}
- Seri Numarası: {machine_context.get('serial_number', 'Bilinmiyor')}
- Kurulum Tarihi: {machine_context.get('installation_date', 'Bilinmiyor')}
- Son Bakım: {machine_context.get('last_maintenance', 'Bilinmiyor')}

Daha hedefli sorun giderme tavsiyeleri sağlamak için bu makineye özgü bilgileri kullanın.""",
                
                "no": f"""

Maskininformasjon:
- Modell: {machine_context.get('model', 'Ukjent')}
- Serienummer: {machine_context.get('serial_number', 'Ukjent')}
- Installasjonsdato: {machine_context.get('installation_date', 'Ukjent')}
- Siste vedlikehold: {machine_context.get('last_maintenance', 'Ukjent')}

Bruk denne maskinspesifikke informasjonen til å gi mer målrettet feilsøkingsråd."""
            }
            
            machine_info = machine_info_prompts.get(language, machine_info_prompts["en"])
            base_prompt += machine_info
        
        return base_prompt
    
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
            return "I'm sorry, but the AI assistant is currently unavailable. Please check that the OpenAI API key is configured correctly."
        
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
        
        return response.content if response.success else response.error_message or "I'm sorry, I couldn't generate a response."
    
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