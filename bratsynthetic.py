# bratsynthetic.py
"""
Replaces tagged personal information text with synthetic substitutes.
Input is a directory of brat files.
Output will create new .text and .ann files with synthetic replacements.
"""

import argparse
import sys
import os
import logging
from tqdm import tqdm

from bratsynthetic import BratSynthetic, BratSyntheticConfig

def setup_logging(output_dir):
    """Configure logging with:
       - info.log (INFO+)
       - error.log (ERROR+)
       - TqdmLoggingHandler (ERROR+ to console) 
         so that only errors appear in console and do not break the TQDM bar.
    """
    # 1) Ensure the root logger doesn’t spam the console
    logging.basicConfig(level=logging.WARNING)

    logs_dir = os.path.join(output_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # 2) Create and configure our main logger
    logger = logging.getLogger('BratSynthetic')
    logger.setLevel(logging.INFO)
    # Prevent logs from propagating to the root logger
    logger.propagate = False
    
    # 3) Create file handlers
    info_handler = logging.FileHandler(os.path.join(logs_dir, 'info.log'))
    info_handler.setLevel(logging.INFO)
    
    error_handler = logging.FileHandler(os.path.join(logs_dir, 'error.log'))
    error_handler.setLevel(logging.ERROR)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    info_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)
    
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    
    # 4) Create TQDM console handler
    class TqdmLoggingHandler(logging.Handler):
        def emit(self, record):
            try:
                msg = self.format(record)
                tqdm.write(msg)  # does not break tqdm progress bar
            except Exception:
                self.handleError(record)
    
    tqdm_handler = TqdmLoggingHandler()
    # Set to ERROR so that only errors appear in the console
    tqdm_handler.setLevel(logging.ERROR)
    tqdm_handler.setFormatter(formatter)
    
    logger.addHandler(tqdm_handler)
    
    return logger


def process_files(bratsyn, input_dir, output_dir, recursive, logger):
    """Process files with progress tracking"""
    file_pairs = []
    
    # Collect all file pairs first for accurate progress tracking
    for root, _, files in os.walk(input_dir):
        if not recursive and root != input_dir:
            continue
            
        for file in files:
            if file.endswith('.txt'):
                txt_path = os.path.join(root, file)
                ann_path = os.path.splitext(txt_path)[0] + '.ann'
                
                if os.path.exists(ann_path):
                    rel_path = os.path.relpath(txt_path, input_dir)
                    out_txt = os.path.join(output_dir, rel_path)
                    out_ann = os.path.splitext(out_txt)[0] + '.ann'
                    file_pairs.append((txt_path, ann_path, out_txt, out_ann))
                else:
                    logger.error(f"Missing ANN file for {txt_path}")

    with tqdm(total=len(file_pairs), desc="Processing files", unit="file") as pbar:
        for txt_path, ann_path, out_txt, out_ann in file_pairs:
            try:
                # Create output directory if needed
                os.makedirs(os.path.dirname(out_txt), exist_ok=True)
                
                # Synthetic replacements
                replaced_text, replaced_ann = bratsyn.syntheticize(txt_path)
                
                # Write output .txt and .ann
                with open(out_txt, 'w', encoding='utf-8') as f:
                    f.write(replaced_text)
                with open(out_ann, 'w', encoding='utf-8') as f:
                    f.write(replaced_ann)
                    
                logger.info(f"Processed {os.path.basename(txt_path)}")
                
            except Exception as e:
                logger.error(f"Error processing {txt_path}: {str(e)}", exc_info=True)
            finally:
                pbar.update(1)

class _ArgParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"error: {message}", file=sys.stderr)
        print("Hint: specify a config file with -c/--config_file. See README for a minimal example.", file=sys.stderr)
        sys.exit(2)


def parse_args() -> argparse.Namespace:
    parser = _ArgParser(description="BRATsynthetic — generate surrogate-replaced text from BRAT .ann + .txt")
    parser.add_argument('-c', '--config_file', type=str, 
                        required=True, help='Configuration file path')
    return parser.parse_args()

def load_config_file(config_file_path: str) -> BratSyntheticConfig:
    return BratSyntheticConfig(config_file_path)

if __name__ == '__main__':
    args = parse_args()
    config = load_config_file(args.config_file)
    
    # Initialize logging *before* instantiating BratSynthetic
    logger = setup_logging(config.general.output_dir)
    
    # Create and run syntheticizer
    brat_synthetic = BratSynthetic(config=config, logger=logger)
    process_files(
        brat_synthetic,
        config.general.input_dir,
        config.general.output_dir,
        config.general.recursive,
        logger
    )
    
    logger.info(f"Processing complete. Output directory: {config.general.output_dir}")
