# Reuse the installed CUDA runtime; replace both Strata application components.
FROM local-ai/strata:0.2.0-beta
USER root
RUN rm -rf /opt/strata/terminal /opt/strata/components/engine
COPY terminal/ /opt/strata/terminal/
COPY engine/ /opt/strata/components/engine/
RUN chmod -R a+rX /opt/strata/terminal /opt/strata/components/engine
USER 1000:1000
WORKDIR /opt/strata/terminal
RUN ./python/bin/python3 strata.py --version \
 && ./python/bin/python3 -m serve.server --help >/dev/null \
 && test -x /opt/strata/components/engine/0.1.48-linux-x86_64-cuda-cuda13/strata \
 && test -x /opt/strata/components/engine/0.1.48-linux-x86_64-cuda-cuda13/strata-vision
LABEL org.opencontainers.image.version="0.2.4.2" \
      com.strata.engine="0.1.48-linux-x86_64-cuda-cuda13"
