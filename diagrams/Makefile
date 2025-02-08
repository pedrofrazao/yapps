CC=java -jar jar/plantuml.jar
CCOPTS=
SRCS=$(wildcard *.puml)
OBJS=$(subst .puml,.png,$(SRCS))
TARGET=$(shell ls -t *.png| head -1)

all: ${OBJS}

%.png: %.puml
	$(CC) $(CCOPTS) $<

show:
	eog $(TARGET)