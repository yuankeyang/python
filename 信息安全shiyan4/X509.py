#yang
#自签证书的生成
from OpenSSL import crypto,SSL
from time import gmtime
CERT_FILE="yang_selfsigned.crt"
PRIVATE_KEY_FILE="private.key"
PUBLIC_KEY_FILE="public.key"

def create_selfsigned():
    #创建一个密钥对
    k=crypto.PKey()
    k.generate_key(crypto.TYPE_RSA,1024)
    #证书
    cert=crypto.X509()
    #cert.get_subject().C="China"
    cert.get_subject().ST="Hunan"
    cert.get_subject().L="Changsha"
    cert.get_subject().O="HNU"
    cert.get_subject().OU="HNU"
    cert.get_subject().CN="201208010127"
    cert.set_serial_number(8888)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10*365*24*60*60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha1')
    #输出证书、密钥、公钥
    open(CERT_FILE, "wb").write(
        crypto.dump_certificate(crypto.FILETYPE_PEM,cert))
    open(PRIVATE_KEY_FILE, "wb").write(
        crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
    open(PUBLIC_KEY_FILE,"wb").write(
        crypto.dump_privatekey(crypto.FILETYPE_PEM, cert.get_pubkey()))
    print("hash value is:")
    print(cert.subject_name_hash())

create_selfsigned()
