# prepend the following disclaimer to each document:
# THIS IS NOT A REAL CLINICAL DOCUMENT. SYNTHETIC NAMES AND OTHER PERSONAL IDENTIFYING INFORMATION (PHI) CORRESPONDING TO THE PHI OF ANY REAL PERSON IS UNINTENTIONAL
# Usage: bash add_disclaimer.sh <input_dir> <output_dir>
# Example: bash add_disclaimer.sh /data/brats2018/train/HGG/ /data/brats2018/train/HGG_disclaimer/

# Check if the number of arguments is correct
if [ "$#" -ne 2 ]; then
    echo "Illegal number of parameters"
    echo "Usage: bash add_disclaimer.sh <input_dir> <output_dir>"
    exit 1
fi

# Check if the input directory exists
if [ ! -d "$(dirname "$1")" ]; then
    echo "Input directory does not exist"
    exit 1
fi

# Check if the output directory exists, if not create it
mkdir -p "$2"

## Add disclaimer to the input files
#for file in "$1"/*.txt; do
#    [[ -e "$file" ]] || break  # handle the case of no *.txt files
#    file=$(basename "$file")
#    echo "THIS IS NOT A REAL CLINICAL DOCUMENT. SYNTHETIC NAMES AND OTHER PERSONAL IDENTIFYING INFORMATION (PHI) CORRESPONDING TO THE PHI OF ANY REAL PERSON IS UNINTENTIONAL" > "$2$file"
#    cat "$1$file" >> "$2$file"
#done

# Recursively add disclaimer to the input files
for file in "$1"/*; do
    [[ -e "$file" ]] || break  # handle the case of no files
    if [ -d "$file" ]; then
        mkdir -p "$2/$(basename "$file")"
        bash add_disclaimer.sh "$file" "$2/$(basename "$file")"
    else
        file=$(basename "$file")
        echo "THIS IS NOT A REAL CLINICAL DOCUMENT. SYNTHETIC NAMES AND OTHER PERSONAL IDENTIFYING INFORMATION (PHI) CORRESPONDING TO THE PHI OF ANY REAL PERSON IS UNINTENTIONAL" > "$2/$file"
        cat "$1/$file" >> "$2/$file"
    fi
done

#echo "Disclaimer added to the input files"

# End of script
