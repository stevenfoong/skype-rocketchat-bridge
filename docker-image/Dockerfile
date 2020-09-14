FROM centos:7.8.2003

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8
RUN yum -y install epel-release
RUN yum -y install python3-3.6.8 supervisor wget git

# Exposing container port for binding with host
EXPOSE 5000

RUN mkdir -p /opt/skype-rocketchat-bridge \
  && cd /opt/skype-rocketchat-bridge \
  && touch /opt/skype-rocketchat-bridge/.tokens \
  && chmod g+rw /opt/skype-rocketchat-bridge/.tokens \
  && chmod o+rw /opt/skype-rocketchat-bridge/.tokens \
  && wget -O python-requirements.txt https://raw.githubusercontent.com/stevenfoong/skype-rocketchat-bridge/master/docker-image/python-requirements.txt \
  && wget -O skype-bridge.py https://raw.githubusercontent.com/stevenfoong/skype-rocketchat-bridge/master/skype-bridge.py \
  && wget -O rocketchat-bridge.py https://raw.githubusercontent.com/stevenfoong/skype-rocketchat-bridge/master/rocketchat-bridge.py \
  && pip3 install -r python-requirements.txt \
  && pip3 install -e "git+https://github.com/Terrance/SkPy@live-login-fix#egg=skpy" \
  && mkdir -p /opt/skype-rocketchat-bridge/data \
  && cd /opt/skype-rocketchat-bridge/data \
  && wget -O channel.py https://raw.githubusercontent.com/stevenfoong/skype-rocketchat-bridge/master/channel.py \
  && wget -O /etc/supervisord.conf https://raw.githubusercontent.com/foongws/skype-rocketchat-bridge/master/docker-image/supervisor-service-script.conf

CMD ["/usr/bin/supervisord"]

