from pathlib import Path
p = Path('/usr/local/lib/python3.12/dist-packages/vllm/model_executor/models/qwen3_5.py')
old = '        self.embed_tokens = VocabParallelEmbedding(\n            self.vocab_size,\n            config.hidden_size,\n        )'
new = '        self.embed_tokens = VocabParallelEmbedding(\n            self.vocab_size,\n            config.hidden_size,\n            quant_config=self.quant_config,\n            prefix=f"{prefix}.embed_tokens",\n        )'
src = p.read_text()
assert src.count(old) == 1, 'Qwen embedding constructor anchor drift'
p.write_text(src.replace(old, new, 1))
