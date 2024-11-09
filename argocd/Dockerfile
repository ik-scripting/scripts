FROM alpine as sops

# renovate: datasource=github-releases depName=mozilla/sops versioning=loose
ENV SOPS_VERSION=v4.11.1
ENV SOPS_SHASUM="abracadabra"

RUN wget https://github.com/mozilla/sops/releases/download/${SOPS_VERSION}/sops-${SOPS_VERSION}.linux && \
    mv sops-${SOPS_VERSION}.linux /root/sops && \
    chmod a+x /root/sops && \
    sha256sum /root/sops && \
    echo "${SOPS_SHASUM}  /root/sops" | sha256sum -c

FROM argoproj/argocd:v2.13.0

USER root

RUN apt-get update && apt-get upgrade -y

RUN mv /usr/local/bin/helm /usr/local/bin/_helm

COPY --from=sops /root/sops /usr/local/bin/sops
COPY ./helm-wrapper.sh /usr/local/bin/helm

USER 999

COPY ./test /home/argocd/test-helm-wrapper

RUN cd /home/argocd/test-helm-wrapper && WRAPPER_PATH=helm ./test.sh > /tmp/actual.txt && diff /tmp/actual.txt expected.txt
