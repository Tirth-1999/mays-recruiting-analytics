"""
Vector store for schema embeddings using ChromaDB
"""

import os
import tempfile
from typing import List, Dict, Optional

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("⚠️ chromadb not installed. Run: pip install chromadb")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️ sentence-transformers not installed. Run: pip install sentence-transformers")


class VectorStore:
    """Manages vector embeddings for schema and platform knowledge."""
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize vector store.
        
        Args:
            persist_directory: Directory to persist ChromaDB data (defaults to temp dir for Streamlit Cloud)
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("chromadb package not installed")
        
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers package not installed")
        
        # Use temp directory for Streamlit Cloud compatibility
        if persist_directory is None:
            # Try to use a writable directory
            if os.path.exists("/tmp") and os.access("/tmp", os.W_OK):
                persist_directory = "/tmp/chromadb"
            else:
                persist_directory = os.path.join(tempfile.gettempdir(), "chromadb")
        
        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        print(f"📁 ChromaDB persist directory: {persist_directory}")
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize embedding model (lightweight and fast)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collections with corruption handling
        try:
            self.schema_collection = self.client.get_or_create_collection(
                name="schema_collection",
                metadata={"description": "Database schema embeddings"}
            )
        except KeyError as e:
            # ChromaDB collection is corrupted, delete and recreate
            print(f"⚠️ ChromaDB schema collection corrupted, recreating: {e}")
            try:
                self.client.delete_collection("schema_collection")
            except Exception:
                pass
            self.schema_collection = self.client.create_collection(
                name="schema_collection",
                metadata={"description": "Database schema embeddings"}
            )
        
        try:
            self.platform_collection = self.client.get_or_create_collection(
                name="platform_collection",
                metadata={"description": "Platform knowledge embeddings"}
            )
        except KeyError as e:
            # ChromaDB collection is corrupted, delete and recreate
            print(f"⚠️ ChromaDB platform collection corrupted, recreating: {e}")
            try:
                self.client.delete_collection("platform_collection")
            except Exception:
                pass
            self.platform_collection = self.client.create_collection(
                name="platform_collection",
                metadata={"description": "Platform knowledge embeddings"}
            )
        
        # Auto-initialize if collections are empty
        try:
            if self.schema_collection.count() == 0:
                self.initialize_schema_embeddings()
            
            if self.platform_collection.count() == 0:
                self.initialize_platform_embeddings()
        except Exception as e:
            print(f"Warning: Error initializing embeddings: {e}")
    
    def add_schema_embedding(
        self,
        doc_id: str,
        text: str,
        metadata: Dict
    ):
        """
        Add schema embedding to collection.
        
        Args:
            doc_id: Unique document ID
            text: Text to embed
            metadata: Metadata dict
        """
        embedding = self.embedding_model.encode(text).tolist()
        
        self.schema_collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata]
        )
    
    def add_platform_embedding(
        self,
        doc_id: str,
        text: str,
        metadata: Dict
    ):
        """
        Add platform knowledge embedding to collection.
        
        Args:
            doc_id: Unique document ID
            text: Text to embed
            metadata: Metadata dict
        """
        embedding = self.embedding_model.encode(text).tolist()
        
        self.platform_collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata]
        )
    
    def search_schema(
        self,
        query: str,
        n_results: int = 3
    ) -> List[Dict]:
        """
        Search schema collection for relevant context.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of result dicts
        """
        query_embedding = self.embedding_model.encode(query).tolist()
        
        results = self.schema_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def search_platform(
        self,
        query: str,
        n_results: int = 2
    ) -> List[Dict]:
        """
        Search platform knowledge for relevant pages.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of result dicts
        """
        query_embedding = self.embedding_model.encode(query).tolist()
        
        results = self.platform_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
        
        return formatted_results
    
    def initialize_schema_embeddings(self):
        """Initialize schema embeddings for the database."""
        # Check if already initialized
        count = self.schema_collection.count()
        if count > 0:
            return  # Silently skip if already initialized
        
        # Define enhanced schema documents with column details and relationships
        schema_docs = [
            {
                'id': 'admissions_metrics_table',
                'text': 'Table: admissions_metrics. Contains core admissions funnel metrics including inquiries_received, total_applications, applications_received, admits, enrolled, deposits, confirmed for each program and cohort year. Columns: program (TEXT, e.g., MBA, MS ACCT), cohort_year (INTEGER, e.g., 2024, 2025), metric_name (TEXT, lowercase with underscores), metric_value (REAL, count), report_date (TEXT, YYYY-MM-DD format). Use for: enrollment data, application counts, conversion analysis. Sample values: metric_name can be inquiries_received, total_applications, enrolled.',
                'metadata': {'type': 'table', 'name': 'admissions_metrics', 'primary_use': 'enrollment_data'}
            },
            {
                'id': 'marketing_spend_table',
                'text': 'Table: marketing_spend. Contains marketing channel spend data by program and month. Columns: program (TEXT, matches admissions_metrics.program), channel (TEXT, e.g., Google Ads, Facebook, LinkedIn, Email), amount (REAL, USD), spend_date (TEXT, YYYY-MM-DD), fiscal_year (TEXT, e.g., FY25). Use for: marketing ROI, cost per inquiry/application, channel effectiveness. Can JOIN with admissions_metrics on program to calculate cost per enrollment.',
                'metadata': {'type': 'table', 'name': 'marketing_spend', 'primary_use': 'marketing_roi'}
            },
            {
                'id': 'programs_table',
                'text': 'Table: programs. Contains list of active programs. Columns: program_code (TEXT, e.g., MBA, MS ACCT), program_name (TEXT, full name), is_active (INTEGER, 1 or 0). Use for: program lookup, filtering active programs. Reference table for program codes.',
                'metadata': {'type': 'table', 'name': 'programs', 'primary_use': 'reference'}
            },
            {
                'id': 'model_predictions_table',
                'text': 'Table: model_predictions. Contains ML-generated forecasts for future metrics. Columns: program_code (TEXT), cohort_year (INTEGER, future years), metric_name (TEXT), predicted_value (REAL), confidence_lower (REAL), confidence_upper (REAL), prediction_date (DATE). Use for: forecasting, future planning, trend prediction.',
                'metadata': {'type': 'table', 'name': 'model_predictions', 'primary_use': 'forecasting'}
            },
            {
                'id': 'metric_inquiries',
                'text': 'Metric: inquiries_received. Initial interest from prospective students. Found in admissions_metrics table with metric_name = "inquiries_received". Top of funnel metric. Synonyms: inquiries, leads, prospects.',
                'metadata': {'type': 'metric', 'name': 'inquiries_received', 'funnel_stage': 'top'}
            },
            {
                'id': 'metric_applications',
                'text': 'Metric: total_applications. Formal applications submitted. Found in admissions_metrics table with metric_name = "total_applications". Mid-funnel metric. Synonyms: applications, apps, applicants. Use for conversion rate calculations.',
                'metadata': {'type': 'metric', 'name': 'total_applications', 'funnel_stage': 'mid'}
            },
            {
                'id': 'metric_enrolled',
                'text': 'Metric: enrolled. Students who enrolled in the program. Found in admissions_metrics table with metric_name = "enrolled". Bottom of funnel metric. Synonyms: enrollments, enrollment, enrolled students. Final conversion metric.',
                'metadata': {'type': 'metric', 'name': 'enrolled', 'funnel_stage': 'bottom'}
            },
            {
                'id': 'metric_admits',
                'text': 'Metric: admits. Students who were admitted to the program. Found in admissions_metrics table with metric_name = "admits". Mid-funnel metric between applications and enrollment.',
                'metadata': {'type': 'metric', 'name': 'admits', 'funnel_stage': 'mid'}
            },
            {
                'id': 'join_marketing_admissions',
                'text': 'JOIN relationship: marketing_spend and admissions_metrics can be joined on program column to calculate cost per inquiry, cost per application, cost per enrollment, and marketing ROI. Example: SELECT SUM(amount) / SUM(metric_value) FROM marketing_spend JOIN admissions_metrics ON marketing_spend.program = admissions_metrics.program WHERE metric_name = "enrolled"',
                'metadata': {'type': 'relationship', 'tables': 'marketing_spend, admissions_metrics', 'join_key': 'program'}
            },
            {
                'id': 'comparison_pattern',
                'text': 'Comparison queries: For year-over-year or program-to-program comparisons, use subqueries or UNION. Example for year comparison: SELECT cohort_year, SUM(metric_value) FROM admissions_metrics WHERE metric_name = "total_applications" GROUP BY cohort_year. For growth rate: ((new - old) / old) * 100.',
                'metadata': {'type': 'pattern', 'use_case': 'comparison'}
            },
            {
                'id': 'aggregation_pattern',
                'text': 'Aggregation queries: Use GROUP BY with SUM, AVG, COUNT, MIN, MAX. Example: SELECT program, AVG(metric_value) FROM admissions_metrics WHERE metric_name = "enrolled" GROUP BY program. Use HAVING to filter aggregated results.',
                'metadata': {'type': 'pattern', 'use_case': 'aggregation'}
            }
        ]
        
        # Add embeddings
        for doc in schema_docs:
            self.add_schema_embedding(doc['id'], doc['text'], doc['metadata'])
        
        print(f"✅ Initialized {len(schema_docs)} schema embeddings (enhanced with relationships and patterns)")
    
    def initialize_platform_embeddings(self):
        """Initialize platform knowledge embeddings."""
        # Check if already initialized
        count = self.platform_collection.count()
        if count > 0:
            return  # Silently skip if already initialized
        
        # Define platform documents with enhanced details
        platform_docs = [
            {
                'id': 'page_home',
                'text': 'Home Dashboard: High-level overview of all programs and key metrics. Best for quick snapshot, executive summary, overall trends. Filters: cohort year. Shows total inquiries, applications, admits, enrolled across all programs. Use when you need: overall performance, big picture view, all programs summary.',
                'metadata': {
                    'type': 'page',
                    'name': 'Home Dashboard',
                    'filters': 'cohort_year',
                    'metrics': 'inquiries, applications, admits, enrolled',
                    'use_cases': 'overview, summary, all programs'
                }
            },
            {
                'id': 'page_executive',
                'text': 'Executive Deep Dive: Detailed program-specific analysis with trends. Best for deep analysis of single program, trend identification, time-series analysis. Filters: program, cohort year, date range. Shows program-specific funnel, conversion rates, time-series trends, detailed metrics. Use when you need: single program analysis, trends over time, detailed metrics.',
                'metadata': {
                    'type': 'page',
                    'name': 'Executive Deep Dive',
                    'filters': 'program, cohort_year, date_range',
                    'metrics': 'funnel, conversion_rates, trends',
                    'use_cases': 'program_analysis, trends, deep_dive'
                }
            },
            {
                'id': 'page_comparison',
                'text': 'Comparison Tool: Year-over-year and program-to-program comparisons. Best for comparative analysis, identifying winners and losers, growth analysis. Filters: two cohorts or two programs. Shows percentage changes, variance, statistical comparisons, growth rates. Use when you need: compare years, compare programs, identify changes.',
                'metadata': {
                    'type': 'page',
                    'name': 'Comparison Tool',
                    'filters': 'cohort_comparison, program_comparison',
                    'metrics': 'percentage_change, variance, growth',
                    'use_cases': 'comparison, year_over_year, program_comparison'
                }
            },
            {
                'id': 'page_marketing',
                'text': 'Marketing Analysis: Marketing spend, channel performance, ROI analysis. Best for marketing effectiveness, budget allocation decisions, channel optimization. Filters: program, fiscal year, channel. Shows spend by channel, cost per inquiry/application, ROI, channel performance. Use when you need: marketing ROI, channel effectiveness, budget decisions.',
                'metadata': {
                    'type': 'page',
                    'name': 'Marketing Analysis',
                    'filters': 'program, fiscal_year, channel',
                    'metrics': 'spend, cost_per_inquiry, roi',
                    'use_cases': 'marketing, roi, channel_analysis'
                }
            },
            {
                'id': 'page_data_explorer',
                'text': 'Data Explorer: Raw data access with flexible filtering. Best for custom analysis, data export, detailed investigation, creating custom reports. Filters: all dimensions. Shows all available metrics in tabular format, exportable data. Use when you need: raw data, custom analysis, data export.',
                'metadata': {
                    'type': 'page',
                    'name': 'Data Explorer',
                    'filters': 'all',
                    'metrics': 'all',
                    'use_cases': 'data_export, custom_analysis, raw_data'
                }
            },
            {
                'id': 'page_predictive',
                'text': 'Predictive Analytics: ML-powered forecasting and predictions. Best for future planning, budget forecasting, trend prediction, enrollment projections. Filters: program, forecast horizon. Shows predicted inquiries/applications/enrollments with confidence intervals, future trends. Use when you need: forecasts, predictions, future planning.',
                'metadata': {
                    'type': 'page',
                    'name': 'Predictive Analytics',
                    'filters': 'program, forecast_horizon',
                    'metrics': 'predictions, confidence_intervals',
                    'use_cases': 'forecasting, predictions, future_planning'
                }
            },
            # Workflow templates
            {
                'id': 'workflow_program_report',
                'text': 'Workflow: Create program performance report. Steps: 1) Go to Executive Deep Dive page, 2) Select your program from dropdown, 3) Choose cohort year, 4) Review funnel metrics and conversion rates, 5) Check time-series trends, 6) Export data if needed. Best for: comprehensive program analysis.',
                'metadata': {
                    'type': 'workflow',
                    'name': 'Program Performance Report',
                    'pages': 'Executive Deep Dive, Data Explorer',
                    'keywords': 'report, program performance, analysis'
                }
            },
            {
                'id': 'workflow_marketing_roi',
                'text': 'Workflow: Analyze marketing ROI. Steps: 1) Go to Marketing Analysis page, 2) Select program, 3) Choose fiscal year, 4) Review spend by channel, 5) Check cost per inquiry and application, 6) Calculate ROI for each channel, 7) Identify best performing channels. Best for: marketing effectiveness analysis.',
                'metadata': {
                    'type': 'workflow',
                    'name': 'Marketing ROI Analysis',
                    'pages': 'Marketing Analysis',
                    'keywords': 'marketing, roi, effectiveness'
                }
            },
            {
                'id': 'workflow_year_comparison',
                'text': 'Workflow: Compare year-over-year performance. Steps: 1) Go to Comparison Tool page, 2) Select two cohort years to compare, 3) Choose metrics to analyze, 4) Review percentage changes, 5) Identify growth or decline areas, 6) Export comparison data. Best for: trend analysis and growth tracking.',
                'metadata': {
                    'type': 'workflow',
                    'name': 'Year-over-Year Comparison',
                    'pages': 'Comparison Tool',
                    'keywords': 'comparison, year over year, trends'
                }
            },
            {
                'id': 'workflow_forecast',
                'text': 'Workflow: Forecast future enrollments. Steps: 1) Go to Predictive Analytics page, 2) Select program, 3) Choose forecast horizon (months ahead), 4) Review predicted values with confidence intervals, 5) Compare with historical trends, 6) Use for budget planning. Best for: future planning and projections.',
                'metadata': {
                    'type': 'workflow',
                    'name': 'Enrollment Forecasting',
                    'pages': 'Predictive Analytics',
                    'keywords': 'forecast, prediction, future'
                }
            }
        ]
        
        # Add embeddings
        for doc in platform_docs:
            self.add_platform_embedding(doc['id'], doc['text'], doc['metadata'])
        
        print(f"✅ Initialized {len(platform_docs)} platform embeddings (6 pages + 4 workflows)")
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about collections."""
        return {
            'schema_count': self.schema_collection.count(),
            'platform_count': self.platform_collection.count()
        }


if __name__ == "__main__":
    # Test vector store
    print("Testing VectorStore...")
    
    store = VectorStore()
    
    # Initialize embeddings
    store.initialize_schema_embeddings()
    store.initialize_platform_embeddings()
    
    # Get stats
    stats = store.get_collection_stats()
    print(f"\n📊 Collection stats: {stats}")
    
    # Test schema search
    print("\n🔍 Testing schema search: 'How many applications?'")
    results = store.search_schema("How many applications?", n_results=2)
    for r in results:
        print(f"   - {r['id']}: {r['document'][:100]}...")
    
    # Test platform search
    print("\n🔍 Testing platform search: 'Where can I compare programs?'")
    results = store.search_platform("Where can I compare programs?", n_results=2)
    for r in results:
        print(f"   - {r['metadata']['name']}: {r['document'][:100]}...")
    
    print("\n✅ VectorStore tests complete")
