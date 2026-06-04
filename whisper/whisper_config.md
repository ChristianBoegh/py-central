# Whisper Batch Config

## Input Files
- C:\whisper-input\file-1.mp3
- C:\whisper-input\file-2.mp3
- # C:\whisper-input\file-3.mp3


## Output Folder
C:\whisper-output

---

## Parameters

### Model
- [x] --model large
- [ ] --model large-v2
- [ ] --model large-v3
- [ ] --model medium
- [ ] --model small
- [ ] --model base
- [ ] --model tiny

### Task
- [x] --task transcribe
- [ ] --task translate

### Language
- [x] --language Danish
- [ ] --language English
- [ ] --language German
- [ ] --language French
- [ ] --language Spanish
- [ ] --language Norwegian
- [ ] --language Swedish

### Output Format
- [x] --output_format srt
- [ ] --output_format txt
- [ ] --output_format vtt
- [ ] --output_format tsv
- [ ] --output_format json
- [ ] --output_format all

### Timestamps
- [x] --word_timestamps True
- [ ] --word_timestamps False
- [ ] --highlight_words True
- [ ] --prepend_punctuations "\"'"¿([{-"
- [ ] --append_punctuations "\"'.。,，!！?？:：")]}、"

### Decoding
- [ ] --temperature 0
- [ ] --temperature 0.2
- [ ] --best_of 5
- [ ] --beam_size 5
- [ ] --patience 1.0
- [ ] --length_penalty 1.0
- [ ] --suppress_tokens -1
- [ ] --initial_prompt ""
- [ ] --condition_on_previous_text True
- [ ] --condition_on_previous_text False
- [ ] --compression_ratio_threshold 2.4
- [ ] --logprob_threshold -1.0
- [ ] --no_speech_threshold 0.6

### Compute
- [ ] --fp16 True
- [ ] --fp16 False
- [ ] --device cuda
- [ ] --device cpu
- [ ] --threads 4

### Misc
- [x] --verbose True
- [ ] --verbose False
