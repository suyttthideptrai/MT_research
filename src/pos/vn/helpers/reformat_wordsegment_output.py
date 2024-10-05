# path: src/pos/vn/helpers

# path: src/pos/vn/helpers

def reformat_wordsegment_output(input_file_path, output_file_path):
    with open(input_file_path, 'r', encoding='utf-8') as infile:
        lines = infile.read().strip().split('\n\n')

    output_lines = []
    for block in lines:
        sentences = block.strip().split('\n')
        sentence_parts = []
        for line in sentences:
            parts = line.split('\t')
            if len(parts) > 1:  # Ensure there are enough parts
                word = parts[1]
                # Keep underscores only if they are part of the word
                if word.strip() and '_' in word:  
                    sentence_parts.append(word)
                elif word.strip():  # Add non-empty words without underscores
                    sentence_parts.append(word)

        output_lines.append(' '.join(sentence_parts).strip())

    # Write the output to a new file without extra new lines between sentences
    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        outfile.write(' '.join(output_lines))  # Join sentences with space instead of newline
    return output_file_path

# Example usage








