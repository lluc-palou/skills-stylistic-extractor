"""
Utility functions for the coding stylistic extractor.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

import anthropic
from dotenv import load_dotenv

# Loads environment variables from a .env file
load_dotenv()

class StylisticExtractorUtils:
    """
    A utility class for handling file operations and API interactions.
    """
    
    def __init__(self, code_repository_path: str, output_file_path: str) -> None:
        """
        Initializes the stylistic extractor utility.
        
        Args:
            code_repository_path: Path to the code repository to analyze
            output_file_path: Path where the style guide will be saved
        """
        self.repo_path = Path(code_repository_path)
        self.output_file = output_file_path
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.conversation_history: List[Dict[str, str]] = []
        self.current_draft: Optional[str] = None

    def scan_repository(self, max_files: int = 20, extensions: List[str] = None) -> List[Path]:
        """
        Scans the code repository and retrieves a list of code files with specified extensions.
        
        Args:
            max_files: Maximum number of files to scan
            extensions: List of file extensions to look for
            
        Returns:
            List of Path objects for found code files
        """
        if extensions is None:
            extensions = [".py"]
            
        code_files = []

        for ext in extensions:
            for filepath in self.repo_path.rglob(f'*{ext}'):
                code_files.append(filepath)

                if len(code_files) >= max_files:
                    break
        
        print(f"\nFound {len(code_files)} code files in the repository.")
        return code_files
    
    def read_files(self, filepaths: List[Path]) -> List[Dict[str, any]]:
        """
        Reads the content of the provided list of file paths.
        
        Args:
            filepaths: List of Path objects to read
            
        Returns:
            List of dictionaries containing file path, content, and line count
        """
        samples = []
        total_lines = 0

        for filepath in filepaths:
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    lines = len(content.splitlines())
                    total_lines += lines
                    samples.append({
                        "path": str(filepath.relative_to(self.repo_path)),
                        "content": content,
                        "lines": lines
                    })

                    print(f"Read {lines} lines from {filepath}")

            except Exception as e:
                print(f"Error reading {filepath.name}: {e}")
        
        print(f"\nTotal: {total_lines} lines of code read from {len(samples)} files.")
        return samples
    
    def extraction(self, code_samples: List[Dict[str, any]]) -> str:
        """
        Performs the initial stylistic extraction from the code samples.
        
        Args:
            code_samples: List of dictionaries containing file information
            
        Returns:
            Generated style guide as a string
        """
        # Prepares code for LLM processing
        combined_code = "\n\n".join([
            f"### File: {sample['path']}\n```python\n{sample['content']}\n```"
            for sample in code_samples
        ])

        # Coding stylistic extraction prompt declaration
        prompt = f"""I want you to analyze these Python files from a coding samples repository and create a comprehensive coding style guide.

IMPORTANT: These files are SAMPLES of my personal coding style. The specific application context is NOT part of my coding style. Focus ONLY on the coding patterns, conventions, and formatting choices that are consistent across all samples, regardless of what the code does.

Your task is to:

1. **Identify patterns and conventions** that appear consistently across all files
2. **Create a detailed markdown style guide** that captures my personal and distinctive coding style patterns
3. **Include specific snippet examples** from my actual code showing the STYLE, not the application logic
4. **Make it prescriptive** so another AI could replicate my style exactly when writing ANY type of Python code

Analyze these aspects:

**Documentation:**
- Docstring format (Google/NumPy/Sphinx style?)
- What sections do I include? (Args, Returns, etc.)
- Level of detail in docstrings
- Module-level documentation patterns
- How I describe parameters and return values

**Type Hints:**
- Where and when do I use type annotations?
- Always on function signatures? Sometimes on variables?
- Complex types (Union, Optional, List, Dict patterns)

**Naming Conventions:**
- Variable naming (length, descriptiveness, patterns)
- Function naming (verbs, patterns)
- Class naming
- Constants (if any)
- Private/protected members (underscore usage)

**Code Organization:**
- Import ordering and grouping
- Class structure (method ordering, organization)
- File structure patterns
- Global variables and constants placement

**Comments:**
- When do I add comments?
- Inline vs block comments
- Comment style and detail level
- What do I explain vs what do I leave uncommented?

**Code Style:**
- Line length preferences
- Indentation patterns
- Blank line usage
- String quotes (single vs double)

**Python Idioms:**
- List/dict comprehensions usage
- Use of decorators
- Context managers
- Generators and iterators
- Exception handling patterns

**Distinctive Patterns:**
- Any unique or characteristic patterns you notice
- Preferred libraries or approaches
- Code complexity preferences
- How I structure error handling
- Logging patterns

REMEMBER: Extract only the STYLE patterns that are consistent across samples. Do NOT include application-specific conventions. Focus on HOW I write code, not WHAT the code does.

Here are my Python code samples:

{combined_code}

Create a markdown document with clear sections, snippet examples showing STYLE patterns, and actionable rules.
Format it as a professional style guide that could be given to a coding agent for writing ANY Python code in my style."""

        # Calls LLM API to generate a coding stylistic draft
        print("\nAnalyzing code samples with Claude Sonnet 4.5...")
        
        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Stores the draft and updates the conversation history
        self.current_draft = message.content[0].text
        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": self.current_draft
        })

        # Displays statistics
        print(f"\nCoding stylistic draft generated")
        print(f"  Input tokens: {message.usage.input_tokens:,}")
        print(f"  Output tokens: {message.usage.output_tokens:,}")
        
        return self.current_draft
    
    def save_draft(self, content: str = None) -> None:
        """
        Saves the current draft to a file.
        
        Args:
            content: Content to save (defaults to self.current_draft)
        """
        if content is None:
            content = self.current_draft
            
        if content is None:
            print("No content to save!")
            return
            
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Saved draft to: {self.output_file}")
        except Exception as e:
            print(f"Error saving file: {e}")


def main() -> None:
    """
    Main execution function.
    """
    # Configuration
    MAX_FILES = 20
    CODE_SAMPLES_DIR = "code_samples"
    SKILL_SET_DIR = "skill_set"
    OUTPUT_FILE = os.path.join(SKILL_SET_DIR, "coding_stylistic_guide.md")

    print("="*70)
    print("Coding Style Extractor")
    print("="*70)

    # Creates skill_set directory if it doesn't exist
    os.makedirs(SKILL_SET_DIR, exist_ok=True)

    # Validates the code samples directory path
    if not Path(CODE_SAMPLES_DIR).exists():
        print(f"\nError: Code samples directory does not exist: {CODE_SAMPLES_DIR}")
        return
    
    if not Path(CODE_SAMPLES_DIR).is_dir():
        print(f"\nError: Not a directory: {CODE_SAMPLES_DIR}")
        return

    # Initializes the utility class
    extractor_utils = StylisticExtractorUtils(
        code_repository_path=CODE_SAMPLES_DIR,
        output_file_path=OUTPUT_FILE
    )

    # Step 1: Scans repository for code files
    code_files = extractor_utils.scan_repository(
        max_files=MAX_FILES,
        extensions=[".py"]
    )

    if not code_files:
        print("\nNo code files of the specified format found in the repository.")
        return
    
    # Step 2: Reads code files
    code_samples = extractor_utils.read_files(code_files)

    if not code_samples:
        print("\nNo code samples could be read from the files.")
        return
    
    # Step 3: Performs the coding stylistic extraction
    draft = extractor_utils.extraction(code_samples)

    # Step 4: Saves the draft
    extractor_utils.save_draft()

    print(f"\nCoding stylistic extraction complete")

if __name__ == "__main__":
    main()