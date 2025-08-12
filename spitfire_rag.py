"""
LUCY - 1978 Triumph Spitfire RAG System
Main RAG class with persistent memory and personality
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import Chroma
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.schema.messages import HumanMessage, AIMessage

from config import SpitfireConfig
from prompts import (
    LUCY_SPITFIRE_PROMPT, 
    MEMORY_UPDATE_PROMPT, 
    TECHNICAL_KNOWLEDGE_UPDATE_PROMPT,
    TODO_DETECTION_PROMPT,
    TODO_COMPLETION_CONFIRMATION_PROMPT,
    LUCY_GREETING,
    LUCY_SYSTEM_INFO
)


class TriumphSpitfireRAG:
    """
    LUCY - A charming 1978 Triumph Spitfire RAG system with persistent memory
    """
    
    def __init__(self, docs_dir: str = None, vectordb_dir: str = None):
        """Initialize LUCY with memory and personality"""
        
        # Configuration
        self.config = SpitfireConfig()
        self.config.validate_api_keys()
        
        # Paths
        self.docs_dir = Path(docs_dir or self.config.DOCS_DIR)
        self.vectordb_dir = Path(vectordb_dir or self.config.VECTORDB_DIR)
        self.maintenance_log_path = Path(self.config.MAINTENANCE_LOG_PATH)
        self.technical_knowledge_path = Path(self.config.TECHNICAL_KNOWLEDGE_PATH)
        self.todo_list_path = Path(self.config.TODO_LIST_PATH)
        
        # Ensure directories exist
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.vectordb_dir.mkdir(parents=True, exist_ok=True)
        self.maintenance_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.embeddings = OpenAIEmbeddings(
            model=self.config.EMBEDDING_MODEL,
            api_key=self.config.OPENAI_API_KEY
        )
        
        self.llm = ChatAnthropic(
            model=self.config.LLM_MODEL,
            api_key=self.config.ANTHROPIC_API_KEY,
            temperature=0.7
        )
        
        # Memory for conversation
        self.memory = ConversationBufferWindowMemory(
            k=self.config.CONVERSATION_MEMORY_SIZE,
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Initialize components
        self.vectorstore = None
        self.qa_chain = None
        self.maintenance_log = self.load_maintenance_log()
        self.technical_knowledge = self.load_technical_knowledge()
        self.todo_list = self.load_todo_list()
        
        # Clean up any planned work that was incorrectly added to maintenance log
        self.cleanup_maintenance_log()
        
        # Setup RAG system
        self.setup_vectorstore()
        self.setup_qa_chain()
    
    def load_maintenance_log(self) -> Dict[str, Any]:
        """Load LUCY's maintenance memory from persistent storage"""
        if self.maintenance_log_path.exists():
            try:
                with open(self.maintenance_log_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load maintenance log: {e}")
        
        # Return default maintenance log structure
        return {
            "recent_work": [],
            "current_issues": ["Time for a general inspection - I haven't been checked in a while!"],
            "last_service_date": None,
            "mileage": 89000,
            "oil_type": "20W-50",
            "last_oil_change": None,
                            "notes": "LUCY is ready for some proper care and attention!"
        }
    
    def save_maintenance_log(self):
        """Persist LUCY's maintenance memory"""
        try:
            with open(self.maintenance_log_path, 'w') as f:
                json.dump(self.maintenance_log, f, indent=2, default=str)
        except IOError as e:
            print(f"Warning: Could not save maintenance log: {e}")
    
    def load_technical_knowledge(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load LUCY's technical knowledge from persistent storage"""
        if self.technical_knowledge_path.exists():
            try:
                with open(self.technical_knowledge_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load technical knowledge: {e}")
        
        # Return default technical knowledge structure
        return {
            "specifications": [],
            "part_numbers": [],
            "procedures": [],
            "corrections": []
        }
    
    def save_technical_knowledge(self):
        """Persist LUCY's technical knowledge"""
        try:
            with open(self.technical_knowledge_path, 'w') as f:
                json.dump(self.technical_knowledge, f, indent=2, default=str)
        except IOError as e:
            print(f"Warning: Could not save technical knowledge: {e}")
    
    def update_technical_knowledge(self, user_input: str) -> bool:
        """
        Detect and update technical knowledge from user input
        Returns True if technical knowledge was detected and saved
        """
        try:
            # Use LLM to extract technical information
            knowledge_prompt = TECHNICAL_KNOWLEDGE_UPDATE_PROMPT.format(user_input=user_input)
            response = self.llm.invoke(knowledge_prompt)
            
            # Parse the response
            response_text = response.content.strip()
            if response_text and response_text != "{}":
                try:
                    json_text = self._extract_json_from_response(response_text)
                    if json_text:
                        knowledge_data = json.loads(json_text)
                    else:
                        knowledge_data = None
                    if knowledge_data and "category" in knowledge_data and "information" in knowledge_data:
                        # Add timestamp and format entry
                        knowledge_entry = {
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "topic": knowledge_data.get("topic", "Technical information"),
                            "information": knowledge_data["information"],
                            "source": knowledge_data.get("source", "User provided"),
                            "category": knowledge_data["category"]
                        }
                        
                        # Add to appropriate category
                        category = knowledge_data["category"]
                        if category in self.technical_knowledge:
                            self.technical_knowledge[category].append(knowledge_entry)
                            
                            # Keep only last 20 entries per category to prevent bloat
                            if len(self.technical_knowledge[category]) > 20:
                                self.technical_knowledge[category] = self.technical_knowledge[category][-20:]
                            
                            self.save_technical_knowledge()
                            return True
                        
                except json.JSONDecodeError:
                    pass  # Not valid JSON, no technical knowledge detected
                    
        except Exception as e:
            print(f"Warning: Error processing technical knowledge: {e}")
        
        return False
    
    def load_todo_list(self) -> List[Dict[str, Any]]:
        """Load LUCY's todo list from persistent storage"""
        if self.todo_list_path.exists():
            try:
                with open(self.todo_list_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load todo list: {e}")
        
        # Return default empty todo list
        return []
    
    def save_todo_list(self):
        """Persist LUCY's todo list"""
        try:
            with open(self.todo_list_path, 'w') as f:
                json.dump(self.todo_list, f, indent=2, default=str)
        except IOError as e:
            print(f"Warning: Could not save todo list: {e}")
    
    def process_todo_operations(self, user_input: str) -> Dict[str, Any]:
        """
        Detect and process todo list operations from user input
        Returns dict with operation details and any confirmations needed
        """
        try:
            # Use LLM to detect todo operations
            todo_prompt = TODO_DETECTION_PROMPT.format(user_input=user_input)
            response = self.llm.invoke(todo_prompt)
            
            # Parse the response - extract JSON from potentially multi-line response
            response_text = response.content.strip()
            if response_text and response_text != "{}":
                try:
                    # Extract JSON from the response (may have explanation text after)
                    json_text = self._extract_json_from_response(response_text)
                    if json_text:
                        todo_data = json.loads(json_text)
                        operation = todo_data.get("operation", "none")
                        
                        if operation == "add":
                            return self._add_todo_item(todo_data)
                        elif operation == "complete":
                            return self._handle_todo_completion(todo_data)
                    
                except json.JSONDecodeError:
                    pass  # Not valid JSON, no todo operation detected
                    
        except Exception as e:
            print(f"Warning: Error processing todo operations: {e}")
        
        return {"operation": "none", "message": "", "confirmation_needed": False}
    
    def _extract_json_from_response(self, response_text: str) -> str:
        """Extract JSON object from LLM response that may contain additional text"""
        lines = response_text.strip().split('\n')
        json_lines = []
        in_json = False
        brace_count = 0
        
        for line in lines:
            stripped = line.strip()
            if not in_json and stripped.startswith('{'):
                in_json = True
                json_lines = [line]
                brace_count = stripped.count('{') - stripped.count('}')
            elif in_json:
                json_lines.append(line)
                brace_count += stripped.count('{') - stripped.count('}')
                if brace_count <= 0:  # Found closing brace
                    break
        
        if json_lines:
            return '\n'.join(json_lines)
        return ""
    
    def _add_todo_item(self, todo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new todo item to the list"""
        import uuid
        
        todo_item = {
            "id": str(uuid.uuid4())[:8],  # Short unique ID
            "task": todo_data.get("task", ""),
            "details": todo_data.get("details", ""),
            "priority": todo_data.get("priority", "medium"),
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "pending",
            "date_completed": None
        }
        
        self.todo_list.append(todo_item)
        self.save_todo_list()
        
        return {
            "operation": "add",
            "message": f"Added to todo list: {todo_item['task']}",
            "confirmation_needed": False,
            "todo_item": todo_item
        }
    
    def _handle_todo_completion(self, todo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle when user mentions completing work - check for matching todos"""
        completed_work = todo_data.get("completed_task", "")
        
        # Find matching pending todos
        pending_todos = [todo for todo in self.todo_list if todo["status"] == "pending"]
        
        if not pending_todos:
            return {
                "operation": "complete",
                "message": "Great work! No pending todos to mark as complete.",
                "confirmation_needed": False
            }
        
        # Use LLM to find matching todos
        try:
            matching_prompt = TODO_COMPLETION_CONFIRMATION_PROMPT.format(
                completed_work=completed_work,
                matching_todos=json.dumps(pending_todos, indent=2)
            )
            response = self.llm.invoke(matching_prompt)
            response_text = response.content.strip()
            
            if response_text and response_text != "{}":
                json_text = self._extract_json_from_response(response_text)
                if json_text:
                    matches_data = json.loads(json_text)
                else:
                    matches_data = {}
                matches = matches_data.get("matches", [])
                
                if matches:
                    # Return matches for user confirmation
                    return {
                        "operation": "complete",
                        "message": f"You mentioned completing: {completed_work}",
                        "confirmation_needed": True,
                        "matches": matches,
                        "completed_work": completed_work
                    }
        
        except (json.JSONDecodeError, Exception) as e:
            print(f"Warning: Error matching todo completions: {e}")
        
        return {
            "operation": "complete", 
            "message": "Great work! Couldn't find matching todos to mark complete.",
            "confirmation_needed": False
        }
    
    def confirm_todo_completion(self, todo_id: str, completed_work: str) -> bool:
        """Mark a specific todo as completed after user confirmation"""
        for todo in self.todo_list:
            if todo["id"] == todo_id and todo["status"] == "pending":
                todo["status"] = "completed"
                todo["date_completed"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                todo["completion_notes"] = completed_work
                self.save_todo_list()
                return True
        return False
    
    def get_todo_summary(self) -> str:
        """Get a formatted summary of the current todo list"""
        if not self.todo_list:
            return "Todo list is empty - no pending tasks!"
        
        pending_todos = [todo for todo in self.todo_list if todo["status"] == "pending"]
        completed_todos = [todo for todo in self.todo_list if todo["status"] == "completed"]
        
        summary = []
        
        if pending_todos:
            summary.append("🔧 **Pending Tasks:**")
            for todo in pending_todos:
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(todo["priority"], "⚪")
                summary.append(f"  {priority_icon} {todo['task']} (ID: {todo['id']})")
                if todo.get("details"):
                    summary.append(f"     • {todo['details']}")
        
        if completed_todos:
            summary.append("\n✅ **Recently Completed:**")
            recent_completed = completed_todos[-3:]  # Show last 3 completed
            for todo in recent_completed:
                summary.append(f"  ✓ {todo['task']} ({todo['date_completed']})")
        
        return "\n".join(summary)
    
    def cleanup_maintenance_log(self):
        """Clean up maintenance log to remove planned work (should be in todo list)"""
        if not hasattr(self, 'maintenance_log') or not self.maintenance_log:
            return
        
        # Filter out planned/future work from maintenance log
        completed_work = []
        planned_work_found = []
        
        for entry in self.maintenance_log.get("recent_work", []):
            action = entry.get("action", "").lower()
            notes = entry.get("notes", "").lower()
            
            # Check if this is planned work
            is_planned = any(keyword in action or keyword in notes for keyword in [
                "planned", "planning", "going to", "will", "should", "need to", 
                "future", "research", "looking for", "plan to"
            ])
            
            if is_planned:
                planned_work_found.append(entry)
            else:
                completed_work.append(entry)
        
        # Update maintenance log with only completed work
        if len(completed_work) != len(self.maintenance_log.get("recent_work", [])):
            self.maintenance_log["recent_work"] = completed_work
            self.save_maintenance_log()
            print(f"Cleaned up maintenance log: moved {len(planned_work_found)} planned items")
            
        return planned_work_found
    
    def update_maintenance_memory(self, user_input: str) -> bool:
        """
        Detect and update maintenance memory from user input
        Returns True if maintenance was detected and logged
        """
        try:
            # Use LLM to extract maintenance information
            memory_prompt = MEMORY_UPDATE_PROMPT.format(user_input=user_input)
            response = self.llm.invoke(memory_prompt)
            
            # Parse the response
            response_text = response.content.strip()
            if response_text and response_text != "{}":
                try:
                    json_text = self._extract_json_from_response(response_text)
                    if json_text:
                        maintenance_data = json.loads(json_text)
                    else:
                        maintenance_data = None
                    if maintenance_data and "action" in maintenance_data:
                        # Add to maintenance log
                        maintenance_entry = {
                            "date": maintenance_data.get("date", datetime.now().strftime("%Y-%m-%d")),
                            "action": maintenance_data["action"],
                            "notes": maintenance_data.get("notes", "")
                        }
                        
                        self.maintenance_log["recent_work"].append(maintenance_entry)
                        
                        # Keep only last 10 maintenance entries
                        if len(self.maintenance_log["recent_work"]) > 10:
                            self.maintenance_log["recent_work"] = self.maintenance_log["recent_work"][-10:]
                        
                        # Update last service date if it's a major service
                        if any(keyword in maintenance_data["action"].lower() for keyword in 
                               ["service", "tune-up", "major", "inspection"]):
                            self.maintenance_log["last_service_date"] = maintenance_entry["date"]
                        
                        # Check for mileage/odometer updates in the notes or action
                        full_text = f"{maintenance_data['action']} {maintenance_data.get('notes', '')}".lower()
                        import re
                        # Look for patterns like "68,092", "68092", "odometer: 68,092", "mileage 68092"
                        mileage_patterns = [
                            r'odometer[:\s]+([0-9,]+)',
                            r'mileage[:\s]+([0-9,]+)', 
                            r'miles[:\s]+([0-9,]+)',
                            r'read[:\s]+([0-9,]+)',
                            r'\b([0-9]{2,3}[,]?[0-9]{3})\b'  # Match 5-6 digit numbers with optional comma
                        ]
                        
                        for pattern in mileage_patterns:
                            match = re.search(pattern, full_text)
                            if match:
                                try:
                                    # Extract and clean the mileage number
                                    mileage_str = match.group(1).replace(',', '')
                                    new_mileage = int(mileage_str)
                                    # Only update if it's a reasonable mileage (20,000 - 200,000)
                                    if 20000 <= new_mileage <= 200000:
                                        self.maintenance_log["mileage"] = new_mileage
                                        print(f"Updated mileage to: {new_mileage:,}")
                                        break
                                except (ValueError, IndexError):
                                    continue
                        
                        self.save_maintenance_log()
                        return True
                        
                except json.JSONDecodeError:
                    pass  # Not valid JSON, no maintenance detected
                    
        except Exception as e:
            print(f"Warning: Error processing maintenance memory: {e}")
        
        return False
    
    def format_maintenance_history(self) -> str:
        """Format recent maintenance work for prompt injection"""
        if not self.maintenance_log["recent_work"]:
            return "No recent maintenance work recorded. I'm ready for some attention!"
        
        history = []
        for work in self.maintenance_log["recent_work"][-5:]:  # Last 5 entries
            entry = f"- {work['date']}: {work['action']}"
            if work.get('notes'):
                entry += f" ({work['notes']})"
            history.append(entry)
        
        return "\n".join(history)
    
    def format_technical_knowledge(self) -> str:
        """Format technical knowledge for prompt injection"""
        if not any(self.technical_knowledge.values()):
            return "No additional technical knowledge recorded yet."
        
        knowledge_sections = []
        
        for category, entries in self.technical_knowledge.items():
            if entries:
                section_name = category.replace("_", " ").title()
                knowledge_sections.append(f"\n{section_name}:")
                for entry in entries[-5:]:  # Last 5 entries per category
                    knowledge_sections.append(f"- {entry['topic']}: {entry['information']} (Source: {entry['source']})")
        
        return "\n".join(knowledge_sections)
    
    def get_document_metadata_file(self):
        """Get path to document metadata tracking file"""
        return self.vectordb_dir / "document_metadata.json"
    
    def save_document_metadata(self, doc_metadata: Dict[str, Any]):
        """Save document metadata for tracking changes"""
        try:
            with open(self.get_document_metadata_file(), 'w') as f:
                json.dump(doc_metadata, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save document metadata: {e}")
    
    def load_document_metadata(self) -> Dict[str, Any]:
        """Load document metadata for tracking changes"""
        metadata_file = self.get_document_metadata_file()
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load document metadata: {e}")
        return {}
    
    def check_and_update_documents(self):
        """Check for new or modified documents and update vector database"""
        existing_metadata = self.load_document_metadata()
        current_metadata = {}
        new_documents = []
        
        # Scan current documents
        for file_path in self.docs_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.txt', '.md']:
                file_key = str(file_path.relative_to(self.docs_dir))
                file_stat = file_path.stat()
                current_metadata[file_key] = {
                    "size": file_stat.st_size,
                    "modified": file_stat.st_mtime
                }
                
                # Check if file is new or modified
                if (file_key not in existing_metadata or 
                    existing_metadata[file_key]["modified"] != file_stat.st_mtime or
                    existing_metadata[file_key]["size"] != file_stat.st_size):
                    
                    try:
                        if file_path.suffix.lower() == '.pdf':
                            from langchain_community.document_loaders import PyPDFLoader
                            loader = PyPDFLoader(str(file_path))
                            docs = loader.load()
                        else:
                            from langchain_community.document_loaders import TextLoader
                            loader = TextLoader(str(file_path), encoding='utf-8')
                            docs = loader.load()
                        
                        # Add metadata
                        for doc in docs:
                            doc.metadata["source"] = str(file_path)
                            new_documents.append(doc)
                        
                        print(f"Detected new/updated: {file_path.name}")
                        
                    except Exception as e:
                        print(f"Warning: Could not load {file_path}: {e}")
        
        # Process new documents if any
        if new_documents:
            print(f"Processing {len(new_documents)} new/updated documents...")
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.CHUNK_SIZE,
                chunk_overlap=self.config.CHUNK_OVERLAP,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            
            split_docs = text_splitter.split_documents(new_documents)
            print(f"Split into {len(split_docs)} new chunks")
            
            # Add to existing vectorstore
            self.vectorstore.add_documents(split_docs)
            print(f"Added {len(split_docs)} new document chunks")
            
            # Save updated metadata
            self.save_document_metadata(current_metadata)
        else:
            print("No new documents detected")
    
    def setup_vectorstore(self):
        """Initialize or load the vector database"""
        # Check if vectorstore already exists by looking for chroma.sqlite3 file
        chroma_db_file = self.vectordb_dir / "chroma.sqlite3"
        
        if chroma_db_file.exists() and chroma_db_file.stat().st_size > 0:
            # Load existing vectorstore
            self.vectorstore = Chroma(
                collection_name=self.config.COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=str(self.vectordb_dir)
            )
            print("Loaded existing vector database")
            
            # Check for new or modified documents
            self.check_and_update_documents()
        else:
            # Create new vectorstore and ingest documents
            self.vectorstore = Chroma(
                collection_name=self.config.COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=str(self.vectordb_dir)
            )
            print("Created new vector database")
            self.ingest_documents()
    
    def ingest_documents(self):
        """Load and process documents into the vector database"""
        documents = []
        
        # Add LUCY's system information as a document
        system_doc = Document(
            page_content=LUCY_SYSTEM_INFO,
            metadata={"source": "lucy_system_info", "type": "specifications"}
        )
        documents.append(system_doc)
        
        # Sample data removed - using real manuals and forum posts instead
        
        # Load documents from docs directory
        for file_path in self.docs_dir.rglob("*"):
            if file_path.is_file():
                try:
                    if file_path.suffix.lower() == '.pdf':
                        loader = PyPDFLoader(str(file_path))
                        docs = loader.load()
                    elif file_path.suffix.lower() in ['.txt', '.md']:
                        loader = TextLoader(str(file_path), encoding='utf-8')
                        docs = loader.load()
                    else:
                        continue
                    
                    # Add metadata
                    for doc in docs:
                        doc.metadata["source"] = str(file_path)
                        documents.append(doc)
                    
                    print(f"Loaded: {file_path.name}")
                    
                except Exception as e:
                    print(f"Warning: Could not load {file_path}: {e}")
        
        if documents:
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.CHUNK_SIZE,
                chunk_overlap=self.config.CHUNK_OVERLAP,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            
            split_docs = text_splitter.split_documents(documents)
            print(f"Split {len(documents)} documents into {len(split_docs)} chunks")
            
            # Add to vectorstore
            self.vectorstore.add_documents(split_docs)
            print(f"Added {len(split_docs)} document chunks to vector database")
            
            # Save document metadata for future change detection
            doc_metadata = {}
            for file_path in self.docs_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.txt', '.md']:
                    file_key = str(file_path.relative_to(self.docs_dir))
                    file_stat = file_path.stat()
                    doc_metadata[file_key] = {
                        "size": file_stat.st_size,
                        "modified": file_stat.st_mtime
                    }
            self.save_document_metadata(doc_metadata)
        else:
            print("No documents found to ingest")
    

    
    def setup_qa_chain(self):
        """Setup the conversational retrieval chain with LUCY's personality"""
        if not self.vectorstore:
            raise ValueError("Vector database not initialized")
        
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": self.config.TOP_K_RETRIEVAL}
        )
        
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=self.memory,
            return_source_documents=True,
            verbose=False
        )
    
    def ask_lucy(self, question: str) -> Dict[str, Any]:
        """
        Main method to ask LUCY a question with memory integration
        """
        # Check for maintenance updates, technical knowledge, and todo operations
        maintenance_detected = self.update_maintenance_memory(question)
        technical_knowledge_detected = self.update_technical_knowledge(question)
        todo_result = self.process_todo_operations(question)
        
        try:
            # Prepare the enhanced question with LUCY's personality and context
            maintenance_context = self.format_maintenance_history()
            technical_context = self.format_technical_knowledge()
            todo_context = self.get_todo_summary()
            
            # Add detection status to the question if knowledge was detected
            detection_note = ""
            if technical_knowledge_detected:
                detection_note = "\n[SYSTEM: Technical knowledge was just detected and saved from this input - acknowledge this!]"
            if maintenance_detected:
                detection_note += "\n[SYSTEM: Maintenance work was just detected and saved from this input - acknowledge this!]"
            if todo_result["operation"] == "add":
                detection_note += f"\n[SYSTEM: Todo item was added: {todo_result['message']} - acknowledge this!]"
            
            # Create a personality-infused question using the proper prompt
            enhanced_question = LUCY_SPITFIRE_PROMPT.format(
                lucy_age=self.config.LUCY_AGE,
                maintenance_history=maintenance_context,
                technical_knowledge=technical_context,
                todo_list=todo_context,
                context="",  # Will be filled by RAG retrieval
                chat_history="",  # Will be filled by conversation memory
                question=question + detection_note
            )
            
            # Get response from RAG system
            result = self.qa_chain.invoke({"question": enhanced_question})
            
            response = {
                "answer": result["answer"],
                "source_documents": result.get("source_documents", []),
                "maintenance_detected": maintenance_detected,
                "technical_knowledge_detected": technical_knowledge_detected,
                "todo_result": todo_result
            }
            
            return response
            
        except Exception as e:
            return {
                "answer": f"Oh dear! I seem to be having a bit of trouble with my electrical system (error: {str(e)}). Could you try asking me again?",
                "source_documents": [],
                "maintenance_detected": maintenance_detected,
                "technical_knowledge_detected": technical_knowledge_detected
            }
    
    def get_greeting(self) -> str:
        """Get LUCY's personalized greeting"""
        recent_maintenance = self.format_maintenance_history()
        if not recent_maintenance:
            recent_maintenance = "Nothing recent - I could use some attention!"
        
        return LUCY_GREETING.format(
            lucy_age=self.config.LUCY_AGE,
            recent_maintenance=recent_maintenance
        )
    
    def clear_conversation_memory(self):
        """Clear conversation memory (but keep maintenance log)"""
        self.memory.clear()
        print("Conversation memory cleared (maintenance log preserved)")
    
    def get_maintenance_summary(self) -> Dict[str, Any]:
        """Get a summary of LUCY's maintenance status"""
        return {
            "recent_work_count": len(self.maintenance_log["recent_work"]),
            "last_service": self.maintenance_log.get("last_service_date"),
            "current_mileage": self.maintenance_log.get("mileage"),
            "current_issues": self.maintenance_log.get("current_issues", []),
            "recent_work": self.maintenance_log["recent_work"][-3:] if self.maintenance_log["recent_work"] else []
        }
    
    def get_technical_knowledge_summary(self) -> Dict[str, Any]:
        """Get a summary of LUCY's learned technical knowledge"""
        total_entries = sum(len(entries) for entries in self.technical_knowledge.values())
        return {
            "total_knowledge_entries": total_entries,
            "specifications_count": len(self.technical_knowledge.get("specifications", [])),
            "part_numbers_count": len(self.technical_knowledge.get("part_numbers", [])),
            "procedures_count": len(self.technical_knowledge.get("procedures", [])),
            "corrections_count": len(self.technical_knowledge.get("corrections", [])),
            "recent_knowledge": {
                category: entries[-2:] if entries else []
                for category, entries in self.technical_knowledge.items()
            }
        }