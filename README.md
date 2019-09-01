# South Bay Supercontest

## Stack

* Language: Python 3
* Application: Flask
* Server: uWSGI <img src="https://www.fullstackpython.com/img/logos/uwsgi.png" width="20">
* Proxy: nginx <img src="https://logo.clearbit.com/nginx.com" width="20">
* Database: PostgreSQL <img src="https://logo.clearbit.com/postgresql.org" width="20">
* Frontend: Bootstrap 4 <img src="https://logo.clearbit.com/getbootstrap.com" width="20">
* API: GraphQL <img src="https://logo.clearbit.com/graphql.org" width="20">
* Migration: Alembic <img src="https://logo.clearbit.com/python.org" width="20">
* Composition: Docker <img src="https://logo.clearbit.com/docker.com" width="20">
* Deployment: Ansible <img src="https://logo.clearbit.com/ansible.com" width="20">

<img src="https://logo.clearbit.com/python.org" width="20" style="display: inline;">
<img src="https://flask.palletsprojects.com/en/1.1.x/_static/flask-icon.png" width="20" style="display: inline;">

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
    session.post(root_url + '/user/sign-in', data=creds, headers=dict(referer=response.url))
    response = session.get(root_url + '/graphql', json=dict(query=query))
data = response.json()
```

<a href="https://clearbit.com">Logos provided by Clearbit</a>
