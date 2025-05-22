# AES Library Module
# Contains shared functions for AES encryption used by both app.py and tests

import binascii

# AES S-box
Sbox = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5,
    0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0,
    0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc,
    0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a,
    0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0,
    0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b,
    0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85,
    0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5,
    0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17,
    0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88,
    0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c,
    0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9,
    0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6,
    0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e,
    0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94,
    0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68,
    0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
]

# Round constants
Rcon = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]

def pad(data):
    """
    Pad the data to a multiple of 16 bytes.
    """
    length = 16 - (len(data) % 16)
    return data + bytes([length]) * length

def bytes_to_matrix(text):
    """
    Convert a 16-byte array into a 4x4 matrix.
    The bytes are arranged column by column.
    """
    matrix = [[0 for _ in range(4)] for _ in range(4)]
    for i in range(4):
        for j in range(4):
            matrix[i][j] = text[i + 4*j]
    return matrix

def matrix_to_bytes(matrix):
    """
    Convert a 4x4 matrix into a 16-byte array.
    The bytes are arranged column by column.
    """
    result = bytearray(16)
    for i in range(4):
        for j in range(4):
            result[i + 4*j] = matrix[i][j]
    return bytes(result)

def sub_bytes(state, log=None):
    """
    Apply the S-box substitution to each byte in the state matrix.
    """
    return [[Sbox[b] for b in row] for row in state]

def shift_rows(state, log=None):
    """
    Shift the rows of the state matrix.
    Row 0: unchanged
    Row 1: left-rotate by 1
    Row 2: left-rotate by 2
    Row 3: left-rotate by 3
    """
    shifted = [
        state[0],
        state[1][1:] + state[1][:1],
        state[2][2:] + state[2][:2],
        state[3][3:] + state[3][:3]
    ]
    if log is not None:
        log.append(("ShiftRows Transformation", shifted))
    return shifted

