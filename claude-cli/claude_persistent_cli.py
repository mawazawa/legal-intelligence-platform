#!/usr/bin/env python3
"""
Claude Persistent CLI - Unlimited thread length with file-based memory
Similar to TypingMind but for Claude API with persistent context
"""

import os
import sys
import json
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import anthropic
from anthropic.types import ContentBlock, ToolUseBlock
import pickle
import tiktoken

class ClaudePersistentCLI:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Please set ANTHROPIC_API_KEY environment variable")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.db_path = Path.home() / ".claude_persistent" / "conversations.db"
        self.files_path = Path.home() / ".claude_persistent" / "files"
        self.context_path = Path.home() / ".claude_persistent" / "contexts"
        
        # Create directories
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.files_path.mkdir(parents=True, exist_ok=True)
        self.context_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.init_db()
        
        # Token counter
        self.encoding = tiktoken.encoding_for_model("gpt-4")  # Close approximation
        
        # Model settings for evidence parsing
        self.evidence_mode_settings = {
            "temperature": 0.0,  # Deterministic for evidence
            "top_p": 1.0,
            "max_tokens": 8192
        }
        
        self.creative_mode_settings = {
            "temperature": 0.7,
            "top_p": 0.95,
            "max_tokens": 8192
        }
    
    def init_db(self):
        """Initialize SQLite database for conversation history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                title TEXT,
                model TEXT,
                total_tokens INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP,
                tokens INTEGER,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                conversation_id TEXT,
                filename TEXT,
                content TEXT,
                file_type TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_conversation(self, title: str = None) -> str:
        """Create a new conversation with persistent ID"""
        conv_id = hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:12]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO conversations (id, created_at, updated_at, title, model)
            VALUES (?, ?, ?, ?, ?)
        """, (conv_id, datetime.now(), datetime.now(), title or f"Conversation {conv_id}", "claude-opus-4-20250514"))
        
        conn.commit()
        conn.close()
        
        return conv_id
    
    def save_message(self, conv_id: str, role: str, content: str):
        """Save message to database with token count"""
        tokens = len(self.encoding.encode(content))
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO messages (conversation_id, role, content, timestamp, tokens)
            VALUES (?, ?, ?, ?, ?)
        """, (conv_id, role, content, datetime.now(), tokens))
        
        # Update total tokens
        cursor.execute("""
            UPDATE conversations 
            SET total_tokens = total_tokens + ?, updated_at = ?
            WHERE id = ?
        """, (tokens, datetime.now(), conv_id))
        
        conn.commit()
        conn.close()
    
    def get_conversation_context(self, conv_id: str, max_tokens: int = 100000) -> List[Dict]:
        """Retrieve conversation history with intelligent truncation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get messages in reverse order to prioritize recent context
        cursor.execute("""
            SELECT role, content, tokens 
            FROM messages 
            WHERE conversation_id = ?
            ORDER BY timestamp DESC
        """, (conv_id,))
        
        messages = []
        total_tokens = 0
        
        for role, content, tokens in cursor.fetchall():
            if total_tokens + tokens > max_tokens:
                break
            messages.insert(0, {"role": role, "content": content})
            total_tokens += tokens
        
        conn.close()
        return messages
    
    def upload_file(self, conv_id: str, file_path: str) -> str:
        """Upload file and associate with conversation"""
        file_id = hashlib.sha256(f"{conv_id}_{file_path}".encode()).hexdigest()[:12]
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO files (id, conversation_id, filename, content, file_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (file_id, conv_id, os.path.basename(file_path), content, 
              os.path.splitext(file_path)[1], datetime.now()))
        
        conn.commit()
        conn.close()
        
        return file_id
    
    def get_files(self, conv_id: str) -> List[Dict]:
        """Get all files associated with a conversation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, filename, content, file_type 
            FROM files 
            WHERE conversation_id = ?
        """, (conv_id,))
        
        files = [{"id": row[0], "filename": row[1], "content": row[2], "type": row[3]} 
                 for row in cursor.fetchall()]
        
        conn.close()
        return files
    
    def chat(self, conv_id: str, message: str, evidence_mode: bool = False):
        """Main chat function with persistent context"""
        # Save user message
        self.save_message(conv_id, "user", message)
        
        # Get conversation context
        context = self.get_conversation_context(conv_id)
        
        # Get associated files
        files = self.get_files(conv_id)
        if files:
            file_context = "\n\n=== PERSISTENT FILES ===\n"
            for f in files:
                file_context += f"File: {f['filename']}\n```\n{f['content'][:1000]}...\n```\n\n"
            context.insert(0, {"role": "system", "content": file_context})
        
        # Choose settings based on mode
        settings = self.evidence_mode_settings if evidence_mode else self.creative_mode_settings
        
        # Make API call
        response = self.client.messages.create(
            model="claude-opus-4-20250514",
            messages=context,
            **settings
        )
        
        # Save assistant response
        assistant_message = response.content[0].text
        self.save_message(conv_id, "assistant", assistant_message)
        
        return assistant_message
    
    def interactive_mode(self, conv_id: str = None):
        """Interactive CLI mode"""
        if not conv_id:
            conv_id = self.create_conversation()
            print(f"📝 New conversation created: {conv_id}")
        else:
            print(f"📂 Resuming conversation: {conv_id}")
        
        print("\n🤖 Claude Persistent CLI")
        print("Commands: /file <path>, /evidence (toggle evidence mode), /new, /list, /exit")
        print("-" * 50)
        
        evidence_mode = False
        
        while True:
            try:
                user_input = input(f"\n{'🔍' if evidence_mode else '💬'} You: ").strip()
                
                if user_input.startswith("/"):
                    if user_input == "/exit":
                        break
                    elif user_input == "/new":
                        conv_id = self.create_conversation()
                        print(f"📝 New conversation: {conv_id}")
                    elif user_input.startswith("/file "):
                        file_path = user_input[6:].strip()
                        file_id = self.upload_file(conv_id, file_path)
                        print(f"📎 File uploaded: {file_id}")
                    elif user_input == "/evidence":
                        evidence_mode = not evidence_mode
                        print(f"🔧 Evidence mode: {'ON' if evidence_mode else 'OFF'}")
                    elif user_input == "/list":
                        self.list_conversations()
                    continue
                
                print("\n🤔 Claude is thinking...")
                response = self.chat(conv_id, user_input, evidence_mode)
                print(f"\n🤖 Claude: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def list_conversations(self):
        """List all conversations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, created_at, total_tokens 
            FROM conversations 
            ORDER BY updated_at DESC 
            LIMIT 10
        """)
        
        print("\n📚 Recent Conversations:")
        for conv_id, title, created_at, tokens in cursor.fetchall():
            print(f"  {conv_id}: {title} ({tokens:,} tokens) - {created_at}")
        
        conn.close()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Claude Persistent CLI")
    parser.add_argument("--conversation", "-c", help="Resume specific conversation")
    parser.add_argument("--api-key", help="Anthropic API key")
    parser.add_argument("--evidence-mode", "-e", action="store_true", help="Start in evidence mode")
    
    args = parser.parse_args()
    
    cli = ClaudePersistentCLI(api_key=args.api_key)
    cli.interactive_mode(conv_id=args.conversation)

if __name__ == "__main__":
    main()
