import os
import sqlite3
from openai import OpenAI, APIError, APIConnectionError, RateLimitError

DB_PATH = "chat_history.db"

class LLMClient:
    def __init__(self, api_key: str = None, max_history: int = 20, clear_on_start=True, system_prompt=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.max_history = max_history
        self.system_prompt = (
            "You are a friendly robot assistant named Karen. "
            "You always respond in a natural, human-like way. "
            "You only describe the scene if the user asks about it. "
            "Do not provide scene descriptions unless requested."
            "Actually you can hear user voice, using stt."
            "Actually you can speak by voice, using tts."
            "Actually you can see scene using camera."
        )

        if not self.api_key:
            print("[Warning] OPENAI_API_KEY not set, using DummyLLMClient")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)

        # DB setup
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._init_db()
        if clear_on_start:
            self.clear_history()

        # simpan system prompt
        self._add_message("system", self.system_prompt)

    def _init_db(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def clear_history(self):
        c = self.conn.cursor()
        c.execute("DELETE FROM messages")
        self.conn.commit()
        print("[LLMClient] Chat history cleared")

    def _add_message(self, role: str, content: str):
        c = self.conn.cursor()
        c.execute("INSERT INTO messages (role, content) VALUES (?, ?)", (role, content))
        self.conn.commit()

    def _get_history(self):
        c = self.conn.cursor()
        c.execute(f"SELECT role, content FROM messages ORDER BY id ASC LIMIT {self.max_history}")
        rows = c.fetchall()
        return [{"role": r[0], "content": r[1]} for r in rows]

    def chat(self, messages: list, model: str = "gpt-4o-mini") -> str:
        for m in messages:
            self._add_message(m["role"], m["content"])

        history = self._get_history()
        if not self.client:
            return "[Dummy Response] (no API key configured)"

        try:
            resp = self.client.responses.create(
                model=model,
                input=history
            )
            text = getattr(resp, "output_text", "").strip()
            if text:
                self._add_message("assistant", text)
            return text or None
        except (APIError, APIConnectionError, RateLimitError) as e:
            print(f"[Error] OpenAI API error: {e}")
            return None
        except Exception as e:
            print(f"[Error] Unexpected LLM error: {e}")
            return None