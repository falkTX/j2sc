# INSTALL for J2SC

To install J2SC, simply run as usual:

```
make`
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

## BUILD DEPENDENCIES

The only required build dependencies is PyQt6.

On Debian and Ubuntu, use these commands to install all build dependencies:

```
[sudo] apt-get install python3-dbus python3-pyqt6 pyqt6-dev-tools
```

Optional but recommended:

 - a2jmidid
