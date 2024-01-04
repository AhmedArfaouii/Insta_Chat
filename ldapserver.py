import pika
import ldap
import hashlib

class LDAPServer:
    
    ou_dn = 'ou=users,dc=python666,dc=local'
    def __init__(self):
        self.ldap_connection = None

    def get_user_info(self):
        print("Please enter user information:")
        login = input("Login: ")
        first_name = input("First Name: ")
        last_name = input("Last Name: ")
        email = input("Email: ")
        password = input("Password: ")  # Consider using getpass.getpass() for password input

        user_data = {
            'login': login,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': password
        }

        return user_data

    def hash_password(self, password):
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return hashed_password

    def ldap_initialize(self):
        ldap_server = 'ldap://192.168.162.135'
        ldap_base_dn = 'dc=python666,dc=local'
        ldap_admin_dn = 'cn=admin,dc=python666,dc=local'
        ldap_admin_password = 'looklook11'

        try:
            ldap_conn = ldap.initialize(ldap_server)
            ldap_conn.simple_bind_s(ldap_admin_dn, ldap_admin_password)
            print("LDAP Connection initialized!")
            return ldap_conn, ldap_base_dn
        except ldap.LDAPError as e:
            print(f"Error initializing LDAP connection: {e}")
            return None, None

    def add_user_to_ldap(self, ldap_conn, ldap_base_dn):
        user_data = self.get_user_info()
        try:
            attrs = [
                ('objectClass', [b'top', b'person', b'organizationalPerson', b'inetOrgPerson']),
                ('uid', user_data['login'].encode('utf-8')),
                ('cn', f'{user_data["first_name"]} {user_data["last_name"]}'.encode('utf-8')),
                ('sn', user_data['last_name'].encode('utf-8')),
                ('givenName', user_data['first_name'].encode('utf-8')),
                ('mail', user_data['email'].encode('utf-8')),
                ('userPassword', self.hash_password(user_data['password']).encode('utf-8')),
            ]

            dn = f'cn={user_data["login"]},{self.ou_dn}'

            ldap_conn.add_s(dn, attrs)
            print(f"User {user_data['login']} successfully added to the LDAP server.")
        except ldap.LDAPError as e:
            print(f"Error adding user to the LDAP server: {e}")

    def authenticate_user(self, ldap_conn):
        login = input("Enter your login: ")
        initial_password = input("Enter your password: ")

        try:
            base_dn = 'dc=python666,dc=local'
            search_filter = f'(uid={login})'
            result = ldap_conn.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter)

            if not result:
                print("User not found.")
                return False

            stored_password = result[0][1]['userPassword'][0].decode('utf-8')
            hashed_password = self.hash_password(initial_password)

            if stored_password == hashed_password:
                print("Authentication successful.")
                return True
            else:
                print("Authentication failed.")
                return False
        except ldap.LDAPError as e:
            print(f"Error authenticating user: {e}")
            return False

    def check_rabbitmq_connection(self):
        try:
            login = input("Enter your login: ")
            initial_password = input("Enter your password: ")
            password = self.hash_password(initial_password)
            credentials = pika.PlainCredentials(login, password)
            parameters = pika.ConnectionParameters('localhost', 5672, '/', credentials)

            connection = pika.BlockingConnection(parameters)
            connection.close()
            print("Connection to RabbitMQ established successfully: All good!")
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")

    def close_connection(self):
        if self.ldap_connection:
            self.ldap_connection.unbind_s()
            print("LDAP Connection closed")



# # Create an instance of the LDAPServer class
# ldap_server = LDAPServer()

# # Initialize LDAP connection
# ldap_connection, ldap_base_dn = ldap_server.ldap_initialize()

# # Add user to LDAP
# if ldap_connection:
#     ldap_server.add_user_to_ldap(ldap_connection, ldap_base_dn)

# # Close LDAP connection
# ldap_server.close_connection()
