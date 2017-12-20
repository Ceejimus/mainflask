from domain import AuthDomain

HOST = "192.168.0.104"
PORT = 5432
DB = "main"
USER = "postgres"
PASS = "postgres"

auth_domain = AuthDomain(HOST, PORT, DB, USER, PASS)

auth_domain.add_user('testuser', "testuser@test.com", 'testpass')

token = auth_domain.login('testuser', 'testpass')

print("Testing Token: {}".format(token))
print("Token is {}", "valid" if auth_domain.is_token_valid(token) else "invalid")

auth_domain.delete_user('testuser')
