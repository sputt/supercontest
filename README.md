# South Bay Supercontest

## Stack

* Language: Python 3
* Framework: Flask/WSGI
* Backend: PostgreSQL
* Server: nginx
* API: GraphQL
* Composition: Docker
* Deployment: Ansible
* Migration: Alembic

## Queries

I have chosen to enable GraphiQL on [southbaysupercontest](https://southbaysupercontest.com) because it is protected
by auth and CSRF. It's a valuable tool for users. [You may explore the data here](https://southbaysupercontest.com/graphql).

In order to fetch data programmatically, you must provide the auth and CSRF token.
Here is an example using basic HTTP requests (although Selenium and other heavy-handed
browser solutions work as well):

```python
# Credentials and query. This is the only section you need to modify.
creds = dict(email='myemail@domain.com', password='mypassword')
query = """
{
  users {
    email
  }
}
"""

# Fetch the data. A supercontest python client (like gql) could be released in the future.
import requests, bs4
root_url = 'https://southbaysupercontest.com'
with requests.session() as session:
    response = session.get(root_url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find(id='csrf_token')['value']
    creds['csrf_token'] = csrf_token
    session.post(root_url + '/user/sign-in', data=creds)
    response = session.get(root_url + '/graphql', json=dict(query=query))
data = response.json()
```
