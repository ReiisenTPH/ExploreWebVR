import http.server
import ssl

# Port dla HTTPS
PORT = 5000

class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Wymagane nagłówki dla WebXR i SharedArrayBuffer w Godocie
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        super().end_headers()

server_address = ('0.0.0.0', PORT)
httpd = http.server.HTTPServer(server_address, HTTPRequestHandler)

# Konfiguracja szyfrowania SSL (używamy wygenerowanego certyfikatu i klucza)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print(f"Serwer HTTPS wystartował na https://192.168.1.10:{PORT}")
httpd.serve_forever()