from setuptools import setup, find_packages

version = '1.0.0'

setup(
    name='ackr',
    version=version,
    author='Bart Janssens',
    author_email='bart.janssens@vito.be',
    description='Simple webUI for icinga',
    url='https://github.com/bartjanssens92/ackr',
    setup_requires=['pytest-runner>=5.2'],
    tests_require=['pytest>=5.3.1', 'requests-mock>=1.7.0', 'munch>=2.5.0'],
    install_requires=['blinker==1.7.0', 'certifi==2023.11.17', 'charset-normalizer==3.3.2', 'click==8.1.7', 'flask==3.0.1', 'Flask-Login==0.6.3', 'flask-sqlalchemy==3.1.1', 'flask-wtf==1.2.1', 'greenlet==3.0.3', 'idna==3.6', 'importlib-metadata==7.0.1', 'itsdangerous==2.1.2', 'Jinja2==3.1.3', 'ldap3==2.9.1', 'MarkupSafe==2.1.4', 'pyasn1==0.5.1', 'requests==2.31.0', 'SQLAlchemy==2.0.25', 'typing-extensions==4.9.0', 'urllib3==2.1.0', 'werkzeug==3.0.1', 'wtforms==3.1.2', 'zipp==3.17.0'],
    packages=find_packages(),
    entry_points={}
)
