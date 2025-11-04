"""
Codebase Tools for SWE-bench Agents

Provides tools for agents to interact with real codebases:
- Read files
- List files in directories
- Search for patterns in code
"""

from pathlib import Path
from typing import List, Dict, Optional
import re


class CodebaseTools:
    """
    Tools for agent to interact with a codebase.

    These tools are exposed to the agent as capabilities it can use
    during problem-solving. All file operations are relative to the
    repository root.
    """

    def __init__(self, repo_path: Path):
        """
        Initialize tools for a specific repository.

        Args:
            repo_path: Absolute path to cloned repository
        """
        self.repo_path = Path(repo_path)
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")

        self.files_read_count = 0
        self.files_read = []

    def read_file(self, path: str) -> str:
        """
        Read a file from the repository.

        Args:
            path: Relative path from repository root (e.g., "src/main.py")

        Returns:
            File contents as string, or error message if file not found
        """
        try:
            full_path = self.repo_path / path
            if not full_path.exists():
                return f"Error: File not found: {path}"

            if not full_path.is_file():
                return f"Error: {path} is not a file"

            # Security check: ensure path is within repo
            if not str(full_path.resolve()).startswith(str(self.repo_path.resolve())):
                return f"Error: Access denied - path outside repository"

            content = full_path.read_text(encoding='utf-8', errors='ignore')

            # Track usage
            self.files_read_count += 1
            if path not in self.files_read:
                self.files_read.append(path)

            return content

        except Exception as e:
            return f"Error reading file {path}: {str(e)}"

    def list_files(self, directory: str = ".", pattern: str = "*.py") -> List[str]:
        """
        List files in a directory matching a pattern.

        Args:
            directory: Relative directory path (default: repo root)
            pattern: Glob pattern to match (default: "*.py")

        Returns:
            List of relative file paths
        """
        try:
            dir_path = self.repo_path / directory
            if not dir_path.exists():
                return []

            # Security check
            if not str(dir_path.resolve()).startswith(str(self.repo_path.resolve())):
                return []

            # Find matching files
            matches = []
            for file_path in dir_path.rglob(pattern):
                if file_path.is_file():
                    rel_path = file_path.relative_to(self.repo_path)
                    matches.append(str(rel_path))

            return sorted(matches)

        except Exception:
            return []

    def search_code(self, pattern: str, file_pattern: str = "*.py",
                    max_results: int = 50) -> Dict[str, List[Dict[str, any]]]:
        """
        Search for a pattern in code files.

        Args:
            pattern: Text or regex pattern to search for
            file_pattern: Glob pattern for files to search (default: "*.py")
            max_results: Maximum number of matches to return

        Returns:
            Dictionary mapping file paths to lists of matches:
            {
                "path/to/file.py": [
                    {"line_number": 42, "line": "matching line content"},
                    ...
                ]
            }
        """
        try:
            matches = {}
            result_count = 0

            for file_path in self.repo_path.rglob(file_pattern):
                if not file_path.is_file():
                    continue

                if result_count >= max_results:
                    break

                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    file_matches = []

                    for line_num, line in enumerate(content.split('\n'), 1):
                        if pattern in line:  # Simple substring match
                            file_matches.append({
                                'line_number': line_num,
                                'line': line.strip()
                            })
                            result_count += 1

                            if result_count >= max_results:
                                break

                    if file_matches:
                        rel_path = str(file_path.relative_to(self.repo_path))
                        matches[rel_path] = file_matches

                except Exception:
                    # Skip files that can't be read
                    continue

            return matches

        except Exception:
            return {}

    def get_file_info(self, path: str) -> Optional[Dict[str, any]]:
        """
        Get metadata about a file.

        Args:
            path: Relative file path

        Returns:
            Dictionary with file info:
            {
                "exists": bool,
                "size_bytes": int,
                "lines": int,
                "extension": str
            }
        """
        try:
            full_path = self.repo_path / path

            if not full_path.exists():
                return {"exists": False}

            if not full_path.is_file():
                return {"exists": False}

            # Security check
            if not str(full_path.resolve()).startswith(str(self.repo_path.resolve())):
                return {"exists": False}

            content = full_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.count('\n') + 1

            return {
                "exists": True,
                "size_bytes": full_path.stat().st_size,
                "lines": lines,
                "extension": full_path.suffix
            }

        except Exception:
            return {"exists": False}

    def get_stats(self) -> Dict[str, any]:
        """
        Get usage statistics.

        Returns:
            Dictionary with tool usage stats
        """
        return {
            "files_read_count": self.files_read_count,
            "unique_files_read": len(self.files_read),
            "files_read": self.files_read.copy()
        }


def test_codebase_tools():
    """Test CodebaseTools with current repository"""
    import os

    print("Testing CodebaseTools...")

    # Use current repo as test
    repo_path = Path(__file__).parent.parent.parent
    tools = CodebaseTools(repo_path)

    print(f"✓ Initialized tools for: {repo_path.name}")

    # Test read_file
    content = tools.read_file("README.md")
    print(f"✓ Read README.md: {len(content)} chars")

    # Test list_files
    py_files = tools.list_files("experiments/experiment_4", "*.py")
    print(f"✓ Listed files: found {len(py_files)} Python files in experiment_4/")

    # Test search_code
    matches = tools.search_code("AgentConfig", file_pattern="*.py", max_results=5)
    print(f"✓ Search 'AgentConfig': found {len(matches)} files")

    # Test get_file_info
    info = tools.get_file_info("pruner.py")
    if info['exists']:
        print(f"✓ Get file info: pruner.py has {info['lines']} lines")

    # Test stats
    stats = tools.get_stats()
    print(f"✓ Tool stats: read {stats['files_read_count']} files")

    print("\n✅ All CodebaseTools tests passed!")


if __name__ == "__main__":
    test_codebase_tools()
