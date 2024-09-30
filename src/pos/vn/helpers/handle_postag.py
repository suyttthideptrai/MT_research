# path: src/pos/vn/helpers

# path: src/pos/vn/helpers

def process_postag(input_file, output_file):
    pos_tags = []

    # Open the input file and process each line
    with open(input_file, 'r') as file:
        for line in file:
            if line.strip():  # Only process non-empty lines
                parts = line.strip().split('\t')
                if len(parts) >= 3:  # Ensure the line contains word and POS tag
                    pos_tags.append(parts[2])  # POS tag is in the third column
            else:
                # Empty line marks the end of a sentence; write the collected POS tags
                if pos_tags:
                    with open(output_file, 'a') as out_file:
                        out_file.write(' '.join(pos_tags) + '\n')
                    pos_tags = []  # Reset for the next sentence

    # Write the remaining POS tags in case there's no empty line at the end
    if pos_tags:
        with open(output_file, 'a') as out_file:
            out_file.write(' '.join(pos_tags) + '\n')







