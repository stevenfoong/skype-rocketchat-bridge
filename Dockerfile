FROM centos:7.8.2003

# ensure local python is preferred over distribution python
ENV PATH /usr/local/bin:$PATH

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8

RUN yum -y install python3-3.6.8 supervisor-3.4.0

# Exposing container port for binding with host
EXPOSE 5000

# Initializing python script from supervisord
CMD ["supervisord","-c","/src/supervisor/service_script.conf"]
