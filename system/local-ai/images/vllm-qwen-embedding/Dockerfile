FROM vllm/vllm-openai@sha256:c2914767605584b6d8f45686b82de173ecc99e781897aa3d0a66dacd72c51ae1

# Connect Qwen's embedding layer to vLLM's existing compressed-tensors loader.
# The immutable base and exact-match replacement make the change reproducible.
RUN python3 -c 'from pathlib import Path; import py_compile; p = Path("/usr/local/lib/python3.12/dist-packages/vllm/model_executor/models/qwen3_5.py"); old = "        self.embed_tokens = VocabParallelEmbedding(\n            self.vocab_size,\n            config.hidden_size,\n        )"; new = "        self.embed_tokens = VocabParallelEmbedding(\n            self.vocab_size,\n            config.hidden_size,\n            quant_config=self.quant_config,\n            prefix=f\"{prefix}.embed_tokens\",\n        )"; text = p.read_text(); assert text.count(old) == 1, "Qwen embedding constructor changed"; p.write_text(text.replace(old, new)); py_compile.compile(str(p), doraise=True)'

LABEL org.opencontainers.image.description="vLLM 0.29.0 with Qwen packed embedding support"
LABEL org.opencontainers.image.source="https://github.com/vllm-project/vllm/blob/v0.29.0/vllm/model_executor/models/qwen3_5.py"
