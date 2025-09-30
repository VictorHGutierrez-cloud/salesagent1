"""
🧠 SALES AGENT IA - SISTEMA DE EMBEDDINGS
========================================
Converte o AE_SENIOR_TOOLKIT em base de conhecimento inteligente
"""

import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass

import chromadb
from sentence_transformers import SentenceTransformer
import pandas as pd
from rich.console import Console
from rich.progress import track
from loguru import logger

from config import Config

console = Console()

@dataclass
class KnowledgeChunk:
    """Representa um pedaço de conhecimento"""
    content: str
    source_file: str
    category: str
    keywords: List[str]
    importance: int  # 1-10

class SalesKnowledgeEmbedder:
    """Sistema de embeddings para base de conhecimento de vendas"""
    
    def __init__(self):
        Config.create_directories()
        
        # Inicializa modelo de embeddings
        self.model = SentenceTransformer(Config.EMBEDDING_MODEL)
        
        # Inicializa ChromaDB
        self.client = chromadb.PersistentClient(path=str(Config.EMBEDDINGS_DIR))
        self.collection = self.client.get_or_create_collection(
            name="sales_knowledge",
            metadata={"description": "AE Senior Toolkit Knowledge Base"}
        )
        
        logger.info("✅ Sistema de embeddings inicializado")
    
    def extract_chunks_from_file(self, file_path: Path) -> List[KnowledgeChunk]:
        """Extrai chunks relevantes de um arquivo do toolkit"""
        chunks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determina categoria baseada no diretório
            category = self._get_category_from_path(file_path)
            
            # Divide em seções lógicas
            sections = self._split_into_sections(content)
            
            for section in sections:
                if len(section.strip()) > 50:  # Ignora seções muito pequenas
                    chunk = KnowledgeChunk(
                        content=section.strip(),
                        source_file=str(file_path.relative_to(Config.BASE_DIR)),
                        category=category,
                        keywords=self._extract_keywords(section),
                        importance=self._calculate_importance(section, category)
                    )
                    chunks.append(chunk)
                    
        except Exception as e:
            logger.error(f"❌ Erro ao processar {file_path}: {e}")
            
        return chunks
    
    def _get_category_from_path(self, file_path: Path) -> str:
        """Determina categoria baseada no caminho do arquivo"""
        path_parts = file_path.parts
        
        category_map = {
            "01_PROSPECCAO_AVANCADA": "prospecting",
            "02_QUALIFICACAO_LEADS": "qualification", 
            "03_DISCOVERY_COMPLETO": "discovery",
            "04_DEMO_PERSONALIZADA": "demo",
            "05_PROPOSTA_COMERCIAL": "proposal",
            "06_NEGOCIACAO_FECHAMENTO": "closing",
            "07_ANALISE_COMPETITIVA": "competitive",
            "08_ROI_BUSINESS_CASE": "roi",
            "09_PLAYBOOKS_VERTICAIS": "industry",
            "10_CRM_AUTOMACAO": "automation",
            "11_FOLLOW_UP_SEQUENCES": "follow_up",
            "12_OBJECTION_HANDLING": "objections",
            "13_RECURSOS_EXECUTIVOS": "executive",
            "14_POS_VENDA_EXPANSION": "expansion"
        }
        
        for part in path_parts:
            if part in category_map:
                return category_map[part]
                
        return "general"
    
    def _split_into_sections(self, content: str) -> List[str]:
        """Divide conteúdo em seções lógicas"""
        sections = []
        
        # Divisores comuns no toolkit
        dividers = ['===', '---', '###', '##', '🎯', '💡', '⚡', '🔥']
        
        current_section = ""
        lines = content.split('\n')
        
        for line in lines:
            # Verifica se é uma nova seção
            is_new_section = any(div in line for div in dividers)
            
            if is_new_section and len(current_section.strip()) > 100:
                sections.append(current_section.strip())
                current_section = line + '\n'
            else:
                current_section += line + '\n'
        
        # Adiciona última seção
        if len(current_section.strip()) > 100:
            sections.append(current_section.strip())
            
        # Se não encontrou divisores, divide por paragrafos
        if len(sections) < 2:
            paragraphs = content.split('\n\n')
            sections = [p.strip() for p in paragraphs if len(p.strip()) > 100]
            
        return sections
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrai palavras-chave importantes do texto"""
        # Palavras-chave específicas de vendas
        sales_keywords = [
            'objeção', 'fechamento', 'prospect', 'lead', 'discovery', 'demo',
            'proposta', 'negociação', 'roi', 'valor', 'benefício', 'dor',
            'necessidade', 'orçamento', 'autoridade', 'decisor', 'urgência',
            'competição', 'diferencial', 'case', 'referência', 'follow-up'
        ]
        
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in sales_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
                
        return found_keywords[:5]  # Máximo 5 keywords
    
    def _calculate_importance(self, text: str, category: str) -> int:
        """Calcula importância do chunk (1-10)"""
        importance = 5  # Base
        
        # Aumenta importância por categoria estratégica
        strategic_categories = ['qualification', 'discovery', 'closing', 'objections']
        if category in strategic_categories:
            importance += 2
            
        # Aumenta por palavras-chave de alta importância
        high_value_words = ['fechamento', 'objeção', 'decisor', 'orçamento', 'roi']
        for word in high_value_words:
            if word in text.lower():
                importance += 1
                
        # Aumenta por estrutura (listas, frameworks)
        if any(char in text for char in ['1.', '2.', '•', '-', '✓']):
            importance += 1
            
        return min(importance, 10)
    
    def build_knowledge_base(self) -> Dict:
        """Constrói base de conhecimento completa"""
        console.print("🧠 [bold blue]Construindo base de conhecimento...[/bold blue]")
        
        all_chunks = []
        processed_files = 0
        
        # Processa todos os arquivos .txt do toolkit
        for txt_file in track(
            list(Config.TOOLKIT_DIR.rglob("*.txt")), 
            description="Processando arquivos..."
        ):
            chunks = self.extract_chunks_from_file(txt_file)
            all_chunks.extend(chunks)
            processed_files += 1
        
        console.print(f"📄 Processados: {processed_files} arquivos")
        console.print(f"🧩 Chunks extraídos: {len(all_chunks)}")
        
        # Cria embeddings
        console.print("🔄 [bold yellow]Gerando embeddings...[/bold yellow]")
        
        # Limpa collection anterior
        self.collection.delete()
        self.collection = self.client.get_or_create_collection(
            name="sales_knowledge",
            metadata={"description": "AE Senior Toolkit Knowledge Base"}
        )
        
        # Processa em batches
        batch_size = 100
        for i in track(range(0, len(all_chunks), batch_size), description="Embedding..."):
            batch = all_chunks[i:i+batch_size]
            
            # Prepara dados para ChromaDB
            documents = [chunk.content for chunk in batch]
            metadatas = [
                {
                    "source_file": chunk.source_file,
                    "category": chunk.category,
                    "keywords": ",".join(chunk.keywords),
                    "importance": chunk.importance
                }
                for chunk in batch
            ]
            ids = [f"chunk_{i+j}" for j in range(len(batch))]
            
            # Adiciona ao ChromaDB
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        
        # Salva estatísticas
        stats = {
            "total_chunks": len(all_chunks),
            "files_processed": processed_files,
            "categories": list(set(chunk.category for chunk in all_chunks)),
            "avg_importance": sum(chunk.importance for chunk in all_chunks) / len(all_chunks)
        }
        
        with open(Config.EMBEDDINGS_DIR / "stats.json", 'w') as f:
            json.dump(stats, f, indent=2)
            
        console.print(f"✅ [bold green]Base de conhecimento construída![/bold green]")
        console.print(f"📊 Estatísticas salvas em: {Config.EMBEDDINGS_DIR / 'stats.json'}")
        
        return stats
    
    def search_knowledge(self, query: str, top_k: int = 3) -> List[Dict]:
        """Busca conhecimento relevante para uma query"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            formatted_results = []
            for i, doc in enumerate(results['documents'][0]):
                result = {
                    "content": doc,
                    "source": results['metadatas'][0][i]['source_file'],
                    "category": results['metadatas'][0][i]['category'],
                    "keywords": results['metadatas'][0][i]['keywords'].split(','),
                    "importance": results['metadatas'][0][i]['importance'],
                    "similarity": 1 - results['distances'][0][i]  # Convert distance to similarity
                }
                formatted_results.append(result)
                
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Erro na busca: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas da base de conhecimento"""
        try:
            with open(Config.EMBEDDINGS_DIR / "stats.json", 'r') as f:
                return json.load(f)
        except:
            return {"error": "Estatísticas não encontradas. Execute build_knowledge_base() primeiro."}

def main():
    """Função principal para construir a base de conhecimento"""
    embedder = SalesKnowledgeEmbedder()
    
    # Constrói base de conhecimento
    stats = embedder.build_knowledge_base()
    
    # Teste rápido
    console.print("\n🧪 [bold cyan]Teste rápido:[/bold cyan]")
    test_query = "como lidar com objeção de preço"
    results = embedder.search_knowledge(test_query)
    
    console.print(f"Query: '{test_query}'")
    for i, result in enumerate(results, 1):
        console.print(f"  {i}. [{result['category']}] {result['source']}")
        console.print(f"     Relevância: {result['similarity']:.2f}")
        console.print(f"     Preview: {result['content'][:100]}...")
        console.print()

if __name__ == "__main__":
    main()
