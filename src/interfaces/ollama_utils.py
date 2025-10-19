import os
import sys
import json
import requests

# 1) อ่านปลายทาง Ollama จาก env (ที่เราตั้งไว้ก่อนหน้า)
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "127.0.0.1:11434")

# 2) ตั้งค่าพื้นฐานของโมเดล
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")

# 3) helper: เรียก /api/generate แบบ non-stream (รับผลทีเดียว)
def generate(prompt: str, system: str | None = None, temperature: float = 0.7, max_tokens: int = 512) -> str:
    """
    เรียก Ollama /api/generate
    - prompt: ข้อความผู้ใช้
    - system: system prompt (ทางเลือก)
    - temperature: คุมความสุ่ม (0-1 ต่ำ=คงที่ สูง=ครีเอทีฟ)
    - max_tokens: จำนวน token ใหม่สูงสุด
    """
    url = f"http://{OLLAMA_HOST}/api/generate"
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    # ใส่ system prompt ถ้ามี
    if system:
        payload["system"] = system

    # ยิง HTTP POST ไปที่ Ollama
    res = requests.post(url, json=payload, timeout=600)
    res.raise_for_status()  # ถ้า HTTP != 200 จะ throw error
    data = res.json()       # แปลงเป็น dict
    return data.get("response", "").strip()

# 4) โหมด chat loop ง่าย ๆ ใน terminal
def chat_loop():
    """
    loop คุยทีละบรรทัด:
    - 'exit' หรือ Ctrl+C เพื่อออก
    """
    print(f"Connected to Ollama at http://{OLLAMA_HOST} with model '{MODEL}'")
    print("Type your message. Type 'exit' to quit.\n")

    # system prompt ตั้งกติกาให้บอท (เป็นทางเลือก)
    system_prompt = (
        "You are a helpful bilingual assistant. "
        "Reply in Thai by default but include concise English when useful."
    )

    while True:
        try:
            user_msg = input("คุณ: ").strip()
            if user_msg.lower() in {"exit", "quit"}:
                print("จบการสนทนา 👋")
                break

            # เรียก generate() เพื่อให้โมเดลตอบ
            reply = generate(user_msg, system=system_prompt, temperature=0.7, max_tokens=512)
            print("\nบอท:", reply, "\n")

        except KeyboardInterrupt:
            print("\nออกจากโปรแกรม 👋")
            break
        except requests.RequestException as e:
            print(f"\n[HTTP ERROR] {e}\n")
        except Exception as e:
            print(f"\n[ERROR] {type(e).__name__}: {e}\n")

if __name__ == "__main__":
    # 5) ทางลัด: ถ้าพิมพ์ argument ต่อท้ายไฟล์ จะถามครั้งเดียวแล้วจบ
    #    เช่น: python chat_ollama.py "สรุป LLM คืออะไร 3 บรรทัด"
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        ans = generate(prompt, system="ตอบสั้น ชัด และสุภาพ", temperature=0.7, max_tokens=256)
        print(ans)
    else:
        chat_loop()
