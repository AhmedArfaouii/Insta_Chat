import pika
import ldap
import hashlib

ou_dn = 'ou=users,dc=python666,dc=local'


def get_user_info():
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


def hash_password(password):
    # Hacher le mot de passe avec SHA-256
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return hashed_password

def ldap_initialize():
    # Configurations LDAP
    ldap_server = 'ldap://192.168.162.135'
    ldap_base_dn = 'dc=python666,dc=local'
    ldap_admin_dn = 'cn=admin,dc=python666,dc=local'
    ldap_admin_password = 'looklook11'

    try:
        # Initialiser la connexion au serveur LDAP
        ldap_conn = ldap.initialize(ldap_server)
        ldap_conn.simple_bind_s(ldap_admin_dn, ldap_admin_password)
        print("Ldap Connexion initialized!")
        return ldap_conn, ldap_base_dn
    except ldap.LDAPError as e:
        print(f"Erreur lors de l'initialisation de la connexion LDAP : {e}")
        return None, None

def add_user_to_ldap(ldap_conn, ldap_base_dn):
    user_data = get_user_info()
    try:
        # Définir les attributs LDAP pour le nouvel utilisateur
        attrs = [
            ('objectClass', [b'top', b'person', b'organizationalPerson', b'inetOrgPerson']),
            ('uid', user_data['login'].encode('utf-8')),
            ('cn', f'{user_data["first_name"]} {user_data["last_name"]}'.encode('utf-8')),
            ('sn', user_data['last_name'].encode('utf-8')),
            ('givenName', user_data['first_name'].encode('utf-8')),
            ('mail', user_data['email'].encode('utf-8')),
            ('userPassword', hash_password(user_data['password']).encode('utf-8')),
            # Ajoutez d'autres attributs LDAP en fonction de votre schéma
        ]

        # Définir le DN (Distinguished Name) pour le nouvel utilisateur
        dn = f'cn={user_data["login"]},{ou_dn}'

        # Ajouter l'utilisateur au serveur LDAP
        ldap_conn.add_s(dn, attrs)
        print(f"Utilisateur {user_data['login']} ajouté avec succès au serveur LDAP.")
    except ldap.LDAPError as e:
        print(f"Erreur lors de l'ajout de l'utilisateur au serveur LDAP: {e}")

def authenticate_user(ldap_conn):
    login = input ("Enter your login: ")
    initial_password = input ("Enter your password: ")
    
    try:
        # Rechercher l'utilisateur dans le serveur LDAP
        base_dn = 'dc=python666,dc=local'
        search_filter = f'(uid={login})'
        result = ldap_conn.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter)

        if not result:
            print("Utilisateur non trouvé.")
            return False

        # Récupérer le mot de passe haché de l'utilisateur dans le serveur LDAP
        stored_password = result[0][1]['userPassword'][0].decode('utf-8')
        
        # Hacher le mot de passe fourni pour l'authentification
        hashed_password = hash_password(initial_password)

        # Vérifier si les mots de passe correspondent
        if stored_password == hashed_password:
            print("Authentification réussie.")
            return True
        else:
            print("Authentification échouée.")
            return False
    except ldap.LDAPError as e:
        print(f"Erreur lors de l'authentification de l'utilisateur: {e}")
        return False
def check_rabbitmq_connection():
    try:
        # Define RabbitMQ connection parameters with credentials
        login = input ("Enter your login : ")
        intial_password = input ("Enter your password : ")
        password = hash_password (intial_password)
        credentials = pika.PlainCredentials(login, password)
        parameters = pika.ConnectionParameters('localhost', 5672, '/', credentials)

        # Establish a connection to RabbitMQ
        connection = pika.BlockingConnection(parameters)
        connection.close()  # Close the connection if successful
        print("Connection to RabbitMQ established successfully: All good!")
    except Exception as e:
        print(f"Failed to connect to RabbitMQ: {e}")


# ldap_conn,ldap_base_dn= ldap_initialize()
#add_user_to_ldap(ldap_conn,ldap_base_dn)
#authenticate_user(ldap_conn)
#check_rabbitmq_connection()