def mix_columns(state, log=None):
    """
    Mix the columns of the state matrix using the Galois field multiplication.
    """
    mix_matrix = [
        [2, 3, 1, 1],
        [1, 2, 3, 1],
        [1, 1, 2, 3],
        [3, 1, 1, 2]
    ]

    def galois_mult(a, b):
        p = 0
        for _ in range(8):
            if b & 1:
                p ^= a
            carry = a & 0x80
            a <<= 1
            if carry:
                a ^= 0x1B
            a &= 0xFF
            b >>= 1
        return p

    new_state = [[0] * 4 for _ in range(4)]

    # Create a detailed visual explanation for MixColumns
    if log is not None:
        # Create a header for the MixColumns explanation
        mix_columns_html = f"""
        <div class="key-expansion-explanation">
            <h4>🧾 Input Matrix (Before MixColumns)</h4>
            <div class="key-matrix">
                <table>
                    <tr>
                        <th>Column 0</th><th>Column 1</th><th>Column 2</th><th>Column 3</th>
                    </tr>
                    <tr>
                        <td>{hex(state[0][0])}</td>
                        <td>{hex(state[0][1])}</td>
                        <td>{hex(state[0][2])}</td>
                        <td>{hex(state[0][3])}</td>
                    </tr>
                    <tr>
                        <td>{hex(state[1][0])}</td>
                        <td>{hex(state[1][1])}</td>
                        <td>{hex(state[1][2])}</td>
                        <td>{hex(state[1][3])}</td>
                    </tr>
                    <tr>
                        <td>{hex(state[2][0])}</td>
                        <td>{hex(state[2][1])}</td>
                        <td>{hex(state[2][2])}</td>
                        <td>{hex(state[2][3])}</td>
                    </tr>
                    <tr>
                        <td>{hex(state[3][0])}</td>
                        <td>{hex(state[3][1])}</td>
                        <td>{hex(state[3][2])}</td>
                        <td>{hex(state[3][3])}</td>
                    </tr>
                </table>
            </div>

            <h4>🧮 Diffusion Matrix</h4>
            <p>Each column [b0, b1, b2, b3]ᵗ is multiplied with:</p>
            <div class="key-matrix">
                <table>
                    <tr>
                        <td>02</td><td>03</td><td>01</td><td>01</td>
                    </tr>
                    <tr>
                        <td>01</td><td>02</td><td>03</td><td>01</td>
                    </tr>
                    <tr>
                        <td>01</td><td>01</td><td>02</td><td>03</td>
                    </tr>
                    <tr>
                        <td>03</td><td>01</td><td>01</td><td>02</td>
                    </tr>
                </table>
            </div>

            <p>To produce:</p>
            <ol>
                <li>r0 = [02·b0 ⊕ 03·b1 ⊕ b2 ⊕ b3]</li>
                <li>r1 = [b0 ⊕ 02·b1 ⊕ 03·b2 ⊕ b3]</li>
                <li>r2 = [b0 ⊕ b1 ⊕ 02·b2 ⊕ 03·b3]</li>
                <li>r3 = [03·b0 ⊕ b1 ⊕ b2 ⊕ 02·b3]</li>
            </ol>

            <p>Where:</p>
            <ul>
                <li>b0–b3 = input column bytes (top to bottom)</li>
                <li>r0–r3 = transformed output bytes</li>
            </ul>

            <h4>🔍 Column 0 Transformation</h4>
            <p>Input:</p>
            <ul>
                <li>b0 = {hex(state[0][0])}</li>
                <li>b1 = {hex(state[1][0])}</li>
                <li>b2 = {hex(state[2][0])}</li>
                <li>b3 = {hex(state[3][0])}</li>
            </ul>

            <p>Output:</p>
        """

        # Calculate the results for column 0
        col0_results = []
        for row in range(4):
            result = (
                galois_mult(state[0][0], mix_matrix[row][0]) ^
                galois_mult(state[1][0], mix_matrix[row][1]) ^
                galois_mult(state[2][0], mix_matrix[row][2]) ^
                galois_mult(state[3][0], mix_matrix[row][3])
            )
            col0_results.append(result)

        # Add the column 0 transformation results
        mix_columns_html += f"""
            <ul>
                <li>r0 = 02·{hex(state[0][0])} ⊕ 03·{hex(state[1][0])} ⊕ 01·{hex(state[2][0])} ⊕ 01·{hex(state[3][0])} = {hex(col0_results[0])}</li>
                <li>r1 = 01·{hex(state[0][0])} ⊕ 02·{hex(state[1][0])} ⊕ 03·{hex(state[2][0])} ⊕ 01·{hex(state[3][0])} = {hex(col0_results[1])}</li>
                <li>r2 = 01·{hex(state[0][0])} ⊕ 01·{hex(state[1][0])} ⊕ 02·{hex(state[2][0])} ⊕ 03·{hex(state[3][0])} = {hex(col0_results[2])}</li>
                <li>r3 = 03·{hex(state[0][0])} ⊕ 01·{hex(state[1][0])} ⊕ 01·{hex(state[2][0])} ⊕ 02·{hex(state[3][0])} = {hex(col0_results[3])}</li>
            </ul>
        """

    # Calculate the new state
    for col in range(4):
        for row in range(4):
            new_state[row][col] = (
                galois_mult(state[0][col], mix_matrix[row][0]) ^
                galois_mult(state[1][col], mix_matrix[row][1]) ^
                galois_mult(state[2][col], mix_matrix[row][2]) ^
                galois_mult(state[3][col], mix_matrix[row][3])
            )
            if log is not None:
                log.append((
                    f"Column {col}, Row {row}",
                    f"Result: 0x{new_state[row][col]:02X}"
                ))

    # Complete the detailed explanation with the output matrix
    if log is not None:
        mix_columns_html += f"""
            <h4>✅ Output Matrix (After MixColumns)</h4>
            <div class="key-matrix">
                <table>
                    <tr>
                        <th>Column 0</th><th>Column 1</th><th>Column 2</th><th>Column 3</th>
                    </tr>
                    <tr>
                        <td>{hex(new_state[0][0])}</td>
                        <td>{hex(new_state[0][1])}</td>
                        <td>{hex(new_state[0][2])}</td>
                        <td>{hex(new_state[0][3])}</td>
                    </tr>
                    <tr>
                        <td>{hex(new_state[1][0])}</td>
                        <td>{hex(new_state[1][1])}</td>
                        <td>{hex(new_state[1][2])}</td>
                        <td>{hex(new_state[1][3])}</td>
                    </tr>
                    <tr>
                        <td>{hex(new_state[2][0])}</td>
                        <td>{hex(new_state[2][1])}</td>
                        <td>{hex(new_state[2][2])}</td>
                        <td>{hex(new_state[2][3])}</td>
                    </tr>
                    <tr>
                        <td>{hex(new_state[3][0])}</td>
                        <td>{hex(new_state[3][1])}</td>
                        <td>{hex(new_state[3][2])}</td>
                        <td>{hex(new_state[3][3])}</td>
                    </tr>
                </table>
            </div>

            <p>💡 Purpose: Every output byte becomes a mix of all 4 input bytes → ensuring strong byte diffusion across each column.</p>
        </div>
        """

        # Add the detailed HTML explanation as a single log entry
        log.append(("MixColumns Detailed", mix_columns_html))

    return new_state

def add_round_key(state, round_key, log=None):
    """
    XOR each byte of the state matrix with the corresponding byte of the round key.
    """
    return [[state[i][j] ^ round_key[i][j] for j in range(4)] for i in range(4)]

