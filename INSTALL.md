# INSTALL for j2sc

To install j2sc, simply run as usual:

```
make`
[sudo] make install
```

You can run j2sc without installing, by using instead:

```
make
./src/cadence.py
```

Packagers can make use of the 'PREFIX' and 'DESTDIR' variable during install, like this:

```
make install PREFIX=/usr DESTDIR=./test-dir
```

## BUILD DEPENDENCIES

The only required build dependencies is PyQt5.

On Debian and Ubuntu, use these commands to install all build dependencies:

```
[sudo] apt-get install python3-pyqt5 python3-pyqt5.qtsvg pyqt5-dev-tools
```

To run all the apps/tools, you'll additionally need:

 - python3-dbus
 - python3-dbus.mainloop.qt

Optional but recommended:

 - a2jmidid
