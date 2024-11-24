from OpenSSL import crypto
import os

def create_self_signed_cert():
    """개발용 자체 서명 인증서 생성"""
    # 인증서 저장 디렉토리 생성
    cert_dir = "certs"
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)
    
    # 키 파일과 인증서 파일 경로
    key_file = os.path.join(cert_dir, "key.pem")
    cert_file = os.path.join(cert_dir, "cert.pem")
    
    # 이미 존재하면 반환
    if os.path.exists(key_file) and os.path.exists(cert_file):
        return key_file, cert_file
    
    # 키 생성
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)
    
    # 인증서 생성
    cert = crypto.X509()
    cert.get_subject().C = "KR"
    cert.get_subject().ST = "Seoul"
    cert.get_subject().L = "Seoul"
    cert.get_subject().O = "SnapS"
    cert.get_subject().OU = "Development"
    cert.get_subject().CN = "localhost"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)  # 1년
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha256')
    
    # 파일로 저장
    with open(cert_file, "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open(key_file, "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
    
    return key_file, cert_file 