def rotate_word(word):
    """
    Rotate a word (list of 4 bytes) to the left by 1 position.
    """
    return word[1:] + word[:1]

def expand_key(key, log=None):
    """
    Expands the 16-byte key into 11 round keys according to the AES key schedule.
    Returns a list of 11 round keys, each as a 4x4 matrix.
    """
    # First round key is the original key
    key_bytes = key
    key_matrix = bytes_to_matrix(key_bytes)
    round_keys = [key_matrix]

    # Generate the remaining 10 round keys
    for i in range(10):
        # Create a detailed visual explanation for this round key generation
        if log is not None:
            # Create a header for the round key generation
            key_html = f"""
            <div class="key-expansion-explanation">
                <h4>🔑 Input: Cipher Key</h4>
                <div class="key-matrix">
                    <table>
                        <tr>
                            <th>w0</th><th>w1</th><th>w2</th><th>w3</th>
                        </tr>
                        <tr>
                            <td>{hex(round_keys[i][0][0])}</td>
                            <td>{hex(round_keys[i][0][1])}</td>
                            <td>{hex(round_keys[i][0][2])}</td>
                            <td>{hex(round_keys[i][0][3])}</td>
                        </tr>
                        <tr>
                            <td>{hex(round_keys[i][1][0])}</td>
                            <td>{hex(round_keys[i][1][1])}</td>
                            <td>{hex(round_keys[i][1][2])}</td>
                            <td>{hex(round_keys[i][1][3])}</td>
                        </tr>
                        <tr>
                            <td>{hex(round_keys[i][2][0])}</td>
                            <td>{hex(round_keys[i][2][1])}</td>
                            <td>{hex(round_keys[i][2][2])}</td>
                            <td>{hex(round_keys[i][2][3])}</td>
                        </tr>
                        <tr>
                            <td>{hex(round_keys[i][3][0])}</td>
                            <td>{hex(round_keys[i][3][1])}</td>
                            <td>{hex(round_keys[i][3][2])}</td>
                            <td>{hex(round_keys[i][3][3])}</td>
                        </tr>
                    </table>
                </div>

                <h4>🧠 How Round Key {i+1} Is Generated</h4>
                <ol>
                    <li>Take last column (w3)<br>
                    → [{', '.join(f'{hex(round_keys[i][j][3])}' for j in range(4))}]</li>
            """

            # Take the last column of the previous round key
            last_col = [round_keys[i][j][3] for j in range(4)]
            log.append((f"Round {i+1} Key Generation", f"Creating round key for round {i+1}"))

            # Rotate, substitute, and XOR with round constant
            rotated = rotate_word(last_col)
            key_html += f"""
                    <li>RotWord<br>
                    → [{', '.join(f'{hex(b)}' for b in rotated)}]</li>
            """

            substituted = [Sbox[b] for b in rotated]
            key_html += f"""
                    <li>SubBytes (S-box)<br>
                    → [{', '.join(f'{hex(b)}' for b in substituted)}]</li>
            """

            original_first_byte = substituted[0]
            substituted[0] ^= Rcon[i]
            key_html += f"""
                    <li>XOR with Rcon [{hex(Rcon[i])}, 0x00, 0x00, 0x00]<br>
                    → [{', '.join(f'{hex(b)}' for b in substituted)}]</li>
            """

            # Generate the first column of the new round key
            new_key = [[0 for _ in range(4)] for _ in range(4)]

            for j in range(4):
                new_key[j][0] = round_keys[i][j][0] ^ substituted[j]

            key_html += f"""
                    <li>w4 = w0 ⊕ result<br>
                    → [{', '.join(f'{hex(new_key[j][0])}' for j in range(4))}]</li>
            """

            # Generate the remaining columns
            for col in range(1, 4):
                for row in range(4):
                    new_key[row][col] = round_keys[i][row][col] ^ new_key[row][col-1]

                key_html += f"""
                    <li>w{col+4} = w{col} ⊕ w{col+3}<br>
                    → [{', '.join(f'{hex(new_key[j][col])}' for j in range(4))}]</li>
                """

            key_html += f"""
                </ol>

                <h4>✅ Output: Round Key {i+1}</h4>
                <div class="key-matrix">
                    <table>
                        <tr>
                            <th>w4</th><th>w5</th><th>w6</th><th>w7</th>
                        </tr>
                        <tr>
                            <td>{hex(new_key[0][0])}</td>
                            <td>{hex(new_key[0][1])}</td>
                            <td>{hex(new_key[0][2])}</td>
                            <td>{hex(new_key[0][3])}</td>
                        </tr>
                        <tr>
                            <td>{hex(new_key[1][0])}</td>
                            <td>{hex(new_key[1][1])}</td>
                            <td>{hex(new_key[1][2])}</td>
                            <td>{hex(new_key[1][3])}</td>
                        </tr>
                        <tr>
                            <td>{hex(new_key[2][0])}</td>
                            <td>{hex(new_key[2][1])}</td>
                            <td>{hex(new_key[2][2])}</td>
                            <td>{hex(new_key[2][3])}</td>
                        </tr>
                        <tr>
                            <td>{hex(new_key[3][0])}</td>
                            <td>{hex(new_key[3][1])}</td>
                            <td>{hex(new_key[3][2])}</td>
                            <td>{hex(new_key[3][3])}</td>
                        </tr>
                    </table>
                </div>
                <p>Each round key is built by extending and transforming the previous key using a combination of rotation, substitution (S-box), and XOR logic.</p>
            </div>
            """

            # Add the detailed HTML explanation as a single log entry
            log.append((f"Round {i+1} Key Generation Detailed", key_html))

            # Also keep the original log entries for compatibility
            log.append((f"Last column of previous round key", f"[{', '.join(f'0x{b:02X}' for b in last_col)}]"))
            log.append((f"After rotation (RotWord)", f"[{', '.join(f'0x{b:02X}' for b in rotated)}]"))
            log.append((f"After S-box substitution (SubWord)", f"[{', '.join(f'0x{b:02X}' for b in substituted)}]"))
            log.append((f"XOR first byte with round constant (Rcon[{i}]=0x{Rcon[i]:02X})", 
                       f"0x{original_first_byte:02X} ⊕ 0x{Rcon[i]:02X} = 0x{substituted[0]:02X}"))
            log.append((f"Generate first column of round key {i+1}", f"Applying transformations to generate the first column"))

            for j in range(4):
                log.append((f"Word[0][{j}] = PrevKey[{j}][0] ⊕ Temp[{j}]", 
                           f"0x{round_keys[i][j][0]:02X} ⊕ 0x{substituted[j]:02X} = 0x{new_key[j][0]:02X}"))

            log.append((f"Generate remaining columns of round key {i+1}", f"Generating columns 1-3 using XOR operations"))

            for col in range(1, 4):
                for row in range(4):
                    log.append((f"Word[{col}][{row}] = PrevKey[{row}][{col}] ⊕ Word[{col-1}][{row}]", 
                               f"0x{round_keys[i][row][col]:02X} ⊕ 0x{new_key[row][col-1]:02X} = 0x{new_key[row][col]:02X}"))
        else:
            # Take the last column of the previous round key
            last_col = [round_keys[i][j][3] for j in range(4)]

            # Rotate, substitute, and XOR with round constant
            rotated = rotate_word(last_col)
            substituted = [Sbox[b] for b in rotated]
            substituted[0] ^= Rcon[i]

            # Generate the first column of the new round key
            new_key = [[0 for _ in range(4)] for _ in range(4)]
            for j in range(4):
                new_key[j][0] = round_keys[i][j][0] ^ substituted[j]

            # Generate the remaining columns
            for col in range(1, 4):
                for row in range(4):
                    new_key[row][col] = round_keys[i][row][col] ^ new_key[row][col-1]

        round_keys.append(new_key)

    return round_keys

