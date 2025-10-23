"""
Thai Tokenizer Utilities
========================

Tokenization utilities specifically designed for Thai text processing.
"""

import re
from typing import List, Dict, Optional
try:
    import pythainlp
    from pythainlp import word_tokenize
    HAS_PYTHAINLP = True
except ImportError:
    HAS_PYTHAINLP = False

class ThaiTokenizer:
    """
    Thai-specific tokenizer wrapper that provides enhanced functionality
    for Thai text processing on top of the base model tokenizer.
    """
    
    def __init__(self, base_tokenizer):
        """
        Initialize Thai tokenizer with base tokenizer.
        
        Args:
            base_tokenizer: Base tokenizer from transformers
        """
        self.base_tokenizer = base_tokenizer
        self.has_pythainlp = HAS_PYTHAINLP
        
        # Chat templates
        self.chat_template = """<|im_start|>system
คุณคือผู้ช่วย AI ที่มีความเชี่ยวชาญด้านภาษาไทย ตอบคำถามด้วยความแม่นยำและมีประโยชน์<|im_end|>
{conversation}<|im_start|>assistant
"""
        
        self.message_template = "<|im_start|>{role}\n{content}<|im_end|>\n"
    
    def preprocess_thai_text(self, text: str) -> str:
        """
        Preprocess Thai text for better tokenization.
        
        Args:
            text: Input Thai text
            
        Returns:
            Preprocessed text
        """
        if not isinstance(text, str):
            return text
        
        # Normalize Thai characters
        text = self.normalize_thai_characters(text)
        
        # Handle Thai word segmentation if pythainlp is available
        if self.has_pythainlp and self.contains_thai(text):
            # Use pythainlp for better Thai word boundaries
            words = word_tokenize(text, engine='newmm')
            text = ''.join(words)
        
        return text
    
    def normalize_thai_characters(self, text: str) -> str:
        """
        Normalize Thai characters for consistency.
        
        Args:
            text: Input text with Thai characters
            
        Returns:
            Normalized text
        """
        # Thai character normalization mappings
        normalizations = {
            'ๆ': 'ๆ',  # Ensure correct mai yamok
            '์': '์',  # Ensure correct thanthakhat
        }
        
        for old, new in normalizations.items():
            text = text.replace(old, new)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def contains_thai(self, text: str) -> bool:
        """
        Check if text contains Thai characters.
        
        Args:
            text: Input text
            
        Returns:
            True if text contains Thai characters
        """
        thai_pattern = r'[\u0E00-\u0E7F]'
        return bool(re.search(thai_pattern, text))
    
    def format_chat_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        Format chat messages into a prompt suitable for the Thai model.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            
        Returns:
            Formatted prompt string
        """
        conversation = ""
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            # Preprocess Thai content
            content = self.preprocess_thai_text(content)
            
            conversation += self.message_template.format(
                role=role,
                content=content
            )
        
        return self.chat_template.format(conversation=conversation)
    
    def format_summarization_prompt(self, text: str) -> str:
        """
        Format text for Thai summarization task.
        
        Args:
            text: Text to summarize
            
        Returns:
            Formatted prompt for summarization
        """
        text = self.preprocess_thai_text(text)
        return f"สรุปข้อความต่อไปนี้อย่างกระชับและชัดเจน:\n\n{text}\n\nสรุป:"
    
    def format_instruction_prompt(self, instruction: str, input_text: str = "") -> str:
        """
        Format instruction-following prompt for Thai model.
        
        Args:
            instruction: Task instruction
            input_text: Optional input text
            
        Returns:
            Formatted instruction prompt
        """
        instruction = self.preprocess_thai_text(instruction)
        input_text = self.preprocess_thai_text(input_text)
        
        if input_text:
            return f"คำสั่ง: {instruction}\n\nข้อมูลนำเข้า: {input_text}\n\nผลลัพธ์:"
        else:
            return f"คำสั่ง: {instruction}\n\nผลลัพธ์:"
    
    def tokenize(self, text: str, **kwargs) -> Dict:
        """
        Tokenize text with Thai preprocessing.
        
        Args:
            text: Input text
            **kwargs: Additional tokenization arguments
            
        Returns:
            Tokenization result
        """
        processed_text = self.preprocess_thai_text(text)
        return self.base_tokenizer(processed_text, **kwargs)
    
    def decode(self, token_ids, **kwargs) -> str:
        """
        Decode token IDs to text with Thai post-processing.
        
        Args:
            token_ids: Token IDs to decode
            **kwargs: Additional decoding arguments
            
        Returns:
            Decoded text
        """
        text = self.base_tokenizer.decode(token_ids, **kwargs)
        return self.postprocess_thai_text(text)
    
    def postprocess_thai_text(self, text: str) -> str:
        """
        Post-process decoded Thai text.
        
        Args:
            text: Decoded text
            
        Returns:
            Post-processed text
        """
        # Remove extra spaces around Thai characters
        text = re.sub(r'\s+', ' ', text)
        
        # Fix spacing around Thai punctuation
        text = re.sub(r'\s+([.!?,:;])', r'\1', text)
        
        # Clean up
        text = text.strip()
        
        return text
    
    def get_thai_stats(self, text: str) -> Dict[str, int]:
        """
        Get statistics about Thai content in text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with Thai text statistics
        """
        stats = {
            'total_chars': len(text),
            'thai_chars': len(re.findall(r'[\u0E00-\u0E7F]', text)),
            'words': len(text.split()),
            'has_thai': self.contains_thai(text)
        }
        
        if self.has_pythainlp and stats['has_thai']:
            thai_words = word_tokenize(text, engine='newmm')
            stats['thai_words'] = len([w for w in thai_words if self.contains_thai(w)])
        
        stats['thai_ratio'] = stats['thai_chars'] / max(stats['total_chars'], 1)
        
        return stats