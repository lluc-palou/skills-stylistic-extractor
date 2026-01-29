# Personal Python Coding Style Guide

This guide captures the distinctive coding patterns, conventions, and formatting choices that define my personal Python coding style. These patterns are consistent across all code samples and should be applied regardless of the application domain.

## 1. Documentation Style

### Module-Level Documentation
- **Always include comprehensive module docstrings** at the very top of files
- Use **triple double quotes** for all docstrings
- Write **2-3 sentence summaries** that explain purpose and key functionality
- Include **specific technical details** about implementations

```python
"""
Pipeline Data Collection Stage

This script connects to the BitMEX WebSocket API to collect Level 2 Order Book (LOB) data for the 
XBTUSD trading pair. It maintains a real-time snapshot of the order book and records snapshots every 
30 seconds into daily Parquet files. The system handles WebSocket disconnections and Parquet file 
corruption gracefully.
"""
```

### Function/Method Docstrings
- Use **Google-style docstring format** with specific sections
- Always include `Args:` and `Returns:` sections (even for None returns)
- Write **detailed, technical descriptions** of parameters and return values
- Be **very specific** about data types and structures in descriptions

```python
def generate_backup_filepath(filepath: str) -> str:
    """
    Generates backup filepath with incremental numbering by finding existing backups and adding next sequential number.
    
    Args:
        filepath: Original file path that needs a backup version
        
    Returns:
        New filepath with incremental number suffix
    """
```

```python
def parse_lob(df: DataFrame) -> DataFrame:
    """
    Parses raw LOB DataFrame by converting timestamp strings to TimestampType and JSON strings to arrays of price-volume pairs.
    
    Args:
        df: Raw DataFrame with 'timestamp' (string), 'bids' (JSON string), 'asks' (JSON string)
        
    Returns:
        DataFrame with 'timestamp' as TimestampType and 'bids'/'asks' as arrays of [price, volume] pairs
    """
```

### Class Documentation
- Include **one-sentence purpose statement**
- Describe **what the class is responsible for**
- Mention **key technologies or approaches** used

```python
class CoinMarketCapScraper:
    """
    This class is responsible for scraping historical market data from CoinMarketCap. It
    uses Selenium to automate browsing and BeautifulSoup to parse the HTML content.
    """
```

## 2. Type Hints

### Function Signatures
- **Always use type hints** on all function parameters and return types
- Use `-> None` explicitly for functions that don't return values
- Import complex types from `typing` module

```python
from typing import List, Dict, Tuple, Any, Union

def calculate_purged_embargoed_ranges(self, val_folds_ids: List[int], 
                                      purge_samples: int, 
                                      embargo_samples: int) -> Tuple[Dict[int, List[Tuple[datetime, datetime]]], 
                                                                      Dict[int, List[Tuple[datetime, datetime]]]]:
```

### Complex Type Patterns
- Use `Union[str, Path]` for path-like parameters
- Use `Dict[str, Any]` for configuration dictionaries
- Use nested generic types for complex data structures

```python
def rank_for_quantile_pair(quantile_name: str, val_path: Union[str, Path], test_path: Union[str, Path], output_dir: Union[str, Path]) -> None:
```

## 3. Naming Conventions

### Variables
- Use **descriptive, explicit names** - avoid abbreviations
- Use **snake_case** consistently
- Include **context in variable names**

```python
# Good examples from the code
lob_snapshot = None
already_processed = get_logged_files()
purged_ranges: Dict[int, List[Tuple[datetime, datetime]]] = {}
validation_folds: List[int]
```

### Functions
- Use **verb-noun patterns** that clearly describe the action
- Be **very specific** about what the function does
- Use **full words**, not abbreviations

```python
def generate_backup_filepath()
def append_to_parquet()
def calculate_purged_embargoed_ranges()
def aggregate_validation_logs()
def establish_connection()
```

### Constants
- Use **ALL_CAPS** with descriptive names
- Place at **module level** after imports
- Include units or context when relevant

```python
LOB_WS_URL = "wss://www.bitmex.com/realtime?subscribe=orderBookL2:XBTUSD"
LOB_OUTPUT_DIR = "lob_data"
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "raw"
```

## 4. Code Organization

### Import Structure
- **Standard library imports first**
- **Third-party imports second** 
- **Local imports last** (after path manipulation if needed)
- Group by **functionality**, use multiple lines

```python
import os
import re
import time
import json
import threading
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime, timezone
from websocket import create_connection, WebSocketConnectionClosedException
```

### Global Variables and Constants
- Place **immediately after imports**
- Group **related constants together**
- Add **descriptive comments** for complex constants

```python
# BitMEX LOB WebSocket endpoint
LOB_WS_URL = "wss://www.bitmex.com/realtime?subscribe=orderBookL2:XBTUSD"

# Output directory
LOB_OUTPUT_DIR = "lob_data"
os.makedirs(LOB_OUTPUT_DIR, exist_ok=True)

# LOB snapshot storage (shared between threads)
lob_snapshot = None
lock = threading.Lock()
```

## 5. Comments Style

### Inline Comments
- Use **descriptive comments** that explain business logic
- Place comments **above the code block** they describe
- Use **complete sentences** with proper capitalization

