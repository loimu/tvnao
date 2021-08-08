# tvnao

A convenience utility meant to improve IPTV watching experience with `mpv` player.

Written in Python 3 and PyQt. Supports only .m3u playlists and JTV tv guide format.

Dependencies: PyQt5

Requirements: mpv

## Running and Debugging

```bash
git clone https://github.com/loimu/tvnao.git
cd tvnao/
python3 -m pip install -r requirements.txt
python3 debug.py <playlist_url>
```

## Ubuntu

```bash
# install
sudo add-apt-repository ppa:blaze/dev
sudo apt update
sudo apt install tvnao

# run the application
tvnao <playlist_url>
```
