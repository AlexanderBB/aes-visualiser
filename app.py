from awsgi import response
from flask import Flask, request, render_template
import binascii

app = Flask(__name__)

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


# Helper Functions

def pad(data):
    length = 16 - (len(data) % 16)
    return data + bytes([length]) * length


def bytes_to_matrix(text):
    return [list(text[i:i + 4]) for i in range(0, len(text), 4)]


def matrix_to_bytes(matrix):
    return bytes(sum(matrix, []))


def sub_bytes(state, log):
    new_state = []
    for row in state:
        new_row = []
        for b in row:
            transformed = Sbox[b]
            log.append((f"0x{b:02X}", f"SBox = 0x{transformed:02X}"))
            new_row.append(transformed)
        new_state.append(new_row)
    return new_state


def shift_rows(state, log):
    shifted = [
        state[0],
        state[1][1:] + state[1][:1],
        state[2][2:] + state[2][:2],
        state[3][3:] + state[3][:3]
    ]
    for i in range(4):
        log.append((f"Row {i}", f"{[hex(x) for x in state[i]]} → {[hex(x) for x in shifted[i]]}"))
    return shifted


def add_round_key(state, round_key, log):
    new_state = []
    for r, row in enumerate(state):
        new_row = []
        for c, b in enumerate(row):
            xored = b ^ round_key[r][c]
            log.append((f"0x{b:02X} XOR 0x{round_key[r][c]:02X}", f"= 0x{xored:02X}"))
            new_row.append(xored)
        new_state.append(new_row)
    return new_state


def matrix_to_html(matrix):
    html = "<table border='1' style='border-collapse: collapse; margin: 0 auto; padding: 10px;'>"
    for row in matrix:
        html += "<tr>"
        for cell in row:
            hex_value = f"0x{format(cell, '02X')}"
            html += f"<td style='padding:8px;text-align:center;'>{hex_value}</td>"
        html += "</tr>"
    html += "</table>"
    return html


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        key = request.form['key']
        word = request.form['word']

        print(f"Received key: {key}")
        print(f"Received word: {word}")

        error = None
        if not key or not word:
            error = "Key and Word fields cannot be empty."
        elif len(key) > 32:
            error = "Key is too long! Maximum 32 bytes for AES-256."
        elif len(word) > 32:
            error = "Word is too long! Should be 16-32 bytes."

        if error:
            print(f"Error detected: {error}")
            return render_template('landing.html', error=error)

        key = pad(key.encode('utf-8'))[:16]
        word = pad(word.encode('utf-8'))[:16]

        print(f"Padded key: {key}")
        print(f"Padded word: {word}")

        steps = []

        try:
            state = bytes_to_matrix(word)
            key_matrix = bytes_to_matrix(key)

            # Step 1
            explanation_word = [(f"Char '{chr(ch)}'", f"ASCII 0x{ch:02X}") for ch in word]
            steps.append({
                'title': '🛠️ Step 1: Transform Word to Hex Matrix',
                'matrix_html': matrix_to_html(state),
                'explanation_rows': explanation_word,
                'id_suffix': 'exp0',
                'description': 'Converts the input word into a 4x4 hexadecimal matrix, preparing it for AES operations.',
            })

            # Step 2
            explanation_key = [(f"Char '{chr(ch)}'", f"ASCII 0x{ch:02X}") for ch in key]
            steps.append({
                'title': '🛠️ Step 2: Transform Key to Hex Matrix',
                'matrix_html': matrix_to_html(key_matrix),
                'explanation_rows': explanation_key,
                'id_suffix': 'exp1',
                'description': 'Converts the encryption key into a 4x4 hexadecimal matrix for use in encryption rounds.',
            })

            # Step 3
            log = []
            state = add_round_key(state, key_matrix, log)
            steps.append({
                'title': '🔒 Step 3: AddRoundKey (Initial XOR)',
                'matrix_html': matrix_to_html(state),
                'explanation_rows': log,
                'id_suffix': 'exp2',
                'description': 'XORs the plaintext matrix with the key matrix to start the encryption process.',
            })

            # Step 4
            log = []
            state = sub_bytes(state, log)
            steps.append({
                'title': '🔁 Step 4: SubBytes (Replace Values)',
                'matrix_html': matrix_to_html(state),
                'explanation_rows': log,
                'id_suffix': 'exp3',
                'description': 'Each byte is substituted using the AES S-Box to introduce non-linearity (confusion).',
            })

            # Step 5
            log = []
            state = shift_rows(state, log)
            steps.append({
                'title': '🔃 Step 5: ShiftRows (Mix Rows)',
                'matrix_html': matrix_to_html(state),
                'explanation_rows': log,
                'id_suffix': 'exp4',
                'description': 'Rows of the matrix are cyclically shifted to create diffusion.',
            })

            # Step 6
            log = []
            state = add_round_key(state, key_matrix, log)
            steps.append({
                'title': '🔒 Step 6: AddRoundKey (XOR Again)',
                'matrix_html': matrix_to_html(state),
                'explanation_rows': log,
                'id_suffix': 'exp5',
                'description': 'Another XOR operation with the key matrix to further mix the state.',
            })

            # Step 7
            final_bytes = matrix_to_bytes(state)
            steps.append({
                'title': '🎯 Step 7: Final Encrypted Output',
                'matrix_html': '',
                'explanation_rows': [("Final Hex Output", binascii.hexlify(final_bytes).decode())],
                'id_suffix': 'finalexp6',
                'description': 'The final encrypted output is combined into a hexadecimal string.',
            })

            # Add animation delay for each step
            for idx, step in enumerate(steps):
                step['animation_delay'] = f"{0.5 * idx}s"

            print(f"Total steps created: {len(steps)}")
        except Exception as e:
            print(f"Error during encryption: {e}")
            error = "Internal error during encryption."
            return render_template('landing.html', error=error)

        return render_template('visualize.html', steps=steps)

    return render_template('landing.html')


if __name__ == '__main__':
    app.run(debug=True)


def normalize_event(event):
    """Normalize AWS Function URL event to API Gateway v1 style."""
    if "httpMethod" not in event and "requestContext" in event and "http" in event["requestContext"]:
        event["httpMethod"] = event["requestContext"]["http"]["method"]
        event["path"] = event["rawPath"]
        event["queryStringParameters"] = {}
        event["headers"] = event.get("headers", {})
    return event


def handler(event, context):
    event = normalize_event(event)
    return response(app, event, context)