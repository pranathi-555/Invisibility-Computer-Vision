import mediapipe as mp

print("=" * 60)
print("FILE:", mp.__file__)
print("VERSION:", getattr(mp, "__version__", None))
print("HAS SOLUTIONS:", hasattr(mp, "solutions"))
print("DIR:", dir(mp))
print("=" * 60)

raise SystemExit