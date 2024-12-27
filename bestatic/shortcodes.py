import os
import re
import warnings
from typing import Dict, Any, Callable, Optional, Tuple
import importlib.util

class ShortcodeProcessor:
    def __init__(self):
        self.shortcodes: Dict[str, Callable] = {}
        self._load_shortcodes()

    def _load_shortcodes(self):
        """Load shortcode handlers from _shortcodes directory"""
        shortcodes_dir = os.path.join(os.getcwd(), '_shortcodes')
        if not os.path.exists(shortcodes_dir):
            return

        for file in os.listdir(shortcodes_dir):
            if file.endswith('.py'):
                shortcode_name = file[:-3]
                file_path = os.path.join(shortcodes_dir, file)
                
                # Load module dynamically
                spec = importlib.util.spec_from_file_location(shortcode_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    if hasattr(module, 'render'):
                        self.shortcodes[shortcode_name] = module.render

    def _parse_shortcode(self, match: str) -> Tuple[Optional[str], Dict[str, str], Optional[str]]:
        """Parse shortcode syntax into name, attributes and class"""
        try:
            # Remove the wrapper syntax {!!{ }!!}
            content = match[4:-4].strip()
            if not content:
                warnings.warn("Empty shortcode found, skipping")
                return None, {}, None
            
            # Split into parts (command and arguments)
            parts = content.split()
            if not parts:
                warnings.warn("Malformed shortcode found, skipping")
                return None, {}, None
                
            name = parts[0]
            attrs = {}
            
            # Process remaining parts
            current_key = None
            for part in parts[1:]:
                if '=' in part:
                    # It's a key-value pair
                    key, value = part.split('=', 1)
                    attrs[key] = value.strip('"\'')
                elif current_key:
                    # It's a value for the previous key
                    attrs[current_key] = part
                    current_key = None
                else:
                    # It's content
                    if 'content' in attrs:
                        attrs['content'] += f' {part}'
                    else:
                        attrs['content'] = part
            
            return name, attrs, attrs.get('align')
            
        except Exception as e:
            warnings.warn(f"Error processing shortcode: {str(e)}")
            return None, {}, None

    def process_content(self, content: str) -> str:
        """Process content and replace shortcodes with rendered HTML"""
        def replace_shortcode(match):
            try:
                shortcode = match.group(0)
                name, attrs, class_name = self._parse_shortcode(shortcode)
                
                if name is None:
                    return shortcode
                
                if name not in self.shortcodes:
                    warnings.warn(f"Unknown shortcode '{name}', keeping original content")
                    return shortcode
                
                try:
                    rendered = self.shortcodes[name](attrs)
                    if class_name:
                        return f'<div class="{class_name}">\n{rendered}\n</div>'
                    return rendered
                except Exception as e:
                    warnings.warn(f"Error rendering shortcode '{name}': {str(e)}")
                    return shortcode
                    
            except Exception as e:
                warnings.warn(f"Unexpected error processing shortcode: {str(e)}")
                return match.group(0)

        # Update pattern to match simpler syntax
        pattern = r'\{!!\{[^}]+\}!!\}'
        try:
            return re.sub(pattern, replace_shortcode, content)
        except Exception as e:
            warnings.warn(f"Failed to process shortcodes: {str(e)}")
            return content
