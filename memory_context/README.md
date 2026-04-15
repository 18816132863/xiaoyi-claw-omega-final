# Memory Context Module - L2 Layer

## Overview

This module provides memory context, knowledge base, and vector storage capabilities for the OpenClaw system.

## Structure

```
memory_context/
├── __init__.py          # Module entry
├── README.md            # This file
├── index/               # Index management
├── vector/              # Vector storage
├── data/                # Memory data
└── unified_search.py    # Unified search interface
```

## Components

### Index Management
- Memory indexing
- Fast retrieval

### Vector Storage
- 4096-dimension embeddings
- Similarity search

### Data Storage
- Session memory
- Long-term memory

## Usage

```python
from memory_context import UnifiedSearch

search = UnifiedSearch()
results = search.query("example query")
```
