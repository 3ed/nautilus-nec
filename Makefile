PREFIX ?= $(HOME)/.local
INSTALL_PATH = $(DESTDIR)$(PREFIX)/share/nautilus-python/extensions

all:

install:   $(patsubst nec-%.py,install-%,  $(notdir $(wildcard src/nec-*.py)))
uninstall: $(patsubst nec-%.py,uninstall-%,$(notdir $(wildcard $(INSTALL_PATH)/nec-*.py)))

pycache:
	python -m compileall src

clean:
	rm -rf src/__pycache__/ || true

install-%:
	install -dm755 $(INSTALL_PATH)/__pycache__/
	install -m755 src/nec-$*.py $(INSTALL_PATH)/
	test -f src/__pycache__/nec-$*.*.pyc && install -m755 src/__pycache__/nec-$*.*.pyc $(INSTALL_PATH)/__pycache__/ || true

uninstall-%:
	rm $(INSTALL_PATH)/nec-$*.py || true
	rm $(INSTALL_PATH)/__pycache__/nec-$*.*.pyc || true
