import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from PIL import Image
except ImportError:
    Image = None

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Process images for optimization and format conversion."""
    
    # Supported input formats
    PROCESSABLE_FORMATS = {'.jpg', '.jpeg', '.png', '.gif'}
    
    # Output format configurations
    FORMAT_EXTENSIONS = {
        'webp': '.webp',
        'avif': '.avif'
    }
    
    def __init__(self, config: Dict):
        """
        Initialize ImageProcessor with configuration.
        
        Args:
            config: Image processing configuration dictionary
                   Expected keys: enabled, formats, quality, keep_original, etc.
        """
        if Image is None:
            raise ImportError("Pillow is required for image processing. Install with: pip install Pillow")
        
        self.config = config
        self.enabled = config.get('enabled', False)
        self.formats = config.get('formats', ['webp'])
        self.quality = config.get('quality', 80)
        self.keep_original = config.get('keep_original', False)
        
        # File inclusion/exclusion
        self.include_formats = set(
            ext.lower() if ext.startswith('.') else f'.{ext.lower()}'
            for ext in config.get('include_formats', ['.jpg', '.jpeg', '.png', '.gif'])
        )
    
    def should_process(self, filepath: str) -> bool:
        """
        Check if a file should be processed.
        
        Args:
            filepath: Path to the file
            
        Returns:
            True if file should be processed, False otherwise
        """
        if not self.enabled:
            return False
        
        ext = Path(filepath).suffix.lower()
        return ext in self.include_formats and ext in self.PROCESSABLE_FORMATS
    
    def process_image(self, input_path: str, output_dir: str) -> Dict[str, str]:
        """
        Process a single image: convert, optimize, and save.
        
        Args:
            input_path: Path to input image
            output_dir: Directory where processed images should be saved
            
        Returns:
            Dictionary mapping format to output path
            Example: {'webp': 'output/images/photo.webp', 'original': 'output/images/photo.jpg'}
        """
        results = {}
        input_path_obj = Path(input_path)
        output_dir_obj = Path(output_dir)
        
        # Ensure output directory exists
        output_dir_obj.mkdir(parents=True, exist_ok=True)
        
        try:
            # Open and process image
            with Image.open(input_path) as img:
                # Convert RGBA to RGB for formats that don't support transparency
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Check if image actually has transparency
                    if img.mode == 'P' and 'transparency' in img.info:
                        # Keep as-is for WebP (supports transparency)
                        if 'webp' not in self.formats:
                            # Convert to RGB with white background
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            if img.mode == 'P':
                                img = img.convert('RGBA')
                            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                            img = background
                    elif img.mode in ('RGBA', 'LA'):
                        # WebP supports transparency, but for other formats use white background
                        if 'webp' in self.formats:
                            pass  # Keep RGBA for WebP
                        else:
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            background.paste(img, mask=img.split()[-1])
                            img = background
                    else:
                        img = img.convert('RGB')
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save in requested formats
                base_name = input_path_obj.stem
                
                for fmt in self.formats:
                    if fmt not in self.FORMAT_EXTENSIONS:
                        logger.warning(f"Unsupported format '{fmt}', skipping")
                        continue
                    
                    ext = self.FORMAT_EXTENSIONS[fmt]
                    output_path = output_dir_obj / f"{base_name}{ext}"
                    
                    # Save with format-specific options
                    save_kwargs = {'quality': self.quality}
                    
                    if fmt == 'webp':
                        save_kwargs['method'] = 6  # Better compression
                    elif fmt == 'avif':
                        # AVIF support may vary by Pillow version
                        pass
                    
                    img.save(str(output_path), format=fmt.upper(), **save_kwargs)
                    results[fmt] = str(output_path)
                    logger.info(f"Converted {input_path} to {output_path}")
                
                # Keep original if configured
                if self.keep_original:
                    original_output = output_dir_obj / input_path_obj.name
                    if str(original_output) != input_path:
                        img_original = Image.open(input_path)
                        img_original.save(str(original_output))
                        results['original'] = str(original_output)
        
        except Exception as e:
            logger.error(f"Error processing image {input_path}: {e}")
            # Copy original on error
            original_output = output_dir_obj / input_path_obj.name
            if str(original_output) != input_path:
                import shutil
                shutil.copy2(input_path, original_output)
                results['original'] = str(original_output)
        
        return results
    
    def _normalize_path(self, path: str) -> str:
        """
        Normalize path for comparison (handle backslashes, etc.).
        
        Args:
            path: File path
            
        Returns:
            Normalized path with forward slashes
        """
        return path.replace('\\', '/')
    
    def _build_conversion_map(self, processed_files: Dict[str, Dict[str, str]]) -> Dict[str, str]:
        """
        Build a mapping of original filenames to converted filenames.
        
        Args:
            processed_files: Dict mapping input paths to result dicts
            
        Returns:
            Dict mapping original filename to converted filename
        """
        conversion_map = {}
        
        for input_path, results in processed_files.items():
            input_name = Path(input_path).name
            
            # Use first available format
            for fmt in self.formats:
                if fmt in results:
                    converted_path = results[fmt]
                    converted_name = Path(converted_path).name
                    conversion_map[input_name] = converted_name
                    break
        
        return conversion_map
    
    def update_references_in_file(self, filepath: str, conversion_map: Dict[str, str]) -> int:
        """
        Update image references in HTML, CSS, or JS file.
        
        Args:
            filepath: Path to file to update
            conversion_map: Dict mapping original filename to converted filename
            
        Returns:
            Number of replacements made
        """
        if not conversion_map:
            return 0
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            replacements = 0
            
            # Replace each file individually with careful checks
            for original_name, converted_name in conversion_map.items():
                # Escape special regex characters
                escaped_name = re.escape(original_name)
                
                # Find all occurrences of the filename
                def replace_func(match):
                    nonlocal replacements
                    matched_text = match.group(0)
                    start_pos = match.start()
                    
                    # Check if this match is part of an external URL
                    # Look back up to 100 characters for protocol indicators
                    lookback_start = max(0, start_pos - 100)
                    preceding = content[lookback_start:start_pos]
                    
                    # Skip if part of external URL - check for :// pattern which indicates a protocol
                    if '://' in preceding:
                        return matched_text
                    
                    # Check for protocol-relative URLs (//)
                    # Look for // followed by domain structure (no spaces, has domain name)
                    # Pattern: //domain.com/path/filename
                    if '//' in preceding:
                        # Get text after the last //
                        after_slashes = preceding.split('//')[-1]
                        # Check if it looks like a URL: should have domain with dots, slashes for path
                        # and importantly, should NOT have quotes or spaces between // and filename
                        if after_slashes and not any(c in after_slashes for c in ['"', "'", ' ', '\n', '\t']):
                            # Looks like a URL path after //
                            if '.' in after_slashes or '/' in after_slashes:
                                return matched_text
                    
                    replacements += 1
                    return converted_name
                
                # Use word boundary to avoid partial matches
                # Match the filename when it appears as a complete word
                pattern = r'\b' + escaped_name + r'\b'
                content = re.sub(pattern, replace_func, content)
            
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Updated {replacements} image references in {filepath}")
            
            return replacements
        
        except Exception as e:
            logger.error(f"Error updating references in {filepath}: {e}")
            return 0
    
    def scan_and_update_output(self, output_dir: str, conversion_map: Dict[str, str]) -> int:
        """
        Scan all HTML, CSS, and JS files in output directory and update image references.
        
        Args:
            output_dir: Root output directory
            conversion_map: Dict mapping original filename to converted filename
            
        Returns:
            Total number of replacements made
        """
        if not conversion_map:
            return 0
        
        total_replacements = 0
        output_path = Path(output_dir)
        
        # File extensions to process
        extensions = ['.html', '.css', '.js']
        
        for ext in extensions:
            for filepath in output_path.rglob(f'*{ext}'):
                replacements = self.update_references_in_file(str(filepath), conversion_map)
                total_replacements += replacements
        
        logger.info(f"Total image reference updates: {total_replacements}")
        return total_replacements
    
    def process_static_content(self, static_dir: str, output_static_dir: str) -> Dict[str, str]:
        """
        Process all images in static content directory.
        
        Args:
            static_dir: Source static-content directory
            output_static_dir: Destination static-content directory in _output
            
        Returns:
            Conversion map (original filename -> converted filename)
        """
        if not self.enabled:
            return {}
        
        static_path = Path(static_dir)
        if not static_path.exists():
            logger.warning(f"Static content directory not found: {static_dir}")
            return {}
        
        processed_files = {}
        
        # Walk through all files in static-content
        for root, dirs, files in os.walk(static_dir):
            for filename in files:
                input_path = os.path.join(root, filename)
                
                if not self.should_process(input_path):
                    continue
                
                # Calculate relative path from static_dir
                rel_path = os.path.relpath(root, static_dir)
                output_dir = os.path.join(output_static_dir, rel_path) if rel_path != '.' else output_static_dir
                
                # Process the image
                results = self.process_image(input_path, output_dir)
                if results:
                    processed_files[input_path] = results
        
        # Build conversion map
        conversion_map = self._build_conversion_map(processed_files)
        
        logger.info(f"Processed {len(processed_files)} images")
        return conversion_map
