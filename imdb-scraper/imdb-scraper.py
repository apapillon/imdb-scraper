import argparse
import bs4
import re
import urllib.parse
import urllib.request

url_root = 'http://www.imdb.com/'
url_find = urllib.parse.urljoin(url_root, 'find')

def get_actor_url(name):
    """
    Return Actor url if name exactly find, otherwise None.

    :param name: Nom de l'acteur recherché
    :type name: str
    :return: url de la fiche de l'acteur ou None
    :rtype: str or None
    
    :Exemple:
    
    >>> get_actor_url('will smith')
    'http://www.imdb.com/name/nm0000226/?ref_=fn_nm_nm_1'
    >>> get_actor_url('Charles Chaplin')
    'http://www.imdb.com/name/nm0000122/?ref_=fn_nm_nm_1'
    
    """
    params = urllib.parse.urlencode({'q': name, 's': 'nm', 'exact': True})
    url = '{}?{}'.format(url_find, params)

    with urllib.request.urlopen(url) as f:
        data = f.read().decode('utf-8')
        soup = bs4.BeautifulSoup(data, 'html.parser')
        
        result = soup.find('td', class_='result_text')
        if result:
            url_actor = result.a.get('href')
            return urllib.parse.urljoin(url_root, url_actor)
    return None


def get_filmography(actor_url):
    """
    Return a list of movies where actor are actor.
    
    :param actor_url: Url to actor card
    :type actor_url: string
    :return: List of movies with actor of fiche
    :rtype: list of tuple
    
    :Exemple:
    
    >>> get_filmography(None)
    []
    >>> get_filmography('http://www.imdb.com/name/nm0825757/?ref_=fn_nm_nm_1')
    []
    >>> len(get_filmography('http://www.imdb.com/name/nm0000122/'))
    88
    """
    if actor_url:
        with urllib.request.urlopen(actor_url) as f:
            data = f.read().decode('utf-8')
            soup = bs4.BeautifulSoup(data, 'html.parser')

            movies = list()
            for d in soup.find_all(id=re.compile('^actor-.*')):
                year = d.find(class_='year_column').get_text(' ', strip=True)
                name = d.b.get_text(' ', strip=True)
                movies.append((year, name))
            return movies

    return []


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Return list of film where actor are an actor (source:imdb site).')
    parser.add_argument('actor', type=str, nargs='+',
                       help='The name of the actor you want filmography')
    args = parser.parse_args()
    
    actor = ' '.join((x.capitalize() for x in args.actor))
    print('Searching actor: {} ....'.format(actor))

    actor_url = get_actor_url(args.actor)
    if actor_url:
        print(actor_url)
        print('Actor found !!!\n\nFilmography:\n')
        for year, name in get_filmography(actor_url):
            print('\t{:10} {}'.format(year, name))
        else:
            print('No films found.')
    else:
        print('Actor not found. Check the name.')

