import requests
import bs4

def query(email, password, query):
    """Runs a single query in a single session to fetch supercontest data
    programatically. It first uses your credentials to retrieve a valid
    CSRF token, then runs the query against the graphql endpoint.

    Args:
        email (str): Your email credential
        password (str): Your password credential (this is passed
            encrypted over https)
        query (str): The graphql query string to run

    Returns:
        (json) The data your query returned
    """
    creds = dict(email=email, password=password)
    root_url = 'https://southbaysupercontest.com'

    with requests.session() as session:
        response = session.get(root_url)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find(id='csrf_token')['value']
        creds['csrf_token'] = csrf_token
        session.post(root_url + '/user/sign-in',
                     data=creds,
                     headers=dict(referer=response.url))
        response = session.get(root_url + '/graphql',
                               json=dict(query=query))
    data = response.json()

    return data
