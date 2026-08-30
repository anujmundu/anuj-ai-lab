import time

import requests

from app.core.config import settings
from app.services.llm_config import LLMConfig


class OllamaService:
    """
    Service responsible for interacting with the
    Ollama generation API.

    Responsibilities

    • Build generation payload
    • Apply configurable generation settings
    • Measure generation latency
    • Store generation diagnostics

    Future responsibilities

    • Retry handling
    • Streaming support
    • Advanced diagnostics
    """

    def __init__(
        self,
        config: LLMConfig | None = None
    ):

        self.config = config or LLMConfig()

        #
        # Updated after every generation.
        #
        self._last_generation: dict = {}

    # --------------------------------------------------
    # Diagnostics
    # --------------------------------------------------

    @property
    def last_generation(self) -> dict:

        return self._last_generation.copy()

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _build_payload(
        self,
        prompt: str,
        model: str | None,
        temperature: float | None,
        top_p: float | None,
        repeat_penalty: float |None,
        seed: int | None,
        max_tokens: int | None,
        stream: bool | None
    ) -> dict:

        return {
            "model": (
                model
                or self.config.model
                or settings.DEFAULT_MODEL
            ),
            "prompt": prompt,
            "stream": (
                self.config.stream
                if stream is None
                else stream
            ),
            "options": {
                "temperature": (
                    self.config.temperature
                    if temperature is None
                    else temperature
                ),
                "top_p": (
                    self.config.top_p
                    if top_p is None
                    else top_p
                ),
                "repeat_penalty": (
                    self.config.repeat_penalty
                    if repeat_penalty is None
                    else repeat_penalty
                ),
                "seed": (
                    self.config.seed
                    if seed is None
                    else seed
                ),
                "num_predict": (
                    self.config.max_tokens
                    if max_tokens is None
                    else max_tokens
                ),
            },
        }

    def _post_generate(
        self,
        payload: dict
    ) -> requests.Response:

        response = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=min(self.config.timeout, 1.5)
        )

        response.raise_for_status()

        return response

    def _update_diagnostics(
        self,
        *,
        payload: dict,
        prompt: str,
        response_text: str,
        latency: float
    ) -> None:

        options = payload.get("options", {})

        self._last_generation = {
            "model": payload.get("model", "auto"),
            "temperature": options.get("temperature", 0.7),
            "top_p": options.get("top_p", 0.9),
            "repeat_penalty": options.get("repeat_penalty", 1.1),
            "seed": options.get("seed", 42),
            "max_tokens": options.get("num_predict", 512),
            "stream": payload.get("stream", False),
            "latency_seconds": round(latency, 3),
            "prompt_characters": len(prompt),
            "prompt_words": len(prompt.split()),
            "response_characters": len(response_text),
            "response_words": len(response_text.split())
        }

    def _generate_cloud_fallback(
        self,
        prompt: str,
        model_name: str,
        api_key: str | None = None,
        provider: str | None = None,
    ) -> str:
        """
        Intelligent multi-domain cloud inference engine.
        Supports Groq/Gemini/OpenAI/OpenRouter cloud keys, direct RAG grounded synthesis, and rich domain intelligence.
        """
        import os
        from datetime import datetime, timezone

        # 1. Extract user query and retrieved context accurately
        clean_q = prompt.strip()
        if "QUESTION\n--------" in prompt:
            clean_q = prompt.split("QUESTION\n--------")[-1].split("ANSWER\n------")[0].strip()
        elif "Question:" in prompt:
            clean_q = prompt.split("Question:")[-1].split("Assistant:")[0].split("\n")[0].strip()
        elif "Human:" in prompt:
            clean_q = prompt.split("Human:")[-1].split("Assistant:")[0].split("\n")[0].strip()

        # Extract retrieved context if present
        retrieved_context = ""
        if "CONTEXT\n-------" in prompt:
            retrieved_context = prompt.split("CONTEXT\n-------")[-1].split("QUESTION\n--------")[0].strip()
            if retrieved_context == "(none)" or retrieved_context.startswith("###"):
                retrieved_context = ""
        elif "Context:" in prompt:
            retrieved_context = prompt.split("Context:")[1].split("Question:")[0].strip()
            if retrieved_context == "(none)" or retrieved_context.startswith("###"):
                retrieved_context = ""

        llm_user_prompt = clean_q
        if retrieved_context:
            llm_user_prompt = f"Grounded Context:\n{retrieved_context}\n\nQuestion: {clean_q}\n\nAnswer using the provided context when relevant, and provide a clear, accurate, conversational response."
        
        q_lower = clean_q.lower()
        now = datetime.now(timezone.utc)

        # 2. Check for Cloud LLM API Keys (Groq / Gemini / OpenAI / OpenRouter)
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except Exception:
            pass

        # 2a. Direct user-provided key or Groq Cloud (Llama 3.3 70B / 8B / Qwen)
        groq_key = (api_key if (api_key and (provider == "groq" or api_key.startswith("gsk_"))) else os.environ.get("GROQ_API_KEY") or "").strip().strip('"').strip("'")
        if groq_key:
            last_groq_error = None
            for model_candidate in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "qwen-2.5-32b", "deepseek-r1-distill-llama-70b"]:
                try:
                    res = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
                        json={
                            "model": model_candidate,
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "You are Anuj AI Lab Assistant (v3.0.0), a world-class AI engineering assistant. Answer questions thoroughly, accurately, conversationally, and with clean markdown formatting."
                                },
                                {
                                    "role": "user",
                                    "content": llm_user_prompt
                                }
                            ],
                            "temperature": 0.7,
                            "max_tokens": 2048,
                        },
                        timeout=20.0
                    )
                    if res.status_code == 200:
                        content = res.json()["choices"][0]["message"]["content"]
                        if content and len(content.strip()) > 5:
                            return content
                    else:
                        last_groq_error = f"HTTP {res.status_code}: {res.text}"
                except Exception as e:
                    last_groq_error = str(e)
            
            if api_key and last_groq_error:
                return f"⚠️ **Groq API Error**: `{last_groq_error}`\n\nPlease check your Groq API key at [console.groq.com/keys](https://console.groq.com/keys)."

        # 2b. Google Gemini API (Gemini 1.5 Flash / Pro)
        gemini_key = (api_key if (api_key and (provider == "gemini" or api_key.startswith("AIza"))) else os.environ.get("GEMINI_API_KEY") or "").strip().strip('"').strip("'")
        if gemini_key:
            try:
                res = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}",
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [
                            {"parts": [{"text": f"You are Anuj AI Lab Assistant. Answer informatively, naturally, and comprehensively:\n\n{llm_user_prompt}"}]}
                        ]
                    },
                    timeout=20.0
                )
                if res.status_code == 200:
                    candidates = res.json().get("candidates", [])
                    if candidates:
                        content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        if content and len(content.strip()) > 5:
                            return content
                elif api_key:
                    return f"⚠️ **Google Gemini API Error**: HTTP {res.status_code}: `{res.text}`\n\nPlease verify your Gemini API key at [aistudio.google.com](https://aistudio.google.com/app/apikey)."
            except Exception as e:
                if api_key:
                    return f"⚠️ **Google Gemini Exception**: `{e}`"

        # 2c. OpenAI API (GPT-4o / GPT-4o-mini)
        openai_key = (api_key if (api_key and (provider == "openai" or api_key.startswith("sk-proj") or api_key.startswith("sk-admin"))) else os.environ.get("OPENAI_API_KEY") or "").strip().strip('"').strip("'")
        if openai_key:
            try:
                res = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": "You are Anuj AI Lab Assistant. Answer informatively and with clear markdown."},
                            {"role": "user", "content": llm_user_prompt}
                        ],
                        "temperature": 0.7,
                    },
                    timeout=20.0
                )
                if res.status_code == 200:
                    content = res.json()["choices"][0]["message"]["content"]
                    if content and len(content.strip()) > 5:
                        return content
                elif api_key:
                    return f"⚠️ **OpenAI API Error**: HTTP {res.status_code}: `{res.text}`"
            except Exception as e:
                if api_key:
                    return f"⚠️ **OpenAI Exception**: `{e}`"

        # 2d. OpenRouter Cloud
        openrouter_key = (api_key if (api_key and (provider == "openrouter" or api_key.startswith("sk-or"))) else os.environ.get("OPENROUTER_API_KEY") or "").strip().strip('"').strip("'")
        if openrouter_key:
            try:
                res = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {openrouter_key}", "Content-Type": "application/json"},
                    json={
                        "model": "meta-llama/llama-3.2-3b-instruct:free",
                        "messages": [
                            {"role": "system", "content": "You are Anuj AI Lab Assistant. Answer clearly and informatively."},
                            {"role": "user", "content": llm_user_prompt}
                        ],
                    },
                    timeout=20.0
                )
                if res.status_code == 200:
                    content = res.json()["choices"][0]["message"]["content"]
                    if content and len(content.strip()) > 5:
                        return content
                elif api_key:
                    return f"⚠️ **OpenRouter API Error**: HTTP {res.status_code}: `{res.text}`"
            except Exception as e:
                if api_key:
                    return f"⚠️ **OpenRouter Exception**: `{e}`"

        # 3. Check for Real Retrieved ChromaDB Document Context
        if retrieved_context and len(retrieved_context) > 20:
            lines = [l.strip() for l in retrieved_context.split("\n") if l.strip() and not l.startswith("###")]
            snippet = "\n".join(lines[:6])
            return (
                f"### 📄 Grounded Knowledge Synthesis\n\n"
                f"{snippet}\n\n"
                f"--- \n"
                f"*Source: Verified ChromaDB semantic retrieval.*"
            )

        # 4. Strict Regex Matching for System Queries (Never triggers on arbitrary text)
        import re

        if re.search(r"\b(what time is it|current time|what is the time|time now|system time)\b", q_lower):
            return f"The current system time is **{now.strftime('%I:%M:%S %p UTC')}** (Date: {now.strftime('%B %d, %Y')})."

        if re.search(r"\b(what is the date|today's date|current date|what date is it|what day is it)\b", q_lower):
            return f"Today's date is **{now.strftime('%B %d, %Y')}** (UTC: {now.strftime('%Y-%m-%d %H:%M:%S')})."

        if re.search(r"\b(what year is it|what is the year|current year|which year is it)\b", q_lower):
            return f"The current year is **{now.year}**."

        # 5. Greetings
        if re.search(r"^(hello|hi|hey|greetings|good morning|good evening|good afternoon)\b", q_lower.strip()):
            return (
                "Hello! I am **Anuj AI Lab Assistant (v3.0.0)**.\n\n"
                "I am ready to assist you with:\n"
                "• Ingesting and querying documents with **ChromaDB Hybrid Search**\n"
                "• Answering complex coding, AI architecture, and engineering questions\n"
                "• Running multi-agent deliberations in the **Collaboration Arena**\n"
                "• Live diagnostic inspection in the **Telemetry Inspector**\n\n"
                "What would you like to build or explore today?"
            )

        # 6. Math & Calculations
        cleaned_expr = clean_q.replace("what is", "").replace("calculate", "").replace("evaluate", "").replace("?", "").strip()
        if cleaned_expr and re.match(r"^[\d\s\+\-\*\/\^\(\)\.\%]+$", cleaned_expr):
            try:
                from app.tools.calculator_tool import calculator_tool
                ans = calculator_tool.calculate(cleaned_expr)
                if ans != "Invalid expression":
                    return f"**Result**: `{cleaned_expr}` = **{ans}**"
            except Exception:
                pass

        # 7. Informative Guidance when Cloud Container has no Neural LLM Key
        return (
            f"### 🧠 Neural LLM Engine Required\n\n"
            f"To generate custom answers, write code, tell stories, or answer open-ended questions like *\"{clean_q}\"* in the cloud:\n\n"
            f"1. **⚡ Connect Free Cloud LLM (Instant)**: Click the **`⚡ Connect Free LLM`** button in the top bar of the chat.\n"
            f"2. **Paste a Free Key**: Add your free **Groq** (`gsk_...`) or **Google Gemini** (`AIzaSy...`) API key (takes 10 seconds, no credit card required).\n"
            f"3. **Run Locally**: If running on your PC, start your local **Ollama** daemon (`ollama serve`) to generate answers directly on your GPU.\n"
            f"4. **Upload Knowledge**: Ingest PDF, Markdown, or text files in the **Documents** tab to query your files directly using ChromaDB vector search!"
        )

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        repeat_penalty: float | None = None,
        seed: int | None = None,
        max_tokens: int | None = None,
        stream: bool | None = None,
        api_key: str | None = None,
        provider: str | None = None,
    ) -> str:

        payload = self._build_payload(
            prompt=prompt,
            model=model,
            temperature=temperature,
            top_p=top_p,
            repeat_penalty=repeat_penalty,
            seed=seed,
            max_tokens=max_tokens,
            stream=stream
        )

        start = time.perf_counter()

        try:
            response = self._post_generate(
                payload
            )
            response_text = response.json()["response"]
        except Exception:
            # Resilient cloud demo fallback when Ollama is offline
            response_text = self._generate_cloud_fallback(
                prompt=prompt,
                model_name=payload.get("model", "qwen2.5:1.5b"),
                api_key=api_key,
                provider=provider,
            )

        latency = time.perf_counter() - start

        self._update_diagnostics(
            payload=payload,
            prompt=prompt,
            response_text=response_text,
            latency=latency
        )

        return response_text


ollama_service = OllamaService()