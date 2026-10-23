import json
import urllib.request


class OllamaLLM:
    def __init__(
        self,
        model: str = "llama3.2:3b",
        url: str = "http://localhost:11434/api/generate",
        timeout: int = 120,
    ) -> None:
        self.model = model
        self.url = url
        self.timeout = timeout

    def complete(self, prompt: str) -> str:
        body = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode()
        request = urllib.request.Request(
            self.url, data=body, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            return json.loads(response.read())["response"].strip()
