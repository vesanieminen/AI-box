FROM nvidia/cuda:12.8.1-devel-ubuntu24.04@sha256:520292dbb4f755fd360766059e62956e9379485d9e073bbd2f6e3c20c270ed66 AS build
RUN apt-get update && apt-get install -y --no-install-recommends build-essential cmake git curl ca-certificates libssl-dev
ARG LLAMA_REVISION=620d2225cc436ab0b001e3200e590e3b286ef9ab
WORKDIR /src
RUN curl -fsSL https://github.com/ggml-org/llama.cpp/archive/${LLAMA_REVISION}.tar.gz | tar -xz --strip-components=1
RUN cmake -B build -DCMAKE_BUILD_TYPE=Release -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=86 -DGGML_NATIVE=OFF -DBUILD_SHARED_LIBS=OFF -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF -DLLAMA_BUILD_APP=OFF -DLLAMA_BUILD_UI=OFF -DLLAMA_USE_PREBUILT_UI=OFF \
    && cmake --build build --target llama-server --parallel 2
FROM nvidia/cuda:12.8.1-runtime-ubuntu24.04@sha256:ebef3c171eeef0298e4eb2e4be843105edf3b8b0ac45e0b43acee358e8046867
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 libssl3 curl && rm -rf /var/lib/apt/lists/*
COPY --from=build /src/build/bin/llama-server /app/llama-server
LABEL org.opencontainers.image.source="https://github.com/ggml-org/llama.cpp" \
      org.opencontainers.image.revision="620d2225cc436ab0b001e3200e590e3b286ef9ab"
ENTRYPOINT ["/app/llama-server"]
