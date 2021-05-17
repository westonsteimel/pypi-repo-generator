import os
import requests
import shutil
from bs4 import BeautifulSoup, Comment

packages = {
    'awscli',
    'awslambdaric',
    'aws-xray-sdk',
    'backcall',
    'boto3',
    'botocore',
    'certifi',
    'cffi',
    'chardet',
    'click',
    'colorama',
    'cryptography',
    'cycler',
    'decorator',
    'dnspython',
    'docutils',
    'dparse',
    'fastapi',
    'future',
    'greenlet',
    'gunicorn',
    'h11',
    'httpie',
    'idna',
    'ipykernel',
    'ipython',
    'ipython-genutils',
    'jedi',
    'jinja2',
    'jmespath',
    'jupyter-client',
    'jupyter-console',
    'jupyter-core',
    'kiwisolver',
    'mangum',
    'markupsafe',
    'matplotlib',
    'matplotlib-inline',
    'more-itertools',
    'moto',
    'orjson',
    'packaging',
    'parso',
    'pexpect',
    'pickleshare',
    'pillow',
    'pip',
    'pluggy',
    'prompt-toolkit',
    'ptyprocess',
    'py',
    'pyasn1',
    'pycparser',
    'pygments',
    'pymongo',
    'pymssql',
    'pyparsing',
    'pysocks',
    'pytest',
    'python-dateutil',
    'pytz',
    'pyyaml',
    'pyzmq',
    'requests',
    'requests-toolbelt',
    'responses',
    'rsa',
    's3fs',
    's3transfer',
    'safety',
    'setuptools',
    'shellingham',
    'simplejson',
    'six',
    'sqlalchemy',
    'starlette',
    'toml',
    'tornado',
    'traitlets',
    'typer',
    'typing-extensions',
    'urllib3',
    'uvicorn',
    'wcwidth',
    'werkzeug',
    'wrapt',
    'xmltodict',
    'zipp',
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

