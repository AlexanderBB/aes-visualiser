from flask import Flask, request, render_template
import binascii
from aes_lib import (
    Sbox, pad, bytes_to_matrix, matrix_to_bytes, sub_bytes, shift_rows, mix_columns,
    add_round_key, rotate_word, expand_key, matrix_to_html, matrices_to_process_html
)

app = Flask(__name__)

# Add a custom filter for hex formatting
@app.template_filter('hex')
def hex_filter(value):
    """Format a value as a hexadecimal string."""
    if isinstance(value, int):
        return f"0x{value:02X}"
    return value


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        key = request.form['key']
        word = request.form['word']
        error = None

        if not key or not word:
            error = "Key and word cannot be empty"
        elif len(key) != 16 or len(word) != 16:
            error = "Key and word must be exactly 16 characters (16 bytes)"

        if error:
            return render_template('landing.html', error=error)

        key = key.encode('utf-8')
        word = word.encode('utf-8')

        steps = []
        explanation_rows = []

        # Step 1: Convert Plaintext to 4×4 Hex Matrix
        state = bytes_to_matrix(word)
        explanation_rows = []
        for i in range(4):
            for j in range(4):
                explanation_rows.append((
                    f"Character '{chr(word[i+4*j])}' to Hex",
                    f"0x{word[i+4*j]:02X}"
                ))
        steps.append({
            'title': 'Step 1: Convert Plaintext to 4×4 Hex Matrix',
            'matrix_html': matrix_to_html(state),
            'description': 'Transform each ASCII character of the input word into hex and populate a 4×4 matrix column-wise.',
            'explanation_rows': explanation_rows,
            'id_suffix': 'step1_explanation'
        })

        # Step 2: Convert Key to 4×4 Hex Matrix
        key_matrix = bytes_to_matrix(key)
        explanation_rows = []
        for i in range(4):
            for j in range(4):
                explanation_rows.append((
                    f"Character '{chr(key[i+4*j])}' to Hex",
                    f"0x{key[i+4*j]:02X}"
                ))
        steps.append({
            'title': 'Step 2: Convert Key to 4×4 Hex Matrix',
            'matrix_html': matrix_to_html(key_matrix),
            'description': 'Transform each ASCII character of the key into hex and populate a 4×4 matrix column-wise.',
            'explanation_rows': explanation_rows,
            'id_suffix': 'step2_explanation'
        })

        # Round 0 — Initial Round (Pre-Whitening)
        # Step 3: AddRoundKey
        explanation_rows = []
        for i in range(4):
            for j in range(4):
                explanation_rows.append((
                    f"State[{i}][{j}] ⊕ Key[{i}][{j}]",
                    f"0x{state[i][j]:02X} ⊕ 0x{key_matrix[i][j]:02X} = 0x{state[i][j] ^ key_matrix[i][j]:02X}"
                ))

        state = add_round_key(state, key_matrix, [])
        steps.append({
            'title': 'Round 0 — Initial Round (Pre-Whitening): AddRoundKey',
            'matrix_html': matrix_to_html(state),
            'description': 'XOR each byte of the plaintext matrix with the corresponding byte of the key matrix.',
            'explanation_rows': explanation_rows,
            'id_suffix': 'step3_explanation'
        })

        # Generate all round keys in advance using the correct key expansion
        key_expansion_logs = []
        round_keys = expand_key(key, key_expansion_logs)

        # Rounds 1 to 9 — Main AES Rounds
        for round_idx in range(1, 10):
            round_title = f"Round {round_idx}"

            # SubBytes
            explanation_rows = []
            for i in range(4):
                for j in range(4):
                    explanation_rows.append((
                        f"S-box[0x{state[i][j]:02X}]",
                        f"0x{Sbox[state[i][j]]:02X}"
                    ))

            before_state = [row[:] for row in state]
            state = sub_bytes(state, [])
            steps.append({
                'title': f"{round_title}: SubBytes",
                'matrix_html': matrices_to_process_html(before_state, state, 'SubBytes Transformation'),
                'description': 'Substitute each byte in the matrix using the AES S-box.',
                'explanation_rows': explanation_rows,
                'id_suffix': f'round{round_idx}_subbytes_explanation'
            })

            # ShiftRows
            explanation_rows = []
            explanation_rows.append(("Row 0", "Unchanged"))
            explanation_rows.append(("Row 1", "Left-rotate by 1"))
            explanation_rows.append(("Row 2", "Left-rotate by 2"))
            explanation_rows.append(("Row 3", "Left-rotate by 3"))

            before_state = [row[:] for row in state]
            state = shift_rows(state, [])
            steps.append({
                'title': f"{round_title}: ShiftRows",
                'matrix_html': matrices_to_process_html(before_state, state, 'ShiftRows Transformation'),
                'description': 'Row 0: unchanged, Row 1: left-rotate by 1, Row 2: left-rotate by 2, Row 3: left-rotate by 3.',
                'explanation_rows': explanation_rows,
                'id_suffix': f'round{round_idx}_shiftrows_explanation'
            })

            # MixColumns
            log = []
            before_state = [row[:] for row in state]
            state = mix_columns(state, log)

            # Check for detailed MixColumns explanation
            mix_columns_explanation_rows = []
            detailed_html = None

            # First, look for the detailed HTML explanation
            for log_entry in log:
                if log_entry[0] == "MixColumns Detailed":
                    detailed_html = log_entry[1]
                    break

            # If we found a detailed explanation, use it as the only explanation row
            if detailed_html:
                mix_columns_explanation_rows = [("MixColumns Detailed", detailed_html)]
            else:
                # Otherwise, fall back to the original log entries
                mix_columns_explanation_rows = log

            steps.append({
                'title': f"{round_title}: MixColumns",
                'matrix_html': matrices_to_process_html(before_state, state, 'MixColumns Transformation'),
                'description': 'This step enhances diffusion — every output byte depends on all 4 bytes of the column.',
                'explanation_rows': mix_columns_explanation_rows,
                'id_suffix': f'round{round_idx}_mixcolumns_explanation'
            })

            # Round Key Generation Explanation
            key_gen_explanation_rows = []
            detailed_html = None

            # First, look for the detailed HTML explanation
            for log_entry in key_expansion_logs:
                if log_entry[0] == f"Round {round_idx} Key Generation Detailed":
                    detailed_html = log_entry[1]
                    break

            # If we found a detailed explanation, use it as the only explanation row
            if detailed_html:
                key_gen_explanation_rows = [(f"Round {round_idx} Key Generation Detailed", detailed_html)]
            else:
                # Otherwise, fall back to the original log entries
                for log_entry in key_expansion_logs:
                    # Use exact match to avoid confusion between rounds (e.g., Round 1 vs Round 10)
                    if (log_entry[0].startswith(f"Round {round_idx} ") or
                        log_entry[0].startswith(f"Generate first column of round key {round_idx}") and (len(log_entry[0]) == len(f"Generate first column of round key {round_idx}") or not log_entry[0][len(f"Generate first column of round key {round_idx}")].isdigit()) or
                        log_entry[0].startswith(f"Generate remaining columns of round key {round_idx}") and (len(log_entry[0]) == len(f"Generate remaining columns of round key {round_idx}") or not log_entry[0][len(f"Generate remaining columns of round key {round_idx}")].isdigit())):
                        key_gen_explanation_rows.append(log_entry)

            steps.append({
                'title': f"{round_title}: Round Key Generation",
                'matrix_html': matrix_to_html(round_keys[round_idx]),
                'description': f'Generation of Round Key {round_idx} using the AES key schedule algorithm.',
                'explanation_rows': key_gen_explanation_rows,
                'id_suffix': f'round{round_idx}_key_generation_explanation'
            })

            # AddRoundKey
            explanation_rows = []
            for i in range(4):
                for j in range(4):
                    explanation_rows.append((
                        f"State[{i}][{j}] ⊕ RoundKey{round_idx}[{i}][{j}]",
                        f"0x{state[i][j]:02X} ⊕ 0x{round_keys[round_idx][i][j]:02X} = 0x{state[i][j] ^ round_keys[round_idx][i][j]:02X}"
                    ))

            before_state = [row[:] for row in state]
            state = add_round_key(state, round_keys[round_idx], [])
            steps.append({
                'title': f"{round_title}: AddRoundKey",
                'matrix_html': matrices_to_process_html(before_state, state, 'AddRoundKey Transformation'),
                'description': 'XOR current state with round key.',
                'explanation_rows': explanation_rows,
                'id_suffix': f'round{round_idx}_addroundkey_explanation'
            })

        # Round 10 — Final Round
        # SubBytes
        explanation_rows = []
        for i in range(4):
            for j in range(4):
                explanation_rows.append((
                    f"S-box[0x{state[i][j]:02X}]",
                    f"0x{Sbox[state[i][j]]:02X}"
                ))

        before_state = [row[:] for row in state]
        state = sub_bytes(state, [])
        steps.append({
            'title': "Round 10 (Final): SubBytes",
            'matrix_html': matrices_to_process_html(before_state, state, 'SubBytes Transformation'),
            'description': 'Substitute each byte in the matrix using the AES S-box.',
            'explanation_rows': explanation_rows,
            'id_suffix': 'round10_subbytes_explanation'
        })

        # ShiftRows
        explanation_rows = []
        explanation_rows.append(("Row 0", "Unchanged"))
        explanation_rows.append(("Row 1", "Left-rotate by 1"))
        explanation_rows.append(("Row 2", "Left-rotate by 2"))
        explanation_rows.append(("Row 3", "Left-rotate by 3"))

        before_state = [row[:] for row in state]
        state = shift_rows(state, [])
        steps.append({
            'title': "Round 10 (Final): ShiftRows",
            'matrix_html': matrices_to_process_html(before_state, state, 'ShiftRows Transformation'),
            'description': 'Row 0: unchanged, Row 1: left-rotate by 1, Row 2: left-rotate by 2, Row 3: left-rotate by 3.',
            'explanation_rows': explanation_rows,
            'id_suffix': 'round10_shiftrows_explanation'
        })

        # Round Key Generation Explanation (Final)
        key_gen_explanation_rows = []
        detailed_html = None

        # First, look for the detailed HTML explanation
        for log_entry in key_expansion_logs:
            if log_entry[0] == "Round 10 Key Generation Detailed":
                detailed_html = log_entry[1]
                break

        # If we found a detailed explanation, use it as the only explanation row
        if detailed_html:
            key_gen_explanation_rows = [("Round 10 Key Generation Detailed", detailed_html)]
        else:
            # Otherwise, fall back to the original log entries
            for log_entry in key_expansion_logs:
                # Use exact match to avoid confusion between rounds
                if (log_entry[0].startswith("Round 10 ") or
                    log_entry[0].startswith("Generate first column of round key 10") and (len(log_entry[0]) == len("Generate first column of round key 10") or not log_entry[0][len("Generate first column of round key 10")].isdigit()) or
                    log_entry[0].startswith("Generate remaining columns of round key 10") and (len(log_entry[0]) == len("Generate remaining columns of round key 10") or not log_entry[0][len("Generate remaining columns of round key 10")].isdigit())):
                    key_gen_explanation_rows.append(log_entry)

        steps.append({
            'title': "Round 10 (Final): Round Key Generation",
            'matrix_html': matrix_to_html(round_keys[10]),
            'description': 'Generation of the final Round Key (10) using the AES key schedule algorithm.',
            'explanation_rows': key_gen_explanation_rows,
            'id_suffix': 'round10_key_generation_explanation'
        })

        # AddRoundKey (Final)
        explanation_rows = []
        for i in range(4):
            for j in range(4):
                explanation_rows.append((
                    f"State[{i}][{j}] ⊕ RoundKey10[{i}][{j}]",
                    f"0x{state[i][j]:02X} ⊕ 0x{round_keys[10][i][j]:02X} = 0x{state[i][j] ^ round_keys[10][i][j]:02X}"
                ))

        before_state = [row[:] for row in state]
        state = add_round_key(state, round_keys[10], [])
        steps.append({
            'title': "Round 10 (Final): AddRoundKey",
            'matrix_html': matrices_to_process_html(before_state, state, 'AddRoundKey Transformation'),
            'description': 'XOR current state with the final round key.',
            'explanation_rows': explanation_rows,
            'id_suffix': 'round10_addroundkey_explanation'
        })

        # Final Output
        final_bytes = matrix_to_bytes(state)
        final_hex = binascii.hexlify(final_bytes).decode('utf-8').upper()

        explanation_rows = []
        explanation_rows.append((
            "Final Encrypted Output (Hex)",
            f"<div style='font-size: 1.2em; font-weight: bold; margin: 15px 0;'>{final_hex}</div>"
        ))
        explanation_rows.append((
            "Original Plaintext",
            f"<div style='margin: 5px 0;'>{word.decode('utf-8')}</div>"
        ))
        explanation_rows.append((
            "Encryption Key",
            f"<div style='margin: 5px 0;'>{key.decode('utf-8')}</div>"
        ))

        steps.append({
            'title': "Final Encrypted Result",
            'matrix_html': None,
            'description': 'The final AES-128 encrypted output in hexadecimal format.',
            'explanation_rows': explanation_rows,
            'id_suffix': 'final_result'
        })

        return render_template('visualize.html', steps=steps)

    return render_template('landing.html')


if __name__ == '__main__':
    app.run(debug=True)
