## BUILDING

The only required build dependency is PyQt6 (dev tools).

On Debian and Ubuntu, use these commands to install all build and run-time dependencies:

```
[sudo] apt-get install python3-dbus python3-pyqt6 pyqt6-dev-tools
```

After building the `pyqt6-dev-tools` package is no longer needed.

Optional but recommended run-time dependency:

 - a2jmidid
 - alsa-utils (for the `aplay` and `arecord` utilities, used to fill list of ALSA devices)

# INSTALLING

To install J2SC, simply run as usual:

```
make
[sudo] make install
```

You can run J2SC without installing, by using instead:

```
make && ./src/j2sc.py
```

Packagers can make use of the 'PREFIX' and 'DESTDIR' variable during install, like this:

```
make install PREFIX=/usr DESTDIR=$(pwd)/test-dir
```
