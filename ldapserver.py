import ldap
import hashlib
def hash_password(password):
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        return hashed_password
class LDAPServer:
    ou_dn = 'ou=users,dc=python666,dc=local'

    def __init__(self):
        self.ldap_connection = None

    def ldap_initialize(self):
        ldap_server = 'ldap://192.168.162.135'
        ldap_base_dn = 'dc=python666,dc=local'
        ldap_admin_dn = 'cn=admin,dc=python666,dc=local'
        ldap_admin_password = 'looklook11'

        try:
            self.ldap_connection = ldap.initialize(ldap_server)
            self.ldap_connection.simple_bind_s(ldap_admin_dn, ldap_admin_password)
            print("LDAP Connection initialized!")
            return self.ldap_connection, ldap_base_dn
        except ldap.LDAPError as e:
            print(f"Error initializing LDAP connection: {e}")
            return None, None

    def add_user_to_ldap(self, user_data):
        if not self.ldap_connection:
            self.ldap_initialize()

        try:
            attrs = [
                ('objectClass', [b'top', b'person', b'organizationalPerson', b'inetOrgPerson']),
                ('uid', user_data['login'].encode('utf-8')),
                ('cn', f'{user_data["first_name"]} {user_data["last_name"]}'.encode('utf-8')),
                ('sn', user_data['last_name'].encode('utf-8')),
                ('givenName', user_data['first_name'].encode('utf-8')),
                ('mail', user_data['email'].encode('utf-8')),
                ('userPassword', hash_password(user_data['password']).encode('utf-8')),
            ]

            dn = f'cn={user_data["login"]},{self.ou_dn}'

            self.ldap_connection.add_s(dn, attrs)
            print(f"User {user_data['login']} successfully added to the LDAP server.")
        except ldap.LDAPError as e:
            print(f"Error adding user to the LDAP server: {e}")

    def get_all_users(self):
        if not self.ldap_connection:
            self.ldap_initialize()

        try:
            search_filter = '(objectClass=inetOrgPerson)'
            attributes = ['uid', 'cn', 'sn', 'givenName', 'mail']
            result = self.ldap_connection.search_s(self.ou_dn, ldap.SCOPE_SUBTREE, search_filter, attributes)
            users = [entry[1] for entry in result if isinstance(entry, tuple)]
            return users
        except ldap.LDAPError as e:
            print(f"Error fetching users from the LDAP server: {e}")
            return []

    def close_connection(self):
        if self.ldap_connection:
            self.ldap_connection.unbind_s()
            print("LDAP Connection closed")


