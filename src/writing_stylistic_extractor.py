"""
Utility functions for the writing stylistic extractor.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

import anthropic
from dotenv import load_dotenv

# Loads environment variables from a .env file
load_dotenv()

class WritingStylisticExtractorUtils:
    """
    A utility class for handling file operations and API interactions for writing style extraction.
    """
    
    def __init__(self, writing_repository_path: str, output_file_path: str) -> None:
        """
        Initializes the writing stylistic extractor utility.
        
        Args:
            writing_repository_path: Path to the writing samples repository to analyze
            output_file_path: Path where the style guide will be saved
        """
        self.repo_path = Path(writing_repository_path)
        self.output_file = output_file_path
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.conversation_history: List[Dict[str, str]] = []
        self.current_draft: Optional[str] = None

    def scan_repository(self, max_files: int = 20, extensions: List[str] = None) -> List[Path]:
        """
        Scans the writing samples repository and retrieves a list of files with specified extensions.
        
        Args:
            max_files: Maximum number of files to scan
            extensions: List of file extensions to look for
            
        Returns:
            List of Path objects for found writing sample files
        """
        if extensions is None:
            extensions = [".md", ".txt"]
            
        writing_files = []

        for ext in extensions:
            for filepath in self.repo_path.rglob(f'*{ext}'):
                writing_files.append(filepath)

                if len(writing_files) >= max_files:
                    break
        
        print(f"\nFound {len(writing_files)} writing sample files in the repository.")
        return writing_files
    
    def read_files(self, filepaths: List[Path]) -> List[Dict[str, any]]:
        """
        Reads the content of the provided list of file paths.
        
        Args:
            filepaths: List of Path objects to read
            
        Returns:
            List of dictionaries containing file path, content, and word count
        """
        samples = []
        total_words = 0

        for filepath in filepaths:
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    words = len(content.split())
                    total_words += words
                    samples.append({
                        "path": str(filepath.relative_to(self.repo_path)),
                        "content": content,
                        "words": words
                    })

                    print(f"Read {words} words from {filepath.name}")

            except Exception as e:
                print(f"Error reading {filepath.name}: {e}")
        
        print(f"\nTotal: {total_words:,} words read from {len(samples)} files.")
        return samples
    
    def extraction(self, writing_samples: List[Dict[str, any]]) -> str:
        """
        Performs the initial writing stylistic extraction from the writing samples.
        
        Args:
            writing_samples: List of dictionaries containing file information
            
        Returns:
            Generated writing style guide as a string
        """
        # Prepares writing samples for LLM processing
        combined_writing = "\n\n".join([
            f"### Sample: {sample['path']}\n\n{sample['content']}"
            for sample in writing_samples
        ])

        # Writing stylistic extraction prompt declaration
        prompt = f"""I want you to analyze these writing samples and create a comprehensive writing style guide.

IMPORTANT: These texts are SAMPLES of my personal writing style. The specific subject matter is NOT part of my writing style. Focus ONLY on the writing patterns, conventions, and stylistic choices that are consistent across all samples, regardless of what the content is about.

Your task is to:

1. **Identify patterns and conventions** that appear consistently across all writing samples
2. **Create a detailed markdown style guide** that captures my personal and distinctive writing style
3. **Include specific examples** from my actual writing showing the STYLE, not the subject matter
4. **Make it prescriptive** so another AI could replicate my style exactly when writing about ANY topic

Analyze these aspects:

**Sentence Structure:**
- Sentence length patterns (short, medium, long, varied)
- Complexity (simple, compound, complex sentences)
- Use of subordinate clauses
- Parallel structure usage

**Paragraph Organization:**
- Paragraph length preferences
- Topic sentence patterns
- How ideas are developed within paragraphs
- Transition patterns between paragraphs

**Vocabulary and Word Choice:**
- Formality level (academic, professional, casual)
- Technical vs. accessible language balance
- Specific vs. general terminology
- Active vs. passive voice preference

**Tone and Voice:**
- Academic, professional, conversational, authoritative
- First person, third person usage
- Objectivity vs. subjectivity
- Hedging language patterns (may, might, could, possibly)

**Punctuation Patterns:**
- Comma usage patterns
- Semicolon and colon usage
- Em dash, parentheses usage
- List formatting (numbered, bulleted)

**Rhetorical Devices:**
- Use of questions
- Use of examples and analogies
- Enumeration patterns (firstly, secondly, etc.)
- Emphasis techniques (italics, bold, quotation marks)

**Academic/Technical Writing Patterns:**
- Citation style (if present)
- How definitions are introduced
- How concepts are explained
- Use of technical jargon
- Abbreviation patterns

**Text Organization:**
- How sections are structured
- Use of headers and subheaders
- Introduction and conclusion patterns
- How arguments are built

**Distinctive Patterns:**
- Any unique or characteristic phrases
- Preferred sentence openers
- Preferred ways to introduce new concepts
- Preferred ways to conclude ideas
- Use of specific connectors (however, therefore, furthermore)

REMEMBER: Extract only the WRITING STYLE patterns that are consistent across samples. Do NOT include subject-specific conventions. Focus on HOW I write, not WHAT I write about.

Here are my writing samples:

{combined_writing}

Create a markdown document with clear sections, examples showing STYLE patterns, and actionable rules.
Format it as a professional writing style guide that could be given to a writing assistant for producing ANY type of text in my style."""

        # Calls LLM API to generate a writing stylistic draft
        print("\nAnalyzing writing samples with Claude Sonnet 4.5...")
        
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
        print(f"\nWriting stylistic draft generated")
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
    WRITING_SAMPLES_DIR = "writing_samples"
    SKILL_SET_DIR = "skill_set"
    OUTPUT_FILE = os.path.join(SKILL_SET_DIR, "writing_stylistic_guide.md")

    print("="*70)
    print("Writing Style Extractor")
    print("="*70)

    # Creates skill_set directory if it doesn't exist
    os.makedirs(SKILL_SET_DIR, exist_ok=True)

    # Validates the writing samples directory path
    if not Path(WRITING_SAMPLES_DIR).exists():
        print(f"\nError: Writing samples directory does not exist: {WRITING_SAMPLES_DIR}")
        return
    
    if not Path(WRITING_SAMPLES_DIR).is_dir():
        print(f"\nError: Not a directory: {WRITING_SAMPLES_DIR}")
        return

    # Initializes the utility class
    extractor_utils = WritingStylisticExtractorUtils(
        writing_repository_path=WRITING_SAMPLES_DIR,
        output_file_path=OUTPUT_FILE
    )

    # Step 1: Scans repository for writing sample files
    writing_files = extractor_utils.scan_repository(
        max_files=MAX_FILES,
        extensions=[".md", ".txt"]
    )

    if not writing_files:
        print("\nNo writing sample files of the specified format found in the repository.")
        return
    
    # Step 2: Reads writing sample files
    writing_samples = extractor_utils.read_files(writing_files)

    if not writing_samples:
        print("\nNo writing samples could be read from the files.")
        return
    
    # Step 3: Performs the writing stylistic extraction
    draft = extractor_utils.extraction(writing_samples)

    # Step 4: Saves the draft
    extractor_utils.save_draft()

    print(f"\nWriting stylistic extraction complete")
    
if __name__ == "__main__":
    main()