def matrix_to_html(matrix):
    """
    Convert a matrix to an HTML table representation.
    """
    html = "<table border='1'>"
    for row in matrix:
        html += "<tr>"
        for cell in row:
            html += f"<td>{hex(cell)}</td>"
        html += "</tr>"
    html += "</table>"
    return html

def matrices_to_process_html(original, transformed, transformation_name):
    """
    Create HTML to display before and after matrices for a transformation.
    """
    html = "<div>"
    html += "<h4>Before</h4>" + matrix_to_html(original)
    html += f"<h4>{transformation_name}</h4> → "
    html += "<h4>After</h4>" + matrix_to_html(transformed)
    html += "</div>"
    return html

def encrypt_aes(plaintext, key):
    """
    Perform full AES-128 encryption on the given plaintext using the given key.
    """
    # Convert plaintext to matrix
    state = bytes_to_matrix(plaintext)

    # Generate all round keys in advance
    round_keys = expand_key(key)

    # Round 0: AddRoundKey
    state = add_round_key(state, round_keys[0], [])

    # Rounds 1-9
    for round_idx in range(1, 10):
        state = sub_bytes(state, [])
        state = shift_rows(state, [])
        state = mix_columns(state, [])
        state = add_round_key(state, round_keys[round_idx], [])

    # Round 10 (Final)
    state = sub_bytes(state, [])
    state = shift_rows(state, [])
    state = add_round_key(state, round_keys[10], [])

    # Convert back to bytes
    return matrix_to_bytes(state)
