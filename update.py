import os
import requests
import shutil
from bs4 import BeautifulSoup, Comment

packages = {
    'awscli',
    'awslambdaric',
    'boto3',
    'botocore',
    'certifi',
    'cffi',
    'chardet',
    'click',
    'colorama',
    'cryptography',
    'dnspython',
    'docutils',
    'dparse',
    'fastapi',
    'greenlet',
    'gunicorn',
    'h11',
    'httpie',
    'idna',
    'jinja2',
    'jmespath',
    'mangum',
    'markupsafe',
    'orjson',
    'packaging',
    'pip',
    'pyasn1',
    'pycparser',
    'pygments',
    'pymongo',
    'pymssql',
    'pyparsing',
    'pysocks',
    'python-dateutil',
    'pytz',
    'pyyaml',
    'requests',
    'requests-toolbelt',
    'rsa',
    's3transfer',
    'safety',
    'setuptools',
    'simplejson',
    'six',
    'sqlalchemy',
    'starlette',
    'toml',
    'typing-extensions',
    'urllib3',
    'uvicorn',
}

custom_packages = set(os.listdir('packages'))

for custom_package in custom_packages:
    packages.add(custom_package)

with open('index.html.template', 'r') as index:
    index_soup = BeautifulSoup(index, features='html.parser')

outdir = './.publish'
os.makedirs(outdir, exist_ok=True)

for package in sorted(packages):
    os.makedirs(f'{outdir}/{package}', exist_ok=True)
    index_entry = index_soup.find(name='a', string=package)

    if not index_entry:
        if package not in custom_packages:
            pypi_url = f'https://pypi.org/simple/{package}/'
            pypi_html = requests.get(pypi_url).content
            soup = BeautifulSoup(pypi_html, features='html.parser')
            soup.insert(1, Comment(\
                f'This file is replicated from {pypi_url}. Do not update directly as updates will be overwritten when the page is updated on PyPi.'))

            with open(f'{outdir}/{package}/index.html', 'w+') as package_index:
                package_index.write(str(soup))
        else:
            shutil.copytree(f'packages/{package}/', f'{outdir}/{package}/', dirs_exist_ok=True)

    index_entry = index_soup.new_tag('a', href=f'/pypi-repo/{package}/')
    index_entry.string = package
    index_entry.append(index_soup.new_tag('br'))
    index_soup.html.body.append(index_entry)
    index_soup.html.body.append('\n')

with open(f'{outdir}/index.html', 'w+') as index_html:
    index_html.write(str(index_soup))

for directory in os.listdir(f'{outdir}'):
    if os.path.isdir(f'{outdir}/{directory}'):
        if directory not in packages and directory not in ['.git', '.github']:
            print(f'Removing {outdir}/{directory}/')
            shutil.rmtree(f'{outdir}/{directory}')

