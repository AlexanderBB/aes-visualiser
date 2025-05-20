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

Rcon = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]  # Round constants


# Helper functions
def pad(data):
    length = 16 - (len(data) % 16)
    return data + bytes([length]) * length


def bytes_to_matrix(text):
    return [[text[j * 4 + i] for j in range(4)] for i in range(4)]


def matrix_to_bytes(matrix):
    return bytes(sum(matrix, []))


def sub_bytes(state, log):
    return [[Sbox[b] for b in row] for row in state]


def shift_rows(state, log):
    shifted = [
        state[0],
        state[1][1:] + state[1][:1],
        state[2][2:] + state[2][:2],
        state[3][3:] + state[3][:3]
    ]
    log.append(("ShiftRows Transformation", shifted))
    return shifted


def mix_columns(state, log):
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
    for col in range(4):
        for row in range(4):
            new_state[row][col] = (
                galois_mult(state[0][col], mix_matrix[row][0]) ^
                galois_mult(state[1][col], mix_matrix[row][1]) ^
                galois_mult(state[2][col], mix_matrix[row][2]) ^
                galois_mult(state[3][col], mix_matrix[row][3])
            )
            log.append((
                f"Column {col}, Row {row}",
                f"Result: 0x{new_state[row][col]:02X}"
            ))
    return new_state


def add_round_key(state, round_key, log):
    return [[state[i][j] ^ round_key[i][j] for j in range(4)] for i in range(4)]


def rotate_word(word):
    return word[1:] + word[:1]


def generate_round_key(cipher_key, round_index, log):
    words = [[cipher_key[j * 4 + i] for j in range(4)] for i in range(4)]
    temp = rotate_word(words[-1])
    log.append(("Rotate Word", temp))
    temp = [Sbox[b] for b in temp]
    temp[0] ^= Rcon[round_index - 1]
    round_key = [temp]
    for i in range(1, 4):
        round_key.append([round_key[i - 1][j] ^ words[i][j] for j in range(4)])
    return round_key


def matrix_to_html(matrix):
    html = "<table border='1'>"
    for row in matrix:
        html += "<tr>"
        for cell in row:
            html += f"<td>{hex(cell)}</td>"
        html += "</tr>"
    html += "</table>"
    return html


def matrices_to_process_html(original, transformed, transformation_name):
    html = "<div>"
    html += "<h4>Before</h4>" + matrix_to_html(original)
    html += f"<h4>{transformation_name}</h4> → "
    html += "<h4>After</h4>" + matrix_to_html(transformed)
    html += "</div>"
    return html


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        key = request.form['key']
        word = request.form['word']
        error = None

        if not key or not word:
            error = "Key and word cannot be empty"
        elif len(key) > 32 or len(word) > 32:
            error = "Key or word exceeds maximum length (32 bytes)"

        if error:
            return render_template('landing.html', error=error)

        key = pad(key.encode('utf-8'))[:16]
        word = pad(word.encode('utf-8'))[:16]

        steps = []

        # Step 1: Convert word to matrix
        state = bytes_to_matrix(word)
        steps.append({
            'title': 'Step 1: Word to Matrix',
            'matrix_html': matrix_to_html(state),
            'description': 'Converting the input plaintext to a matrix.'
        })

        # Step 2: Convert key to matrix
        key_matrix = bytes_to_matrix(key)
        steps.append({
            'title': 'Step 2: Key to Matrix',
            'matrix_html': matrix_to_html(key_matrix),
            'description': 'Converting the encryption key to a matrix.'
        })

        # Step 3: Initial AddRoundKey
        state = add_round_key(state, key_matrix, [])
        steps.append({
            'title': 'Step 3: Initial AddRoundKey',
            'matrix_html': matrix_to_html(state),
            'description': 'XORing the plaintext matrix with the encryption key matrix.'
        })

        # Step 4: SubBytes
        state = sub_bytes(state, [])
        steps.append({
            'title': 'Step 4: SubBytes',
            'matrix_html': matrix_to_html(state),
            'description': 'Substituting bytes using the AES S-box.'
        })

        # Step 5: ShiftRows
        state = shift_rows(state, [])
        steps.append({
            'title': 'Step 5: ShiftRows',
            'matrix_html': matrix_to_html(state),
            'description': 'Shifting rows to introduce diffusion.'
        })

        # Step 6: MixColumns
        log = []
        before_mix_columns = [row[:] for row in state]
        state = mix_columns(state, log)
        steps.append({
            'title': 'Step 6: MixColumns',
            'matrix_html': matrices_to_process_html(before_mix_columns, state, 'MixColumns Transformation'),
            'description': 'Mixing columns to ensure further diffusion of data.'
        })

        # Step 7: Generate First Round Key
        log = []
        round_key = generate_round_key(key, 1, log)
        steps.append({
            'title': 'Step 7: Generate Round Key',
            'matrix_html': matrix_to_html(round_key),
            'description': 'Generating the first round key by applying the AES key schedule.'
        })

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