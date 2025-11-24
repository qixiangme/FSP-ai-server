from llama_cpp import Llama
from typing import List, Dict

class GGUFModel:
    def __init__(self, model_path, max_ctx=2048, gpu_layers=20):
       self.model = Llama(
            model_path=model_path,
            n_ctx=max_ctx,
            n_gpu_layers=gpu_layers,
            verbose=False,
            
            # --- Continuous Batching 튜닝 파라미터 (4GB 최적화) ---
            n_parallel=1,          # (핵심 튜닝) GPU가 동시에 유지할 Context Slot 개수
            n_batch=512,           # Input Token 처리 배치 사이즈
            # --------------------------------------------------------
        )

    def chat(self, messages: List[Dict], max_tokens=256):
        """
        messages 형태:
        [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."}
        ]
        """
        try:
            result = self.model.create_chat_completion(
                messages=messages,
                temperature=0.7,
                top_p=0.9,
                max_tokens=max_tokens,
            )
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Generation Error: {e}")
            return "오류가 발생하여 응답을 생성할 수 없습니다."