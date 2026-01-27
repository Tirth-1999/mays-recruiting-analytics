# Design: SQLite to Supabase Migration

## Executive Summary

This document outlines the technical design for migrating all 8 Edulytix platform pages from SQLite to Supabase PostgreSQL, covering 15 database tables, 200+ SQL queries, 6 migration scripts, and 2 ETL pipelines.

**Key Design Decisions:**
1. **Dual Database Support** - Automatic fallback to SQLite for local development
2. **Zero Code Duplication** - Single connection layer for all pages
3. **Query Adapter Pattern** - Abstract database-specific syntax differences
4. **Phased Migration** - Test each page independently before full deployment
5. **Keep-Alive System** - GitHub Actions to prevent Supabase auto-pause

---

## Architecture

### Current Architecture (SQLite)

```
┌─────────────────────────────────────────────────────────────┐
│                    Edulytix Platform                        │
├─────────────────────────────────────────────────────────────┤
│  Home Dashboard  │  Executive  │  Comparison  │  Marketing  │
│  Predictive      │  Data Exp   │  AI Chat     │  Auth       │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
      ┌──────────────┐
      │ edulytix.db  │
      │  (SQLite)    │
      │  Local File  │
      └──────────────┘

Problem: Separate database files per environment
- Local: /Users/dev/Edulytix/edulytix.db
- Production: /app/edulytix.db (Streamlit Cloud container)
- Result: Completely isolated, data lost on rebuild
```

### Target Architecture (Supabase)

```
┌─────────────────────┐         ┌─────────────────────┐
│  Local Development  │         │  Production App     │
│  (All 8 Pages)      │         │  (Streamlit Cloud)  │
└──────────┬──────────┘         └──────────┬──────────┘
           │                               │
           │  ┌─────────────────────┐     │
           └──┤  Supabase Cloud     ├─────┘
              │  (PostgreSQL 15)    │
              │                     │
              │  Tables (15):       │
              │  - admissions_metrics
              │  - programs         │
              │  - marketing_spend  │
              │  - users            │
              │  - chat_history     │
              │  - model_predictions│
              │  - ... (9 more)     │
              └─────────────────────┘

Solution: Single shared database for all environments
- Persistent data across deployments
- Real-time user tracking
- Unified analytics
```

### Hybrid Architecture (Development Flexibility)

```
┌─────────────────────┐
│  Local Development  │
│  (Developer Choice) │
└──────────┬──────────┘
           │
           ├─────────────────┐
           │                 │
           ▼                 ▼
    ┌──────────────┐  ┌──────────────┐
    │ edulytix.db  │  │  Supabase    │
    │  (SQLite)    │  │ (PostgreSQL) │
    │  Default     │  │  Optional    │
    │  Offline     │  │  Online      │
    └──────────────┘  └──────────────┘

Flexibility: Choose database based on secrets configuration
- No SUPABASE_URL → SQLite (offline development)
- With SUPABASE_URL → PostgreSQL (test with production data)
```

---

## Component Design

### 1. Database Connection Layer

**File**: `utils/database.py`

**Current Implementation**:
```python
@st.cache_resource
def get_connection():
    return sqlite3.connect('edulytix.db', check_same_thread=False)
```

**New Implementation**:
```python
import sqlite3
import psycopg2
import streamlit as st
from contextlib import contextmanager
from typing import Union
import time

def get_connection() -> Union[sqlite3.Connection, psycopg2.extensions.connection]:
    """
    Get database connection with automatic fallback.
    
    Priority:
    1. Try Supabase PostgreSQL (if SUPABASE_URL in secrets)
    2. Fallback to SQLite (local development)
    
    Returns:
        Database connection object (PostgreSQL or SQLite)
    """
    try:
        if "SUPABASE_URL" in st.secrets:
            return psycopg2.connect(
                st.secrets["SUPABASE_URL"],
                sslmode='require',
                connect_timeout=10
            )
    except Exception as e:
        st.warning(f"⚠️ PostgreSQL unavailable, using SQLite: {e}")
    
    # Fallback to SQLite
    return sqlite3.connect('edulytix.db', check_same_thread=False)

@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Ensures proper commit/rollback and connection cleanup.
    
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            # Auto-commit on success, rollback on error
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_db_type() -> str:
    """
    Determine which database is being used.
    
    Returns:
        'postgresql' or 'sqlite'
    """
    try:
        if "SUPABASE_URL" in st.secrets:
            return 'postgresql'
    except:
        pass
    return 'sqlite'

def check_database_health() -> dict:
    """
    Check database connection and health.
    
    Returns:
        {
            'connected': bool,
            'database_type': str,
            'response_time_ms': int,
            'error': str or None
        }
    """
    health = {
        'connected': False,
        'database_type': None,
        'response_time_ms': None,
        'error': None
    }
    
    try:
        start_time = time.time()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        
        health['connected'] = True
        health['database_type'] = get_db_type()
        health['response_time_ms'] = int((time.time() - start_time) * 1000)
    except Exception as e:
        health['error'] = str(e)
    
    return health
```

**Design Decisions**:
- **Automatic Detection**: No manual configuration needed
- **Graceful Fallback**: Always works, even without Supabase
- **Context Manager**: Ensures proper resource cleanup
- **Type Hints**: Clear return types for IDE support
- **Error Handling**: Catches connection failures gracefully
- **Health Check**: Monitor database status

