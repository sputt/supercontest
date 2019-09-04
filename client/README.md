# Supercontest Client

I have chosen to enable GraphiQL on [southbaysupercontest](https://southbaysupercontest.com) because it is protected
by auth and CSRF. It's a valuable tool for users. [You may explore the data here](https://southbaysupercontest.com/graphql).

There is a Python client to fetch your data programmatically, similar to gql. Simply
`pip install supercontest` and then run a query like the following example:

```python
import supercontest

query = """
{
  users {
    email
  }
}
"""

data = supercontest.query(email='myemail@domain.com',
                          password='mypassword',  # your pw is encrypted over https
                          query=query)
```

Other heavy-handed solutions like Selenium also work. The endpoint simply requires
auth and a CSRF token.
