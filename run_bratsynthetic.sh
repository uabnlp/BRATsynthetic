#!/bin/bash

# ============================================
# USAGE
# ============================================
usage() {
  echo "Usage: $0 -i <input_dir> -o <output_base_dir> [-m] [-r] [-s] [-c]"
  echo "  -i   Input directory (required)"
  echo "  -o   Base output directory (required)"
  echo "  -m   Run Markov method"
  echo "  -r   Run Random method"
  echo "  -s   Run Simple method"
  echo "  -c   Run Consistent method"
  echo
  echo "If no method flags are passed, all four methods will be run."
  exit 1
}

# ============================================
# DEFAULTS
# ============================================
PYTHON_SCRIPT="bratsynthetic.py"
TEMP_CONFIG_DIR="$(mktemp -d)"  # creates unique temp dir
trap 'rm -rf "$TEMP_CONFIG_DIR"' EXIT  # ensure cleanup on script exit

RUN_MARKOV=false
RUN_RANDOM=false
RUN_SIMPLE=false
RUN_CONSISTENT=false

# ============================================
# ARG PARSING
# ============================================
while getopts ":i:o:mrsc" opt; do
  case $opt in
    i ) INPUT_DIR="$OPTARG" ;;
    o ) OUTPUT_BASE="$OPTARG" ;;
    m ) RUN_MARKOV=true ;;
    r ) RUN_RANDOM=true ;;
    s ) RUN_SIMPLE=true ;;
    c ) RUN_CONSISTENT=true ;;
    \? ) usage ;;
    : ) usage ;;
  esac
done

# Validate input/output
if [[ -z "$INPUT_DIR" || -z "$OUTPUT_BASE" ]]; then
  echo "Error: Input and output directories are required."
  usage
fi

# If no method flags are passed, default to all
if ! $RUN_MARKOV && ! $RUN_RANDOM && ! $RUN_SIMPLE && ! $RUN_CONSISTENT; then
  RUN_MARKOV=true
  RUN_RANDOM=true
  RUN_SIMPLE=true
  RUN_CONSISTENT=true
fi

# ============================================
# CONFIG GENERATOR
# ============================================
write_config_file() {
  local strategy=$1
  local config_path=$2

  cat > "$config_path" <<EOL
general:
  input_directory: ${INPUT_DIR}
  output_directory: ${OUTPUT_BASE}/${strategy}/
  recursive: True
  show_replacements: True
  default_strategy: ${strategy}
  default_transition_probability: 0.5
EmailMaker:
  strategy: random
AgeMaker:
  strategy: consistent
EOL
}

# ============================================
# METHOD RUNNER
# ============================================
run_method() {
  local name=$1
  local strategy=$2
  local config_file="${TEMP_CONFIG_DIR}/${name}_config.yaml"

  write_config_file "$strategy" "$config_file"

  echo ""
  echo "Running $name method..."
  python "$PYTHON_SCRIPT" -c "$config_file"
  local status=$?

  if [ $status -ne 0 ]; then
    echo "$name method failed."
  else
    echo "$name method completed."
  fi
}

# ============================================
# EXECUTE SELECTED METHODS
# ============================================
$RUN_MARKOV && run_method "Markov" "markov"
$RUN_RANDOM && run_method "Random" "random"
$RUN_SIMPLE && run_method "Simple" "simple"
$RUN_CONSISTENT && run_method "Consistent" "consistent"

echo ""
echo "All selected methods finished. Output located in: $OUTPUT_BASE"