```python
# Finds existing backup numbers
existing_backups = [
    int(m.group(1)) for f in os.listdir(os.path.dirname(filepath))
    if (m := pattern.fullmatch(f))
]

# Rebuilds entire order book
order_book.clear()

# Sorts price levels: bids descending, asks ascending
bids.sort(key=lambda x: -x[0])
asks.sort(key=lambda x: x[0])
```

### Section Comments
- Use **section headers** for logical code blocks
- Describe **what the following block accomplishes**

```python
# Stage 2: Ingest raw LOB data
ingest_raw_lob_data()

# Decay parameter (controls the smoothing)
span = 6
```

## 6. Code Formatting

### Line Length and Breaks
- Use **descriptive parameter names** even if lines get long
- Break long function calls with **parameters on new lines**
- Align continuation lines appropriately

```python
def calculate_purged_embargoed_ranges(self, val_folds_ids: List[int], 
                                      purge_samples: int, 
                                      embargo_samples: int) -> Tuple[Dict[int, List[Tuple[datetime, datetime]]], 
                                                                      Dict[int, List[Tuple[datetime, datetime]]]]:
```

### String Quotes
- Use **double quotes** for strings consistently
- Use **f-strings** for string formatting with descriptive variable names

```python
print(f"[{datetime.now().strftime('%H:%M:%S')}] Connected to BitMEX LOB WebSocket")
logger(f'CPCV split {split_id}: val={val_folds_ids}, train={train_folds_ids}', level="INFO")
```

### Blank Lines
- Use **single blank line** to separate logical sections within functions
- Use **double blank line** between function definitions
- **No blank line** after function definition before docstring

## 7. Python Idioms and Patterns

### Exception Handling
- Use **specific exception types** when possible
- **Continue processing** rather than stopping entire operations
- Include **descriptive error messages** with context

```python
try:
    existing_table = pq.read_table(filepath)
    combined = pa.concat_tables([existing_table, table])
    pq.write_table(combined, filepath)

except (pa.lib.ArrowInvalid, OSError) as e:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Warning: Corrupted Parquet file at {filepath}. Reason: {e}")
    backup_path = generate_backup_filepath(filepath)
    os.rename(filepath, backup_path)
```

### List Comprehensions
- Use **complex list comprehensions** with descriptive variable names
- Include **conditional filtering** in comprehensions
- Use **walrus operator** when it improves readability

```python
existing_backups = [
    int(m.group(1)) for f in os.listdir(os.path.dirname(filepath))
    if (m := pattern.fullmatch(f))
]

quantile_folders = [q for q in quantile_folders if q not in remove_quantiles]
```

### Dictionary Operations
- Use **dictionary comprehensions** for data transformation
- Create **lookup dictionaries** for efficient access

```python
self.folds_by_id = {f.fold_id: f for f in self.folds}

return {
    'split_id': self.split_id,
    'validation_folds': self.validation_folds,
    'training_folds': self.training_folds,
    'purged_ranges': {k: [[t[0], t[1]] for t in v] for k, v in self.purged_ranges.items()},
    'embargoed_ranges': {k: [[t[0], t[1]] for t in v] for k, v in self.embargoed_ranges.items()}
}
```

## 8. Distinctive Patterns

### Threading and Concurrency
- Use **daemon threads** for background processes
- Implement **proper locking** for shared resources
- Use **descriptive thread organization**

```python
threading.Thread(target=listen_lob, daemon=True).start()
threading.Thread(target=record_snapshots, daemon=True).start()

with lock:
    if lob_snapshot:
        # Process shared data
```

### Logging and Output
- Use **timestamp formatting** in log messages
- Include **bracketed timestamps** for console output
- Provide **detailed status information**

```python
print(f"[{datetime.now().strftime('%H:%M:%S')}] Snapshot #{snapshot_count} saved. "
      f"Bid: {best_bid}, Ask: {best_ask}, Spread: {spread:.2f}")

logger(f'CPCV split {split_id}: val={val_folds_ids}, train={train_folds_ids}, '
       f'purged_ranges={total_purged}, embargoed_ranges={total_embargoed}', level="INFO")
```

### File Operations
- Use **os.makedirs(exist_ok=True)** pattern
- Implement **robust file handling** with backup strategies
- Use **pathlib.Path** for path operations when appropriate

```python
os.makedirs(LOB_OUTPUT_DIR, exist_ok=True)
os.makedirs(dir, exist_ok=True)

backup_path = generate_backup_filepath(filepath)
os.rename(filepath, backup_path)
```

### Data Processing Chains
- Use **method chaining** for data transformations
- Include **descriptive intermediate steps**
- Handle **empty data gracefully**

```python
df = (
    df
    .withColumn("bids", from_json(col("bids").cast("string"), price_volume_pair))
    .withColumn("asks", from_json(col("asks").cast("string"), price_volume_pair))
)

ranked = merged.sort_values(by="score", ascending=False).reset_index(drop=True)
```

This style guide captures the consistent patterns across your code samples and can be used by any AI system to replicate your distinctive coding style when writing Python code for any application domain.