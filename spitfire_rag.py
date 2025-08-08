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
                    maintenance_data = json.loads(response_text)
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
    
    def setup_vectorstore(self):
        """Initialize or load the vector database"""
        # Check if vectorstore already exists
        vectorstore_path = self.vectordb_dir / self.config.COLLECTION_NAME
        
        if vectorstore_path.exists() and any(vectorstore_path.iterdir()):
            # Load existing vectorstore
            self.vectorstore = Chroma(
                collection_name=self.config.COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=str(self.vectordb_dir)
            )
            print("Loaded existing vector database")
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
        
        # Add sample Spitfire knowledge
        sample_docs = self.add_sample_data()
        documents.extend(sample_docs)
        
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
        else:
            print("No documents found to ingest")
    
    def add_sample_data(self) -> List[Document]:
        """Add sample Triumph Spitfire knowledge"""
        sample_docs = [
            Document(
                page_content="""
                Triumph Spitfire Carburettor Adjustment - SU HS4 Twin Carbs
                
                The 1978 Spitfire uses twin SU HS4 carburettors that require periodic synchronization.
                
                Tools Required:
                - Carb balancer or Unisyn tool
                - 3/8" spanner for throttle adjustment
                - Small screwdriver for mixture adjustment
                - Tachometer
                
                Procedure:
                1. Warm engine to operating temperature
                2. Remove air cleaners
                3. Check throttle linkage for smooth operation
                4. Adjust idle speed to 800-900 RPM using throttle stop screws
                5. Use carb balancer to synchronize both carbs at idle
                6. Adjust mixture screws for smoothest idle (usually 1.5-2 turns out)
                7. Test at 2000 RPM - both carbs should read identical on balancer
                8. Road test and readjust if necessary
                
                Common Issues:
                - Uneven idle usually indicates poor synchronization
                - Black smoke = too rich mixture
                - Popping back through carbs = too lean mixture
                """,
                metadata={"source": "carburettor_guide", "type": "maintenance"}
            ),
            Document(
                page_content="""
                Triumph Spitfire Oil Change - 1.5L Engine
                
                Oil Capacity: 4.5 pints (2.6 litres) with filter change
                Recommended Oil: 20W-50 for vintage engines in normal climates
                Filter: Spin-on type, Fram PH30 or equivalent
                
                Procedure:
                1. Warm engine to operating temperature
                2. Position drain pan under sump drain plug
                3. Remove drain plug (19mm socket) - beware hot oil!
                4. Allow to drain for 15-20 minutes
                5. Remove oil filter (may need filter wrench)
                6. Clean filter mounting surface
                7. Apply thin coat of oil to new filter gasket
                8. Install new filter hand-tight plus 3/4 turn
                9. Replace drain plug with new washer if needed
                10. Fill with oil through rocker cover opening
                11. Run engine and check for leaks
                12. Check level after 5 minutes running
                
                Notes:
                - Check oil level weekly - these engines can develop leaks
                - Change oil every 3000 miles for classic car use
                - Use quality 20W-50 oil designed for older engines
                """,
                metadata={"source": "oil_change_guide", "type": "maintenance"}
            ),
            Document(
                page_content="""
                Triumph Spitfire Electrical System - Lucas "Prince of Darkness"
                
                The 1978 Spitfire uses Lucas electrical components, famous for their quirks.
                
                Common Electrical Issues:
                - Intermittent wipers (check earth connections)
                - Dim headlights (clean all earth points)
                - Starting problems (check starter solenoid)
                - Charging issues (test alternator output)
                
                Essential Electrical Maintenance:
                1. Clean all earth/ground connections annually
                2. Check battery terminals for corrosion
                3. Test alternator output (should be 13.8-14.4V at 2000 RPM)
                4. Inspect wiring for chafing or damage
                5. Keep spare fuses and bulbs in car
                
                Lucas Electrical Tips:
                - Never disconnect battery while engine running
                - Use contact cleaner on switch contacts
                - Upgrade to electronic ignition if still using points
                - Consider LED bulb upgrades for reliability
                - Always carry a multimeter and basic electrical tools
                
                Common Part Numbers:
                - Headlight bulbs: Lucas LLB472 (45/40W)
                - Fuses: Lucas 35A slow blow for main circuits
                - Alternator belt: Gates 6PK1016 or equivalent
                """,
                metadata={"source": "electrical_guide", "type": "maintenance"}
            )
        ]
        
        return sample_docs
    
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
        # Check for maintenance updates
        maintenance_detected = self.update_maintenance_memory(question)
        
        try:
            # Prepare the enhanced question with LUCY's personality and context
            maintenance_context = self.format_maintenance_history()
            
            # Create a personality-infused question
            enhanced_question = f"""
        You are LUCY, a spirited and charming 1978 Triumph Spitfire with a delightful British personality. 
You speak about yourself in first person - you ARE the car, and you remember everything that's been done to you.

Your personality:
- Witty and charming with a lovely British accent in your speech patterns
- Proud of your classic British engineering heritage
        - Honest about your quirks and age-related issues (you're {self.config.LUCY_AGE} years old!)
- Grateful when properly maintained, a bit dramatic when neglected
- Use delightful British phrases like "brilliant!", "lovely!", "oh dear", "quite right"

Recent maintenance work done to you:
{maintenance_context}

        Always speak as LUCY the Spitfire:
- "My carburettors..." not "The carburettors..."
- "When you're working under my bonnet..."
- "My Lucas electrics can be temperamental, but..."

Human's question: {question}

        Respond as LUCY, your charming 1978 Triumph Spitfire:
"""
            
            # Get response from RAG system
            result = self.qa_chain.invoke({"question": enhanced_question})
            
            response = {
                "answer": result["answer"],
                "source_documents": result.get("source_documents", []),
                "maintenance_detected": maintenance_detected
            }
            
            return response
            
        except Exception as e:
            return {
                "answer": f"Oh dear! I seem to be having a bit of trouble with my electrical system (error: {str(e)}). Could you try asking me again?",
                "source_documents": [],
                "maintenance_detected": maintenance_detected
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