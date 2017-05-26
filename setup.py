from setuptools import setup

setup(
    name='tvnao',
    version='0.7',
    description='tv here and now',
    long_description='a tool for watching IP TV, shows TV guide',
    author='blaze',
    author_email='blaze@vivaldi.net',
    url='https://bitbucket.org/blaze/tvnao',
    packages=['tvnao'],
    keywords='iptv, tvguide, epg, mpv, mlayer, qt',
    license="GPL-3",
    entry_points={
        'gui_scripts': [ 'tvnao = tvnao.tvnao:main' ]
    },
)
