# src/ui.py
"""Interface customtkinter : Capturer carte, Capturer visage, Verifier.
La verification tourne dans un thread pour ne pas figer la fenetre.
"""

import os
import tempfile
import threading

import customtkinter as ctk
import cv2

import capture
import pipeline

# Source ESP32. #TODO PROP. 6 : deplacer dans config.py (constante ESP32_URL).
ESP32_URL = "http://10.88.252.228/capture"

COLORS = {
    "VALIDE": "#2ecc71",
    "ANOMALIE": "#e74c3c",
    "VERIFICATION_COMPLEMENTAIRE": "#f39c12",
}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Verification d'identite")
        self.geometry("700x520")
        self.card_path = None
        self.face_path = None

        ctk.CTkButton(
            self, text="Capturer la carte", command=lambda: self._capture("card_path")
        ).pack(pady=6)
        ctk.CTkButton(
            self, text="Capturer le visage", command=lambda: self._capture("face_path")
        ).pack(pady=6)
        self.btn_verify = ctk.CTkButton(self, text="Verifier", command=self.on_verify)
        self.btn_verify.pack(pady=6)

        self.lbl_status = ctk.CTkLabel(
            self, text="Aucun resultat", font=ctk.CTkFont(size=22, weight="bold")
        )
        self.lbl_status.pack(pady=10)
        self.txt = ctk.CTkTextbox(self, height=220)
        self.txt.pack(fill="both", expand=True, padx=10, pady=6)

    def _capture(self, attr):
        img = capture.get_frame(ESP32_URL)
        if img is None:
            self.txt.insert("end", "ERREUR: capture ESP32 impossible.\n")
            self.txt.see("end")
            return
        fd, path = tempfile.mkstemp(suffix=".jpg", dir="data/samples")
        os.close(fd)
        cv2.imwrite(path, img)
        setattr(self, attr, path)
        self.txt.insert("end", f"Capture OK -> {path}\n")
        self.txt.see("end")

    def on_verify(self):
        if not (self.card_path and self.face_path):
            self.txt.insert("end", "Capture carte ET visage d'abord.\n")
            self.txt.see("end")
            return
        self.lbl_status.configure(text="Verification...", text_color="#7f8c8d")
        self.btn_verify.configure(state="disabled")
        threading.Thread(target=self._run_verify, daemon=True).start()

    def _run_verify(self):
        try:
            res = pipeline.verify(f"file:{self.card_path}", f"file:{self.face_path}")
            self.after(0, self._show, res)
        except Exception as e:
            self.after(
                0,
                self._show,
                {"status": "ANOMALIE", "reasons": [f"exception: {e}"], "scores": {}},
            )

    def _show(self, res):
        st = res["status"]
        self.lbl_status.configure(text=st, text_color=COLORS.get(st, "#7f8c8d"))
        self.txt.insert("end", f"\n--- {st} ---\n")
        for r in res["reasons"]:
            self.txt.insert("end", f"  - {r}\n")
        for k, v in res["scores"].items():
            self.txt.insert("end", f"  {k} = {v}\n")
        self.txt.see("end")
        self.btn_verify.configure(state="normal")


if __name__ == "__main__":
    App().mainloop()
