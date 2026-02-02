
import os
import json
import subprocess
from typing import List, Dict

class OpenClawProcessor:
    """
    OpenClaw integration for intelligent PDF processing and chapter management.
    """
    def __init__(self, openclaw_dir: str = None):
        self.openclaw_dir = openclaw_dir or os.path.join(os.getcwd(), "openclaw")

    def _call_agent(self, prompt: str) -> str:
        """Call the OpenClaw agent with a prompt."""
        # Try global 'openclaw' command first, then local pnpm version
        try:
            # Using --no-interactive to ensure we get a clean output for parsing
            # We assume the gateway and LM Studio are already configured as per user's previous workflows.
            cmd = ["openclaw", "agent", "--message", prompt, "--no-interactive"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                # Fallback to local checkout if global command is not available
                cmd = ["pnpm", "openclaw", "agent", "--message", prompt, "--no-interactive"]
                result = subprocess.run(cmd, cwd=self.openclaw_dir, capture_output=True, text=True, check=True, shell=True)
                return result.stdout.strip()
            except Exception as e:
                print(f"Warning: OpenClaw call failed: {e}. Falling back to basic processing.")
                return ""

    def clean_text(self, text: str) -> str:
        """Use OpenClaw to remove headers, footers, and other PDF noise."""
        if not text:
            return ""
        
        prompt = (
            "You are a text cleaning assistant. Please clean the following PDF-extracted text by "
            "removing repetitive headers, footers, page numbers, and any other non-content noise. "
            "Preserve the core content and flow of the text. Return ONLY the cleaned text.\n\n"
            f"--- TEXT START ---\n{text[:8000]}\n--- TEXT END ---"
        )
        cleaned = self._call_agent(prompt)
        return cleaned if cleaned else text

    def split_into_chapters(self, text: str) -> List[Dict[str, str]]:
        """Use OpenClaw to identify chapter boundaries and split the text."""
        if not text:
            return []

        prompt = (
            "You are a literary assistant. Analyze the following text and split it into chapters. "
            "Identify natural chapter breaks based on themes, titles, or narrative shifts. "
            "Return the result as a JSON list of objects, each with a 'title' field and a 'content' field. "
            "Return ONLY the JSON.\n\n"
            f"--- TEXT START ---\n{text[:15000]}\n--- TEXT END ---"
        )
        resp = self._call_agent(prompt)
        
        try:
            # Find the JSON array in the response
            start_idx = resp.find('[')
            end_idx = resp.rfind(']') + 1
            if start_idx != -1 and end_idx != -1:
                json_str = resp[start_idx:end_idx]
                chapters = json.loads(json_str)
                if isinstance(chapters, list):
                    return chapters
        except (json.JSONDecodeError, ValueError):
            pass

        # Fallback if AI fails or returns invalid JSON
        return [{"title": "Main Content", "content": text}]

    def plan_audio_files(self, chapters: List[Dict[str, str]], target_duration_sec: int = 3600) -> List[List[Dict[str, str]]]:
        """
        Groups chapters into audio files. 
        Rule: No chapter is cut between 2 adjacent audio files.
        One audio file may contain more than one chapter.
        """
        # Since we don't know the duration of each chapter yet without synthesizing, 
        # we can use character count as a proxy or just group them one by one.
        # However, the user wants OpenClaw to "manage" this.
        # We can ask OpenClaw to group them based on content or estimated length.
        
        prompt = (
            "I have a list of chapters and I need to group them into audio files. "
            "Rules:\n"
            "1. Each audio file should ideally be around 1 hour of content (approx 50,000 characters).\n"
            "2. No chapter should be cut between two audio files.\n"
            "3. One audio file may contain multiple chapters.\n"
            "Please provide a grouping plan as a JSON list of lists, where each inner list contains the indices of the chapters "
            "belonging to that audio file. Return ONLY the JSON.\n\n"
            f"Chapters:\n"
        )
        for i, ch in enumerate(chapters):
            prompt += f"Index {i}: {ch['title']} ({len(ch['content'])} chars)\n"
            
        resp = self._call_agent(prompt)
        
        try:
            start_idx = resp.find('[')
            end_idx = resp.rfind(']') + 1
            if start_idx != -1 and end_idx != -1:
                grouping_indices = json.loads(resp[start_idx:end_idx])
                planned_groups = []
                for group in grouping_indices:
                    planned_groups.append([chapters[i] for i in group if i < len(chapters)])
                return planned_groups
        except:
            pass
            
        # Fallback grouping by character count
        planned_groups = []
        current_group = []
        current_chars = 0
        max_chars = 50000 # Approx 1 hour of speech
        
        for ch in chapters:
            ch_len = len(ch['content'])
            if current_chars + ch_len > max_chars and current_group:
                planned_groups.append(current_group)
                current_group = [ch]
                current_chars = ch_len
            else:
                current_group.append(ch)
                current_chars += ch_len
        
        if current_group:
            planned_groups.append(current_group)
            
        return planned_groups
