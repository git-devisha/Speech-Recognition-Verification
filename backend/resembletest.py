from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np
import os

encoder = VoiceEncoder()

def compare_speakers(file1: str, file2: str) -> dict:
    wav1 = preprocess_wav(file1)
    wav2 = preprocess_wav(file2)

    emb1 = encoder.embed_utterance(wav1)
    emb2 = encoder.embed_utterance(wav2)

    similarity = np.inner(emb1, emb2)
    return {
        "similarity": float(similarity),
        "same_speaker": similarity > 0.75  # Threshold can be adjusted
    }
