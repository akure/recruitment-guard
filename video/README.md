# RecruitmentGuard submission video

`recruitment-guard-submission.mp4` is the judge-facing solution video. It is 1920×1080, 3 minutes 55 seconds, with English documentary narration and deterministic storyboard frames. The narrative follows the required order: problem and baseline, realistic v2.1 execution, measured comparison, changelog, and hot take.

The video uses only synthetic repository data and committed benchmark values. The narrated live-model section is explicit that live quality and cost remain unclaimed because the provider-backed 12-case run did not complete within the bounded timeout.

## Rebuild

```bash
python3 video/make_assets.py
ffmpeg -y -f concat -safe 0 -i video/frames.txt -i video/narration.wav \
  -vf "format=yuv420p,fade=t=in:st=0:d=0.4,fade=t=out:st=210:d=0.8" \
  -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 160k -shortest \
  -movflags +faststart video/recruitment-guard-submission.mp4
```

The full written outline is [`SCRIPT.md`](SCRIPT.md), the spoken narration is [`narration.txt`](narration.txt), and the source frame generator is [`make_assets.py`](make_assets.py).
