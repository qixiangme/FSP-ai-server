from llama_cpp import Llama
from typing import List, Dict

class GGUFModel:
    def __init__(self, model_path, max_ctx=2048, gpu_layers=28,n_batch = 1024):
       self.model = Llama(
            model_path=model_path,
            n_ctx=max_ctx,
            n_gpu_layers=gpu_layers,
            verbose=False,
            
            n_parallel=1,          # (GPU가 동시에 유지할 Slot 개수
            n_batch= n_batch,           # Input Token 처리 사이즈
        )

    def chat(self, messages, max_tokens):
        output = self.model.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
        )

        return {
            "text": output["choices"][0]["message"]["content"],
            "prompt_tokens": output["usage"]["prompt_tokens"],
            "generated_tokens": output["usage"]["completion_tokens"],
            "total_tokens": output["usage"]["total_tokens"],
        }